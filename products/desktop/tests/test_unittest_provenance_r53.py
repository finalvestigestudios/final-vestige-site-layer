"""Adversarial R53 tests for source-suite counts, discovery and privacy."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "unittest_provenance.py"
SPEC = importlib.util.spec_from_file_location("fvs_unittest_provenance_r53", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class UnittestProvenanceR53Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r53-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.tests = self.root / "products" / "desktop" / "tests"
        self.tests.mkdir(parents=True)

    def write(self, name, source):
        path = self.tests / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def invoke(self, *, optimized=False):
        command = [sys.executable]
        if optimized:
            command.append("-OO")
        command.append(str(SCRIPT))
        return subprocess.run(command, cwd=self.root, capture_output=True, timeout=20)

    def test_two_modules_multiple_cases_produce_only_counts_and_digest(self):
        self.write("test_alpha.py", "import unittest\nclass A(unittest.TestCase):\n def test_one(self): self.assertTrue(True)\n def test_two(self): self.assertEqual(3,3)\n")
        self.write("test_beta.py", "import unittest\nclass B(unittest.TestCase):\n def test_three(self): self.assertTrue(True)\n")
        output = self.invoke()
        self.assertEqual(output.returncode, 0, output.stderr)
        value = json.loads(output.stdout)
        self.assertEqual(value["test_count"], 3)
        self.assertEqual(value["module_count"], 2)
        self.assertEqual(value["skipped_count"], 0)
        self.assertRegex(value["test_ids_sha256"], r"^[a-f0-9]{64}$")
        self.assertEqual(output.stderr, b"")
        optimized = self.invoke(optimized=True)
        self.assertEqual(optimized.returncode, 0, optimized.stderr)
        self.assertEqual(value, json.loads(optimized.stdout))

    def test_empty_directory_fails(self):
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_zero_cases_hidden_in_named_test_file_fails(self):
        self.write("test_empty.py", "# intentionally empty\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_partially_discovered_empty_module_fails(self):
        self.write("test_real.py", "import unittest\nclass T(unittest.TestCase):\n def test_yes(self): pass\n")
        self.write("test_empty.py", "# would be silently ignored by unittest\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_failed_test_exposes_no_traceback_or_private_value(self):
        self.write("test_bad.py", "import unittest\nclass T(unittest.TestCase):\n def test_no(self):\n  print('private customer data 123')\n  self.fail('private customer data 456')\n")
        output = self.invoke()
        self.assertNotEqual(output.returncode, 0)
        self.assertNotIn(b"private customer data", output.stdout + output.stderr)
        self.assertNotIn(str(self.root).encode(), output.stdout + output.stderr)

    def test_successful_test_prints_are_not_in_evidence(self):
        self.write("test_print.py", "import unittest\nclass T(unittest.TestCase):\n def test_y(self):\n  print('confidential fixture')\n  self.assertTrue(True)\n")
        output = self.invoke()
        self.assertEqual(output.returncode, 0)
        self.assertNotIn(b"confidential fixture", output.stdout)
        self.assertEqual(json.loads(output.stdout)["test_count"], 1)

    def test_all_skipped_fails_closed(self):
        self.write("test_skip.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skip('not executed')\n def test_x(self): pass\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_one_skip_is_reported_but_real_test_passes(self):
        self.write("test_skip.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skip('skip')\n def test_x(self): pass\n def test_y(self): pass\n")
        data = json.loads(self.invoke().stdout)
        self.assertEqual((data["test_count"],data["skipped_count"]),(2,1))

    def test_import_failure_fails_closed(self):
        self.write("test_import.py", "raise ImportError('private customer location')\n")
        output = self.invoke()
        self.assertNotEqual(output.returncode, 0)
        self.assertNotIn(b"private customer location", output.stderr)

    def test_nested_module_without_importable_package_fails_discovery(self):
        self.write("test_real.py", "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): pass\n")
        self.write("nested/test_orphan.py", "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): pass\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_optimized_only_skip_is_observable_in_counts(self):
        self.write("test_debug.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skipIf(not __debug__, 'optimized')\n def test_sensitive(self): pass\n def test_normal(self): pass\n")
        regular = json.loads(self.invoke().stdout)
        optimized = json.loads(self.invoke(optimized=True).stdout)
        self.assertEqual(regular["test_ids_sha256"], optimized["test_ids_sha256"])
        self.assertNotEqual(regular["skipped_count"], optimized["skipped_count"])
        self.assertNotEqual(regular["active_ids_sha256"], optimized["active_ids_sha256"])
        self.assertNotEqual(regular["skipped_ids_sha256"], optimized["skipped_ids_sha256"])


if __name__ == "__main__":
    unittest.main()
