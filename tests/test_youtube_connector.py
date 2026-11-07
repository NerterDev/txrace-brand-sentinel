"""Deterministic unit tests for YouTubeConnector (third-party builds & ytInitialData parser)."""
import json
import unittest

from src.connectors.youtube import YouTubeConnector
from src.models.mention import BuyingIntent, Platform


class TestYouTubeConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = YouTubeConnector(enable_live=False)

    def test_youtube_fetch_returns_only_verified_third_party_mentions(self) -> None:
        mentions = self.connector.fetch()
        self.assertGreaterEqual(len(mentions), 12)

        for m in mentions:
            self.assertEqual(m.platform, Platform.YOUTUBE)
            self.assertTrue(m.url.startswith("https://www.youtube.com/watch?v="))
            self.assertFalse(self.connector.matcher.is_official_brand_source(m.author, m.url, m.author_url))
            self.assertGreaterEqual(m.metrics.views, 0)
            self.assertIn(m.brand_detected, ["Honda", "Kawasaki", "Suzuki", "Yamaha", "TX RACE"])
            self.assertGreaterEqual(m.priority_score, 0.0)
            self.assertLessEqual(m.priority_score, 100.0)
            self.assertIsNotNone(m.recommended_reply)

    def test_youtube_identifies_real_chase_cr125_and_gen2_builds(self) -> None:
        mentions = self.connector.fetch()
        chase_mention = next((m for m in mentions if m.author == "Chase Builds Bikes"), None)
        self.assertIsNotNone(chase_mention)
        assert chase_mention is not None
        self.assertEqual(chase_mention.url, "https://www.youtube.com/watch?v=4GT4yEOszmE")
        self.assertEqual(chase_mention.model_detected, "CR125")
        self.assertEqual(chase_mention.intent, BuyingIntent.PROJETO_BUILD)
        self.assertTrue(chase_mention.is_viral)
        self.assertGreater(chase_mention.metrics.views, 40000)

        gen2_mention = next((m for m in mentions if m.author == "32:1"), None)
        self.assertIsNotNone(gen2_mention)
        assert gen2_mention is not None
        self.assertEqual(gen2_mention.generation, "Gen2")

    def test_yt_initial_data_parser_filters_official_txrace_channel(self) -> None:
        sample_payload = {
            "contents": [
                {
                    "videoRenderer": {
                        "videoId": "4GT4yEOszmE",
                        "title": {"runs": [{"text": "Incredible CR125 Transformation with TXRACE!"}]},
                        "ownerText": {
                            "runs": [
                                {
                                    "text": "Chase Builds Bikes",
                                    "navigationEndpoint": {
                                        "commandMetadata": {"webCommandMetadata": {"url": "/@ChaseBuiltBikes"}}
                                    },
                                }
                            ]
                        },
                        "viewCountText": {"simpleText": "43,468 views"},
                    }
                },
                {
                    "videoRenderer": {
                        "videoId": "Egi65jNdJt8",
                        "title": {"runs": [{"text": "TX RACE Official KX250 Restyle Kit"}]},
                        "ownerText": {
                            "runs": [
                                {
                                    "text": "TX RACE",
                                    "navigationEndpoint": {
                                        "commandMetadata": {"webCommandMetadata": {"url": "/@txracecom"}}
                                    },
                                }
                            ]
                        },
                        "viewCountText": {"simpleText": "3,350 views"},
                    }
                },
            ]
        }
        html_doc = f"<script>var ytInitialData = {json.dumps(sample_payload)};</script>"
        parsed = self.connector._parse_youtube_search_html(html_doc)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["author"], "Chase Builds Bikes")
        self.assertEqual(parsed[0]["url"], "https://www.youtube.com/watch?v=4GT4yEOszmE")

    def test_youtube_run_wrapper_returns_ok_result(self) -> None:
        res = self.connector.run()
        self.assertEqual(res.status.value, "OK")
        self.assertEqual(res.connector_name, "youtube")
        self.assertGreater(len(res.mentions), 0)
        self.assertGreater(res.execution_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
