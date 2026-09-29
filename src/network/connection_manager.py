import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

from src.transport.base import BaseTransport
from src.transport.lan import LANTransport
from src.network.peer_client import PeerClient


@dataclass
class ConnectedNode:
    node_id: str
    node_name: str
    host: str
    port: int
    transport_type: str = "local_lan"
    status: str = "connected"
    connected_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConnectionManager:
    """
    Transport-Agnostic Connection Manager for Crystal.
    Orchestrates discovery, connection lifecycle, and cross-node communication.
    Supports Local Network (LAN) transport currently, with clean extension points
    for future transports (Internet, BLE/Mesh).
    """

    def __init__(
        self,
        own_node_id: str,
        own_port: int,
        configured_peers: Optional[List[Dict[str, Any]]] = None,
        lan_transport: Optional[LANTransport] = None,
    ):
        self.own_node_id = own_node_id
        self.own_port = own_port
        self.lan_transport = lan_transport or LANTransport(
            own_node_id=own_node_id,
            own_port=own_port,
            configured_peers=configured_peers or [],
        )
        self._connected_nodes: Dict[str, ConnectedNode] = {}
        self._peer_clients: Dict[str, PeerClient] = {}

    def get_transport(self, transport_type: str = "local_lan") -> BaseTransport:
        """Retrieve the appropriate transport engine."""
        if transport_type == "local_lan":
            return self.lan_transport
        raise ValueError(f"Unsupported transport type: {transport_type}")

    async def scan_nodes(
        self,
        additional_targets: Optional[List[Dict[str, Any]]] = None,
        transport_type: str = "local_lan",
    ) -> List[Dict[str, Any]]:
        """
        Scan for nearby available Crystal nodes using the configured transport.
        Reflects real connectivity: nodes that fail the health probe are not returned.
        """
        transport = self.get_transport(transport_type)
        discovered = await transport.discover(additional_targets=additional_targets)

        # Re-check connected status for each discovered node
        results = []
        for node in discovered:
            nid = node["node_id"]
            if nid in self._connected_nodes:
                node_copy = dict(node)
                node_copy["status"] = "connected"
                results.append(node_copy)
            else:
                results.append(node)

        return results

    async def connect_node(
        self,
        host: str,
        port: int,
        node_id: Optional[str] = None,
        transport_type: str = "local_lan",
    ) -> Dict[str, Any]:
        """
        Perform an authentic connection handshake with a target Crystal node.
        Only marks the node as 'Connected' upon successful health verification.
        """
        transport = self.get_transport(transport_type)
        if isinstance(transport, LANTransport):
            probe_result = await transport.probe_node(host=host, port=port)
        else:
            probe_result = None

        if not probe_result:
            return {
                "success": False,
                "error": f"Couldn't connect to Crystal node at {host}:{port}. Check that Crystal is running on the same local network.",
            }

        target_node_id = probe_result["node_id"]
        target_node_name = probe_result["node_name"]

        # Store connected node and peer client
        conn = ConnectedNode(
            node_id=target_node_id,
            node_name=target_node_name,
            host=host,
            port=port,
            transport_type=transport_type,
            status="connected",
        )
        self._connected_nodes[target_node_id] = conn
        self._peer_clients[target_node_id] = PeerClient(host=host, port=port)

        return {
            "success": True,
            "node": conn.to_dict(),
        }

    def disconnect_node(self, node_id: str) -> bool:
        """
        Disconnect a connected node from the active session.
        """
        if node_id in self._connected_nodes:
            del self._connected_nodes[node_id]
            if node_id in self._peer_clients:
                del self._peer_clients[node_id]
            return True
        return False

    def get_connected_nodes(self) -> List[Dict[str, Any]]:
        """
        List all currently connected nodes.
        """
        return [node.to_dict() for node in self._connected_nodes.values()]

    def is_connected(self, node_id: str) -> bool:
        """Check if a specific node is currently connected."""
        return node_id in self._connected_nodes

    async def query_network(
        self,
        query: Optional[str] = None,
        local_service: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query shareable network knowledge across the local node AND all actively connected peer nodes.
        STRICT PRIVACY: Never queries private memory.
        """
        aggregated_results: List[Dict[str, Any]] = []

        # 1. Query local shareable knowledge if local service provided
        if local_service:
            local_records = local_service.search_shareable_knowledge(query=query)
            for rec in local_records:
                aggregated_results.append({
                    "id": rec.id,
                    "content": rec.content,
                    "source_node_id": rec.source_node_id,
                    "is_shareable": rec.is_shareable,
                    "created_at": rec.created_at,
                    "updated_at": rec.updated_at,
                    "origin": "local",
                })

        # 2. Query each connected peer over LAN using PeerClient
        for node_id, client in self._peer_clients.items():
            peer_results = await client.query_shareable_knowledge_async(query=query or "")
            for item in peer_results:
                item_copy = dict(item)
                item_copy["origin"] = "peer"
                aggregated_results.append(item_copy)

        return aggregated_results
