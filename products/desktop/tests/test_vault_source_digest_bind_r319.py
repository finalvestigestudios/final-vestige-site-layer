"""R319 regression: AES gate must execute only exact source bytes witnessed earlier."""
from __future__ import annotations

import contextlib
import hashlib
import io
import inspect
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.source_only_test_loader_r318 import load_source_suite


class SourceDigestBindingR319Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r319-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source_path = self.folder / "test_synthetic_digest.py"
        self.addCleanup(sys.modules.pop, self.source_path.stem, None)

    def source(self, failure=False, marker=False):
        action = "self.fail('PRIVATE_ACCT_321')" if failure else "pass"
        extra = "\nprint('PRIVATE_INVOICE_432')" if marker else ""
        return ("import unittest\nclass ExactCases(unittest.TestCase):\n"
                f" def test_a(self): {action}\n def test_b(self): pass\n" + extra).encode()

    def write(self, *, failure=False):
        data = self.source(failure=failure)
        self.source_path.write_bytes(data)
        return hashlib.sha256(data).digest()

    def run_bound(self, digest):
        suite, module, errors = load_source_suite(self.source_path, expected_sha256=digest)
        self.assertEqual(errors, [])
        self.assertEqual(module.__file__, str(self.source_path))
        result = unittest.TestResult()
        suite.run(result)
        return result

    def test_correct_digest_passes(self):
        self.assertTrue(self.run_bound(self.write()).wasSuccessful())

    def test_current_failure_is_not_hidden(self):
        self.assertFalse(self.run_bound(self.write(failure=True)).wasSuccessful())

    def test_changed_same_size_source_is_rejected_before_compilation(self):
        digest = self.write(failure=True)
        previous = self.source(failure=True)
        modified = self.source(failure=False)
        modified += b" " * (len(previous) - len(modified))
        self.assertEqual(len(previous), len(modified))
        self.source_path.write_bytes(modified)
        with self.assertRaisesRegex(ValueError, "source digest"):
            self.run_bound(digest)
        self.assertNotIn(self.source_path.stem, sys.modules)

    def test_changed_source_is_rejected_even_if_presently_passing(self):
        digest = self.write()
        self.source_path.write_bytes(self.source(failure=True))
        with self.assertRaisesRegex(ValueError, "source digest"):
            self.run_bound(digest)

    def test_digest_uses_bytes_not_unicode_normalization(self):
        original = b"# coding: utf-8\n# caf\xc3\xa9\n" + self.source()
        self.source_path.write_bytes(original)
        digest = hashlib.sha256(original).digest()
        self.assertTrue(self.run_bound(digest).wasSuccessful())
        self.source_path.write_bytes(original.replace(b"caf\xc3\xa9", b"cafe\xcc\x81"))
        with self.assertRaisesRegex(ValueError, "source digest"):
            self.run_bound(digest)

    def test_invalid_digest_types_fail_before_execution(self):
        self.write()
        for digest in ("not bytes", bytearray(32), memoryview(bytes(32)), bytes(31), bytes(33)):
            with self.subTest(kind=type(digest).__name__), self.assertRaises(ValueError):
                self.run_bound(digest)
        self.assertNotIn(self.source_path.stem, sys.modules)

    def test_expected_hash_is_required_by_gate_callsite(self):
        # This uses the full source-controlled gate (not a substitute), and
        # ensures the privileged path passes its preflight SHA-256 into loader.
        from scripts.vault_crypto_gate_r316 import execute_gate
        digest = self.write()
        output = execute_gate(self.folder, targets=((self.source_path.name,
                              ("ExactCases.test_a", "ExactCases.test_b")),))
        self.assertEqual((output["modules"], output["required_cases_executed"]), (1, 2))

    def test_transient_swap_during_loader_read_fails_gate(self):
        # Model attacker-controlled bytes seen *only* by the source loader.
        # Before/after witnesses see unchanged disk bytes and identities.
        from scripts.vault_crypto_gate_r316 import IntegrationHold, execute_gate
        self.write(failure=True)
        replacement = self.source(failure=False)
        real_read = Path.read_bytes
        path = self.source_path
        def read_during_swap(current):
            if current == path and any(f.function == 'load_source_suite' for f in inspect.stack()[1:]):
                return replacement
            return real_read(current)
        out, err = io.StringIO(), io.StringIO()
        with patch.object(Path, "read_bytes", read_during_swap), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(IntegrationHold) as caught:
                execute_gate(self.folder, targets=((path.name,
                              ("ExactCases.test_a", "ExactCases.test_b")),))
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn("PRIVATE_ACCT", str(caught.exception))
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_transient_loader_bytes_cannot_execute_unwitnessed_import_side_effect(self):
        # The injected code is never on disk; a pre/post lstat SHA witness
        # alone would still see a clean source and allow this import side effect.
        from scripts.vault_crypto_gate_r316 import IntegrationHold, execute_gate
        self.write()
        marker = self.folder / "unverified_side_effect"
        injected = (f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n"
                    + self.source().decode()).encode()
        real_read = Path.read_bytes
        def injected_read(path):
            if path == self.source_path and any(
                    f.function == "load_source_suite" for f in inspect.stack()[1:]):
                return injected
            return real_read(path)
        with patch.object(Path, "read_bytes", injected_read):
            with self.assertRaises(IntegrationHold):
                execute_gate(self.folder, targets=((self.source_path.name,
                              ("ExactCases.test_a", "ExactCases.test_b")),))
        self.assertFalse(marker.exists())

    def test_wrong_module_type_not_accepted(self):
        self.write()
        with self.assertRaises(ValueError):
            load_source_suite(str(self.source_path), expected_sha256=bytes(32))


if __name__ == "__main__":
    unittest.main()
