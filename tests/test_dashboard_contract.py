"""Deterministic contract tests for the High-Density Web SPA Dashboard.
Verifies compliance with .harness/invariants/ux_contract.yaml and PROJECT.md requirements.
"""
import re
import unittest
from pathlib import Path


class TestDashboardContract(unittest.TestCase):
    def setUp(self) -> None:
        self.dashboard_dir = Path("dashboard")
        self.html_file = self.dashboard_dir / "index.html"
        self.css_file = self.dashboard_dir / "styles.css"
        self.js_file = self.dashboard_dir / "app.js"

        self.assertTrue(self.html_file.exists(), "dashboard/index.html does not exist")
        self.assertTrue(self.css_file.exists(), "dashboard/styles.css does not exist")
        self.assertTrue(self.js_file.exists(), "dashboard/app.js does not exist")

        self.html_content = self.html_file.read_text(encoding="utf-8")
        self.css_content = self.css_file.read_text(encoding="utf-8")
        self.js_content = self.js_file.read_text(encoding="utf-8")

    def test_7_existential_states_containers_present_in_html(self) -> None:
        """Verifies that all 7 existential state containers exist in index.html."""
        self.assertIn('id="loadingState"', self.html_content)
        self.assertIn('id="emptyState"', self.html_content)
        self.assertIn('id="zeroResultsState"', self.html_content)
        self.assertIn('id="errorState"', self.html_content)
        self.assertIn('id="partialDegradedBanner"', self.html_content)
        self.assertIn('id="populatedState"', self.html_content)
        self.assertIn('id="toastContainer"', self.html_content)

    def test_single_primary_cta_in_header_context(self) -> None:
        """Verifies strict adherence to SINGLE_PRIMARY_CTA rule in the header."""
        header_match = re.search(r"<header.*?</header>", self.html_content, re.DOTALL)
        self.assertIsNotNone(header_match)
        assert header_match is not None
        header_html = header_match.group(0)

        primary_buttons = re.findall(r'class="[^"]*btn-primary[^"]*"', header_html)
        self.assertEqual(
            len(primary_buttons),
            1,
            f"Header must contain strictly 1 btn-primary CTA, found {len(primary_buttons)}",
        )
        self.assertIn('id="btnRefresh"', header_html)

    def test_no_functional_emojis_in_buttons_or_actions(self) -> None:
        """Verifies that functional buttons do not use emojis (NO_FUNCTIONAL_EMOJIS)."""
        button_matches = re.findall(r"<button[^>]*>(.*?)</button>", self.html_content, re.DOTALL)
        emoji_pattern = re.compile(
            r"[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U0001F600-\U0001F64F\U00002702-\U000027B0\U0001F1E0-\U0001F1FF]"
        )

        for btn in button_matches:
            plain_text = re.sub(r"<[^>]+>", "", btn).strip()
            self.assertFalse(
                emoji_pattern.search(plain_text),
                f"Prohibited emoji found in functional button text: '{plain_text}'",
            )

    def test_dark_theme_css_tokens_and_open_post_button_hit_target(self) -> None:
        """Verifies Sentinel Dark Theme tokens, modular spacing, and reliable external link button styling."""
        self.assertIn("#0B0F17", self.css_content)
        self.assertIn("#111827", self.css_content)
        self.assertIn("#1F2937", self.css_content)
        self.assertIn("tabular-nums", self.css_content)
        self.assertIn("min-height: 32px", self.css_content)
        self.assertIn("btn-spinner", self.css_content)
        self.assertIn(".btn-open-post", self.css_content)
        self.assertIn("pointer-events: none", self.css_content)

    def test_external_post_links_sanitized_and_accessible_in_js(self) -> None:
        """Verifies URL protocol sanitization, self-brand guard, rel=noopener, and inert modal management."""
        self.assertIn("function sanitizeExternalUrl(", self.js_content)
        self.assertIn("function isOfficialBrandMention(", self.js_content)
        self.assertIn('class="btn btn-open-post"', self.js_content)
        self.assertIn('rel="noopener noreferrer"', self.js_content)
        self.assertIn('aria-label="Abrir Post:', self.js_content)
        self.assertIn("dom.mainContent.inert = true", self.js_content)
        self.assertIn("dom.mainContent.inert = false", self.js_content)

    def test_behavioral_predictability_escape_dismiss_in_js(self) -> None:
        """Verifies DISMISS_ON_ESCAPE rule is implemented for ForensicDrawer."""
        self.assertIn("Escape", self.js_content)
        self.assertIn("closeForensicDrawer", self.js_content)

    def test_4_views_supported_in_html_and_js(self) -> None:
        """Verifies the 4 views (Cards, Table, Analytics, ForensicDrawer) exist."""
        self.assertIn('id="cardsViewContainer"', self.html_content)
        self.assertIn('id="tableViewContainer"', self.html_content)
        self.assertIn('id="analyticsViewContainer"', self.html_content)
        self.assertIn('id="forensicDrawer"', self.html_content)
        self.assertIn('id="tabCards"', self.html_content)
        self.assertIn('id="tabTable"', self.html_content)
        self.assertIn('id="tabAnalytics"', self.html_content)


if __name__ == "__main__":
    unittest.main()
