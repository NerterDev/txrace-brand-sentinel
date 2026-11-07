"""Dynamic registry and orchestrator for brand intelligence connectors."""
from __future__ import annotations

import importlib
import logging
from typing import Any, Type

from src.connectors.base import BaseConnector, ConnectorResult, ConnectorStatus
from src.models.mention import MentionDTO

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """Manages connector discovery, instantiation, and isolated execution."""

    def __init__(self) -> None:
        self._registry: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        """Registers a connector instance."""
        if not isinstance(connector, BaseConnector):
            raise TypeError("Connector must inherit from BaseConnector.")
        self._registry[connector.name] = connector
        logger.debug("Registered connector: %s (%s)", connector.name, connector.platform.value)

    def get(self, name: str) -> BaseConnector | None:
        """Retrieves a connector by name."""
        return self._registry.get(name)

    def list_connectors(self) -> list[str]:
        """Returns the list of registered connector names."""
        return list(self._registry.keys())

    def clear(self) -> None:
        """Clears all registered connectors."""
        self._registry.clear()

    def load_from_config(self, sources_config: dict[str, Any]) -> None:
        """Dynamically imports and instantiates connectors defined in sources.yaml."""
        sources = sources_config.get("sources", {})
        for key, conf in sources.items():
            if not conf.get("enabled", True):
                logger.info("Source '%s' is marked disabled in configuration.", key)
                continue

            module_path = conf.get("module")
            class_name = conf.get("class_name")

            if not module_path or not class_name:
                logger.warning("Source '%s' missing module or class_name. Skipping.", key)
                continue

            try:
                mod = importlib.import_module(module_path)
                cls: Type[BaseConnector] = getattr(mod, class_name)
                connector_instance = cls()
                self.register(connector_instance)
            except (ImportError, AttributeError) as err:
                logger.debug(
                    "Connector '%s' (%s.%s) not yet implemented or loadable: %s",
                    key, module_path, class_name, err
                )

    def run_all(self) -> list[ConnectorResult]:
        """Executes all registered connectors sequentially with full fault isolation."""
        results: list[ConnectorResult] = []
        for name, connector in self._registry.items():
            try:
                res = connector.run()
                results.append(res)
            except Exception as e:
                logger.critical("Unexpected crash in connector '%s': %s", name, e, exc_info=True)
                results.append(
                    ConnectorResult(
                        connector_name=name,
                        platform=connector.platform,
                        status=ConnectorStatus.ERROR,
                        mentions=[],
                        error_message=f"Critical executor failure: {e}",
                    )
                )
        return results

    def collect_all_mentions(self) -> tuple[list[MentionDTO], list[ConnectorResult]]:
        """Runs all connectors and aggregates deduplicated mentions with execution telemetry."""
        results = self.run_all()
        aggregated_mentions: list[MentionDTO] = []
        for res in results:
            if res.status in (ConnectorStatus.OK, ConnectorStatus.PARTIAL_DEGRADED):
                aggregated_mentions.extend(res.mentions)
        return aggregated_mentions, results


# Global singleton registry instance
default_registry = ConnectorRegistry()

