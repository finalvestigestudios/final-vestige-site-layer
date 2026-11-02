#!/usr/bin/env python3
"""Offline negative/positive tests for privacy-safe, fail-closed lab decisions."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("measure_private_lab.py")
spec = importlib.util.spec_from_file_location("fv_ex2_lab", SCRIPT)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def sample(**changes):
    value = {"profile":"mobile_390_4x_cpu_slow4g","trial":1,
             "viewport":390,"http_status":200,"chapter_count":7,
             "lcp_ms":1580.3,"cls":0.005}
    value.update(changes)
    return value


class PrivateLabTest(unittest.TestCase):
    def test_good_measured_mobile(self):
        self.assertEqual(lab.grade(sample()), [])

    def test_budget_boundaries_accepted(self):
        self.assertEqual(lab.grade(sample(lcp_ms=2500,cls=0.1)), [])

    def test_lcp_regression_fails(self):
        self.assertIn("LCP_MS_LAB_BUDGET_EXCEEDED",
                      lab.grade(sample(lcp_ms=2500.1)))

    def test_cls_regression_fails(self):
        self.assertIn("CLS_LAB_BUDGET_EXCEEDED",lab.grade(sample(cls=0.101)))

    def test_missing_lcp_fails(self):
        self.assertIn("LCP_MS_NOT_MEASURED",lab.grade(sample(lcp_ms=None)))

    def test_not_a_number_fails(self):
        self.assertIn("CLS_NOT_MEASURED",lab.grade(sample(cls=float("nan"))))

    def test_infinite_lcp_fails(self):
        self.assertIn("LCP_MS_NOT_MEASURED",lab.grade(sample(lcp_ms=float("inf"))))

    def test_false_wordpress_or_wrong_chapters_fails(self):
        for changes in ({"http_status":302},{"chapter_count":6},
                        {"http_status":0},{"chapter_count":0}):
            self.assertIn("NOT_CANONICAL_RENDER",lab.grade(sample(**changes)))

    def test_wrong_viewport_fails(self):
        self.assertIn("UNEXPECTED_VIEWPORT",lab.grade(sample(viewport=744)))

    def test_no_runtime_secret_reporting_or_production_calls(self):
        data=SCRIPT.read_text()
        self.assertNotIn("print(private_url)",data)
        self.assertNotIn('str(exc)',data)
        self.assertIn("check_private_render_url",data)
        self.assertIn("NOT_MEASURED",data)
        self.assertIn("production_writes",data)
        self.assertNotIn('https://finalvestige.com/wp-admin',data)


if __name__=="__main__":
    unittest.main()
