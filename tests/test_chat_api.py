import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.config import NodeConfig
from src.node import create_app
from src.inference.local_model_service import LocalModelService


@pytest.fixture
def test_node(tmp_path):
    data_dir = tmp_path / "node_chat_test"
    config = NodeConfig(
        node_id="node-test",
        node_name="Test Node",
        host="127.0.0.1",
        port=8099,
        data_directory=str(data_dir),
        llm_server_url="http://127.0.0.1:8080",
    )
    app = create_app(config)
    client = TestClient(app)
    return app, client, config


def test_chat_request_validation(test_node):
    app, client, config = test_node

    # 1. Empty string query
    res = client.post("/api/chat", json={"query": ""})
    assert res.status_code == 400
    assert "Query cannot be empty" in res.json()["detail"]

    # 2. Whitespace-only query
    res = client.post("/api/chat", json={"query": "   \n  \t  "})
    assert res.status_code == 400
    assert "Query cannot be empty" in res.json()["detail"]

    # 3. Missing query field
    res = client.post("/api/chat", json={})
    assert res.status_code == 422


def test_chat_model_unavailable_behavior(test_node):
    app, client, config = test_node

    # Explicitly verify behavior when local model server is unreachable
    with patch.object(
        app.state.local_model_service,
        "is_available",
        new=AsyncMock(return_value=False),
    ), patch.object(
        app.state.local_model_service,
        "generate_response",
        new=AsyncMock(return_value=None),
    ):
        res = client.post("/api/chat", json={"query": "What is quantum computing?"})
        assert res.status_code == 200
        data = res.json()
        assert data["model_available"] is False
        assert "Local model unavailable. Crystal is still running, but answer generation is not active." in data["answer"]
        assert isinstance(data["sources"], list)
        assert isinstance(data["memory_used"], bool)
        assert isinstance(data["network_used"], bool)


def test_chat_successful_generation_with_mocked_model(test_node):
    app, client, config = test_node

    # Ingest context into local shareable knowledge so generation is grounded
    net_service = app.state.network_knowledge_service
    net_service.add_knowledge(
        content="Title: Quantum computing\nWhat is quantum computing? Quantum computing harnesses quantum mechanics to process information exponentially faster.",
        is_shareable=True,
        source_node_id="node-test",
    )

    mock_answer = "Quantum computing harnesses quantum mechanics to process information exponentially faster for certain problems."

    with patch.object(
        app.state.local_model_service,
        "generate_response",
        new=AsyncMock(return_value=mock_answer),
    ) as mock_gen:
        res = client.post("/api/chat", json={"query": "What is quantum computing?"})
        assert res.status_code == 200
        data = res.json()
        assert data["model_available"] is True
        assert data["answer"] == mock_answer

        # Verify generate_response was called with prompt containing user query
        assert mock_gen.called
        call_kwargs = mock_gen.call_args.kwargs
        assert "What is quantum computing?" in call_kwargs.get("prompt", "")


def test_chat_network_context_retrieval(test_node):
    app, client, config = test_node

    # Ingest a shareable knowledge record
    net_service = app.state.network_knowledge_service
    net_service.add_knowledge(
        content="Title: Quantum computing\nQuantum computers use qubits rather than binary bits.",
        is_shareable=True,
        source_node_id="node-test",
    )

    with patch.object(
        app.state.local_model_service,
        "generate_response",
        new=AsyncMock(return_value="Answer based on quantum context."),
    ) as mock_gen:
        res = client.post("/api/chat", json={"query": "Quantum computers"})
        assert res.status_code == 200
        data = res.json()
        assert data["network_used"] is True
        assert len(data["sources"]) >= 1

        # Check source metadata
        first_source = data["sources"][0]
        assert "Quantum computers use qubits" in first_source["content"]
        assert first_source["source_node_id"] == "node-test"
        assert first_source["origin"] == "local"
        assert first_source["title"] == "Quantum computing"

        # Check that context was injected into the prompt
        call_prompt = mock_gen.call_args.kwargs.get("prompt", "")
        assert "Quantum computers use qubits" in call_prompt
        assert "node-test" in call_prompt


