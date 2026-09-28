from src.config import NodeConfig
from src.identity import NodeIdentity


def test_node_identity_from_config():
    config = NodeConfig(
        node_id="node-x",
        node_name="Node X",
        host="127.0.0.1",
        port=8080,
        data_directory="./data/node_x",
    )
    identity = NodeIdentity.from_config(config)

    assert identity.node_id == "node-x"
    assert identity.node_name == "Node X"
    assert identity.host == "127.0.0.1"
    assert identity.port == 8080


def test_node_identity_to_dict():
    identity = NodeIdentity(
        node_id="node-y",
        node_name="Node Y",
        host="192.168.1.100",
        port=8081,
    )
    data = identity.to_dict()
    assert data == {
        "node_id": "node-y",
        "node_name": "Node Y",
        "host": "192.168.1.100",
        "port": 8081,
    }
