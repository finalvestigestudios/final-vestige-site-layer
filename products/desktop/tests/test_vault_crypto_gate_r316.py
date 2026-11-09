"""R316 adversarial synthetic contracts plus actual full-checkout AES-GCM gate.

The exact real-integration method must execute in the complete checkout;
runnerless synthetic-only validation is explicitly not complete acceptance.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.vault_crypto_gate_r316 import IntegrationHold, REQUIRED, execute_gate


class VaultCryptoGateR316Tests(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("test_synthetic_crypto", None)
        temp = tempfile.TemporaryDirectory(prefix="fvs-r316-")
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.name = "test_synthetic_crypto.py"
        self.methods = ("Synthetic.test_a", "Synthetic.test_b")

    def write(self, body):
        (self.directory / self.name).write_text(body, encoding="utf-8")

    def check(self):
        return execute_gate(self.directory, targets=((self.name, self.methods),))

    def test_synthetic_unskipped_cases_pass(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n def test_a(self): pass\n def test_b(self): pass\n")
        result = self.check()
        self.assertEqual((result["modules"], result["required_cases_executed"], result["skipped"]), (1, 2, 0))
        self.assertIs(result["released"], False)
        self.assertIs(result["qd_approved"], False)
        self.assertIs(result["premium_download_authorized"], False)

    def test_synthetic_skip_is_hold_even_when_count_matches(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n @unittest.skip('PRIVATE FINANCE ROW')\n def test_a(self): pass\n def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold) as caught:
            self.check()
        self.assertNotIn("PRIVATE FINANCE ROW", str(caught.exception))

    def test_synthetic_missing_required_case_is_hold(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n def test_a(self): pass\n")
        with self.assertRaises(IntegrationHold):
            self.check()

    def test_synthetic_failed_assertion_redacted(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n def test_a(self): self.fail('PRIVATE ACCOUNT NUMBER 123')\n def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold) as caught:
            self.check()
        self.assertNotIn("PRIVATE ACCOUNT", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_synthetic_import_exception_redacted(self):
        self.write("raise RuntimeError('CUSTOMER_PRIVATE_PATH')\n")
        with self.assertRaises(IntegrationHold) as caught:
            self.check()
        self.assertNotIn("CUSTOMER", str(caught.exception))

    def test_synthetic_import_stdout_and_stderr_suppressed(self):
        self.write("import unittest,sys\nprint('PRIVATE CSV ROW')\nprint('PRIVATE JOURNAL',file=sys.stderr)\nclass Synthetic(unittest.TestCase):\n def test_a(self): pass\n def test_b(self): pass\n")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.check()
        self.assertEqual((stdout.getvalue(), stderr.getvalue()), ("", ""))

    def test_synthetic_symlinked_source_refused(self):
        elsewhere = self.directory / "elsewhere.txt"
        elsewhere.write_text("import unittest\n", encoding="utf-8")
        (self.directory / self.name).symlink_to(elsewhere)
        with self.assertRaises(IntegrationHold):
            self.check()

    def test_synthetic_missing_second_module_blocks_before_first_runs(self):
        marker = self.directory / "marker"
        self.write("import unittest\nfrom pathlib import Path\nclass Synthetic(unittest.TestCase):\n def test_a(self): Path(" + repr(str(marker)) + ").write_text('ran')\n def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold):
            execute_gate(self.directory, targets=((self.name, self.methods), ("test_absent.py", self.methods)))
        self.assertFalse(marker.exists())

    def test_synthetic_tampered_inventory_holds(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n def test_a(self): pass\n def test_b(self): pass\n")
        for bad in (((self.name, self.methods), (self.name, self.methods)),
                    (("../escape.py", self.methods),),
                    ((self.name, ("Synthetic.test_a", "Synthetic.test_a")),)):
            with self.subTest(targets=bad), self.assertRaises(IntegrationHold):
                execute_gate(self.directory, targets=bad)

    def test_synthetic_system_exit_does_not_disclose(self):
        self.write("import unittest\nclass Synthetic(unittest.TestCase):\n def test_a(self): raise SystemExit('PRIVATE PAYROLL')\n def test_b(self): pass\n")
        with self.assertRaises(IntegrationHold) as caught:
            self.check()
        self.assertEqual(str(caught.exception), "Premium AES-GCM integration gate HOLD: required source tests did not execute cleanly")

    def test_real_aes_gcm_integration_suite_required_in_complete_checkout(self):
        # This is NOT skipped in CI; real cryptography + full desktop source
        # must be available. Otherwise the complete source gate fails closed.
        tests = Path(__file__).resolve().parent
        outcome = execute_gate(tests)
        self.assertEqual(outcome["modules"], len(REQUIRED))
        self.assertEqual(outcome["required_cases_executed"], 22)
        self.assertEqual(outcome["skipped"], 0)


if __name__ == "__main__":
    unittest.main()
