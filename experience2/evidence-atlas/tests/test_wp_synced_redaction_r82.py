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

PRIVATE = "COOKIE=apollo-secret; https://private.invalid/wp-admin"


class StubSuccessfulPage:
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
            "[data-fvx-record]:visible": 6, "[data-fva-record]:visible": 6,
        }
        if selector not in counts:
            raise AssertionError("UNEXPECTED_STUB_SELECTOR")
        return type("LocalLocator", (), {
            "count": lambda instance: counts[selector],
            "evaluate": lambda instance, script: "rgb(9, 10, 10)",
        })()


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
