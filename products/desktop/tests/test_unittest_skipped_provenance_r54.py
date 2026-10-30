"""R54: adversarial coverage for optimization-mode skip-swap and module skips."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "unittest_provenance.py"
SPEC = importlib.util.spec_from_file_location("fvs_unittest_provenance_r54", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class SkippedTestProvenanceR54Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r54-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.tests = self.root / "products" / "desktop" / "tests"
        self.tests.mkdir(parents=True)

    def write(self, name, source):
        path = self.tests / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def invoke(self, optimized=False):
        command = [sys.executable]
        if optimized:
            command.append("-OO")
        command.append(str(SCRIPT))
        return subprocess.run(command, cwd=self.root, capture_output=True, timeout=20)

    def test_normal_and_optimized_same_active_cases_agree(self):
        self.write("test_one.py", "import unittest\nclass T(unittest.TestCase):\n def test_a(self): pass\n @unittest.skip('disabled fixture')\n def test_b(self): pass\n")
        regular, optimized = self.invoke(), self.invoke(True)
        self.assertEqual(regular.returncode, 0)
        self.assertEqual(optimized.returncode, 0)
        self.assertEqual(json.loads(regular.stdout), json.loads(optimized.stdout))
        self.assertEqual(json.loads(regular.stdout)["schema"], "fvs-unittest-provenance-v2")

    def test_opposite_skips_same_counts_detectable(self):
        self.write("test_swap.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skipIf(__debug__, 'normal only')\n def test_a(self): pass\n @unittest.skipIf(not __debug__, 'optimized only')\n def test_b(self): pass\n def test_always(self): pass\n")
        regular, optimized = self.invoke(), self.invoke(True)
        self.assertEqual((regular.returncode, optimized.returncode), (0, 0))
        a, b = json.loads(regular.stdout), json.loads(optimized.stdout)
        for field in ("test_count", "module_count", "skipped_count", "test_ids_sha256"):
            self.assertEqual(a[field], b[field], field)
        self.assertNotEqual(a["active_ids_sha256"], b["active_ids_sha256"])
        self.assertNotEqual(a["skipped_ids_sha256"], b["skipped_ids_sha256"])

    def test_entire_module_skipped_even_when_other_module_active_fails(self):
        self.write("test_active.py", "import unittest\nclass A(unittest.TestCase):\n def test_ok(self): pass\n")
        self.write("test_skipped.py", "import unittest\n@unittest.skip('offline')\nclass B(unittest.TestCase):\n def test_missed(self): pass\n")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(str(self.root).encode(), result.stdout + result.stderr)

    def test_two_active_modules_with_one_skipped_case_pass(self):
        self.write("test_a.py", "import unittest\nclass A(unittest.TestCase):\n def test_a(self): pass\n")
        self.write("test_b.py", "import unittest\nclass B(unittest.TestCase):\n @unittest.skip('manual')\n def test_b(self): pass\n def test_c(self): pass\n")
        data = json.loads(self.invoke().stdout)
        self.assertEqual((data["module_count"], data["test_count"], data["skipped_count"]), (2, 3, 1))

    def test_skip_reason_not_leaked_to_stdout_or_evidence(self):
        self.write("test_private.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skip('PRIVATE CUSTOMER ID 77339')\n def test_skip(self): pass\n def test_pass(self): pass\n")
        result = self.invoke()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(b"PRIVATE CUSTOMER", result.stdout + result.stderr)
        self.assertEqual(set(json.loads(result.stdout)), {"schema", "test_count", "module_count", "skipped_count", "test_ids_sha256", "active_ids_sha256", "skipped_ids_sha256"})

    def test_all_skipped_still_fails(self):
        self.write("test_all.py", "import unittest\nclass T(unittest.TestCase):\n @unittest.skip('no live cases')\n def test_missing(self): pass\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_zero_test_file_still_fails(self):
        self.write("test_blank.py", "# named but no discovered cases\n")
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_failure_keeps_private_tracebacks_out_of_output(self):
        self.write("test_fail.py", "import unittest\nclass T(unittest.TestCase):\n def test_bad(self): self.fail('sensitive file path C:/Acme/finance')\n")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(b"Acme", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
