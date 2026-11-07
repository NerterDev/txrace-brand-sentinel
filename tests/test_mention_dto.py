"""Deterministic unit tests for MentionDTO model and validation."""
import unittest
from dataclasses import FrozenInstanceError

from src.models.mention import (
    BuyingIntent,
    MentionDTO,
    MentionMetrics,
    Platform,
    Sentiment,
)


class TestMentionDTO(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_metrics = MentionMetrics(views=1250, comments=45, likes=230, shares=12)
        self.sample_mention = MentionDTO(
            id="test-sha-12345",
            platform=Platform.YOUTUBE,
            author="Chase Builds Bikes",
            title="CR125 Transformation with TXRACE!",
            content="Fitment on the 2003 CR was dead simple, seat is amazing...",
            url="https://youtube.com/watch?v=sample123",
            published_at="2026-11-03T14:30:00Z",
            scraped_at="2026-11-06T22:50:00Z",
            model_detected="CR125",
            brand_detected="Honda",
            intent=BuyingIntent.PROJETO_BUILD,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.95,
            priority_score=85.0,
            metrics=self.sample_metrics,
            author_url="https://youtube.com/@chasebuildsbikes",
            generation="Gen25",
            geo_country="United States",
            geo_city="San Diego",
            is_viral=False,
            recommended_reply="Thanks Chase! For 2003 CR125 Gen25 kits, visit our official store: txrace.com",
        )

    def test_mention_dto_creation(self) -> None:
        self.assertEqual(self.sample_mention.id, "test-sha-12345")
        self.assertEqual(self.sample_mention.platform, Platform.YOUTUBE)
        self.assertEqual(self.sample_mention.model_detected, "CR125")
        self.assertEqual(self.sample_mention.brand_detected, "Honda")
        self.assertEqual(self.sample_mention.intent, BuyingIntent.PROJETO_BUILD)
        self.assertEqual(self.sample_mention.sentiment, Sentiment.POSITIVE)
        self.assertFalse(self.sample_mention.is_viral)

    def test_mention_dto_immutability(self) -> None:
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            self.sample_mention.model_detected = "CR250"  # type: ignore

    def test_deterministic_hash_generation(self) -> None:
        h1 = MentionDTO.generate_id("youtube", "https://youtube.com/watch?v=abc", "Amazing CR125 restyle kit!")
        h2 = MentionDTO.generate_id("YOUTUBE", "https://youtube.com/watch?v=abc", "Amazing CR125 restyle kit!")
        h3 = MentionDTO.generate_id("youtube", "https://youtube.com/watch?v=diff", "Amazing CR125 restyle kit!")
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)
        self.assertEqual(len(h1), 64)

    def test_to_dict_and_from_dict_roundtrip(self) -> None:
        data = self.sample_mention.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], "test-sha-12345")
        self.assertEqual(data["platform"], "youtube")
        self.assertEqual(data["intent"], "PROJETO_BUILD")
        self.assertEqual(data["sentiment"], "POSITIVE")
        self.assertEqual(data["metrics"]["views"], 1250)

        restored = MentionDTO.from_dict(data)
        self.assertEqual(restored.id, self.sample_mention.id)
        self.assertEqual(restored.platform, self.sample_mention.platform)
        self.assertEqual(restored.author, self.sample_mention.author)
        self.assertEqual(restored.model_detected, self.sample_mention.model_detected)
        self.assertEqual(restored.metrics.views, 1250)

    def test_score_clipping(self) -> None:
        dto = MentionDTO(
            id="clip-test",
            platform=Platform.FORUMS,
            author="ThumperUser",
            title="Question",
            content="Where to buy?",
            url="https://thumpertalk.com/p/1",
            published_at="2026-11-06T10:00:00Z",
            scraped_at="2026-11-06T12:00:00Z",
            model_detected="CRF250X",
            brand_detected="Honda",
            intent=BuyingIntent.COMPRA_ATIVA,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=1.5,  # Exceeds 1.0 -> should clip to 1.0
            priority_score=150.0,  # Exceeds 100.0 -> should clip to 100.0
            metrics=MentionMetrics(views=50),
        )
        self.assertEqual(dto.sentiment_score, 1.0)
        self.assertEqual(dto.priority_score, 100.0)

    def test_auto_viral_flag(self) -> None:
        viral_dto = MentionDTO(
            id="viral-test",
            platform=Platform.TIKTOK,
            author="MotoViral",
            title="Insane Restyle",
            content="Watch this bike turn from 2002 to 2025 in 10 seconds",
            url="https://tiktok.com/@motoviral/video/1",
            published_at="2026-11-05T00:00:00Z",
            scraped_at="2026-11-06T00:00:00Z",
            model_detected="KX250",
            brand_detected="Kawasaki",
            intent=BuyingIntent.VIRAL,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.9,
            priority_score=90.0,
            metrics=MentionMetrics(views=45000, comments=800, likes=12000, shares=3200),
            is_viral=False,  # auto-recalculated by __post_init__
        )
        self.assertTrue(viral_dto.is_viral)

    def test_negative_metrics_rejection(self) -> None:
        with self.assertRaises(ValueError):
            MentionMetrics(views=-10)

    def test_unknown_enum_fallbacks(self) -> None:
        raw_data = {
            "platform": "nonexistent_platform",
            "intent": "RANDOM_INTENT",
            "sentiment": "SUPER_HAPPY",
            "author": "Tester",
            "url": "https://example.com/test",
            "content": "Just testing fallback enums",
        }
        dto = MentionDTO.from_dict(raw_data)
        self.assertEqual(dto.platform, Platform.OTHER)
        self.assertEqual(dto.intent, BuyingIntent.GERAL)
        self.assertEqual(dto.sentiment, Sentiment.NEUTRAL)


if __name__ == "__main__":
    unittest.main()

