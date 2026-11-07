"""Deterministic unit tests for DDoSGuard rate limiting and backoff calculation."""
import unittest

from src.engine.ddos_guard import DDoSGuard


class TestDDoSGuard(unittest.TestCase):
    def setUp(self) -> None:
        # Use synthetic test parameters: 1.0s default, factor 2.0, max 3 retries
        self.guard = DDoSGuard(default_delay_seconds=1.0, max_retries=3, backoff_factor=2.0)

    def test_default_delay_with_jitter(self) -> None:
        delay = self.guard.get_delay("youtube.com")
        # 1.0s +/- 15% jitter -> [0.85, 1.15]
        self.assertGreaterEqual(delay, 0.8)
        self.assertLessEqual(delay, 1.25)

    def test_exponential_backoff_on_failures(self) -> None:
        domain = "thumpertalk.com"
        self.assertTrue(self.guard.can_request(domain))

        # 1st failure: base 1.0 * 2^1 = 2.0s
        delay1 = self.guard.record_failure(domain)
        self.assertGreaterEqual(delay1, 1.6)
        self.assertLessEqual(delay1, 2.4)
        self.assertTrue(self.guard.can_request(domain))

        # 2nd failure: base 1.0 * 2^2 = 4.0s
        delay2 = self.guard.record_failure(domain)
        self.assertGreaterEqual(delay2, 3.2)
        self.assertLessEqual(delay2, 4.8)
        self.assertTrue(self.guard.can_request(domain))

        # 3rd failure: reaches max_retries
        self.guard.record_failure(domain)
        self.assertFalse(self.guard.can_request(domain))

    def test_success_resets_failures(self) -> None:
        domain = "ebay.com"
        self.guard.record_failure(domain)
        self.guard.record_failure(domain)
        self.guard.record_success(domain)

        self.assertTrue(self.guard.can_request(domain))
        delay = self.guard.get_delay(domain)
        # Should be back to base ~1.0s
        self.assertLessEqual(delay, 1.25)

    def test_wait_turn_does_not_sleep_when_enough_time_passed(self) -> None:
        mock_sleep_called = False

        def mock_sleep(seconds: float) -> None:
            nonlocal mock_sleep_called
            mock_sleep_called = True

        domain = "vitalmx.com"
        # First call has no previous request -> sleep_needed = 0
        sleep_needed = self.guard.wait_turn(domain, sleep_func=mock_sleep)
        self.assertEqual(sleep_needed, 0.0)
        self.assertFalse(mock_sleep_called)


if __name__ == "__main__":
    unittest.main()

