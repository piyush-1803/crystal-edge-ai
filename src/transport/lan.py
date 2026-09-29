import asyncio
from typing import Any, Dict, List, Optional
import httpx

from src.transport.base import BaseTransport


class LANTransport(BaseTransport):
    """
    Local Network / LAN Transport implementation for Crystal.
    Discovers and communicates with peer Crystal nodes over HTTP/LAN.
    """

    def __init__(
        self,
        own_node_id: str,
        own_port: int,
        configured_peers: Optional[List[Dict[str, Any]]] = None,
        timeout: float = 1.0,
    ):
        self.own_node_id = own_node_id
        self.own_port = own_port
        self.configured_peers = configured_peers or []
        self.timeout = timeout

    async def send(self, destination_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a payload to a peer node if target host/port is specified in payload.
        """
        host = payload.get("host", "127.0.0.1")
        port = payload.get("port")
        path = payload.get("path", "/api/health")
        method = payload.get("method", "GET").upper()
        data = payload.get("data")

        if not port:
            return None

        url = f"http://{host}:{port}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "POST":
                    resp = await client.post(url, json=data)
                else:
                    resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError):
            return None
        return None

    async def receive(self, source_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming payload.
        """
        return {"status": "received", "source_id": source_id}

    async def probe_node(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Probe a single candidate address for a responsive Crystal node via /api/health.
        Returns node health metadata if valid and not self, otherwise None.
        """
        # Avoid probing own port on localhost
        if (host in ("127.0.0.1", "localhost", "0.0.0.0")) and port == self.own_port:
            return None

        url = f"http://{host}:{port}/api/health"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Validate Crystal health response contract
                    if data.get("status") == "ok" and "node_id" in data:
                        if data["node_id"] != self.own_node_id:
                            return {
                                "node_id": data["node_id"],
                                "node_name": data.get("node_name", f"Crystal Node ({data['node_id']})"),
                                "host": host,
                                "port": port,
                                "status": "available",
                            }
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass
        return None

    async def discover(self, additional_targets: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Scan candidate LAN endpoints for nearby active Crystal nodes:
        1. Configured peers from node config
        2. Common local edge ports (8001 through 8006) on 127.0.0.1
        3. Any explicitly supplied candidate targets
        """
        candidates: List[tuple[str, int]] = []
        seen = set()

        # 1. Configured peers
        for peer in self.configured_peers:
            h = peer.get("host", "127.0.0.1")
            p = peer.get("port")
            if p and (h, p) not in seen:
                candidates.append((h, int(p)))
                seen.add((h, int(p)))

        # 2. Local standard edge ports for multi-node dev/LAN
        for port in [8001, 8002, 8003, 8004, 8005]:
            if port != self.own_port and ("127.0.0.1", port) not in seen:
                candidates.append(("127.0.0.1", port))
                seen.add(("127.0.0.1", port))

        # 3. Additional targets
        if additional_targets:
            for target in additional_targets:
                h = target.get("host", "127.0.0.1")
                p = target.get("port")
                if p and (h, int(p)) not in seen:
                    candidates.append((h, int(p)))
                    seen.add((h, int(p)))

        # Run probes concurrently
        tasks = [self.probe_node(host, port) for host, port in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        discovered = []
        seen_nodes = set()
        for res in results:
            if isinstance(res, dict) and res.get("node_id"):
                nid = res["node_id"]
                if nid not in seen_nodes:
                    discovered.append(res)
                    seen_nodes.add(nid)

        return discovered
