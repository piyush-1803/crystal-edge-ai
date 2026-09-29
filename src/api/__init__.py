"""
API Routes Package for Crystal Node.
"""

from src.api.health import router as health_router
from src.api.knowledge import router as knowledge_router
from src.api.network import router as network_router
from src.api.chat import router as chat_router

__all__ = ["health_router", "knowledge_router", "network_router", "chat_router"]
