#!/usr/bin/env python3
"""Offline source-integrity regression for complete WordPress/Assembler axe QA.

These checks are STRUCTURAL ONLY. They cannot claim Chromium/axe PASS;
the exact-head GitHub Actions real WordPress workflow is still required.
"""
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("playground_assembler_render_gate.mjs")
WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "ex2-assembler-front-render-HOLD.yml"


class CompleteDocumentAxeRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SOURCE.read_text(encoding="utf-8")

    def test_component_is_not_mistaken_for_whole_page(self):
        self.assertIn("window.axe.run(scope,opts)", self.script)
        self.assertIn("runBounded(document.querySelector('[data-fv-home-flagship]'))", self.script)
        self.assertIn("runBounded(document)", self.script)

    def test_both_scan_results_are_release_blocking(self):
        self.assertIn("if(scans.flagship.length || scans.whole_document.length)", self.script)
        self.assertIn("throw new Error(`Automated axe findings", self.script)

    def test_real_axe_is_required_not_silently_skipped(self):
        self.assertIn("if(!window.axe)throw", self.script)
        self.assertIn("'wcag22aa'", self.script)

    def test_scans_are_bounded(self):
        self.assertIn("Promise.race([", self.script)
        self.assertIn("axe scan exceeded 40s", self.script)
        self.assertIn("40000", self.script)
        self.assertIn("clearTimeout(timer)", self.script)

    def test_failure_screenshots_are_captured_before_axe(self):
        screenshot = self.script.index("await page.screenshot(")
        axe = self.script.index("await page.addScriptTag({path:axePath})")
        self.assertLess(screenshot, axe)
        self.assertIn("fullPage:false", self.script)
        self.assertIn("width=>checkView(page,width,axePath,outputDirectory)", self.script)
        self.assertIn("collectViewportEvidence(", self.script)
        self.assertIn("if(viewportFailures.length)", self.script)
        self.assertIn("ISOLATED_ASSEMBLER_VIEWPORT_ADMISSION_HOLD", self.script)
        self.assertLess(self.script.index("await noContext.close();"),
                        self.script.index("if(viewportFailures.length)"))

    def test_existing_branch_still_requires_disposable_loopback(self):
        self.assertIn("assert.ok(loopback(server.serverUrl))", self.script)
        self.assertIn("const noContext=await browser.newContext({javaScriptEnabled:false", self.script)
        self.assertNotIn("wpcom_mcp_pages_update", self.script)

    def test_staging_language_is_not_parity_claim(self):
        self.assertIn("ISOLATED_WP_ASSEMBLER_RENDER_SYNTHETIC_ONLY", self.script)
        self.assertIn("not WP.com Atomic parity", self.script)
        self.assertIn("not manual WCAG 2.2 AA", self.script)


if __name__ == "__main__":
    unittest.main()
