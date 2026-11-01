"""R100: privacy-preserving, AST-verified CI failure-method diagnostics.

All fixtures, paths, invoice labels, and customer strings are synthetic.
The actual financial source suite must still pass before Windows packaging.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import offline_source_gate as gate
from scripts import unittest_provenance as child

RUNNER = Path(child.__file__).resolve()


def _payload(**override):
    record = {
        "schema": child.DIAG_SCHEMA,
        "phase": "execution",
        "failures": 1,
        "errors": 0,
        "modules": ["test_safe"],
        "omitted_module_count": 0,
        "methods": ["test_safe.test_known"],
        "omitted_method_count": 0,
    }
    record.update(override)
    return (child.DIAG_PREFIX + json.dumps(
        record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


class StaticMethodDiagnosticsR100(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r100-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.tests = self.root / "products" / "desktop" / "tests"
        self.tests.mkdir(parents=True)
        (self.tests / "test_safe.py").write_text(
            "import unittest\n"
            "class Fixture(unittest.TestCase):\n"
            " def test_known(self): pass\n"
            " def helper(self): pass\n"
            "class Outer:\n"
            " class Inner:\n"
            "  def test_nested(self): pass\n",
            encoding="utf-8",
        )

    def test_only_top_level_static_test_methods_admitted(self):
        self.assertEqual(child._source_method_inventory(self.tests),
                         {"test_safe.test_known"})

    def test_static_method_diagnostic_round_trips_through_strict_parent(self):
        self.assertIsNotNone(gate._safe_child_diagnostic(
            _payload(), allowed_methods=child._source_method_inventory(self.tests)))

    def test_child_rejects_synthetic_subtest_parameter_for_method_identity(self):
        class Fixture(unittest.TestCase):
            def test_known(self):
                with self.subTest(account="PRIVATE_ACCOUNT_VALUE"):
                    self.fail("PRIVATE_FILE/CUSTOMER_A.csv")
        Fixture.__module__ = "test_safe"
        result = unittest.TestResult()
        unittest.TestSuite([Fixture("test_known")]).run(result)
        note = child._public_failure_summary(
            result, {"test_safe"}, child._source_method_inventory(self.tests))
        self.assertEqual(note["methods"], ["test_safe.test_known"])
        self.assertEqual(note["failures"], 1)
        self.assertNotIn("PRIVATE", repr(note))
        self.assertNotIn("CUSTOMER_A", repr(note))
        self.assertIsNotNone(gate._safe_child_diagnostic(
            _payload(**note), allowed_methods={"test_safe.test_known"}))

    def test_untrusted_child_cannot_supply_uninventoried_method(self):
        self.assertIsNone(gate._safe_child_diagnostic(
            _payload(methods=["test_safe.test_forget_security"]),
            allowed_methods=child._source_method_inventory(self.tests)))

    def test_child_methods_are_not_accepted_without_parent_inventory(self):
        self.assertIsNone(gate._safe_child_diagnostic(_payload()))

    def test_unknown_customer_values_cannot_escape_via_method_field(self):
        for methods in (["test_safe.PRIVATE"], ["test_safe.test_known/PRIVATE"],
                        ["test_safe.test_known\\nSECRET"], ["PRIVATE.test_known"],
                        ["test_safe.test_" + "x" * 120]):
            with self.subTest(methods=methods):
                self.assertIsNone(gate._safe_child_diagnostic(
                    _payload(methods=methods),
                    allowed_methods=child._source_method_inventory(self.tests)))

    def test_parent_rejects_duplicated_unsorted_and_bogus_counts(self):
        allowed = {"test_safe.test_known", "test_safe.test_second"}
        for changes in (
            {"methods": ["test_safe.test_known", "test_safe.test_known"], "failures": 2},
            {"methods": ["test_safe.test_second", "test_safe.test_known"], "failures": 2},
            {"omitted_method_count": True},
            {"omitted_method_count": -1},
            {"omitted_method_count": 1},
            {"methods": ["test_safe.test_known", "test_safe.test_second"], "failures": 1},
            {"phase": "discovery", "failures": 0, "methods": []},
        ):
            with self.subTest(changes=changes):
                self.assertIsNone(gate._safe_child_diagnostic(
                    _payload(**changes), allowed_methods=allowed))

    def test_module_only_legacy_diagnostic_remains_accepted(self):
        original = child._discovery_summary({"test_safe", "test_missing"}, {"test_safe"})
        raw = (child.DIAG_PREFIX + json.dumps(original, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        self.assertIsNotNone(gate._safe_child_diagnostic(raw))
        self.assertNotIn("methods", original)

    def test_many_failures_are_sorted_and_limited_to_ten(self):
        methods = [f"test_{i:02d}" for i in range(16)]
        (self.tests / "test_safe.py").write_text(
            "class Fixture:\n" +
            "".join(f" def {method}(self): pass\n" for method in methods),
            encoding="utf-8",
        )
        class DummyResult:
            errors = []
            failures = []
        result = DummyResult()
        original = type("CodeOwnedCase", (), {"__module__": "test_safe"})
        for method in reversed(methods):
            item = original()
            item._testMethodName = method
            result.failures.append((item, "PRIVATE traceback"))
        allowed = child._source_method_inventory(self.tests)
        summary = child._public_failure_summary(result, {"test_safe"}, allowed)
        self.assertEqual(summary["methods"], ["test_safe.test_" + f"{i:02d}" for i in range(10)])
        self.assertEqual(summary["omitted_method_count"], 6)
        self.assertIsNotNone(gate._safe_child_diagnostic(_payload(**summary), allowed_methods=allowed))
        self.assertLess(len(_payload(**summary)), 2048)

    def test_real_subprocess_keeps_private_exception_data_hidden_both_modes(self):
        (self.tests / "test_safe.py").write_text(
            "import unittest\n"
            "class Fixture(unittest.TestCase):\n"
            " def test_known(self):\n"
            "  with self.subTest(customer='PRIVATE_CUSTOMER_447'):\n"
            "   self.fail('PRIVATE/INVOICE/NUMBER')\n",
            encoding="utf-8",
        )
        allowed = child._source_method_inventory(self.tests)
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                cmd = [sys.executable] + (["-OO"] if optimized else []) + [str(RUNNER)]
                output = subprocess.run(
                    cmd, cwd=self.root, stdin=subprocess.DEVNULL,
                    capture_output=True, timeout=30, check=False)
                self.assertNotEqual(output.returncode, 0)
                self.assertNotIn(b"PRIVATE_CUSTOMER", output.stdout + output.stderr)
                self.assertNotIn(b"PRIVATE/INVOICE", output.stdout + output.stderr)
                report = gate._safe_child_diagnostic(output.stdout, allowed_methods=allowed)
                self.assertIsNotNone(report)
                self.assertIn('"methods":["test_safe.test_known"]', report)
                self.assertIn(b"REJECTED: desktop unittest provenance unavailable", output.stderr)


if __name__ == "__main__":
    unittest.main()
