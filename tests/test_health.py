from fastapi.testclient import TestClient
from src.config import NodeConfig
from src.node import create_app


def test_health_endpoint():
    config = NodeConfig(
        node_id="node-health-test",
        node_name="Health Test Node",
        host="127.0.0.1",
        port=8001,
        data_directory="./data/test_health",
    )
    app = create_app(config)
    client = TestClient(app)

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["node_id"] == "node-health-test"
    assert data["node_name"] == "Health Test Node"
    # Ensure sensitive data is not exposed
    assert "data_directory" not in data
    assert "host" not in data
    assert "port" not in data
