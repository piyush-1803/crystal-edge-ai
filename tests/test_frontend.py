import os
from fastapi.testclient import TestClient
from src.config import NodeConfig
from src.node import create_app


def test_frontend_served_at_root():
    config = NodeConfig(
        node_id="node-frontend-test",
        node_name="Frontend Test Node",
        host="127.0.0.1",
        port=8001,
        data_directory="./data/test_frontend",
    )
    app = create_app(config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    html = response.text

    # Verify essential branding & layout markers from design
    assert "Crystal" in html
    assert "Your private AI" in html
    assert "Local &amp; Private" in html or "Local & Private" in html
    assert "Explain how edge AI could reduce dependence on cloud systems." in html
    assert "Used from memory" in html
    assert "Ask Crystal anything..." in html
    assert "Crystal runs locally · Private by default · Memories stay on your device" in html


def test_frontend_logo_asset_served():
    config = NodeConfig(
        node_id="node-frontend-test",
        node_name="Frontend Test Node",
        host="127.0.0.1",
        port=8001,
        data_directory="./data/test_frontend",
    )
    app = create_app(config)
    client = TestClient(app)

    response = client.get("/assets/crystal-logo.png")
    assert response.status_code == 200
    assert "image/png" in response.headers.get("content-type", "")
    assert len(response.content) > 1000
