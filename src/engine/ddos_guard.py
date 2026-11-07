"""Rate limiter and exponential backoff manager to ensure polite crawling and avoid anti-bot blocks."""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class DomainState:
    last_request_time: float = 0.0
    consecutive_failures: int = 0
    total_requests: int = 0


class DDoSGuard:
    """Controls request pacing, rate-limiting per source, and exponential backoff."""

    def __init__(
        self,
        default_delay_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_factor: float | None = None,
        settings_path: str = "config/settings.yaml",
    ) -> None:
        cfg = {}
        cfg_file = Path(settings_path)
        if cfg_file.exists():
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        rate_cfg = cfg.get("rate_limiting", {})

        self.default_delay = float(
            default_delay_seconds if default_delay_seconds is not None
            else rate_cfg.get("default_delay_seconds", 1.5)
        )
        self.max_retries = int(
            max_retries if max_retries is not None
            else rate_cfg.get("max_retries", 3)
        )
        self.backoff_factor = float(
            backoff_factor if backoff_factor is not None
            else rate_cfg.get("backoff_factor", 2.0)
        )

        self._domains: dict[str, DomainState] = {}

    def _get_state(self, domain: str) -> DomainState:
        if domain not in self._domains:
            self._domains[domain] = DomainState()
        return self._domains[domain]

    def get_delay(self, domain: str) -> float:
        """Calculates current required delay for a given domain including backoff and jitter."""
        state = self._get_state(domain)
        base_delay = self.default_delay
        if state.consecutive_failures > 0:
            multiplier = self.backoff_factor ** state.consecutive_failures
            base_delay = base_delay * multiplier

        # Add modest randomized jitter (+/- 15%) to avoid synchronized hammering
        jitter = random.uniform(0.85, 1.15)
        return round(base_delay * jitter, 3)

    def wait_turn(self, domain: str, sleep_func: Any = time.sleep) -> float:
        """Ensures adequate spacing between requests. Sleeps if necessary and updates timestamps."""
        state = self._get_state(domain)
        now = time.time()
        required_delay = self.get_delay(domain)
        elapsed = now - state.last_request_time

        sleep_needed = max(0.0, required_delay - elapsed)
        if sleep_needed > 0.0:
            sleep_func(sleep_needed)

        state.last_request_time = time.time()
        state.total_requests += 1
        return sleep_needed

    def record_failure(self, domain: str) -> float:
        """Records an HTTP error/timeout and returns the next backoff wait time."""
        state = self._get_state(domain)
        state.consecutive_failures += 1
        next_backoff = self.get_delay(domain)
        logger.warning(
            "Recorded failure for domain '%s' (attempt %d/%d). Next backoff: %.2fs",
            domain, state.consecutive_failures, self.max_retries, next_backoff,
        )
        return next_backoff

    def record_success(self, domain: str) -> None:
        """Resets the failure counter upon successful request/fetch."""
        state = self._get_state(domain)
        state.consecutive_failures = 0

    def can_request(self, domain: str) -> bool:
        """Returns False if consecutive failures have reached or exceeded max_retries."""
        state = self._get_state(domain)
        return state.consecutive_failures < self.max_retries

    def reset(self) -> None:
        """Resets all domain tracking."""
        self._domains.clear()
