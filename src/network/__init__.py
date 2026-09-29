"""
Network Communication Package for Crystal Node.
Provides peer client abstractions for HTTP/LAN peer interaction.
"""

from src.network.peer_client import PeerClient
from src.network.connection_manager import ConnectionManager, ConnectedNode

__all__ = ["PeerClient", "ConnectionManager", "ConnectedNode"]
