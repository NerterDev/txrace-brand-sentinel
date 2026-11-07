"""Deterministic unit tests for YouTubeConnector."""
import unittest

from src.connectors.youtube import YouTubeConnector
from src.models.mention import BuyingIntent, Platform


class TestYouTubeConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = YouTubeConnector()

    def test_youtube_fetch_returns_valid_mentions(self) -> None:
        mentions = self.connector.fetch()
        self.assertGreater(len(mentions), 0)

        for m in mentions:
            self.assertEqual(m.platform, Platform.YOUTUBE)
            self.assertTrue(m.url.startswith("https://www.youtube.com/watch?v="))
            self.assertGreaterEqual(m.metrics.views, 0)
            self.assertIn(m.brand_detected, ["Honda", "Kawasaki", "Suzuki", "Yamaha", "TX RACE"])
            self.assertGreaterEqual(m.priority_score, 0.0)
            self.assertLessEqual(m.priority_score, 100.0)
            self.assertIsNotNone(m.recommended_reply)

    def test_youtube_identifies_viral_and_project_build(self) -> None:
        mentions = self.connector.fetch()
        # Find the Chase CR125 build
        chase_mention = next((m for m in mentions if "Chase" in m.author), None)
        self.assertIsNotNone(chase_mention)
        assert chase_mention is not None
        self.assertEqual(chase_mention.model_detected, "CR125")
        self.assertEqual(chase_mention.generation, "Gen25")
        self.assertEqual(chase_mention.intent, BuyingIntent.PROJETO_BUILD)
        self.assertTrue(chase_mention.is_viral)
        self.assertGreater(chase_mention.metrics.views, 50000)

    def test_youtube_run_wrapper_returns_ok_result(self) -> None:
        res = self.connector.run()
        self.assertEqual(res.status.value, "OK")
        self.assertEqual(res.connector_name, "youtube")
        self.assertGreater(len(res.mentions), 0)
        self.assertGreater(res.execution_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()

