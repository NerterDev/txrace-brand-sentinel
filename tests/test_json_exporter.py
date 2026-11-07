"""Deterministic unit tests for JsonExporter."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.dispatchers.json_exporter import JsonExporter
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment


class TestJsonExporter(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = JsonExporter(default_output_dir=self.temp_dir)

        # Build sample mentions
        self.sample_mentions = [
            MentionDTO(
                id="m1",
                platform=Platform.YOUTUBE,
                author="MXChannel",
                title="CR250 restyle build with TX Race",
                content="Full transformation video of Honda CR250",
                url="https://youtube.com/watch?v=123",
                published_at="2026-11-06T12:00:00Z",
                scraped_at="2026-11-06T12:05:00Z",
                model_detected="CR250",
                brand_detected="Honda",
                generation="Gen25",
                intent=BuyingIntent.PROJETO_BUILD,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.95,
                priority_score=92.0,
                metrics=MentionMetrics(views=15000, likes=1200, comments=85),
                geo_country="United States",
            ),
            MentionDTO(
                id="m2",
                platform=Platform.FORUMS,
                author="Rider_99",
                title="Where to buy TX Race kit in Canada?",
                content="Looking for price and shipping details to Ontario",
                url="https://thumpertalk.com/123",
                published_at="2026-11-06T14:00:00Z",
                scraped_at="2026-11-06T14:05:00Z",
                model_detected="KX250",
                brand_detected="Kawasaki",
                generation="Gen24",
                intent=BuyingIntent.COMPRA_ATIVA,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.88,
                priority_score=88.5,
                metrics=MentionMetrics(views=2500, likes=40, comments=12),
                geo_country="Canada",
            ),
        ]

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_all_creates_three_valid_json_files(self) -> None:
        files = self.exporter.export_all(self.sample_mentions)
        self.assertTrue(Path(files["current_mentions"]).exists())
        self.assertTrue(Path(files["kpis"]).exists())
        self.assertTrue(Path(files["analytics"]).exists())

        # Inspect current_mentions.json
        mentions_data = json.loads(Path(files["current_mentions"]).read_text(encoding="utf-8"))
        self.assertEqual(mentions_data["count"], 2)
        self.assertEqual(len(mentions_data["mentions"]), 2)
        # Should be sorted by priority score descending
        self.assertEqual(mentions_data["mentions"][0]["id"], "m1")
        self.assertEqual(mentions_data["mentions"][1]["id"], "m2")

    def test_kpi_metrics_calculations(self) -> None:
        kpis = self.exporter.build_kpis(self.sample_mentions)
        self.assertEqual(kpis["total_mentions_30d"], 2)
        self.assertEqual(kpis["total_reach_estimated"], 17500)
        self.assertEqual(kpis["viral_count"], 1)  # m1 has 15000 views
        self.assertEqual(kpis["buying_leads_count"], 1)  # m2 is COMPRA_ATIVA
        self.assertEqual(kpis["sentiment_positive_pct"], 100.0)

    def test_analytics_generation(self) -> None:
        analytics = self.exporter.build_analytics(self.sample_mentions)
        self.assertIn("timeline_30d", analytics)
        self.assertIn("model_share", analytics)
        self.assertIn("platform_distribution", analytics)
        self.assertIn("intent_distribution", analytics)
        self.assertIn("geo_distribution", analytics)

        models = [item["model"] for item in analytics["model_share"]]
        self.assertIn("CR250", models)
        self.assertIn("KX250", models)


if __name__ == "__main__":
    unittest.main()
