"""SQLite-backed SHA-256 deduplication and persistence store for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from src.models.mention import MentionDTO

logger = logging.getLogger(__name__)


class Deduplicator:
    """Manages mention deduplication using an ACID-compliant local SQLite database."""

    def __init__(self, db_path: str = "data/sentinel_cache.sqlite") -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the database schema if not present."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_mentions (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT,
                    scraped_at TEXT,
                    author TEXT,
                    model_detected TEXT,
                    intent TEXT,
                    priority_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_seen_url ON seen_mentions(url);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_seen_platform ON seen_mentions(platform);")

    def is_duplicate(self, mention_id: str) -> bool:
        """Checks if a mention ID is already recorded in the database."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM seen_mentions WHERE id = ?", (mention_id,))
        return cur.fetchone() is not None

    def register(self, mention: MentionDTO) -> bool:
        """Registers a new mention. Returns True if inserted, False if already present."""
        if self.is_duplicate(mention.id):
            return False

        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO seen_mentions (
                        id, platform, url, published_at, scraped_at, author,
                        model_detected, intent, priority_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mention.id,
                        mention.platform.value if hasattr(mention.platform, "value") else str(mention.platform),
                        mention.url,
                        mention.published_at,
                        mention.scraped_at,
                        mention.author,
                        mention.model_detected,
                        mention.intent.value if hasattr(mention.intent, "value") else str(mention.intent),
                        mention.priority_score,
                    ),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def filter_new(self, mentions: list[MentionDTO]) -> list[MentionDTO]:
        """Filters a list of mentions, returning only previously unseen ones and registering them."""
        new_mentions: list[MentionDTO] = []
        for m in mentions:
            if self.register(m):
                new_mentions.append(m)
        return new_mentions

    def get_count(self) -> int:
        """Returns the total number of seen mentions in the cache."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM seen_mentions")
        row = cur.fetchone()
        return row[0] if row else 0

    def purge_older_than(self, days: int = 60) -> int:
        """Purges records older than specified days to keep the database size lean."""
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM seen_mentions WHERE created_at < datetime('now', ?)",
                (f"-{days} days",),
            )
            deleted = cur.rowcount
        logger.info("Purged %d historical records older than %d days.", deleted, days)
        return deleted

    def close(self) -> None:
        """Closes the SQLite database connection."""
        self.conn.close()

