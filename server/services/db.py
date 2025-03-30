import sqlite3
import json
from contextlib import contextmanager
from typing import List
from core.memory.entry import MemoryEntry 


class MemoryDatabase:
    """SQLite记忆存储实现"""

    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                session_id TEXT,
                timestamp REAL,
                role TEXT,
                content TEXT,
                metadata TEXT,
                PRIMARY KEY (session_id, timestamp)
            )
        """)

    @contextmanager
    def cursor(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        finally:
            cursor.close()

    def save_entry(self, session_id: str, entry: MemoryEntry):
        with self.cursor() as c:
            c.execute("""
                INSERT INTO memories VALUES (?, ?, ?, ?, ?)
            """, (
                str(session_id),
                entry.timestamp,
                entry.role,
                entry.content,
                json.dumps(entry.metadata)
            ))

    def get_entries(self, session_id: str, limit=100) -> List[MemoryEntry]:
        with self.cursor() as c:
            c.execute("""
                SELECT * FROM memories
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (str(session_id), limit))

            return [
                MemoryEntry(
                    timestamp=row[1],
                    role=row[2],
                    content=row[3],
                    metadata=json.loads(row[4])
                ) for row in c.fetchall()
            ]
