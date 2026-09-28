import os
import pytest
from src.storage.private_memory import PrivateMemoryStore, PrivateMemoryRecord


def test_private_memory_crud(tmp_path):
    db_file = str(tmp_path / "private_memory.sqlite")
    store = PrivateMemoryStore(db_path=db_file)

    # 1. Add private record
    record = store.add("User A secret API key is 12345")
    assert record.id is not None
    assert record.content == "User A secret API key is 12345"
    assert record.created_at is not None

    # 2. Get private record by ID
    fetched = store.get(record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.content == record.content

    # 3. Search private memory
    results = store.search("secret")
    assert len(results) == 1
    assert results[0].id == record.id

    # 4. List all
    all_records = store.list_all()
    assert len(all_records) == 1

    # 5. Delete private record
    deleted = store.delete(record.id)
    assert deleted is True
    assert store.get(record.id) is None
    assert len(store.list_all()) == 0
