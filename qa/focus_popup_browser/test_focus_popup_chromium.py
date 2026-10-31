"""Isolated Chromium smoke test of unpublished PR #349 Focus popup assets.

No network calls, subscriber submissions, WordPress writes, or actual Jetpack form.
Representative mocked form only; native Gutenberg/Jetpack rendering and email
confirmation-to-welcome-to-PDF acceptance remain separate RELEASE HOLD gates.
"""
import os
import shutil
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
CONVERSION = ROOT / "experience2" / "conversion"
HTML = (CONVERSION / "focus-popup.html").read_text(encoding="utf-8")
CSS = (CONVERSION / "focus-popup.css").read_text(encoding="utf-8")
SCRIPT = (CONVERSION / "focus-popup.js").read_text(encoding="utf-8")
BLOCK = '<!-- wp:jetpack/subscriptions {"submitButtonText":"Join & get the Fieldbook"} /-->'
MOCK_FORM = (
    '<form action="/" method="post">'
    '<label>Email <input type="email" name="email" required></label>'
    '<button type="submit">Subscribe</button></form>'
)
WIDTHS = (320, 390, 768, 1440)
MODES = ("unrendered_js", "form_js", "unrendered_nojs", "form_nojs")


class FocusPopupChromiumQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HTML.count(BLOCK) == 1, "Jetpack placeholder changed; review mock substitution"
        cls.browser_context = sync_playwright()
        cls.playwright = cls.browser_context.start()
        chrome = os.environ.get("FV_CHROMIUM") or shutil.which("chromium")
        launch = {"headless": True, "args": ["--no-sandbox"]}
        if chrome:
            launch["executable_path"] = chrome
        cls.browser = cls.playwright.chromium.launch(**launch)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_sixteen_fail_open_and_keyboard_cases(self):
        for width in WIDTHS:
            for mode in MODES:
                with self.subTest(width=width, mode=mode):
                    js_enabled = not mode.endswith("nojs")
                    rendered_form = mode.startswith("form")
                    page = self.browser.new_page(
                        viewport={"width": width, "height": 800},
                        java_script_enabled=js_enabled,
                    )
                    errors = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    try:
                        fragment = HTML.replace(BLOCK, MOCK_FORM) if rendered_form else HTML
                        page.set_content(
                            "<!doctype html><html><head><meta name='viewport' "
                            "content='width=device-width,initial-scale=1'>"
                            "<style>body{margin:0;font:16px Arial,sans-serif}</style>"
                            f"<style>{CSS}</style></head><body>{fragment}</body></html>"
                        )
                        if js_enabled:
                            page.evaluate(SCRIPT)
                        state = page.evaluate("""() => ({
                            button: !!document.querySelector('.fv-focus-invite__open').getClientRects().length,
                            fallback: !!document.querySelector('.fv-focus-invite__fallback').getClientRects().length,
                            forms: document.querySelectorAll('form').length,
                            horizontalOverflow: document.documentElement.scrollWidth-innerWidth
                        })""")
                        self.assertLessEqual(state["horizontalOverflow"], 1)
                        self.assertEqual(state["forms"], 1 if rendered_form else 0)
                        expected_dialog_button = rendered_form and js_enabled
                        self.assertEqual(state["button"], expected_dialog_button)
                        self.assertEqual(state["fallback"], not expected_dialog_button)
                        if expected_dialog_button:
                            opener = page.locator(".fv-focus-invite__open")
                            opener.focus()
                            opener.press("Enter")
                            self.assertTrue(page.locator("dialog").evaluate("el => el.open"))
                            self.assertEqual(page.evaluate("document.activeElement.type"), "email")
                            page.keyboard.press("Escape")
                            self.assertFalse(page.locator("dialog").evaluate("el => el.open"))
                            page.wait_for_timeout(30)
                            self.assertTrue(opener.evaluate("el => document.activeElement === el"))
                        self.assertFalse(errors, errors)
                    finally:
                        page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
