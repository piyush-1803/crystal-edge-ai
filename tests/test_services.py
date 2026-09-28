import os
import pytest
from src.config import NodeConfig
from src.node import create_app
from src.storage import PrivateMemoryStore, NetworkKnowledgeStore
from src.services import PrivateMemoryService, NetworkKnowledgeService


def test_private_memory_service_crud(tmp_path):
    db_file = str(tmp_path / "private_memory.sqlite")
    store = PrivateMemoryStore(db_path=db_file)
    service = PrivateMemoryService(store=store)

    # 1. Create
    rec = service.add_private_memory("My secret personal note")
    assert rec.id is not None
    assert rec.content == "My secret personal note"

    # 2. Retrieve
    fetched = service.get_private_memory(rec.id)
    assert fetched is not None
    assert fetched.content == "My secret personal note"

    # 3. Search
    results = service.search_private_memory("secret")
    assert len(results) == 1
    assert results[0].id == rec.id

    # 4. List
    assert len(service.list_private_memory()) == 1

    # 5. Delete
    deleted = service.delete_private_memory(rec.id)
    assert deleted is True
    assert service.get_private_memory(rec.id) is None


def test_network_knowledge_service_shareable(tmp_path):
    db_file = str(tmp_path / "network_knowledge.sqlite")
    store = NetworkKnowledgeStore(db_path=db_file, node_id="node-a")
    service = NetworkKnowledgeService(store=store)

    # 1. Create shareable
    rec1 = service.add_knowledge("Shareable node-a dataset", is_shareable=True)
    assert rec1.source_node_id == "node-a"
    assert rec1.is_shareable is True

    # 2. Create non-shareable draft
    rec2 = service.add_knowledge("Internal unlisted draft", is_shareable=False)
    assert rec2.is_shareable is False

    # 3. Search shareable knowledge only
    results = service.search_shareable_knowledge()
    assert len(results) == 1
    assert results[0].id == rec1.id
    assert results[0].source_node_id == "node-a"


def test_multi_node_service_isolation(tmp_path):
    dir_a = str(tmp_path / "node_a")
    dir_b = str(tmp_path / "node_b")

    config_a = NodeConfig(node_id="node-a", node_name="Node A", port=8001, data_directory=dir_a)
    config_b = NodeConfig(node_id="node-b", node_name="Node B", port=8002, data_directory=dir_b)

    app_a = create_app(config_a)
    app_b = create_app(config_b)

    service_a_private: PrivateMemoryService = app_a.state.private_memory_service
    service_b_private: PrivateMemoryService = app_b.state.private_memory_service

    service_a_net: NetworkKnowledgeService = app_a.state.network_knowledge_service
    service_b_net: NetworkKnowledgeService = app_b.state.network_knowledge_service

    # Add records to Node A
    rec_a_priv = service_a_private.add_private_memory("Node A private secret")
    rec_a_net = service_a_net.add_knowledge("Node A public paper", is_shareable=True)

    # Add records to Node B
    rec_b_priv = service_b_private.add_private_memory("Node B private secret")
    rec_b_net = service_b_net.add_knowledge("Node B public paper", is_shareable=True)

    # Verify Node A cannot see Node B data
    assert service_a_private.get_private_memory(rec_b_priv.id) is None
    assert len(service_a_private.list_private_memory()) == 1

    net_a_results = service_a_net.list_shareable_knowledge()
    assert len(net_a_results) == 1
    assert net_a_results[0].source_node_id == "node-a"

    # Verify Node B cannot see Node A data
    assert service_b_private.get_private_memory(rec_a_priv.id) is None
    assert len(service_b_private.list_private_memory()) == 1

    net_b_results = service_b_net.list_shareable_knowledge()
    assert len(net_b_results) == 1
    assert net_b_results[0].source_node_id == "node-b"
