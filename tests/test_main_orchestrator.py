"""Deterministic unit and integration tests for SentinelOrchestrator and GitOps workflow."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from src.main import SentinelOrchestrator, main


class TestMainOrchestrator(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "data"
        self.db_path = Path(self.temp_dir) / "test_cache.sqlite"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_orchestrator_full_cycle_exports_only_real_third_party_mentions(self) -> None:
        orchestrator = SentinelOrchestrator(
            sources_config_path="config/sources.yaml",
            keywords_config_path="config/keywords.yaml",
        )
        summary = orchestrator.run_cycle(
            output_dir=self.output_dir,
            db_path=self.db_path,
            dry_run=False,
        )

        self.assertEqual(summary["status"], "success")
        self.assertGreaterEqual(summary["total_collected"], 25)
        self.assertGreaterEqual(summary["total_enriched"], 25)
        self.assertGreaterEqual(summary["connectors_executed"], 9)

        mentions_file = self.output_dir / "current_mentions.json"
        self.assertTrue(mentions_file.exists())
        self.assertTrue((self.output_dir / "kpis.json").exists())
        self.assertTrue((self.output_dir / "analytics.json").exists())
        self.assertTrue(self.db_path.exists())

        payload = json.loads(mentions_file.read_text(encoding="utf-8"))
        urls = [m["url"] for m in payload["mentions"]]
        self.assertEqual(len(urls), len(set(urls)), "Duplicate post URLs found in current_mentions.json")
        for m in payload["mentions"]:
            self.assertFalse(
                orchestrator.matcher.is_official_brand_source(m["author"], m["url"], m.get("author_url")),
                f"Official TX RACE mention leaked into export: {m['author']} ({m['url']})",
            )

    def test_orchestrator_dry_run_does_not_write_files(self) -> None:
        dry_out = Path(self.temp_dir) / "dry_data"
        orchestrator = SentinelOrchestrator(
            sources_config_path="config/sources.yaml",
            keywords_config_path="config/keywords.yaml",
        )
        summary = orchestrator.run_cycle(
            output_dir=dry_out,
            db_path=":memory:",
            dry_run=True,
        )

        self.assertTrue(summary["dry_run"])
        self.assertFalse(dry_out.exists())

    def test_cli_main_entrypoint(self) -> None:
        exit_code = main([
            "--output-dir", str(self.output_dir),
            "--db-path", str(self.db_path),
            "--offline",
            "--dry-run",
        ])
        self.assertEqual(exit_code, 0)

    def test_gitops_workflow_yaml_contract(self) -> None:
        workflow_file = Path(".github/workflows/sentinel_radar.yml")
        self.assertTrue(workflow_file.exists(), "sentinel_radar.yml does not exist")

        content = workflow_file.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)

        triggers = parsed.get("on") or parsed.get(True)
        self.assertIsNotNone(triggers)
        self.assertIn("schedule", triggers)
        self.assertIn("workflow_dispatch", triggers)

        cron_expression = triggers["schedule"][0]["cron"]
        self.assertEqual(cron_expression, "0 */4 * * *")

        jobs = parsed.get("jobs", {})
        self.assertIn("radar_scan", jobs)
        self.assertIn("deploy_pages", jobs)

        deploy_job = jobs["deploy_pages"]
        self.assertEqual(deploy_job["environment"]["name"], "github-pages")


if __name__ == "__main__":
    unittest.main()
