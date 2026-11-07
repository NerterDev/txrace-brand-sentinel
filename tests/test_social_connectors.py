"""Deterministic unit tests for TikTok, Instagram, Facebook, and Reddit connectors."""
import unittest
from pathlib import Path

import yaml

from src.connectors.facebook import FacebookConnector
from src.connectors.instagram import InstagramConnector
from src.connectors.reddit import RedditConnector
from src.connectors.registry import ConnectorRegistry
from src.connectors.tiktok import TikTokConnector
from src.connectors.youtube import YouTubeConnector
from src.models.mention import Platform


class TestSocialConnectors(unittest.TestCase):
    def test_tiktok_connector_fetch(self) -> None:
        conn = TikTokConnector()
        mentions = conn.fetch()
        self.assertGreater(len(mentions), 0)
        for m in mentions:
            self.assertEqual(m.platform, Platform.TIKTOK)
            self.assertTrue(m.url.startswith("https://www.tiktok.com/@"))
            self.assertGreater(m.metrics.views, 10000)
            self.assertTrue(m.is_viral)
            self.assertIsNotNone(m.recommended_reply)

    def test_instagram_connector_fetch(self) -> None:
        conn = InstagramConnector()
        mentions = conn.fetch()
        self.assertGreater(len(mentions), 0)
        for m in mentions:
            self.assertEqual(m.platform, Platform.INSTAGRAM)
            self.assertTrue(m.url.startswith("https://www.instagram.com/"))
            self.assertIn(m.model_detected, ["RM250", "CR125"])

    def test_facebook_connector_fetch(self) -> None:
        conn = FacebookConnector()
        mentions = conn.fetch()
        self.assertGreater(len(mentions), 0)
        for m in mentions:
            self.assertEqual(m.platform, Platform.FACEBOOK)
            self.assertTrue(m.url.startswith("https://www.facebook.com/"))
            self.assertIn(m.brand_detected, ["Kawasaki", "Honda"])

    def test_reddit_connector_fetch(self) -> None:
        conn = RedditConnector()
        mentions = conn.fetch()
        self.assertGreater(len(mentions), 0)
        for m in mentions:
            self.assertEqual(m.platform, Platform.REDDIT)
            self.assertTrue(m.url.startswith("https://www.reddit.com/r/"))
            self.assertIn(m.model_detected, ["CR250", "YZ125"])

    def test_registry_loads_all_social_connectors_from_config(self) -> None:
        cfg = yaml.safe_load(Path("config/sources.yaml").read_text(encoding="utf-8"))
        reg = ConnectorRegistry()
        reg.load_from_config(cfg)

        loaded = reg.list_connectors()
        self.assertIn("youtube", loaded)
        self.assertIn("tiktok", loaded)
        self.assertIn("instagram", loaded)
        self.assertIn("facebook", loaded)
        self.assertIn("reddit", loaded)

        # Run all 5 and verify aggregated results
        all_mentions, results = reg.collect_all_mentions()
        self.assertGreaterEqual(len(all_mentions), 10)
        self.assertGreaterEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()

