import pytest
from fastapi.testclient import TestClient
from src.config import NodeConfig
from src.node import create_app
from src.services import PrivateMemoryService, NetworkKnowledgeService
from src.network.peer_client import PeerClient


def test_knowledge_query_endpoint(tmp_path):
    data_dir = str(tmp_path / "node_a")
    config = NodeConfig(node_id="node-a", node_name="Node A", port=8001, data_directory=data_dir)
    app = create_app(config)

    net_service: NetworkKnowledgeService = app.state.network_knowledge_service
    priv_service: PrivateMemoryService = app.state.private_memory_service

    # Add shareable knowledge to Node A
    rec_shareable = net_service.add_knowledge(
        content="Title: Quantum computing\n\nQuantum computers process information using qubits.",
        is_shareable=True,
        source_node_id="node-a",
    )

    # Add private secret memory to Node A with matching keywords
    rec_private = priv_service.add_private_memory("Quantum secret API master key 9999")

    client = TestClient(app)

    # 1. Query matching shareable article
    response = client.post("/api/knowledge/query", json={"query": "Quantum"})
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    results = data["results"]
    assert len(results) == 1

    item = results[0]
    assert item["id"] == rec_shareable.id
    assert item["source_node_id"] == "node-a"
    assert item["is_shareable"] is True
    assert "Quantum computers process information" in item["content"]

    # 2. PRIVACY TEST: Query for private secret keyword
    priv_response = client.post("/api/knowledge/query", json={"query": "master key"})
    assert priv_response.status_code == 200
    priv_data = priv_response.json()

    # Must return 0 results and NEVER expose private memory
    assert len(priv_data["results"]) == 0


def test_peer_client_clean_failure():
    # Attempt to query an unavailable port (e.g. port 59999)
    client = PeerClient(host="127.0.0.1", port=59999, timeout=1.0)
    results = client.query_shareable_knowledge("quantum")

    # Must fail cleanly and return an empty list without raising an unhandled exception
    assert isinstance(results, list)
    assert len(results) == 0
