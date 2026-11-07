"""TX RACE Brand Sentinel — Central Orchestrator & CLI Entrypoint."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from src.connectors.registry import ConnectorRegistry
from src.dispatchers.json_exporter import JsonExporter
from src.engine.deduplicator import Deduplicator
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import MentionDTO

logger = logging.getLogger("sentinel")


class SentinelOrchestrator:
    """Coordinates brand intelligence collection, deduplication, enrichment, and web export."""

    def __init__(
        self,
        sources_config_path: str | Path = "config/sources.yaml",
        keywords_config_path: str | Path = "config/keywords.yaml",
        settings_config_path: str | Path = "config/settings.yaml",
    ) -> None:
        self.sources_path = Path(sources_config_path)
        self.keywords_path = Path(keywords_config_path)
        self.settings_path = Path(settings_config_path)

        # Load configs
        self.sources_cfg = (
            yaml.safe_load(self.sources_path.read_text(encoding="utf-8"))
            if self.sources_path.exists()
            else {}
        )
        self.keywords_cfg = (
            yaml.safe_load(self.keywords_path.read_text(encoding="utf-8"))
            if self.keywords_path.exists()
            else {}
        )

        self.matcher = KeywordMatcher(config_dict=self.keywords_cfg)
        self.prioritizer = Prioritizer()
        self.registry = ConnectorRegistry()

        if self.sources_cfg:
            self.registry.load_from_config(self.sources_cfg)

    def run_cycle(
        self,
        output_dir: str | Path = "dashboard/data",
        db_path: str | Path = "data/sentinel_cache.sqlite",
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Executes a full scanning and publishing cycle."""
        logger.info("Starting Sentinel intelligence scanning cycle...")

        # Step 1: Collect from registered connectors
        raw_mentions, results = self.registry.collect_all_mentions()
        logger.info(
            "Gathered %d raw mentions across %d connectors.",
            len(raw_mentions),
            len(results),
        )

        # Step 2: Semantic enrichment, brand self-exclusion & URL deduplication
        enriched_mentions: list[MentionDTO] = []
        seen_urls: set[str] = set()
        for m in raw_mentions:
            norm_url = (m.url or "").strip().rstrip("/").lower()
            if not norm_url or norm_url in seen_urls:
                continue
            enriched = self.matcher.enrich_mention(m)
            if enriched:
                seen_urls.add(norm_url)
                # Add calculated priority score and response if missing or default
                final_mention = self.prioritizer.enrich(enriched)
                enriched_mentions.append(final_mention)
            else:
                logger.debug("Mention %s discarded by official-brand, negative, or brand filter.", m.id)

        # Step 3: Deduplication and persistence
        if dry_run:
            temp_dedup = Deduplicator(db_path=":memory:")
            new_mentions = [m for m in enriched_mentions if not temp_dedup.is_duplicate(m.id)]
            temp_dedup.close()
        else:
            db_file = Path(db_path)
            if db_path != ":memory:":
                db_file.parent.mkdir(parents=True, exist_ok=True)
            deduplicator = Deduplicator(db_path=str(db_path))
            new_mentions = deduplicator.filter_new(enriched_mentions)
            deduplicator.close()

        logger.info(
            "Identified %d new mentions (out of %d enriched).",
            len(new_mentions),
            len(enriched_mentions),
        )

        # Step 4: JSON Export to Web SPA
        exported_files: dict[str, str] = {}
        if not dry_run:
            exporter = JsonExporter(default_output_dir=output_dir)
            exported_files = exporter.export_all(enriched_mentions, output_dir=output_dir)
            logger.info("Successfully exported telemetry data to %s", output_dir)
        else:
            logger.info("[DRY RUN] Skipped exporting files and SQLite mutation.")

        summary = {
            "status": "success",
            "total_collected": len(raw_mentions),
            "total_enriched": len(enriched_mentions),
            "new_mentions_count": len(new_mentions),
            "connectors_executed": len(results),
            "dry_run": dry_run,
            "exported_files": exported_files,
        }

        return summary


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for running the TX RACE Brand Sentinel radar."""
    parser = argparse.ArgumentParser(
        description="TX RACE Brand Sentinel — 360º Social Listening & Radar Orchestrator"
    )
    parser.add_argument(
        "--output-dir",
        default="dashboard/data",
        help="Directory where dashboard JSON files will be written (default: dashboard/data)",
    )
    parser.add_argument(
        "--db-path",
        default="data/sentinel_cache.sqlite",
        help="Path to SQLite deduplication database (default: data/sentinel_cache.sqlite)",
    )
    parser.add_argument(
        "--sources",
        default="config/sources.yaml",
        help="Path to data sources configuration (default: config/sources.yaml)",
    )
    parser.add_argument(
        "--keywords",
        default="config/keywords.yaml",
        help="Path to keywords and intent mapping (default: config/keywords.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute collection and matching without writing files or mutating SQLite cache",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Disable live HTTP scraping during CLI execution (use verified snapshot baseline only)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging",
    )

    args = parser.parse_args(argv)

    if not args.offline and not args.dry_run:
        os.environ.setdefault("SENTINEL_LIVE_NETWORK", "1")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        orchestrator = SentinelOrchestrator(
            sources_config_path=args.sources,
            keywords_config_path=args.keywords,
        )
        res = orchestrator.run_cycle(
            output_dir=args.output_dir,
            db_path=args.db_path,
            dry_run=args.dry_run,
        )
        print(f"Sentinel cycle complete: {res['total_enriched']} mentions processed ({res['new_mentions_count']} new).")
        return 0
    except Exception as exc:
        logger.exception("Fatal error executing Sentinel orchestrator cycle: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
