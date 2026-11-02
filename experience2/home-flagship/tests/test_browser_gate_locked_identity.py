#!/usr/bin/env python3
"""Regression guards for the exact PR #550 locked-direction browser QA.

Source/contract tests only. They cannot certify Chromium, WordPress, WCAG,
image transfer, or release readiness. Run browser suites separately.
"""
from pathlib import Path
import unittest

HOME = Path(__file__).resolve().parents[1]
HTML = HOME / "index.html"
CSS = HOME / "flagship.css"
CSP = HOME / "qa/release-candidate/verify_csp_exact_browser.py"
FULL = HOME / "qa/integration/verify_full_browser.py"


class LockedIdentityBrowserGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.csp = CSP.read_text(encoding="utf-8")
        cls.full = FULL.read_text(encoding="utf-8")

    def test_seven_chapter_locked_candidate(self):
        self.assertIn("DO NOT DEPLOY AS THE WORDPRESS HOME PAGE", self.html)
        self.assertIn('class="fv-hf__folio-note"', self.html)
        self.assertIn('<time datetime="1847-05-28">', self.html)
        self.assertIn("APRIL 1848", self.html)
        self.assertIn("--hf-gold:#d4ad73", self.css)
        self.assertNotIn("data-fv-direction-choice", self.html)
        self.assertNotIn('data-fv-direction="', self.html)

    def test_browser_gates_do_not_target_retired_studio_ui(self):
        for script in (self.csp, self.full):
            with self.subTest(script=script[:45]):
                self.assertNotIn(".fv-hf__studio-controls", script)
                self.assertNotIn('data-fv-direction-choice="museum"', script)
                self.assertNotIn("museum_direction", script)

    def test_full_browser_exercises_rendered_folio(self):
        self.assertIn('width_{width}_locked_editorial_direction', self.full)
        self.assertIn('width_{width}_franklin_folio_painted', self.full)
        self.assertIn('getComputedStyle(node)', self.full)
        self.assertIn('node.getBoundingClientRect()', self.full)
        self.assertIn('time[datetime="1847-05-28"]', self.full)
        self.assertIn('width_{width}_observer_b', self.full)
        self.assertIn('width_{width}_original_selected', self.full)

    def test_csp_four_real_interactions(self):
        self.assertIn('WIDTHS = (320,360,390,768,1024,1440,1920)', self.csp)
        self.assertIn("page.keyboard.press(\"ArrowRight\")", self.csp)
        self.assertIn('data-fv-case-button="franklin"', self.csp)
        self.assertIn('data-fv-case-button="malbone"', self.csp)
        self.assertIn('data-fv-chronicle-view="addition"', self.csp)
        self.assertIn('data-fv-observer-switch="b"', self.csp)
        self.assertIn('"interaction_checks":4', self.csp)

    def test_three_negative_controls_still_fail_closed(self):
        for name in ('"no_js"', '"unapproved_inline_script"', '"bad_flagship_nonce"'):
            with self.subTest(negative=name):
                self.assertIn(name, self.csp)
        self.assertIn('window.FV_HACK !== 1', self.csp)
        self.assertIn('assert violations', self.csp)
        self.assertIn('assert page.locator("[data-fv-case]:visible").count()==3', self.csp)

    def test_no_prod_mutations_or_commercial_additions(self):
        for source in (self.csp, self.full):
            self.assertNotIn("wp_insert_post(", source)
            self.assertNotIn("pages.update", source)
            self.assertNotIn("affiliate_id=", source)


if __name__ == "__main__":
    unittest.main()
