from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTransport(ABC):
    """
    Abstract Base Transport Class.
    Defines the contract for node-to-node transport adapters.
    Future transport layers (e.g. HTTP/LAN, BLE/Mesh) will implement this interface.
    """

    @abstractmethod
    async def send(self, destination_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a payload to a target destination node.
        """
        pass

    @abstractmethod
    async def receive(self, source_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming payload from a source node.
        """
        pass

    async def discover(self) -> List[Dict[str, Any]]:
        """
        Discover reachable peer nodes on the transport layer.
        Base implementation returns an empty list until a transport provider implements discovery.
        """
        return []
