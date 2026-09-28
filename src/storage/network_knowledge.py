import os
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


@dataclass
class NetworkKnowledgeRecord:
    """
    Shareable Network Knowledge Record.
    Contains explicit node source metadata and shareability flag.
    Intended for future distributed search queries across Crystal nodes.
    """
    id: str
    content: str
    source_node_id: str
    is_shareable: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NetworkKnowledgeStore:
    """
    Isolated SQLite storage manager for Shareable Network Knowledge.
    Operates on a node-local network_knowledge.sqlite database file.
    """

    def __init__(self, db_path: str, node_id: str):
        self.db_path = db_path
        self.node_id = node_id
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
                CREATE TABLE IF NOT EXISTS network_knowledge (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source_node_id TEXT NOT NULL,
                    is_shareable INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add(
        self,
        content: str,
        is_shareable: bool = True,
        source_node_id: Optional[str] = None,
    ) -> NetworkKnowledgeRecord:
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        node_origin = source_node_id or self.node_id

        record = NetworkKnowledgeRecord(
            id=record_id,
            content=content,
            source_node_id=node_origin,
            is_shareable=is_shareable,
            created_at=now,
            updated_at=now,
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO network_knowledge (id, content, source_node_id, is_shareable, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.content,
                    record.source_node_id,
                    1 if record.is_shareable else 0,
                    record.created_at,
                    record.updated_at,
                ),
            )
            conn.commit()

        return record

    def get(self, record_id: str) -> Optional[NetworkKnowledgeRecord]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, content, source_node_id, is_shareable, created_at, updated_at FROM network_knowledge WHERE id = ?",
                (record_id,),
            )
            row = cursor.fetchone()
            if row:
                return NetworkKnowledgeRecord(
                    id=row["id"],
                    content=row["content"],
                    source_node_id=row["source_node_id"],
                    is_shareable=bool(row["is_shareable"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
        return None

    def search_shareable(self, query: Optional[str] = None) -> List[NetworkKnowledgeRecord]:
        """
        Search explicitly shareable records (is_shareable = 1).
        This is the primary method that future network search adapters will invoke.
        """
        results = []
        with self._get_connection() as conn:
            if query:
                cursor = conn.execute(
                    """
                    SELECT id, content, source_node_id, is_shareable, created_at, updated_at
                    FROM network_knowledge
                    WHERE is_shareable = 1 AND content LIKE ?
                    ORDER BY created_at DESC
                    """,
                    (f"%{query}%",),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT id, content, source_node_id, is_shareable, created_at, updated_at
                    FROM network_knowledge
                    WHERE is_shareable = 1
                    ORDER BY created_at DESC
                    """
                )

            for row in cursor.fetchall():
                results.append(
                    NetworkKnowledgeRecord(
                        id=row["id"],
                        content=row["content"],
                        source_node_id=row["source_node_id"],
                        is_shareable=bool(row["is_shareable"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def list_all(self) -> List[NetworkKnowledgeRecord]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, content, source_node_id, is_shareable, created_at, updated_at FROM network_knowledge ORDER BY created_at DESC"
            )
            for row in cursor.fetchall():
                results.append(
                    NetworkKnowledgeRecord(
                        id=row["id"],
                        content=row["content"],
                        source_node_id=row["source_node_id"],
                        is_shareable=bool(row["is_shareable"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def delete(self, record_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM network_knowledge WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
