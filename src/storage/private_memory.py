import os
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


@dataclass
class PrivateMemoryRecord:
    """
    Private Personal Memory Record.
    Belongs strictly to the owning node and must NEVER be exposed across the network.
    """
    id: str
    content: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PrivateMemoryStore:
    """
    Isolated SQLite storage manager for Private Personal Memory.
    Operates on a node-local private_memory.sqlite database file.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS private_memory (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add(self, content: str) -> PrivateMemoryRecord:
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        record = PrivateMemoryRecord(
            id=record_id,
            content=content,
            created_at=now,
            updated_at=now,
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO private_memory (id, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (record.id, record.content, record.created_at, record.updated_at),
            )
            conn.commit()

        return record

    def get(self, record_id: str) -> Optional[PrivateMemoryRecord]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, content, created_at, updated_at FROM private_memory WHERE id = ?",
                (record_id,),
            )
            row = cursor.fetchone()
            if row:
                return PrivateMemoryRecord(
                    id=row["id"],
                    content=row["content"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
        return None

    def search(self, query: str) -> List[PrivateMemoryRecord]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, content, created_at, updated_at FROM private_memory WHERE content LIKE ? ORDER BY created_at DESC",
                (f"%{query}%",),
            )
            for row in cursor.fetchall():
                results.append(
                    PrivateMemoryRecord(
                        id=row["id"],
                        content=row["content"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def list_all(self) -> List[PrivateMemoryRecord]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, content, created_at, updated_at FROM private_memory ORDER BY created_at DESC"
            )
            for row in cursor.fetchall():
                results.append(
                    PrivateMemoryRecord(
                        id=row["id"],
                        content=row["content"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def delete(self, record_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM private_memory WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
