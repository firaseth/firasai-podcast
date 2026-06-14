import sqlite3
import json
import os
from datetime import datetime

class DbTool:
    def __init__(self, db_path=None):
        if db_path is None:
            # Vercel is a read-only filesystem except for /tmp
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                db_path = "/tmp/firasai.db"
            else:
                db_path = "data/firasai.db"
        self.db_path = db_path
        
        # Ensure data directory exists
        dir_name = os.path.dirname(self.db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Episodes cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    topic TEXT,
                    status TEXT,
                    script TEXT,
                    research TEXT,
                    show_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Reports cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def cache_episode(self, episode_id: str, title: str, topic: str, status: str, script: str, research: dict, show_notes: dict):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO episodes (id, title, topic, status, script, research, show_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    episode_id,
                    title,
                    topic,
                    status,
                    script,
                    json.dumps(research),
                    json.dumps(show_notes)
                ))
                conn.commit()
                self.log_event("cache_episode", f"Cached episode {episode_id}: {title}")
        except Exception as e:
            print(f"[DbTool] Error caching episode: {e}")

    def cache_report(self, report: dict):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reports (content) VALUES (?)
                """, (json.dumps(report),))
                conn.commit()
                self.log_event("cache_report", "Cached weekly analytics report")
        except Exception as e:
            print(f"[DbTool] Error caching report: {e}")

    def log_event(self, event: str, details: str = None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_logs (event, details) VALUES (?, ?)
                """, (event, details))
                conn.commit()
        except Exception as e:
            print(f"[DbTool] Error logging event: {e}")

    def get_cached_episodes(self, limit=10):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DbTool] Error retrieving cached episodes: {e}")
            return []

    def get_cached_reports(self, limit=5):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DbTool] Error retrieving cached reports: {e}")
            return []

    def get_logs(self, limit=50):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DbTool] Error retrieving audit logs: {e}")
            return []
