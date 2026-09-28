from typing import List, Optional
from src.storage.network_knowledge import NetworkKnowledgeStore, NetworkKnowledgeRecord


class NetworkKnowledgeService:
    """
    Application Service for Shareable Network Knowledge.
    Encapsulates shareable knowledge operations.
    
    This service is eligible to be queried by future transport and network peer handlers
    because it operates strictly on shareable records and preserves node attribution.
    """

    def __init__(self, store: NetworkKnowledgeStore):
        self._store = store

    def add_knowledge(
        self,
        content: str,
        is_shareable: bool = True,
        source_node_id: Optional[str] = None,
    ) -> NetworkKnowledgeRecord:
        """Add a knowledge record to the network compartment."""
        return self._store.add(
            content=content,
            is_shareable=is_shareable,
            source_node_id=source_node_id,
        )

    def get_knowledge(self, record_id: str) -> Optional[NetworkKnowledgeRecord]:
        """Retrieve a network knowledge record by ID."""
        return self._store.get(record_id=record_id)

    def search_shareable_knowledge(
        self, query: Optional[str] = None
    ) -> List[NetworkKnowledgeRecord]:
        """
        Search explicitly shareable records (is_shareable = True).
        Preserves source_node_id on every returned record.
        """
        return self._store.search_shareable(query=query)

    def list_shareable_knowledge(self) -> List[NetworkKnowledgeRecord]:
        """List all explicitly shareable knowledge records."""
        return self._store.search_shareable(query=None)

    def delete_knowledge(self, record_id: str) -> bool:
        """Delete a network knowledge record by ID."""
        return self._store.delete(record_id=record_id)
