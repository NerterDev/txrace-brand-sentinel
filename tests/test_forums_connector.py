"""Deterministic unit tests for ForumsConnector (ThumperTalk, VitalMX, DirtRider)."""
import unittest

from src.connectors.forums import ForumsConnector
from src.models.mention import BuyingIntent, Platform


class TestForumsConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = ForumsConnector()

    def test_forums_fetch_returns_valid_technical_and_buying_mentions(self) -> None:
        mentions = self.connector.fetch()
        self.assertGreaterEqual(len(mentions), 3)

        for m in mentions:
            self.assertEqual(m.platform, Platform.FORUMS)
            self.assertTrue(m.url.startswith("https://www."))
            self.assertIn(m.brand_detected, ["Honda", "Kawasaki", "Yamaha"])
            self.assertIn(m.model_detected, ["CR250", "KX125", "YZ250"])
            self.assertIn(m.intent, [BuyingIntent.DUVIDA_TECNICA, BuyingIntent.COMPRA_ATIVA, BuyingIntent.PROJETO_BUILD])
            self.assertIsNotNone(m.recommended_reply)

    def test_forums_identifies_technical_fitment_query(self) -> None:
        mentions = self.connector.fetch()
        cr250_mention = next((m for m in mentions if m.model_detected == "CR250"), None)
        self.assertIsNotNone(cr250_mention)
        assert cr250_mention is not None
        self.assertEqual(cr250_mention.intent, BuyingIntent.DUVIDA_TECNICA)
        assert cr250_mention.recommended_reply is not None
        self.assertIn("bolt-on", cr250_mention.recommended_reply.lower())

    def test_forums_run_wrapper_status(self) -> None:
        res = self.connector.run()
        self.assertEqual(res.status.value, "OK")
        self.assertEqual(res.connector_name, "forums")
        self.assertGreater(len(res.mentions), 0)


if __name__ == "__main__":
    unittest.main()
