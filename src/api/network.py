from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel


class ScanRequest(BaseModel):
    additional_targets: Optional[List[Dict[str, Any]]] = None


class ConnectRequest(BaseModel):
    host: str = "127.0.0.1"
    port: int
    node_id: Optional[str] = None


class DisconnectRequest(BaseModel):
    node_id: str


class NetworkKnowledgeQueryRequest(BaseModel):
    query: Optional[str] = None


router = APIRouter(prefix="/api/network", tags=["Network"])


@router.get("/status")
async def get_network_status(request: Request):
    """
    Get current network connection status, active transport, and connected nodes.
    """
    manager = getattr(request.app.state, "connection_manager", None)
    identity = getattr(request.app.state, "identity", None)

    connected_nodes = manager.get_connected_nodes() if manager else []
    own_node_id = identity.node_id if identity else "unknown"
    own_node_name = identity.node_name if identity else "Crystal Node"

    return {
        "transport": "local_lan",
        "own_node_id": own_node_id,
        "own_node_name": own_node_name,
        "connected_nodes": connected_nodes,
        "connected_count": len(connected_nodes),
    }


@router.post("/scan")
async def scan_network_nodes(request: Request, body: Optional[ScanRequest] = None):
    """
    Scan for nearby Crystal nodes on the local network (LAN).
    Real health checks are executed against candidate addresses.
    """
    manager = getattr(request.app.state, "connection_manager", None)
    if not manager:
        return {"discovered_nodes": []}

    targets = body.additional_targets if body else None
    discovered = await manager.scan_nodes(additional_targets=targets)
    return {
        "transport": "local_lan",
        "discovered_nodes": discovered,
        "count": len(discovered),
    }


@router.post("/connect")
async def connect_peer_node(request: Request, body: ConnectRequest):
    """
    Execute a real connection/health handshake with a target Crystal node over LAN.
    Only nodes that pass the /api/health probe become connected.
    """
    manager = getattr(request.app.state, "connection_manager", None)
    if not manager:
        raise HTTPException(status_code=500, detail="Connection Manager not initialized")

    result = await manager.connect_node(
        host=body.host,
        port=body.port,
        node_id=body.node_id,
    )
    return result


@router.post("/disconnect")
async def disconnect_peer_node(request: Request, body: DisconnectRequest):
    """
    Disconnect a peer node from the active session.
    """
    manager = getattr(request.app.state, "connection_manager", None)
    if not manager:
        return {"success": False}

    success = manager.disconnect_node(node_id=body.node_id)
    return {"success": success, "node_id": body.node_id}


@router.post("/query")
async def query_network_knowledge(request: Request, body: NetworkKnowledgeQueryRequest):
    """
    Query shareable knowledge across local node AND all actively connected peer nodes.
    STRICT PRIVACY: Never queries private memory.
    """
    manager = getattr(request.app.state, "connection_manager", None)
    net_service = getattr(request.app.state, "network_knowledge_service", None)

    if not manager:
        # Fallback to local shareable search
        if net_service:
            records = net_service.search_shareable_knowledge(query=body.query)
            return {
                "results": [
                    {
                        "id": r.id,
                        "content": r.content,
                        "source_node_id": r.source_node_id,
                        "is_shareable": r.is_shareable,
                        "created_at": r.created_at,
                        "updated_at": r.updated_at,
                        "origin": "local",
                    }
                    for r in records
                ]
            }
        return {"results": []}

    results = await manager.query_network(
        query=body.query,
        local_service=net_service,
    )
    return {
        "results": results,
        "total": len(results),
        "count": len(results),
    }
