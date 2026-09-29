from typing import Any, Dict, List, Optional
import httpx


class PeerClient:
    """
    HTTP Peer Client for querying shareable network knowledge from remote Crystal nodes over LAN/HTTP.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"

    def query_shareable_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Sends a knowledge query request to the peer node's POST /api/knowledge/query endpoint.
        Returns a list of matching shareable knowledge records.
        Fails cleanly by returning an empty list if the target peer is unreachable or encounters an error.
        """
        url = f"{self.base_url}/api/knowledge/query"
        payload = {"query": query}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                return []
        except (httpx.RequestError, httpx.HTTPStatusError):
            # Graceful network failure handling
            return []

    async def query_shareable_knowledge_async(self, query: str) -> List[Dict[str, Any]]:
        """
        Asynchronous variant for querying a peer node.
        """
        url = f"{self.base_url}/api/knowledge/query"
        payload = {"query": query}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                return []
        except (httpx.RequestError, httpx.HTTPStatusError):
            return []
