"""
Transport abstraction layer for Crystal Node.
Decouples application logic from networking implementations (LAN/HTTP, BLE, Mesh, etc.).
"""

from src.transport.base import BaseTransport

__all__ = ["BaseTransport"]
