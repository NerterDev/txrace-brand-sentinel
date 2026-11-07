"""Deterministic unit tests for BaseConnector and ConnectorRegistry."""
import unittest

from src.connectors.base import BaseConnector, ConnectorResult, ConnectorStatus
from src.connectors.registry import ConnectorRegistry
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment


class MockSuccessConnector(BaseConnector):
    def __init__(self, name: str = "mock_success", enabled: bool = True) -> None:
        super().__init__(name=name, platform=Platform.YOUTUBE, enabled=enabled)

    def fetch(self) -> list[MentionDTO]:
        return [
            MentionDTO(
                id="mock-1",
                platform=Platform.YOUTUBE,
                author="MotoGuy",
                title="CR250 Restyle",
                content="Fitting TX Race kit on CR250",
                url="https://youtube.com/watch?v=mock1",
                published_at="2026-11-06T12:00:00Z",
                scraped_at="2026-11-06T12:05:00Z",
                model_detected="CR250",
                brand_detected="Honda",
                intent=BuyingIntent.PROJETO_BUILD,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.85,
                priority_score=75.0,
                metrics=MentionMetrics(views=1200),
            )
        ]


class MockTimeoutConnector(BaseConnector):
    def __init__(self, name: str = "mock_timeout") -> None:
        super().__init__(name=name, platform=Platform.FORUMS)

    def fetch(self) -> list[MentionDTO]:
        raise TimeoutError("Connection to forum host timed out after 10s")


class MockCrashConnector(BaseConnector):
    def __init__(self, name: str = "mock_crash") -> None:
        super().__init__(name=name, platform=Platform.MARKETPLACES)

    def fetch(self) -> list[MentionDTO]:
        raise RuntimeError("Fatal parse error: unexpected HTML schema")


class TestConnectors(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ConnectorRegistry()

    def test_successful_connector_execution(self) -> None:
        conn = MockSuccessConnector()
        result = conn.run()
        self.assertEqual(result.status, ConnectorStatus.OK)
        self.assertEqual(len(result.mentions), 1)
        self.assertEqual(result.mentions[0].model_detected, "CR250")
        self.assertGreaterEqual(result.execution_time_ms, 0.0)
        self.assertIsNone(result.error_message)

    def test_disabled_connector_execution(self) -> None:
        conn = MockSuccessConnector(enabled=False)
        result = conn.run()
        self.assertEqual(result.status, ConnectorStatus.OK)
        self.assertEqual(len(result.mentions), 0)
        self.assertIn("disabled", result.error_message.lower())

    def test_timeout_degrades_gracefully_to_partial_degraded(self) -> None:
        conn = MockTimeoutConnector()
        result = conn.run()
        self.assertEqual(result.status, ConnectorStatus.PARTIAL_DEGRADED)
        self.assertEqual(len(result.mentions), 0)
        self.assertIn("timed out", result.error_message)

    def test_crash_isolated_as_error_status(self) -> None:
        conn = MockCrashConnector()
        result = conn.run()
        self.assertEqual(result.status, ConnectorStatus.ERROR)
        self.assertEqual(len(result.mentions), 0)
        self.assertIn("Fatal parse error", result.error_message)

    def test_registry_registration_and_orchestration(self) -> None:
        success_conn = MockSuccessConnector("success_1")
        timeout_conn = MockTimeoutConnector("timeout_1")
        crash_conn = MockCrashConnector("crash_1")

        self.registry.register(success_conn)
        self.registry.register(timeout_conn)
        self.registry.register(crash_conn)

        self.assertEqual(self.registry.list_connectors(), ["success_1", "timeout_1", "crash_1"])
        self.assertIs(self.registry.get("success_1"), success_conn)

        results = self.registry.run_all()
        self.assertEqual(len(results), 3)

        mentions, exec_results = self.registry.collect_all_mentions()
        # Only success_conn produces mentions
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0].id, "mock-1")
        self.assertEqual(len(exec_results), 3)

    def test_registry_rejects_invalid_connector(self) -> None:
        with self.assertRaises(TypeError):
            self.registry.register(object())  # type: ignore

    def test_load_from_config(self) -> None:
        test_config = {
            "sources": {
                "mock_source": {
                    "enabled": True,
                    "module": "tests.test_connectors",
                    "class_name": "MockSuccessConnector",
                },
                "disabled_source": {
                    "enabled": False,
                    "module": "tests.test_connectors",
                    "class_name": "MockSuccessConnector",
                },
                "nonexistent_source": {
                    "enabled": True,
                    "module": "src.connectors.nonexistent",
                    "class_name": "GhostConnector",
                },
            }
        }
        self.registry.load_from_config(test_config)
        self.assertIn("mock_success", self.registry.list_connectors())
        self.assertEqual(len(self.registry.list_connectors()), 1)


if __name__ == "__main__":
    unittest.main()

