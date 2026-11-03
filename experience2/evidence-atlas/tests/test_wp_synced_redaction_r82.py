#!/usr/bin/env python3
"""R82: failure-path redaction against fake browser lifecycle errors.

No WordPress or external network is used. Genuine WordPress acceptance
continues separately with all R77 assertions unchanged.
"""
from __future__ import annotations
import contextlib
import io
import json
import tempfile
import traceback
import unittest
from pathlib import Path

from wp_reusable_r77 import accept_synced_patterns
from wp_source_parity_r83 import NASA_SOURCE_URLS, CITE_IDS

PRIVATE = "COOKIE=apollo-secret; https://private.invalid/wp-admin"


class StubR83Locator:
    def __init__(self, page, selector, counts):
        self.page = page
        self.selector = selector
        self.counts = counts

    def count(self): return self.counts.get(self.selector, 0)
    def all(self):
        if self.selector == '.fva-card__external':
            return [StubR83Element(value, 'href') for value in NASA_SOURCE_URLS]
        if self.selector == '[data-fva-cite-id]':
            return [StubR83Element(value, 'data-fva-cite-id') for value in CITE_IDS]
        return []
    @property
    def first(self): return self
    def get_attribute(self, attr): return None
    def inner_text(self):
        if self.selector == '.fv-ex2-apollo-suite__head':
            return 'no image-use rights are asserted; unconfirmed S67-19766'
        if self.selector == '.fva-custody-status':
            return '0 of 6; not a human link check, photograph inspection, or rights clearance'
        return ''
    def focus(self): self.page.focused = self.selector
    def evaluate(self, script):
        if self.selector == '[data-fva-drawer]': return self.page.drawer_open
        if self.selector == '[data-fva-drawer] summary': return self.page.focused == self.selector
        return 'rgb(9, 10, 10)'

class StubR83Element:
    def __init__(self, value, attr): self.value, self.attr = value, attr
    def get_attribute(self, attr): return self.value if self.attr == attr else None

class StubKeyboard:
    def __init__(self, page): self.page = page
    def press(self, key):
        if key == 'Enter' and self.page.focused == '[data-fva-drawer] summary':
            self.page.drawer_open = not self.page.drawer_open

class StubSuccessfulPage:
    def __init__(self):
        self.drawer_open = False
        self.focused = None
        self.keyboard = StubKeyboard(self)
    """Minimal first-case no-JS control; exercises teardown-only failure."""

    def on(self, *args):
        pass

    def route(self, *args):
        pass

    def goto(self, *args, **kwargs):
        return type("Local200", (), {"status": 200})()

    def evaluate(self, script):
        if "window.top" in script:
            return 390
        if "scrollWidth" in script:
            return False
        raise AssertionError("UNEXPECTED_STUB_QUERY")

    def locator(self, selector):
        counts = {
            ".fv-ex2-apollo-suite": 1,
            "head link#fv-ex2-apollo-suite-css": 1,
            "head link#fv-ex2-evidence-atlas-css": 1,
            "head link#fv-ex2-research-desk-css": 1,
            "[data-fvx-record]": 6, "[data-fva-record]": 6,
            ".fv-ex2-ledger__custody dd": 30,
            "[data-fva-drawer] dd": 54,
            ".fv-ex2-apollo-suite img": 0,
            ".fv-ex2-apollo-suite [data-lat],[data-lon],[data-geo-edge]": 0,
            ".fva-card__external": 6, "[data-fva-cite-id]": 6,
            "[data-fva-drawer]": 6, "[data-fva-drawer] summary": 6,
            "[data-fvx-record]:visible": 6, "[data-fva-record]:visible": 6,
        }
        if selector not in counts and selector not in (
            '.fv-ex2-apollo-suite__head', '.fva-custody-status'):
            raise AssertionError("UNEXPECTED_STUB_SELECTOR")
        return StubR83Locator(self, selector, counts)


class StubContext:
    def __init__(self, page_error, close_error=None, success_page=False):
        self.page_error = page_error
        self.close_error = close_error
        self.success_page = success_page
        self.closed = False

    def new_page(self):
        if self.success_page:
            return StubSuccessfulPage()
        raise self.page_error

    def close(self):
        self.closed = True
        if self.close_error is not None:
            raise self.close_error


