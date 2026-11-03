"""Fail-closed budget qualification for actual saved Gutenberg Chromium samples.

Known genuine #693 artifact: throttled 390px LCP 4132ms and 4112ms.
Do not confuse passing measurement/instrumentation CI with a releasable page.
"""
import unittest
from verify_saved_gutenberg_lab import PERF_INIT, budget_miss_codes


class SavedNativeBudgetGateTests(unittest.TestCase):
    def sample(self, profile, lcp=True, cls=True):
        return {"profile": profile, "lab_good_lcp": lcp, "lab_good_cls": cls}

    def test_known_real_mobile_lcp_failure_stays_a_release_hold(self):
        recorded = [
            self.sample("mobile_390_trial_1", False, True),
            self.sample("mobile_390_trial_2", False, True),
            self.sample("desktop_1440", True, True),
        ]
        self.assertEqual(
            budget_miss_codes(recorded),
            ["mobile_390_trial_1:LCP", "mobile_390_trial_2:LCP"],
        )

    def test_valid_performance_is_lab_only(self):
        self.assertEqual(budget_miss_codes([
            self.sample("mobile_390_trial_1"),
            self.sample("mobile_390_trial_2"),
            self.sample("desktop_1440"),
        ]), [])

    def test_missing_or_false_qualification_is_a_miss(self):
        self.assertEqual(
            budget_miss_codes([{"profile": "mobile", "lab_good_lcp": None}]),
            ["mobile:LCP", "mobile:CLS"],
        )
        self.assertEqual(
            budget_miss_codes([self.sample("mobile", True, False)]),
            ["mobile:CLS"],
        )

    def test_browser_reports_element_identity_without_sensitive_material(self):
        for token in (
            "largest-contentful-paint", "resourceBacked",
            "e.element", "e.size", "e.startTime", "fv-hf-", "buffered: true",
        ):
            self.assertIn(token, PERF_INIT)
        for forbidden in ("outerHTML", "textContent", "innerHTML",
                          "localStorage", "document.cookie"):
            self.assertNotIn(forbidden, PERF_INIT)


if __name__ == "__main__":
    unittest.main()
