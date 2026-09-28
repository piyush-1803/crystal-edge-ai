from typing import List, Optional
from src.storage.private_memory import PrivateMemoryStore, PrivateMemoryRecord


class PrivateMemoryService:
    """
    Local Application Service for Private Personal Memory.
    Encapsulates private memory operations.
    
    STRICT PRIVACY GUARANTEE:
    This service is intended exclusively for node-local application components (e.g. local AI prompt context).
    It must NEVER be exposed to network handlers, peer endpoints, or transport adapters.
    """

    def __init__(self, store: PrivateMemoryStore):
        self._store = store

    def add_private_memory(self, content: str) -> PrivateMemoryRecord:
        """Add a new private personal memory record."""
        return self._store.add(content=content)

    def get_private_memory(self, record_id: str) -> Optional[PrivateMemoryRecord]:
        """Retrieve a private personal memory record by ID."""
        return self._store.get(record_id=record_id)

    def search_private_memory(self, query: str) -> List[PrivateMemoryRecord]:
        """Search private personal memory records by query string."""
        return self._store.search(query=query)

    def list_private_memory(self) -> List[PrivateMemoryRecord]:
        """List all private personal memory records."""
        return self._store.list_all()

    def delete_private_memory(self, record_id: str) -> bool:
        """Delete a private personal memory record by ID."""
        return self._store.delete(record_id=record_id)