class StubBrowser:
    def __init__(self, context_error=None, page_error=None, close_error=None,
                 success_page=False):
        self.context_error = context_error
        self.page_error = page_error
        self.close_error = close_error
        self.success_page = success_page
        self.context = None

    def new_context(self, **kwargs):
        if self.context_error is not None:
            raise self.context_error
        self.context = StubContext(self.page_error, self.close_error,
                                   self.success_page)
        return self.context


class BrowserFailureTransportTests(unittest.TestCase):
    def run_failure(self, browser):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                try:
                    accept_synced_patterns(browser, None, output,
                        "http://127.0.0.1:9438/", lambda address: True,
                        Path("/nonexistent-axe.js"),
                        lambda *args: None, lambda *args: None)
                except RuntimeError as exc:
                    exposed_traceback = "".join(traceback.format_exception(exc))
                    exception_message = str(exc)
                else:
                    self.fail("Injected browser failure must never pass")
            receipt_path = output / "R81_SYNCED_PATTERN_HOLD.json"
            self.assertTrue(receipt_path.is_file(), "redacted receipt is required")
            receipt_raw = receipt_path.read_text()
            self.assertFalse((output / "R77_REUSABLE_BLOCK_WORDPRESS_RECEIPT.json").exists())
            return json.loads(receipt_raw), receipt_raw, stderr.getvalue(), exposed_traceback, exception_message

    def assert_redacted(self, result):
        receipt, raw, stderr, trace, message = result
        self.assertFalse(receipt["authentic_wordpress_gate_passed"])
        self.assertFalse(receipt["accepted"])
        self.assertEqual(receipt["release"], "STAGING_HOLD")
        self.assertEqual(message, "APOLLO_R82_SYNCED_PATTERN_HOLD")
        self.assertNotIn("apollo-secret", raw + stderr + trace + message)
        self.assertNotIn("private.invalid", raw + stderr + trace + message)
        self.assertNotIn("COOKIE=", raw + stderr + trace + message)

    def test_context_construction_fails_closed_and_redacted(self):
        result = self.run_failure(StubBrowser(context_error=RuntimeError(PRIVATE)))
        self.assert_redacted(result)
        self.assertEqual(result[0]["checkpoint"], "NAVIGATION")
        self.assertEqual(result[0]["assertion_code"], "UNCLASSIFIED_ASSERTION")

    def test_untrusted_page_assertion_never_reaches_ci_logs(self):
        browser = StubBrowser(page_error=AssertionError(PRIVATE))
        result = self.run_failure(browser)
        self.assert_redacted(result)
        self.assertTrue(browser.context.closed)
        self.assertEqual(result[0]["assertion_code"], "UNCLASSIFIED_ASSERTION")
        self.assertIn("APOLLO_R81_SYNCED_HOLD", result[2])

    def test_allowlisted_failure_code_preserved_without_raw_rethrow(self):
        result = self.run_failure(StubBrowser(
            page_error=AssertionError("R77_DESK_CUSTODY_LOST")))
        self.assert_redacted(result)
        self.assertEqual(result[0]["assertion_code"], "R77_DESK_CUSTODY_LOST")
        self.assertNotIn("R77_DESK_CUSTODY_LOST", result[3])

    def test_cleanup_failure_must_not_publish_first_exception(self):
        browser = StubBrowser(page_error=RuntimeError(PRIVATE),
                              close_error=RuntimeError(PRIVATE + ":cleanup"))
        result = self.run_failure(browser)
        self.assert_redacted(result)
        self.assertTrue(browser.context.closed)
        self.assertEqual(result[0]["checkpoint"], "NAVIGATION")
        self.assertEqual(result[0]["completed_r77_cases"], 0)

    def test_teardown_only_failure_has_cleanup_phase_and_no_pass_receipt(self):
        browser = StubBrowser(success_page=True, close_error=RuntimeError(PRIVATE))
        result = self.run_failure(browser)
        self.assert_redacted(result)
        self.assertEqual(result[0]["checkpoint"], "CLEANUP")
        self.assertEqual(result[0]["completed_r77_cases"], 1)
        self.assertIn("APOLLO_R82_CLEANUP_HOLD", result[2])
        self.assertTrue(browser.context.closed)

    def test_no_failure_is_mistaken_for_a_successful_case(self):
        browser = StubBrowser(page_error=ValueError(PRIVATE))
        result = self.run_failure(browser)
        self.assert_redacted(result)
        self.assertEqual(result[0]["completed_r77_cases"], 0)


if __name__ == "__main__":
    unittest.main()
