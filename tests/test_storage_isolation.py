import os
import pytest
from src.config import NodeConfig
from src.node import create_app
from src.storage.private_memory import PrivateMemoryStore
from src.storage.network_knowledge import NetworkKnowledgeStore


def test_physical_database_file_separation(tmp_path):
    priv_db = str(tmp_path / "private_memory.sqlite")
    net_db = str(tmp_path / "network_knowledge.sqlite")

    priv_store = PrivateMemoryStore(db_path=priv_db)
    net_store = NetworkKnowledgeStore(db_path=net_db, node_id="node-a")

    priv_store.add("My personal password")
    net_store.add("Public project guide", is_shareable=True)

    # Verify physical file existence
    assert os.path.exists(priv_db)
    assert os.path.exists(net_db)

    # Verify Network store cannot see private memory record
    assert len(net_store.search_shareable("password")) == 0
    assert len(net_store.list_all()) == 1
    assert net_store.list_all()[0].content == "Public project guide"

    # Verify Private store cannot see network knowledge record
    assert len(priv_store.search("guide")) == 0
    assert len(priv_store.list_all()) == 1
    assert priv_store.list_all()[0].content == "My personal password"


def test_per_node_storage_isolation(tmp_path):
    dir_a = str(tmp_path / "node_a")
    dir_b = str(tmp_path / "node_b")

    config_a = NodeConfig(node_id="node-a", node_name="Node A", port=8001, data_directory=dir_a)
    config_b = NodeConfig(node_id="node-b", node_name="Node B", port=8002, data_directory=dir_b)

    app_a = create_app(config_a)
    app_b = create_app(config_b)

    store_a_private: PrivateMemoryStore = app_a.state.private_memory
    store_b_private: PrivateMemoryStore = app_b.state.private_memory

    store_a_network: NetworkKnowledgeStore = app_a.state.network_knowledge
    store_b_network: NetworkKnowledgeStore = app_b.state.network_knowledge

    # Add records to Node A
    rec_a_priv = store_a_private.add("Node A personal secret")
    rec_a_net = store_a_network.add("Node A shared article", is_shareable=True)

    # Add records to Node B
    rec_b_priv = store_b_private.add("Node B personal diary")
    rec_b_net = store_b_network.add("Node B shared paper", is_shareable=True)

    # Verify physical subdirectory layout exists
    assert os.path.exists(os.path.join(dir_a, "private", "private_memory.sqlite"))
    assert os.path.exists(os.path.join(dir_a, "shareable", "network_knowledge.sqlite"))
    assert os.path.isdir(os.path.join(dir_a, "shareable", "articles"))
    assert os.path.exists(os.path.join(dir_b, "private", "private_memory.sqlite"))
    assert os.path.exists(os.path.join(dir_b, "shareable", "network_knowledge.sqlite"))
    assert os.path.isdir(os.path.join(dir_b, "shareable", "articles"))

    # Verify Node A isolated view
    assert len(store_a_private.list_all()) == 1
    assert store_a_private.get(rec_a_priv.id).content == "Node A personal secret"
    assert store_a_private.get(rec_b_priv.id) is None

    assert len(store_a_network.list_all()) == 1
    assert store_a_network.list_all()[0].source_node_id == "node-a"

    # Verify Node B isolated view
    assert len(store_b_private.list_all()) == 1
    assert store_b_private.get(rec_b_priv.id).content == "Node B personal diary"
    assert store_b_private.get(rec_a_priv.id) is None

    assert len(store_b_network.list_all()) == 1
    assert store_b_network.list_all()[0].source_node_id == "node-b"


