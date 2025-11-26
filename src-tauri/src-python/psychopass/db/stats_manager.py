import time
from typing import Dict

class StatsManager:
    def __init__(self, user_db):
        self.user_db = user_db

    def _ensure_stats_row(self):
        """Make sure there's stats table"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("INSERT OR IGNORE INTO stats (id) VALUES (1)")

    def get(self) -> Dict:
        """Stats getter"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM stats WHERE id = 1")
            row = cursor.fetchone()
            if row is None:
                return {"messages": 0, "uploads": 0, "profiles": 0, "last_upload": None}
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))

    def update_auto(self):
        """Auto stats update"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
        
            cursor.execute("SELECT COUNT(*) FROM profile")
            profiles_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM message")
            messages_count = cursor.fetchone()[0]

            cursor.execute("SELECT uploads FROM stats WHERE id = 1")
            result = cursor.fetchone()
            uploads_count = result[0] + 1 if result else 1

            last_upload = time.strftime(r"%Y.%m.%d")

            cursor.execute("""
                UPDATE stats 
                SET messages = ?, uploads = ?, profiles = ?, last_upload = ?
                WHERE id = 1
            """, (messages_count, uploads_count, profiles_count, last_upload))
