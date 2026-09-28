from fastapi import APIRouter, Request
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    node_id: str
    node_name: str


router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health(request: Request) -> HealthResponse:
    """
    Health check endpoint exposing minimal node status and identity.
    Does not expose sensitive system details, internal paths, or private data.
    """
    identity = getattr(request.app.state, "identity", None)
    if identity:
        node_id = identity.node_id
        node_name = identity.node_name
    else:
        node_id = "unknown"
        node_name = "Unknown Crystal Node"

    return HealthResponse(
        status="ok",
        node_id=node_id,
        node_name=node_name
    )
