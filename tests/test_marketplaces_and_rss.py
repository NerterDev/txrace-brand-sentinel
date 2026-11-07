"""Deterministic unit tests for Marketplaces, Twitter, RssWeb connectors and full registry catalog."""
import unittest
from pathlib import Path

import yaml

from src.connectors.marketplaces import MarketplacesConnector
from src.connectors.registry import ConnectorRegistry
from src.connectors.rss_web import RssWebConnector
from src.connectors.twitter import TwitterConnector
from src.models.mention import BuyingIntent, Platform


class TestMarketplacesAndRss(unittest.TestCase):
    def test_marketplaces_connector(self) -> None:
        conn = MarketplacesConnector()
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 2)
        for m in mentions:
            self.assertEqual(m.platform, Platform.MARKETPLACES)
            self.assertEqual(m.intent, BuyingIntent.COMPRA_ATIVA)
            self.assertIn(m.model_detected, ["CR250", "KX250"])
            self.assertIsNotNone(m.recommended_reply)

    def test_twitter_connector(self) -> None:
        conn = TwitterConnector()
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 1)
        for m in mentions:
            self.assertEqual(m.platform, Platform.TWITTER)
            self.assertEqual(m.model_detected, "CR125")
            self.assertEqual(m.generation, "Gen25")

    def test_rss_web_connector(self) -> None:
        conn = RssWebConnector()
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 1)
        for m in mentions:
            self.assertEqual(m.platform, Platform.RSS_WEB)
            self.assertEqual(m.model_detected, "CR250")
            self.assertIn("https://motocrossactionmag.com", m.url)

    def test_full_catalog_dynamic_loading_and_execution(self) -> None:
        cfg = yaml.safe_load(Path("config/sources.yaml").read_text(encoding="utf-8"))
        reg = ConnectorRegistry()
        reg.load_from_config(cfg)

        loaded = reg.list_connectors()
        # All 9 sources configured in sources.yaml
        expected_sources = [
            "youtube", "tiktok", "instagram", "facebook",
            "reddit", "twitter", "forums", "marketplaces", "rss_web"
        ]
        for src in expected_sources:
            self.assertIn(src, loaded, f"Source '{src}' not loaded in registry")

        all_mentions, results = reg.collect_all_mentions()
        self.assertEqual(len(results), len(expected_sources))
        self.assertGreaterEqual(len(all_mentions), 18)

        # Confirm all 9 platforms are represented in gathered mentions
        platforms = {m.platform for m in all_mentions}
        self.assertEqual(len(platforms), 9)


if __name__ == "__main__":
    unittest.main()
