"""
Transport abstraction layer for Crystal Node.
Decouples application logic from networking implementations (LAN/HTTP, BLE, Mesh, etc.).
"""

from src.transport.base import BaseTransport
from src.transport.lan import LANTransport

__all__ = ["BaseTransport", "LANTransport"]
