"""Deterministic unit tests for Prioritizer scoring and automated response generation."""
import unittest
from datetime import datetime, timezone

from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment


class TestPrioritizer(unittest.TestCase):
    def setUp(self) -> None:
        self.prioritizer = Prioritizer()

    def test_buying_intent_and_viral_scores_highest(self) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        # High buying intent, 50k views, positive sentiment, fresh
        score = self.prioritizer.calculate_priority(
            intent=BuyingIntent.COMPRA_ATIVA,
            views=55000,
            sentiment_score=1.0,
            published_at_iso=now_iso,
        )
        # 40 (intent) + 30 (eng) + 15 (sent) + 15 (fresh) = 100.0
        self.assertEqual(score, 100.0)

    def test_casual_mention_scores_moderately(self) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        score = self.prioritizer.calculate_priority(
            intent=BuyingIntent.GERAL,
            views=100,
            sentiment_score=0.5,
            published_at_iso=now_iso,
        )
        # 10 (intent) + 4.5 (eng) + 7.5 (sent) + 15 (fresh) = ~37.0
        self.assertGreater(score, 30.0)
        self.assertLess(score, 50.0)

    def test_generate_reply_in_multiple_languages(self) -> None:
        # English
        reply_en = self.prioritizer.generate_reply(
            intent=BuyingIntent.COMPRA_ATIVA,
            model="CR250",
            generation="Gen25",
            language="en",
        )
        self.assertIn("CR250 Gen25", reply_en)
        self.assertIn("https://txrace.com", reply_en)

        # Portuguese
        reply_pt = self.prioritizer.generate_reply(
            intent=BuyingIntent.COMPRA_ATIVA,
            model="KX250",
            generation="Gen24",
            language="pt",
        )
        self.assertIn("Olá!", reply_pt)
        self.assertIn("KX250 Gen24", reply_pt)
        self.assertIn("https://txrace.com", reply_pt)

        # Spanish
        reply_es = self.prioritizer.generate_reply(
            intent=BuyingIntent.DUVIDA_TECNICA,
            model="YZ125",
            language="es",
        )
        self.assertIn("¡Hola!", reply_es)
        self.assertIn("YZ125", reply_es)
        self.assertIn("bolt-on", reply_es)

    def test_enrich_lifecycle(self) -> None:
        mention = MentionDTO(
            id="pri-1",
            platform=Platform.YOUTUBE,
            author="MotoBuilder",
            title="CRF250X Restyle Kit Review",
            content="Where can I order this kit in Europe?",
            url="https://youtube.com/watch?v=123",
            published_at=datetime.now(timezone.utc).isoformat(),
            scraped_at=datetime.now(timezone.utc).isoformat(),
            model_detected="CRF250X",
            brand_detected="Honda",
            intent=BuyingIntent.COMPRA_ATIVA,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.9,
            priority_score=0.0,
            metrics=MentionMetrics(views=12000),
            generation="Gen25",
        )

        enriched = self.prioritizer.enrich(mention, language="en")
        self.assertGreater(enriched.priority_score, 80.0)
        self.assertIsNotNone(enriched.recommended_reply)
        assert enriched.recommended_reply is not None
        self.assertIn("https://txrace.com", enriched.recommended_reply)


if __name__ == "__main__":
    unittest.main()

