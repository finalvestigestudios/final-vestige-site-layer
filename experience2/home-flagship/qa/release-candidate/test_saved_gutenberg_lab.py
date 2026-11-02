"""Adversarial admission for measured native saved Gutenberg Chromium samples."""
import math
import unittest
from verify_saved_gutenberg_lab import PERF_INIT, PROFILES, sample_issues


class NativeSavedPerformanceTests(unittest.TestCase):
    def good(self):
        return dict(http_status=200, chapters=7, viewport=390,
                    instrumentation_failed=False, lcp_ms=1740.1, cls=0.006)

    def test_valid_sample(self):
        self.assertEqual(sample_issues(self.good(), 390), [])

    def test_wrong_or_fake_source_rejected(self):
        for changes in (
            {"http_status": 302}, {"chapters": 6}, {"viewport": 1440},
            {"instrumentation_failed": True}):
            with self.subTest(changes=changes):
                self.assertTrue(sample_issues({**self.good(), **changes}, 390))

    def test_missing_nan_infinite_and_boolean_metrics_rejected(self):
        for val in (None, float("nan"), float("inf"), -1, True, "2.5", 0):
            with self.subTest(value=repr(val)):
                self.assertTrue(sample_issues({**self.good(), "lcp_ms": val}, 390))
        for val in (None, float("nan"), float("-inf"), -1, False, "0"):
            with self.subTest(value=repr(val)):
                self.assertTrue(sample_issues({**self.good(), "cls": val}, 390))

    def test_instrumentation_is_genuine_lcp_and_cls(self):
        for contract in ("PerformanceObserver", "largest-contentful-paint",
                         "layout-shift", "hadRecentInput", "buffered: true"):
            self.assertIn(contract, PERF_INIT)

    def test_profiles_cold_cache_throttled_repeat(self):
        self.assertEqual(PROFILES, (("mobile_390_trial_1", 390, 4, True),
                                    ("mobile_390_trial_2", 390, 4, True),
                                    ("desktop_1440", 1440, 1, False)))


if __name__ == "__main__":
    unittest.main()
