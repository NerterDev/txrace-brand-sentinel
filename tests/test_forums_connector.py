"""Deterministic unit tests for ForumsConnector."""
import unittest

from src.connectors.forums import ForumsConnector
from src.models.mention import BuyingIntent, Platform


class TestForumsConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = ForumsConnector()

    def test_forums_fetch_returns_valid_third_party_threads(self) -> None:
        mentions = self.connector.fetch()
        self.assertGreaterEqual(len(mentions), 2)

        for m in mentions:
            self.assertEqual(m.platform, Platform.FORUMS)
            self.assertTrue(m.url.startswith("https://"))
            self.assertNotIn("txrace.com", m.url.lower())
            self.assertFalse(self.connector.matcher.is_official_brand_source(m.author, m.url, m.author_url))
            self.assertIn(m.brand_detected, ["Honda", "Kawasaki"])
            self.assertIn(m.model_detected, ["CR125", "CR250", "KX250"])
            self.assertIn(
                m.intent,
                [BuyingIntent.DUVIDA_TECNICA, BuyingIntent.COMPRA_ATIVA, BuyingIntent.PROJETO_BUILD],
            )
            self.assertIsNotNone(m.recommended_reply)

    def test_forums_identifies_technical_fitment_query(self) -> None:
        mentions = self.connector.fetch()
        tech_mention = next((m for m in mentions if m.intent == BuyingIntent.DUVIDA_TECNICA), None)
        self.assertIsNotNone(tech_mention)
        assert tech_mention is not None
        assert tech_mention.recommended_reply is not None
        self.assertIn("bolt-on", tech_mention.recommended_reply.lower())

    def test_forums_run_wrapper_status(self) -> None:
        res = self.connector.run()
        self.assertEqual(res.status.value, "OK")
        self.assertEqual(res.connector_name, "forums")
        self.assertGreater(len(res.mentions), 0)


if __name__ == "__main__":
    unittest.main()
