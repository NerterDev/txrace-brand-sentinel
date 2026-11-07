"""Deterministic unit tests for Deduplicator SQLite store."""
import unittest

from src.engine.deduplicator import Deduplicator
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment


class TestDeduplicator(unittest.TestCase):
    def setUp(self) -> None:
        # In-memory database for fast deterministic isolated unit tests
        self.dedup = Deduplicator(db_path=":memory:")

        self.mention1 = MentionDTO(
            id="hash-aaa",
            platform=Platform.YOUTUBE,
            author="Author 1",
            title="Title 1",
            content="Content 1",
            url="https://youtube.com/watch?v=1",
            published_at="2026-11-06T12:00:00Z",
            scraped_at="2026-11-06T12:01:00Z",
            model_detected="CR125",
            brand_detected="Honda",
            intent=BuyingIntent.PROJETO_BUILD,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.8,
            priority_score=70.0,
            metrics=MentionMetrics(views=100),
        )

        self.mention2 = MentionDTO(
            id="hash-bbb",
            platform=Platform.FORUMS,
            author="Author 2",
            title="Title 2",
            content="Content 2",
            url="https://thumpertalk.com/2",
            published_at="2026-11-06T13:00:00Z",
            scraped_at="2026-11-06T13:01:00Z",
            model_detected="KX250",
            brand_detected="Kawasaki",
            intent=BuyingIntent.COMPRA_ATIVA,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.9,
            priority_score=85.0,
            metrics=MentionMetrics(views=250),
        )

    def tearDown(self) -> None:
        self.dedup.close()

    def test_initial_state_empty(self) -> None:
        self.assertEqual(self.dedup.get_count(), 0)
        self.assertFalse(self.dedup.is_duplicate("hash-aaa"))

    def test_registration_and_duplicate_detection(self) -> None:
        # First registration should succeed
        inserted = self.dedup.register(self.mention1)
        self.assertTrue(inserted)
        self.assertEqual(self.dedup.get_count(), 1)
        self.assertTrue(self.dedup.is_duplicate("hash-aaa"))

        # Second registration of same item should return False
        inserted_again = self.dedup.register(self.mention1)
        self.assertFalse(inserted_again)
        self.assertEqual(self.dedup.get_count(), 1)

    def test_filter_new(self) -> None:
        # Pre-seed mention1
        self.dedup.register(self.mention1)

        batch = [self.mention1, self.mention2]
        new_items = self.dedup.filter_new(batch)

        self.assertEqual(len(new_items), 1)
        self.assertEqual(new_items[0].id, "hash-bbb")
        self.assertEqual(self.dedup.get_count(), 2)

    def test_purge_older_than(self) -> None:
        self.dedup.register(self.mention1)
        # Purging older than 60 days should keep recent record
        deleted = self.dedup.purge_older_than(days=60)
        self.assertEqual(deleted, 0)
        self.assertEqual(self.dedup.get_count(), 1)


if __name__ == "__main__":
    unittest.main()

