from fastapi.testclient import TestClient
from src.config import NodeConfig
from src.node import create_app


def test_independent_multi_node_configuration():
    config_a = NodeConfig(
        node_id="node-a",
        node_name="Crystal Node A",
        host="127.0.0.1",
        port=8001,
        data_directory="./data/node_a",
    )
    config_b = NodeConfig(
        node_id="node-b",
        node_name="Crystal Node B",
        host="127.0.0.1",
        port=8002,
        data_directory="./data/node_b",
    )
    config_c = NodeConfig(
        node_id="node-c",
        node_name="Crystal Node C",
        host="127.0.0.1",
        port=8003,
        data_directory="./data/node_c",
    )

    app_a = create_app(config_a)
    app_b = create_app(config_b)
    app_c = create_app(config_c)

    client_a = TestClient(app_a)
    client_b = TestClient(app_b)
    client_c = TestClient(app_c)

    resp_a = client_a.get("/api/health").json()
    resp_b = client_b.get("/api/health").json()
    resp_c = client_c.get("/api/health").json()

    assert resp_a["node_id"] == "node-a"
    assert resp_a["node_name"] == "Crystal Node A"

    assert resp_b["node_id"] == "node-b"
    assert resp_b["node_name"] == "Crystal Node B"

    assert resp_c["node_id"] == "node-c"
    assert resp_c["node_name"] == "Crystal Node C"
