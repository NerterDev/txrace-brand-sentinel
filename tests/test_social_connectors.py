"""Deterministic unit tests for Reddit, TikTok, Instagram, and Facebook connectors."""
import unittest
from pathlib import Path

import yaml

from src.connectors.facebook import FacebookConnector
from src.connectors.instagram import InstagramConnector
from src.connectors.reddit import RedditConnector
from src.connectors.registry import ConnectorRegistry
from src.connectors.tiktok import TikTokConnector
from src.models.mention import Platform


class TestSocialConnectors(unittest.TestCase):
    def test_reddit_connector_returns_real_third_party_threads(self) -> None:
        conn = RedditConnector(enable_live=False)
        mentions = conn.fetch()
        self.assertGreaterEqual(len(mentions), 7)
        for m in mentions:
            self.assertEqual(m.platform, Platform.REDDIT)
            self.assertTrue(m.url.startswith("https://www.reddit.com/r/"))
            self.assertTrue(m.author.startswith("u/"))
            self.assertFalse(conn.matcher.is_official_brand_source(m.author, m.url, m.author_url))

    def test_reddit_atom_rss_parser_extracts_entries_and_excludes_official(self) -> None:
        conn = RedditConnector(enable_live=False)
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>t3_1w0nu3w</id>
            <title>2001 KX 250 restyle kit alternatives?</title>
            <link href="https://www.reddit.com/r/Dirtbikes/comments/1w0nu3w/2001_kx_250_restyle_kit_alternatives/" />
            <updated>2026-08-28T11:22:59+00:00</updated>
            <author><name>/u/Emergency_Response19</name><uri>https://www.reddit.com/user/Emergency_Response19</uri></author>
            <content type="html">&lt;div&gt;Looking at the TX race restyle kit for my KX250.&lt;/div&gt;</content>
          </entry>
          <entry>
            <id>t3_official</id>
            <title>Official TX RACE announcement</title>
            <link href="https://www.reddit.com/r/Dirtbikes/comments/999999/official/" />
            <updated>2026-08-29T10:00:00+00:00</updated>
            <author><name>/u/txracecom</name><uri>https://www.reddit.com/user/txracecom</uri></author>
            <content type="html">&lt;div&gt;Official post from TX RACE.&lt;/div&gt;</content>
          </entry>
        </feed>
        """
        parsed = conn._parse_reddit_rss_xml(sample_xml)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["author"], "u/Emergency_Response19")

    def test_walled_garden_connectors_return_empty_without_tokens_and_filter_official(self) -> None:
        # Without API tokens, closed platforms must return [] rather than fake or @txrace fixtures
        self.assertEqual(TikTokConnector(access_token="").fetch(), [])
        self.assertEqual(InstagramConnector(access_token="").fetch(), [])
        self.assertEqual(FacebookConnector(access_token="").fetch(), [])

        # With injected API payloads, third-party posts are normalized while official @txrace posts are dropped
        tt_conn = TikTokConnector(
            seed_items=[
                {
                    "id": "tt_real_rider_1",
                    "author": "@twostroke_builder",
                    "author_url": "https://www.tiktok.com/@twostroke_builder",
                    "title": "CR250 build with TX Race Gen25 kit",
                    "content": "Installed the TX Race Gen25 restyle kit on my 2003 Honda CR250 build.",
                    "url": "https://www.tiktok.com/@twostroke_builder/video/7400000000000000001",
                    "published_at": "2026-10-20T18:00:00Z",
                    "metrics": {"views": 22000, "comments": 45, "likes": 1900, "shares": 80},
                },
                {
                    "id": "tt_official_blocked",
                    "author": "@txrace",
                    "author_url": "https://www.tiktok.com/@txrace",
                    "title": "TX RACE Official TikTok",
                    "content": "Official TX Race restyle kit showcase.",
                    "url": "https://www.tiktok.com/@txrace",
                    "published_at": "2026-10-20T19:00:00Z",
                    "metrics": {"views": 50000, "comments": 100, "likes": 3000, "shares": 200},
                },
            ]
        )
        tt_mentions = tt_conn.fetch()
        self.assertEqual(len(tt_mentions), 1)
        self.assertEqual(tt_mentions[0].author, "@twostroke_builder")
        self.assertTrue(tt_mentions[0].is_viral)

    def test_registry_loads_all_social_connectors_from_config(self) -> None:
        cfg = yaml.safe_load(Path("config/sources.yaml").read_text(encoding="utf-8"))
        reg = ConnectorRegistry()
        reg.load_from_config(cfg)

        loaded = reg.list_connectors()
        for expected in ("youtube", "tiktok", "instagram", "facebook", "reddit"):
            self.assertIn(expected, loaded)

        all_mentions, results = reg.collect_all_mentions()
        self.assertGreaterEqual(len(all_mentions), 18)
        self.assertGreaterEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()
