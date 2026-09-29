from typing import List, Optional
from fastapi import APIRouter, Request
from pydantic import BaseModel


class KnowledgeQueryRequest(BaseModel):
    query: Optional[str] = None


class KnowledgeItemResponse(BaseModel):
    id: str
    content: str
    source_node_id: str
    is_shareable: bool
    created_at: str
    updated_at: str


class KnowledgeQueryResponse(BaseModel):
    results: List[KnowledgeItemResponse]


router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_shareable_knowledge(
    request: Request, body: KnowledgeQueryRequest
) -> KnowledgeQueryResponse:
    """
    Public endpoint for querying explicitly shareable network knowledge.
    Queries ONLY network_knowledge.sqlite via NetworkKnowledgeService.
    STRICT PRIVACY GUARANTEE: Does NOT access or expose private_memory.sqlite.
    """
    service = getattr(request.app.state, "network_knowledge_service", None)
    if not service:
        return KnowledgeQueryResponse(results=[])

    records = service.search_shareable_knowledge(query=body.query)
    results = [
        KnowledgeItemResponse(
            id=rec.id,
            content=rec.content,
            source_node_id=rec.source_node_id,
            is_shareable=rec.is_shareable,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )
        for rec in records
    ]
    return KnowledgeQueryResponse(results=results)