def test_chat_private_memory_privacy_boundary(test_node):
    app, client, config = test_node

    # Add a private personal memory to local store
    private_service = app.state.private_memory_service
    private_service.add_private_memory(
        content="My confidential doctor appointment is on Friday at 4pm."
    )

    with patch.object(
        app.state.local_model_service,
        "generate_response",
        new=AsyncMock(return_value="Your doctor appointment is Friday at 4pm."),
    ) as mock_gen:
        # Chat query matches private memory
        res = client.post("/api/chat", json={"query": "doctor appointment"})
        assert res.status_code == 200
        data = res.json()
        assert data["memory_used"] is True

        # Verify private memory was included in the local prompt
        call_prompt = mock_gen.call_args.kwargs.get("prompt", "")
        assert "confidential doctor appointment" in call_prompt

    # STRICT PRIVACY VERIFICATION:
    # Ensure this private memory is completely unreachable via the public shareable knowledge endpoint
    knowledge_res = client.post("/api/knowledge/query", json={"query": "doctor appointment"})
    assert knowledge_res.status_code == 200
    knowledge_data = knowledge_res.json()
    assert len(knowledge_data["results"]) == 0

    # Ensure private memory is unreachable via network query endpoint
    net_query_res = client.post("/api/network/query", json={"query": "doctor appointment"})
    assert net_query_res.status_code == 200
    net_data = net_query_res.json()
    assert len(net_data["results"]) == 0


def test_chat_no_context_returns_insufficient_context(test_node):
    app, client, config = test_node

    # Query with no matching context in memory or network
    with patch.object(
        app.state.local_model_service,
        "is_available",
        new=AsyncMock(return_value=True),
    ):
        res = client.post("/api/chat", json={"query": "What is the secret flight code?"})
        assert res.status_code == 200
        data = res.json()
        assert data["model_available"] is True
        assert data["network_used"] is False
        assert data["memory_used"] is False
        assert len(data["sources"]) == 0
        assert "Insufficient retrieved context" in data["answer"]


def test_chat_synthetic_unique_fact_peer_retrieval_and_grounding(tmp_path):
    """
    Test verifying that the local LLM acts strictly as an articulation layer
    using peer-retrieved knowledge for a unique synthetic fact.
    Fact exists ONLY on Node A: 'Crystal demo codename: AURORA-7429.'
    """
    # Configure Node A and Node B
    dir_a = tmp_path / "node_a"
    dir_b = tmp_path / "node_b"
    cfg_a = NodeConfig(node_id="node-a", node_name="Node A", host="127.0.0.1", port=8091, data_directory=str(dir_a))
    cfg_b = NodeConfig(node_id="node-b", node_name="Node B", host="127.0.0.1", port=8092, data_directory=str(dir_b))

    app_a = create_app(cfg_a)
    app_b = create_app(cfg_b)

    # 1. Add unique synthetic fact ONLY into Node A's shareable knowledge
    net_service_a = app_a.state.network_knowledge_service
    net_service_a.add_knowledge(
        content="Title: Demo Codename\nCrystal demo codename: AURORA-7429.",
        is_shareable=True,
        source_node_id="node-a",
    )

    client_b = TestClient(app_b)

    # 2. Mock peer client query on Node B to simulate connected Node A over network
    synthetic_peer_record = {
        "id": "synthetic-aurora-id",
        "content": "Title: Demo Codename\nCrystal demo codename: AURORA-7429.",
        "source_node_id": "node-a",
        "is_shareable": True,
        "created_at": "2026-09-29T22:00:00Z",
        "updated_at": "2026-09-29T22:00:00Z",
        "origin": "peer",
    }

    # Test WITH peer network context connected:
    with patch.object(
        app_b.state.connection_manager,
        "query_network",
        new=AsyncMock(return_value=[synthetic_peer_record]),
    ):
        with patch.object(
            app_b.state.local_model_service,
            "generate_response",
            new=AsyncMock(return_value="The Crystal demo codename is AURORA-7429."),
        ) as mock_gen_b:
            res = client_b.post("/api/chat", json={"query": "What is the Crystal demo codename?"})
            assert res.status_code == 200
            data = res.json()
            assert data["network_used"] is True
            assert data["model_available"] is True
            assert len(data["sources"]) == 1
            assert data["sources"][0]["source_node_id"] == "node-a"
            assert data["sources"][0]["origin"] == "peer"
            assert data["sources"][0]["title"] == "Demo Codename"
            assert "AURORA-7429" in data["answer"]

            # Verify the prompt fed to the model contained the peer knowledge
            called_prompt = mock_gen_b.call_args.kwargs.get("prompt", "")
            assert "AURORA-7429" in called_prompt
            assert "node-a" in called_prompt

    # Test WITHOUT network context available (disconnected):
    with patch.object(
        app_b.state.connection_manager,
        "query_network",
        new=AsyncMock(return_value=[]),
    ):
        with patch.object(
            app_b.state.local_model_service,
            "is_available",
            new=AsyncMock(return_value=True),
        ):
            res_no_net = client_b.post("/api/chat", json={"query": "What is the Crystal demo codename?"})
            assert res_no_net.status_code == 200
            data_no_net = res_no_net.json()
            assert data_no_net["network_used"] is False
            assert len(data_no_net["sources"]) == 0
            assert "AURORA-7429" not in data_no_net["answer"]
            assert "Insufficient retrieved context" in data_no_net["answer"]

