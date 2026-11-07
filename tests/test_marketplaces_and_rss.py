"""Deterministic unit tests for Marketplaces, Twitter, RssWeb connectors and full registry catalog."""
import unittest
from pathlib import Path

import yaml

from src.connectors.marketplaces import MarketplacesConnector
from src.connectors.registry import ConnectorRegistry
from src.connectors.rss_web import RssWebConnector
from src.connectors.twitter import TwitterConnector
from src.engine.matcher import KeywordMatcher
from src.models.mention import BuyingIntent, Platform


class TestMarketplacesAndRss(unittest.TestCase):
    def test_marketplaces_connector_excludes_official_txrace_store(self) -> None:
        conn = MarketplacesConnector()
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 4)
        for m in mentions:
            self.assertEqual(m.platform, Platform.MARKETPLACES)
            self.assertNotIn("txrace.com", m.url.lower())
            self.assertNotIn("/sch/i.html", m.url.lower())
            self.assertFalse(conn.matcher.is_official_brand_source(m.author, m.url, m.author_url))
            self.assertIn(m.intent, [BuyingIntent.COMPRA_ATIVA, BuyingIntent.DUVIDA_TECNICA])
            self.assertIn(m.model_detected, ["CR125", "CR250", "KX125", "KX250"])
            self.assertIsNotNone(m.recommended_reply)

    def test_twitter_connector_skips_unauthenticated_and_filters_official(self) -> None:
        self.assertEqual(TwitterConnector(bearer_token="").fetch(), [])

        seeded = TwitterConnector(
            seed_items=[
                {
                    "id": "tw_rider_01",
                    "author": "@mx_privateer",
                    "author_url": "https://x.com/mx_privateer",
                    "title": "CR125 Gen25 TX Race restyle!",
                    "content": "Just bolted on the TX Race Gen25 restyle kit on my Honda CR125 build.",
                    "url": "https://x.com/mx_privateer/status/1850000000000000001",
                    "published_at": "2026-10-25T15:00:00Z",
                    "metrics": {"views": 4200, "comments": 9, "likes": 120, "shares": 14},
                },
                {
                    "id": "tw_official_drop",
                    "author": "@txrace",
                    "author_url": "https://x.com/txrace",
                    "title": "Official X post",
                    "content": "Official TX RACE Gen25 CR125 kit.",
                    "url": "https://x.com/txrace",
                    "published_at": "2026-10-25T16:00:00Z",
                    "metrics": {"views": 9000, "comments": 10, "likes": 200, "shares": 20},
                },
            ]
        )
        mentions = seeded.fetch()
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0].platform, Platform.TWITTER)
        self.assertEqual(mentions[0].model_detected, "CR125")
        self.assertEqual(mentions[0].generation, "Gen25")

    def test_rss_web_connector_uses_verified_editorial_and_web_urls(self) -> None:
        conn = RssWebConnector()
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 3)
        urls = [m.url for m in mentions]
        self.assertIn("https://adbmag.com.au/editorial/2007-honda-cr250r/", urls)
        for m in mentions:
            self.assertEqual(m.platform, Platform.RSS_WEB)
            self.assertNotIn("motocrossactionmag.com", m.url)
            self.assertNotIn("txrace.com", m.url)

    def test_full_catalog_dynamic_loading_and_third_party_purity(self) -> None:
        cfg = yaml.safe_load(Path("config/sources.yaml").read_text(encoding="utf-8"))
        reg = ConnectorRegistry()
        reg.load_from_config(cfg)

        loaded = reg.list_connectors()
        expected_sources = [
            "youtube", "tiktok", "instagram", "facebook",
            "reddit", "twitter", "forums", "marketplaces", "rss_web",
        ]
        for src in expected_sources:
            self.assertIn(src, loaded, f"Source '{src}' not loaded in registry")

        all_mentions, results = reg.collect_all_mentions()
        self.assertEqual(len(results), len(expected_sources))
        self.assertGreaterEqual(len(all_mentions), 25)

        matcher = KeywordMatcher()
        for m in all_mentions:
            self.assertFalse(
                matcher.is_official_brand_source(m.author, m.url, m.author_url),
                f"Official brand mention leaked: {m.author} -> {m.url}",
            )

        platforms = {m.platform for m in all_mentions}
        self.assertEqual(
            platforms,
            {
                Platform.YOUTUBE,
                Platform.REDDIT,
                Platform.FORUMS,
                Platform.MARKETPLACES,
                Platform.RSS_WEB,
            },
        )


if __name__ == "__main__":
    unittest.main()
