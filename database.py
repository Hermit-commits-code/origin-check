import sqlite3


class DatabaseManager:
    """v0.7.0: Handling Forensic data persistance by using SQLite3"""

    def __init__(self, db_path="miner_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the schema if it doesn't already exist."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("""
                               CREATE TABLE IF NOT EXISTS commit_cache(
                               hash TEXT PRIMARY_KEY,
                               comment_ratio REAL,
                               is_suspicious INTEGER,
                               entropy REAL,
                               timestamp TEXT
                               )
                               """)
            connection.commit()

    def get_cached_commit(self, commit_hash):
        """Returns cached data for a hash or returns None"""
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                "SELECT comment_ratio, is_suspicious, entropy FROM commit_cache WHERE hash = ?",
                (commit_hash,),
            )
            return cursor.fetchone()

    def save_commit(self, commit_hash, ratio, suspicious, entropy):
        """Persists analyzed forensic data."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO commit_cache VALUES (?,?,?,?,?)",
                (commit_hash, ratio, int(suspicious), entropy, "now"),
            )
            connection.commit()
