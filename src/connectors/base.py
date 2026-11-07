"""Abstract BaseConnector and status definitions for brand intelligence connectors."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.models.mention import MentionDTO, Platform

logger = logging.getLogger(__name__)


class ConnectorStatus(str, Enum):
    OK = "OK"
    PARTIAL_DEGRADED = "PARTIAL_DEGRADED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ConnectorResult:
    """Standardized result envelope for any connector execution."""
    connector_name: str
    platform: Platform
    status: ConnectorStatus
    mentions: list[MentionDTO] = field(default_factory=list)
    error_message: str | None = None
    execution_time_ms: float = 0.0
    items_scanned: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_name": self.connector_name,
            "platform": self.platform.value if isinstance(self.platform, Platform) else str(self.platform),
            "status": self.status.value if isinstance(self.status, ConnectorStatus) else str(self.status),
            "count": len(self.mentions),
            "error_message": self.error_message,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "items_scanned": self.items_scanned,
        }


class BaseConnector(ABC):
    """Abstract Base Class for all TX RACE Brand Sentinel connectors."""

    def __init__(self, name: str, platform: Platform, enabled: bool = True) -> None:
        self.name = name
        self.platform = platform
        self.enabled = enabled

    @abstractmethod
    def fetch(self) -> list[MentionDTO]:
        """Fetch raw brand mentions from the target source and normalize into MentionDTOs."""
        raise NotImplementedError("Connectors must implement the fetch() method.")

    def health_check(self) -> bool:
        """Lightweight check to verify endpoint or credential reachability."""
        return True

    def run(self) -> ConnectorResult:
        """Safely executes the connector with error isolation and telemetry tracking."""
        if not self.enabled:
            logger.info("Connector '%s' is disabled. Skipping.", self.name)
            return ConnectorResult(
                connector_name=self.name,
                platform=self.platform,
                status=ConnectorStatus.OK,
                mentions=[],
                error_message="Connector disabled by configuration.",
                execution_time_ms=0.0,
                items_scanned=0,
            )

        start_time = time.perf_counter()
        try:
            mentions = self.fetch()
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ConnectorResult(
                connector_name=self.name,
                platform=self.platform,
                status=ConnectorStatus.OK,
                mentions=mentions,
                execution_time_ms=elapsed_ms,
                items_scanned=len(mentions),
            )
        except TimeoutError as te:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("Connector '%s' timed out (PARTIAL_DEGRADED): %s", self.name, te)
            return ConnectorResult(
                connector_name=self.name,
                platform=self.platform,
                status=ConnectorStatus.PARTIAL_DEGRADED,
                mentions=[],
                error_message=f"Timeout: {te}",
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("Connector '%s' encountered an error: %s", self.name, e, exc_info=True)
            return ConnectorResult(
                connector_name=self.name,
                platform=self.platform,
                status=ConnectorStatus.ERROR,
                mentions=[],
                error_message=str(e),
                execution_time_ms=elapsed_ms,
            )

