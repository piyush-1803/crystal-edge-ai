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
