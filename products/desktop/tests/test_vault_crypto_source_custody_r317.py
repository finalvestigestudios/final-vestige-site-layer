"""R317 regression coverage for genuine AES integration source-module custody.

Synthetic Python files only. Actual cryptography/source suites and Windows EXEs
require the private complete checkout and independent QD/founder approval.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from scripts.vault_crypto_gate_r316 import IntegrationHold, execute_gate


class VaultCryptoSourceCustodyR317Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="r317-synthetic-")
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.module = "test_r317_synthetic"
        self.filename = self.module + ".py"
        self.path = self.directory / self.filename
        self.addCleanup(sys.modules.pop, self.module, None)

    def write(self, body):
        self.path.write_text(body, encoding="utf-8")

    def check(self, targets=None):
        return execute_gate(self.directory, targets=targets or
                            ((self.filename, ("Synthetic.test_a", "Synthetic.test_b")),))

    def test_unmodified_disk_source_passes_twice_with_cached_module(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n"
                   " def test_a(self): self.assertTrue(True)\n"
                   " def test_b(self): self.assertEqual(2, 2)\n")
        self.assertEqual(self.check()["required_cases_executed"], 2)
        self.assertEqual(self.check()["required_cases_executed"], 2)

    def test_preloaded_same_path_forgery_cannot_substitute_passing_tests(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n"
                   " def test_a(self): self.fail('PRIVATE BANK TRANSACTION')\n"
                   " def test_b(self): pass\n")
        forgery = types.ModuleType(self.module)
        forgery.__file__ = str(self.path)
        class Synthetic(unittest.TestCase):
            def test_a(self): pass
            def test_b(self): pass
        Synthetic.__module__ = self.module
        forgery.Synthetic = Synthetic
        sys.modules[self.module] = forgery
        with self.assertRaises(IntegrationHold) as caught:
            self.check()
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn("BANK", str(caught.exception))

    def test_execution_cannot_rewrite_its_own_test_module(self):
        self.write("import unittest\nfrom pathlib import Path\n"
                   "class Synthetic(unittest.TestCase):\n"
                   " def test_a(self):\n"
                   "  p=Path(__file__)\n"
                   "  p.write_text(p.read_text().replace('test_b', 'test_c'))\n"
                   " def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold):
            self.check()
        self.assertIn("test_c", self.path.read_text())

    def test_byte_identical_atomic_replacement_is_rejected(self):
        self.write("import unittest\nfrom pathlib import Path\nimport os\n"
                   "class Synthetic(unittest.TestCase):\n"
                   " def test_a(self):\n"
                   "  p=Path(__file__)\n"
                   "  temp=p.with_suffix('.replacement')\n"
                   "  temp.write_bytes(p.read_bytes())\n"
                   "  os.replace(temp,p)\n"
                   " def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold):
            self.check()

    def test_other_vetted_module_changed_before_its_turn_holds(self):
        second = self.directory / "test_r317_second.py"
        self.write("import unittest\nfrom pathlib import Path\n"
                   "class Synthetic(unittest.TestCase):\n"
                   " def test_a(self):\n"
                   f"  p=Path({str(second)!r})\n"
                   "  p.write_text(p.read_text().replace('# stable', '# altered'))\n"
                   " def test_b(self): pass\n")
        second.write_text("import unittest\nclass Second(unittest.TestCase):\n def test_c(self): pass\n# stable\n")
        with self.assertRaises(IntegrationHold):
            self.check(targets=((self.filename, ("Synthetic.test_a", "Synthetic.test_b")),
                                (second.name, ("Second.test_c",))))

    def test_hold_redacts_private_output_and_exceptions(self):
        self.write("import unittest,sys\nclass Synthetic(unittest.TestCase):\n"
                   " def test_a(self):\n"
                   "  print('PRIVATE BUDGET',file=sys.stderr)\n"
                   "  raise RuntimeError('PRIVATE CLIENT FILENAME')\n"
                   " def test_b(self): pass\n")
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            with self.assertRaises(IntegrationHold) as caught:
                self.check()
        self.assertEqual((output.getvalue(), error.getvalue()), ("", ""))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_symlinked_module_holds_even_if_target_valid(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n"
                   " def test_a(self): pass\n def test_b(self): pass\n")
        real_lstat = Path.lstat
        def link_lstat(path, *args, **kwargs):
            v = real_lstat(path, *args, **kwargs)
            if path.name != self.filename:
                return v
            return unittest.mock.Mock(st_mode=0o120777, st_size=v.st_size)
        with patch.object(Path, "lstat", link_lstat):
            with self.assertRaises(IntegrationHold):
                self.check()


if __name__ == "__main__":
    unittest.main()
