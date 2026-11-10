"""R318 synthetic tests: stale import bytecode must never certify AES coverage.

Full-checkout AES/Windows evidence remains a separate mandatory QD gate.
"""
from __future__ import annotations

import os
from pathlib import Path
import py_compile
import sys
import tempfile
import unittest
from scripts.source_only_test_loader_r318 import load_source_suite


class SourceOnlyLoaderR318Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r318-")
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.path = self.folder / "test_r318_synthetic.py"
        self.addCleanup(sys.modules.pop, self.path.stem, None)

    def source(self, fails=False):
        body = "self.fail('PRIVATE BANK DATA')" if fails else "pass"
        return ("import unittest\nclass Synthetic(unittest.TestCase):\n"
                f" def test_a(self): {body}\n def test_b(self): pass\n")

    def stale_pair(self, old_fails=False, new_fails=True):
        old, new = self.source(old_fails), self.source(new_fails)
        length = max(len(old), len(new)) + 2
        def padded(s):
            return s + "#" + " " * (length - len(s) - 2) + "\n"
        self.path.write_text(padded(old), encoding="utf-8")
        py_compile.compile(str(self.path), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        before = self.path.stat()
        self.path.write_text(padded(new), encoding="utf-8")
        self.assertEqual(self.path.stat().st_size, before.st_size)
        os.utime(self.path, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertTrue(any(self.folder.glob("__pycache__/*.pyc")))

    def load_and_run(self):
        suite, module, errors = load_source_suite(self.path)
        self.assertEqual(errors, [])
        self.assertEqual(module.__file__, str(self.path))
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 2)
        return result

    def test_current_source_passes_without_cache(self):
        self.path.write_text(self.source(), encoding="utf-8")
        self.assertTrue(self.load_and_run().wasSuccessful())

    def test_stale_passing_pyc_cannot_hide_failing_source(self):
        self.stale_pair()
        # Demonstrate false positive in the predecessor's discover() loader.
        legacy = unittest.TestLoader().discover(str(self.folder), pattern=self.path.name,
                                                 top_level_dir=str(self.folder))
        legacy_result = unittest.TestResult()
        legacy.run(legacy_result)
        self.assertTrue(legacy_result.wasSuccessful())
        self.assertFalse(self.load_and_run().wasSuccessful())

    def test_stale_failing_pyc_cannot_hide_passing_source(self):
        self.stale_pair(old_fails=True, new_fails=False)
        self.assertTrue(self.load_and_run().wasSuccessful())

    def test_preloaded_module_cache_is_replaced(self):
        self.path.write_text(self.source(), encoding="utf-8")
        self.assertTrue(self.load_and_run().wasSuccessful())
        self.path.write_text(self.source(fails=True), encoding="utf-8")
        self.assertFalse(self.load_and_run().wasSuccessful())

    def test_source_encoding_cookie_supported(self):
        self.path.write_bytes(b"# coding: latin-1\nimport unittest\n# caf\xe9\n"
                              b"class Synthetic(unittest.TestCase):\n"
                              b" def test_a(self): pass\n def test_b(self): pass\n")
        self.assertTrue(self.load_and_run().wasSuccessful())

    def test_import_error_evicts_module(self):
        self.path.write_text("raise RuntimeError('PRIVATE_ACCOUNT_PATH')\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            load_source_suite(self.path)
        self.assertNotIn(self.path.stem, sys.modules)

    def test_wrong_path_type_rejected(self):
        with self.assertRaises(ValueError):
            load_source_suite(str(self.path))

    def test_full_gate_refuses_failing_source_with_stale_passing_pyc(self):
        # Requires the actual R316/R317 gate (present in the complete repo).
        from scripts.vault_crypto_gate_r316 import IntegrationHold, execute_gate
        self.stale_pair()
        with self.assertRaises(IntegrationHold):
            execute_gate(self.folder, targets=((self.path.name,
                         ("Synthetic.test_a", "Synthetic.test_b")),))


if __name__ == "__main__":
    unittest.main()