def test_node_a_private_memory_distinct_from_shareable_knowledge(tmp_path):
    dir_a = str(tmp_path / "node_a")
    config_a = NodeConfig(node_id="node-a", node_name="Node A", port=8001, data_directory=dir_a)
    app_a = create_app(config_a)

    priv_store: PrivateMemoryStore = app_a.state.private_memory
    net_store: NetworkKnowledgeStore = app_a.state.network_knowledge

    # Add distinct records
    priv_rec = priv_store.add("Node A highly sensitive personal encryption key")
    share_rec = net_store.add("Node A public architecture document", is_shareable=True)

    # Prove physical databases are distinct files in distinct subdirectories
    assert priv_store.db_path != net_store.db_path
    assert "private" in priv_store.db_path
    assert "shareable" in net_store.db_path
    assert os.path.exists(priv_store.db_path)
    assert os.path.exists(net_store.db_path)

    # Prove content isolation: private memory != shareable knowledge
    assert priv_rec.content != share_rec.content
    assert len(priv_store.search("architecture")) == 0
    assert len(net_store.search_shareable("encryption key")) == 0
    assert priv_store.get(share_rec.id) is None
    assert net_store.get(priv_rec.id) is None


def test_node_b_cannot_retrieve_node_a_private_memory_via_network_query(tmp_path):
    """
    Requirement 14 & 15:
    Proves Node B cannot retrieve Node A private memory through network query,
    while Node B -> network query -> Node A -> shareable knowledge works cleanly.
    """
    from fastapi.testclient import TestClient

    dir_a = str(tmp_path / "node_a")
    dir_b = str(tmp_path / "node_b")

    config_a = NodeConfig(node_id="node-a", node_name="Crystal Node A", host="127.0.0.1", port=8001, data_directory=dir_a)
    config_b = NodeConfig(node_id="node-b", node_name="Crystal Node B", host="127.0.0.1", port=8002, data_directory=dir_b)

    app_a = create_app(config_a)
    app_b = create_app(config_b)

    priv_service_a = app_a.state.private_memory_service
    net_service_a = app_a.state.network_knowledge_service

    # Seed Node A with private and shareable records
    priv_service_a.add_private_memory("Node A confidential health diagnostic")
    net_service_a.add_knowledge("Node A quantum error correction algorithms", is_shareable=True, source_node_id="node-a")

    client_a = TestClient(app_a)
    client_b = TestClient(app_b)

    # 1. Direct query to Node A knowledge endpoint (used by peers over network)
    # Searching for private data must yield 0 results
    leak_check = client_a.post("/api/knowledge/query", json={"query": "confidential health"}).json()
    assert len(leak_check["results"]) == 0

    # Searching for shareable knowledge yields the record
    share_check = client_a.post("/api/knowledge/query", json={"query": "quantum"}).json()
    assert len(share_check["results"]) == 1
    assert share_check["results"][0]["source_node_id"] == "node-a"
    assert "quantum error correction" in share_check["results"][0]["content"]

    # 2. End-to-end network retrieval flow: Node B -> Node A
    conn_manager_b = app_b.state.connection_manager

    class DirectPeerClientStub:
        def __init__(self, test_client):
            self.test_client = test_client
        async def query_shareable_knowledge_async(self, query: str):
            resp = self.test_client.post("/api/knowledge/query", json={"query": query})
            if resp.status_code == 200:
                return resp.json().get("results", [])
            return []

    conn_manager_b._peer_clients["node-a"] = DirectPeerClientStub(client_a)

    # Node B network query for private keyword returns ZERO
    priv_net_query = client_b.post("/api/network/query", json={"query": "health"}).json()
    assert priv_net_query["count"] == 0
    assert len(priv_net_query["results"]) == 0

    # Node B network query for shareable knowledge returns Node A record with origin='peer'
    share_net_query = client_b.post("/api/network/query", json={"query": "quantum"}).json()
    assert share_net_query["count"] == 1
    rec = share_net_query["results"][0]
    assert rec["source_node_id"] == "node-a"
    assert rec["origin"] == "peer"
    assert rec["is_shareable"] is True
    assert "quantum error correction" in rec["content"]
