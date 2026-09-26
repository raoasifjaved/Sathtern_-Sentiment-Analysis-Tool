import json
import sqlite3
from datetime import datetime, timezone

class SentimentDB:
    def __init__(self, path: str):
        self.path = path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                sensitivity TEXT NOT NULL,
                items INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_analysis(self, result: dict):
        conn = self._connect()
        cur = conn.execute(
            """INSERT INTO analyses(title, sensitivity, items, data_json, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                result["title"],
                result["sensitivity"],
                len(result["items"]),
                json.dumps(result, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def list_analyses(self, limit=8):
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, title, sensitivity, items, created_at FROM analyses ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_analysis(self, analysis_id):
        conn = self._connect()
        row = conn.execute("SELECT data_json FROM analyses WHERE id=?", (analysis_id,)).fetchone()
        conn.close()
        return json.loads(row["data_json"]) if row else None
