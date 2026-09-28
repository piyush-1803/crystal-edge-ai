import os
import json
import pytest
from src.config import NodeConfig


def test_default_config():
    config = NodeConfig()
    assert config.node_id == "node-a"
    assert config.node_name == "Crystal Node A"
    assert config.host == "127.0.0.1"
    assert config.port == 8001
    assert config.data_directory == "./data/node_a"


def test_config_from_file(tmp_path):
    config_data = {
        "node_id": "test-node",
        "node_name": "Test Crystal Node",
        "host": "0.0.0.0",
        "port": 9000,
        "data_directory": str(tmp_path / "data"),
    }
    file_path = tmp_path / "config.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)

    config = NodeConfig.from_file(str(file_path))
    assert config.node_id == "test-node"
    assert config.node_name == "Test Crystal Node"
    assert config.host == "0.0.0.0"
    assert config.port == 9000
    assert config.data_directory == str(tmp_path / "data")


def test_config_env_overrides(monkeypatch):
    monkeypatch.setenv("CRYSTAL_NODE_ID", "env-node")
    monkeypatch.setenv("CRYSTAL_NODE_NAME", "Env Node")
    monkeypatch.setenv("CRYSTAL_PORT", "9999")

    config = NodeConfig.load()
    assert config.node_id == "env-node"
    assert config.node_name == "Env Node"
    assert config.port == 9999
