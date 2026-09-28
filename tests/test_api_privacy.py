import pytest
from src.config import NodeConfig
from src.node import create_app


def get_all_app_routes(app):
    paths = []
    for route in app.routes:
        if hasattr(route, "path"):
            paths.append(route.path)
        if hasattr(route, "original_router") and hasattr(route.original_router, "routes"):
            for sub_route in route.original_router.routes:
                if hasattr(sub_route, "path"):
                    paths.append(sub_route.path)
    return paths


def test_no_private_memory_routes_exposed():
    config = NodeConfig(node_id="node-test", port=8000, data_directory="./data/test_privacy")
    app = create_app(config)

    # Inspect all registered HTTP route paths in FastAPI app
    route_paths = get_all_app_routes(app)

    # Verify health endpoint is present
    assert "/api/health" in route_paths

    # Verify NO private memory or sensitive endpoints exist in the routing table
    for path in route_paths:
        assert "private" not in path.lower()
        assert "secret" not in path.lower()
        assert "memory" not in path.lower()
