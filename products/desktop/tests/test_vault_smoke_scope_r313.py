"""R313 local, synthetic contract tests for packaged premium vault smoke."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fvs_suite.vault_smoke_scope import check_scoped_vault_roundtrip

DENIED = "Encrypted evidence does not match this premium review product"


class ScopedSmokeContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "test.fvault"
        self.archive.write_bytes(b"synthetic encrypted fixture")
        self.report = self.root / "test.csv"
        self.report.write_bytes(b"id,amount\nX,12.34\n")
        self.journal = self.root / "test.jsonl"
        self.journal.write_bytes(b'{"decision":"needs_evidence"}\n')
        self.passphrase = "synthetic-only-secret"
        self.calls = []
        self.restore_override = None

    def restore(self, archive, root, passphrase, *, expected_product):
        self.calls.append((archive, root, passphrase, expected_product))
        if self.restore_override is not None:
            return self.restore_override(archive, root, passphrase, expected_product)
        if expected_product != self.product:
            raise ValueError(DENIED)
        target = root / "fvs-evidence-restored-test"
        target.mkdir()
        (target / "exception-report.csv").write_bytes(self.report.read_bytes())
        (target / "exception-report.review.jsonl").write_bytes(self.journal.read_bytes())
        return target

    def run_scope(self, product="grants"):
        self.product = product
        return check_scoped_vault_roundtrip(self.archive, self.root,
            self.passphrase, product, self.report, self.journal, self.restore)

    def test_grant_roundtrip_and_deny_procurement(self):
        restored = self.run_scope("grants")
        self.assertTrue(restored.is_dir())
        self.assertEqual([c[-1] for c in self.calls], ["grants", "procurement"])

    def test_procurement_roundtrip_and_deny_grants(self):
        self.run_scope("procurement")
        self.assertEqual([c[-1] for c in self.calls], ["procurement", "grants"])

    def test_password_and_archive_same_for_both_calls(self):
        self.run_scope()
        self.assertEqual([c[:3] for c in self.calls], [self.calls[0][:3]] * 2)

    def test_invalid_product_rejected_without_restore(self):
        with self.assertRaisesRegex(RuntimeError, "invalid smoke product"):
            self.run_scope("ledger")
        self.assertEqual(self.calls, [])

    def test_non_native_string_rejected(self):
        class PretendString(str):
            pass
        with self.assertRaisesRegex(RuntimeError, "invalid smoke product"):
            self.run_scope(PretendString("grants"))
        self.assertEqual(self.calls, [])

    def test_denied_cross_product_success_fails(self):
        self.product = "grants"
        def bypass(archive, root, passphrase, expected_product):
            target = root / ("fvs-evidence-restored-" + expected_product)
            target.mkdir()
            (target / "exception-report.csv").write_bytes(self.report.read_bytes())
            (target / "exception-report.review.jsonl").write_bytes(self.journal.read_bytes())
            return target
        self.restore_override = bypass
        with self.assertRaisesRegex(RuntimeError, "cross-product restore accepted"):
            self.run_scope()

    def test_wrong_reason_cannot_masquerade_as_denial(self):
        def other(archive, root, passphrase, expected_product):
            if expected_product != "grants":
                raise ValueError("Wrong passphrase")
            return self.valid_target(root)
        self.restore_override = other
        with self.assertRaisesRegex(RuntimeError, "wrong-product denial reason"):
            self.run_scope()

    def valid_target(self, root):
        target = root / "fvs-evidence-restored-test"
        target.mkdir()
        (target / "exception-report.csv").write_bytes(self.report.read_bytes())
        (target / "exception-report.review.jsonl").write_bytes(self.journal.read_bytes())
        return target

    def test_report_tampering_detected(self):
        def tamper(archive, root, passphrase, expected_product):
            target = self.valid_target(root)
            (target / "exception-report.csv").write_bytes(b"changed")
            return target
        self.restore_override = tamper
        with self.assertRaisesRegex(RuntimeError, "scoped report bytes changed"):
            self.run_scope()

    def test_journal_tampering_detected(self):
        def tamper(archive, root, passphrase, expected_product):
            target = self.valid_target(root)
            (target / "exception-report.review.jsonl").write_bytes(b"changed")
            return target
        self.restore_override = tamper
        with self.assertRaisesRegex(RuntimeError, "scoped journal bytes changed"):
            self.run_scope()

    def test_archive_tampering_detected(self):
        def tamper(archive, root, passphrase, expected_product):
            target = self.valid_target(root)
            archive.write_bytes(b"changed")
            return target
        self.restore_override = tamper
        with self.assertRaisesRegex(RuntimeError, "scoped restore changed encrypted archive"):
            self.run_scope()

    def test_wrong_scope_new_file_detected(self):
        def leak(archive, root, passphrase, expected_product):
            if expected_product != "grants":
                (root / "decrypted-leak.txt").write_bytes(b"bad")
                raise ValueError(DENIED)
            return self.valid_target(root)
        self.restore_override = leak
        with self.assertRaisesRegex(RuntimeError, "cross-product restore left plaintext"):
            self.run_scope()

    def test_wrong_scope_archive_mutation_detected(self):
        def tamper(archive, root, passphrase, expected_product):
            if expected_product != "grants":
                archive.write_bytes(b"changed")
                raise ValueError(DENIED)
            return self.valid_target(root)
        self.restore_override = tamper
        with self.assertRaisesRegex(RuntimeError, "cross-product restore changed encrypted archive"):
            self.run_scope()

    def test_wrong_scope_exception_is_not_swallowed(self):
        def io_error(archive, root, passphrase, expected_product):
            if expected_product != "grants":
                raise OSError("private data")
            return self.valid_target(root)
        self.restore_override = io_error
        with self.assertRaises(OSError):
            self.run_scope()

    def test_scoped_restore_must_create_new_folder(self):
        self.restore_override = lambda archive, root, passphrase, expected_product: root
        with self.assertRaisesRegex(RuntimeError, "scoped restore destination"):
            self.run_scope()

    def test_scoped_restore_must_not_add_stray_file(self):
        def extra(archive, root, passphrase, expected_product):
            target = self.valid_target(root)
            (root / "stray.txt").write_bytes(b"unsafe")
            return target
        self.restore_override = extra
        with self.assertRaisesRegex(RuntimeError, "scoped restore created unexpected contents"):
            self.run_scope()

    def test_root_symlink_rejected(self):
        symlink = self.root / "alias"
        try:
            symlink.symlink_to(self.root, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("platform does not permit symlinks")
        with self.assertRaisesRegex(RuntimeError, "invalid synthetic root"):
            check_scoped_vault_roundtrip(self.archive, symlink,
                self.passphrase, "grants", self.report, self.journal, self.restore)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
