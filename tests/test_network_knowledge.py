import os
import pytest
from src.storage.network_knowledge import NetworkKnowledgeStore, NetworkKnowledgeRecord


def test_network_knowledge_crud(tmp_path):
    db_file = str(tmp_path / "network_knowledge.sqlite")
    store = NetworkKnowledgeStore(db_path=db_file, node_id="node-a")

    # 1. Add shareable network knowledge
    rec1 = store.add("Crystal project documentation v1.0", is_shareable=True)
    assert rec1.id is not None
    assert rec1.content == "Crystal project documentation v1.0"
    assert rec1.source_node_id == "node-a"
    assert rec1.is_shareable is True

    # 2. Add non-shareable item to network knowledge store (draft/unlisted)
    rec2 = store.add("Internal draft notes", is_shareable=False)
    assert rec2.is_shareable is False

    # 3. Search shareable records only
    shareable_results = store.search_shareable("documentation")
    assert len(shareable_results) == 1
    assert shareable_results[0].id == rec1.id

    # Search shareable should NOT return non-shareable items
    all_shareable = store.search_shareable()
    assert len(all_shareable) == 1
    assert all_shareable[0].id == rec1.id

    # 4. List all includes both shareable and unlisted
    assert len(store.list_all()) == 2
