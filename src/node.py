import os
import sys
import argparse
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.config import NodeConfig
from src.identity import NodeIdentity
from src.api.health import router as health_router
from src.api.knowledge import router as knowledge_router
from src.api.network import router as network_router
from src.api.chat import router as chat_router
from src.inference import LocalModelService
from src.storage import PrivateMemoryStore, NetworkKnowledgeStore
from src.services import PrivateMemoryService, NetworkKnowledgeService
from src.network.connection_manager import ConnectionManager


def create_app(config: Optional[NodeConfig] = None) -> FastAPI:
    """
    Factory to create and configure a Crystal Node FastAPI instance.
    """
    if config is None:
        config = NodeConfig.load()

    # Ensure node data directories exist for both independent boundaries
    private_dir = os.path.join(config.data_directory, "private")
    shareable_dir = os.path.join(config.data_directory, "shareable")
    articles_dir = os.path.join(shareable_dir, "articles")
    os.makedirs(private_dir, exist_ok=True)
    os.makedirs(shareable_dir, exist_ok=True)
    os.makedirs(articles_dir, exist_ok=True)

    identity = NodeIdentity.from_config(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        if hasattr(app.state, "local_model_service") and app.state.local_model_service:
            app.state.local_model_service.stop_sidecar()

    app = FastAPI(
        title=f"Crystal Node - {identity.node_name}",
        version="0.1.0",
        description="Distributed Edge-AI Computing Node",
        lifespan=lifespan,
    )

    # Initialize isolated storage engines for node
    private_db_path = os.path.join(private_dir, "private_memory.sqlite")
    network_db_path = os.path.join(shareable_dir, "network_knowledge.sqlite")

    private_store = PrivateMemoryStore(db_path=private_db_path)
    network_store = NetworkKnowledgeStore(db_path=network_db_path, node_id=config.node_id)

    # Initialize local application services, connection manager, and model service
    private_service = PrivateMemoryService(store=private_store)
    network_service = NetworkKnowledgeService(store=network_store)
    connection_manager = ConnectionManager(
        own_node_id=config.node_id,
        own_port=config.port,
        configured_peers=config.peers,
    )
    model_service = LocalModelService(
        server_url=config.llm_server_url,
        binary_path=config.llm_binary_path,
        model_path=config.llm_model_path,
    )
    if config.llm_binary_path and config.llm_model_path:
        model_service.start_sidecar()

    # Attach config, identity, storage engines, services, connection manager, and model service to app state
    app.state.config = config
    app.state.identity = identity
    app.state.private_memory = private_store
    app.state.network_knowledge = network_store
    app.state.private_memory_service = private_service
    app.state.network_knowledge_service = network_service
    app.state.connection_manager = connection_manager
    app.state.local_model_service = model_service

    # Include API routers
    app.include_router(health_router)
    app.include_router(knowledge_router)
    app.include_router(network_router)
    app.include_router(chat_router)

    # Mount frontend static files
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        static_dir = os.path.join(base_dir, "static")
        if not os.path.exists(static_dir):
            static_dir = os.path.join(os.path.dirname(sys.executable), "static")
    else:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


def main():
    parser = argparse.ArgumentParser(description="Start a Crystal Edge-AI Node")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON configuration file (e.g., config/node_a.json)",
    )
    parser.add_argument("--host", type=str, default=None, help="Override listening host")
    parser.add_argument("--port", type=int, default=None, help="Override listening port")
    args = parser.parse_args()

    config = NodeConfig.load(config_path=args.config)
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    app = create_app(config)

    print(f"Starting Crystal Node '{config.node_name}' ({config.node_id}) on http://{config.host}:{config.port}")
    print(f"Data Directory: {os.path.abspath(config.data_directory)}")

    uvicorn.run(app, host=config.host, port=config.port, log_level="info")


if __name__ == "__main__":
    main()
