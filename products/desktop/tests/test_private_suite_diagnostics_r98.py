"""R98 privacy-safe diagnostics: source-owned modules only, never private values."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import offline_source_gate as gate
from scripts import unittest_provenance as child

RUNNER = Path(child.__file__).resolve()


class DiagnosticR98Tests(unittest.TestCase):
    def payload(self, **updates):
        obj = {"schema": child.DIAG_SCHEMA, "phase": "execution", "failures": 1,
               "errors": 0, "modules": ["test_safe"], "omitted_module_count": 0}
        obj.update(updates)
        return (child.DIAG_PREFIX +
                json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")

    def test_valid_marker(self):
        self.assertIn("test_safe", gate._safe_child_diagnostic(self.payload()))

    def test_malformed_child_cannot_leak_data(self):
        attacks = (
            b"private C:/client/invoices.csv",
            self.payload() + b"private extra line\n",
            self.payload().replace(b"test_safe", b"private client"),
            self.payload().replace(b'"failures":1', b'"failures":true'),
            self.payload().replace(b'"failures":1', b'"failures":0'),
            self.payload().replace(b'"modules":["test_safe"]', b'"modules":["../secret"]'),
            b"\xff" + self.payload(), b"x" * 2100,
        )
        for payload in attacks:
            with self.subTest(sample=payload[:20]):
                self.assertIsNone(gate._safe_child_diagnostic(payload))

    def test_module_name_whitelist(self):
        for name in ("private_module", "test_UPPER", "test_bad/file", "test_x y",
                     "test_" + "x" * 91):
            with self.subTest(name=name):
                self.assertIsNone(gate._safe_child_diagnostic(self.payload(modules=[name])))

    def test_strict_counts_and_order(self):
        for changed in (
            {"failures": True}, {"failures": 0}, {"errors": -1},
            {"omitted_module_count": 20001}, {"phase": "other"},
            {"modules": ["test_z", "test_a"], "failures": 2},
            {"modules": ["test_a", "test_a"], "failures": 2},
            {"modules": ["test_a", "test_b"], "failures": 1},
            {"modules": ["test_a"], "omitted_module_count": 1},
        ):
            with self.subTest(change=changed):
                self.assertIsNone(gate._safe_child_diagnostic(self.payload(**changed)))

    def test_discovery_marker_is_separate_from_execution(self):
        obj = child._discovery_summary({"test_alpha", "test_beta"}, {"test_alpha"})
        self.assertEqual(obj["phase"], "discovery")
        self.assertEqual(obj["modules"], ["test_beta"])
        self.assertIsNotNone(gate._safe_child_diagnostic(self.payload(**obj)))
        self.assertIsNone(gate._safe_child_diagnostic(self.payload(
            phase="discovery", failures=1)))

    def test_subtest_parameters_do_not_enter_source_names(self):
        class Fixture(unittest.TestCase):
            def runTest(self):
                with self.subTest(customer="PRIVATE_98765"):
                    self.fail("C:/secret/customer.csv")
        Fixture.__module__ = "test_safe"
        result = unittest.TestResult()
        unittest.TestSuite([Fixture()]).run(result)
        doc = child._public_failure_summary(result, {"test_safe"})
        self.assertEqual(doc["modules"], ["test_safe"])
        self.assertNotIn("PRIVATE", repr(doc))
        self.assertNotIn("C:/secret", repr(doc))
        self.assertIsNotNone(gate._safe_child_diagnostic(self.payload(**doc)))

    def test_unknown_test_module_is_hidden(self):
        class Fixture(unittest.TestCase):
            def runTest(self):
                self.fail("private test input")
        Fixture.__module__ = "customer_defined_name"
        result = unittest.TestResult()
        unittest.TestSuite([Fixture()]).run(result)
        doc = child._public_failure_summary(result, {"test_safe"})
        self.assertEqual(doc["modules"], [])
        self.assertEqual(doc["failures"], 1)

    def test_module_list_capped_to_twelve(self):
        class FakeResult:
            failures = []
            errors = []
        result = FakeResult()
        modules = set()
        for i in range(18):
            name = f"test_{i:02}"
            cls = type(f"Fixture{i}", (), {"__module__": name})
            result.failures.append((cls(), "secret traceback"))
            modules.add(name)
        doc = child._public_failure_summary(result, modules)
        self.assertEqual(len(doc["modules"]), 12)
        self.assertEqual(doc["omitted_module_count"], 6)
        self.assertIsNotNone(gate._safe_child_diagnostic(self.payload(**doc)))

    def test_parent_keeps_child_stderr_in_devnull_and_rejects_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(gate.subprocess, "run") as run:
                run.return_value = subprocess.CompletedProcess(
                    ["python"], 1, stdout=self.payload(), stderr=b"PRIVATE value")
                with self.assertRaises(gate.SourceSuiteFailure) as raised:
                    gate._child_suite(Path(directory), False, timeout=61)
                self.assertIn("test_safe", raised.exception.diagnostic)
                self.assertNotIn("PRIVATE", raised.exception.diagnostic)
                self.assertEqual(run.call_args.kwargs["stderr"], subprocess.DEVNULL)

    def test_parent_refuses_forged_private_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(gate.subprocess, "run") as run:
                run.return_value = subprocess.CompletedProcess(
                    ["python"], 1, stdout=b"C:/private/ledger.csv", stderr=b"")
                with self.assertRaises(gate.SourceSuiteFailure) as raised:
                    gate._child_suite(Path(directory), True, timeout=61)
                self.assertIsNone(raised.exception.diagnostic)

    def test_real_synthetic_subtest_failure_normal_and_optimized(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r98-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_private.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n"
                " def test_bad(self):\n"
                "  with self.subTest(account='PRIVATE_ACCOUNT_123'):\n"
                "   self.fail('C:/private/customer.xlsx')\n", encoding="utf-8")
            for optimized in (False, True):
                command = [sys.executable] + (["-OO"] if optimized else []) + [str(RUNNER)]
                p = subprocess.run(command, cwd=root, capture_output=True, timeout=30)
                self.assertNotEqual(p.returncode, 0)
                self.assertNotIn(b"PRIVATE_ACCOUNT", p.stdout + p.stderr)
                self.assertNotIn(b"C:/private", p.stdout + p.stderr)
                self.assertIn("test_private", gate._safe_child_diagnostic(p.stdout))

    def test_real_synthetic_import_failure_reports_discovery(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r98-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_broken.py").write_text(
                "raise ImportError('C:/private/dir.csv')\n", encoding="utf-8")
            p = subprocess.run([sys.executable, str(RUNNER)], cwd=root,
                               capture_output=True, timeout=30)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('"phase":"discovery"', gate._safe_child_diagnostic(p.stdout))
            self.assertNotIn(b"C:/private", p.stdout + p.stderr)

    def test_successful_child_keeps_v2_manifest(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r98-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_ok.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): pass\n",
                encoding="utf-8")
            p = subprocess.run([sys.executable, str(RUNNER)], cwd=root,
                               capture_output=True, timeout=30)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["schema"], "fvs-unittest-provenance-v2")
            self.assertIsNone(gate._safe_child_diagnostic(p.stdout))


if __name__ == "__main__":
    unittest.main()
