"""Synthetic privacy/security regressions for R101 Windows inventory forensics."""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from scripts import diagnose_windows_inventory_r101 as diagnostic


class InventoryForensicsR101(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "synthetic.py"
        self.path.write_text("assert True\n", encoding="ascii")

    def test_original_fingerprint_authorizes_only_pass(self):
        self.assertEqual(diagnostic._classify(
            self.path, self.root, fingerprint=lambda *_: "synthetic-digest"), "PASS")

    def test_original_failure_cannot_be_reclassified_as_pass(self):
        def reject(*_):
            raise ValueError("PRIVATE_ACCOUNT_AND_INVOICE")
        # Windows may expose a real path-vs-handle metadata mismatch for a
        # freshly created synthetic file. Such a mismatch is a REFUSAL, never
        # a successful override of the rejected original fingerprint.
        label = diagnostic._classify(self.path, self.root, fingerprint=reject)
        self.assertNotEqual(label, "PASS")
        self.assertIn(label, diagnostic.PERMITTED)

    def test_missing_source_is_lstat_failure(self):
        with self.assertRaises(ValueError):
            diagnostic.gate._fingerprint(self.root / "absent.py", self.root)
        self.assertEqual(diagnostic._classify(
            self.root / "absent.py", self.root,
            fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE"))), "LSTAT")

    def test_symbolic_link_fails_without_following_target(self):
        link = self.root / "linked.py"
        try:
            link.symlink_to(self.path)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this runner")
        self.assertEqual(diagnostic._classify(
            link, self.root, fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE"))),
            "REGULAR")

    def test_hard_link_is_flagged(self):
        alias = self.root / "alias.py"
        try:
            os.link(self.path, alias)
        except OSError:
            self.skipTest("Hardlinks unavailable")
        self.assertEqual(diagnostic._classify(
            self.path, self.root, fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE"))),
            "LINKS")

    def test_source_size_boundary_detected(self):
        with patch.object(diagnostic.gate, "MAX_SOURCE_BYTES", 1):
            self.assertEqual(diagnostic._classify(
                self.path, self.root, fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE"))),
                "SIZE")

    def test_outside_root_rejected(self):
        narrower = self.root / "nested"
        narrower.mkdir()
        self.assertEqual(diagnostic._classify(
            self.path, narrower, fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE"))),
            "CONFINEMENT")

    def test_identity_difference_bounded_mask_not_values(self):
        def info(ino=2):
            return types.SimpleNamespace(st_dev=1, st_ino=ino, st_mode=33188,
                st_nlink=1, st_size=13, st_mtime_ns=4, st_ctime_ns=5)
        self.assertEqual(diagnostic._difference(info(), info()), 0)
        self.assertEqual(diagnostic._difference(info(), info(99)), 2)

    def test_probe_outputs_only_counts_not_source_paths_or_private_exceptions(self):
        stdout = io.StringIO()
        def fake_classify(path, root):
            print("PRIVATE_ACCOUNT")
            if path.name == "synthetic.py":
                raise RuntimeError("PRIVATE_INVOICE_PATH")
            return "PASS"
        with patch.object(diagnostic, "_candidate_files",
                          return_value=[self.path, self.root / "another.py"]), \
             contextlib.redirect_stdout(stdout):
            result = diagnostic.probe(self.root, "tests", classify=fake_classify)
        self.assertEqual(result, {"FILES": 2, "UNKNOWN": 1, "PASS": 1})
        rendered = diagnostic.render("tests", result)
        self.assertEqual(rendered, "FVS_R101_TESTS:FILES=2,PASS=1,UNKNOWN=1")
        self.assertNotIn("PRIVATE", stdout.getvalue()+rendered)
        self.assertNotIn("synthetic.py", rendered)

    def test_untrusted_return_label_reclassified_as_unknown(self):
        with patch.object(diagnostic, "_candidate_files", return_value=[self.path]):
            got = diagnostic.probe(self.root, "sources",
                     classify=lambda *_: "SECRET_CUSTOMER")
        self.assertEqual(got, {"FILES":1, "UNKNOWN":1})

    def test_directory_scan_failure_does_not_echo_exception(self):
        with patch.object(diagnostic, "_candidate_files",
                          side_effect=ValueError("PRIVATE_FILEPATH")):
            out = diagnostic.render("sources", diagnostic.probe(self.root, "sources"))
        self.assertEqual(out, "FVS_R101_SOURCES:SOURCES_SCAN=1")
        self.assertNotIn("PRIVATE", out)

    def test_reject_user_selected_scope(self):
        with self.assertRaises(ValueError):
            diagnostic.probe(self.root, "billing")
        with self.assertRaises(ValueError):
            diagnostic.render("billing", {"PASS":1})

    def test_reject_invalid_private_safe_receipt(self):
        for payload in ({"SECRET":1}, {"PASS": "PRIVATE"}, {"PASS": -1},
                        {"PASS": 999999}, {"PASS": True}):
            with self.subTest(payload=repr(payload)):
                with self.assertRaises(ValueError):
                    diagnostic.render("tests", payload)

    def test_real_fingerprint_remains_unchanged_and_positive(self):
        self.assertEqual(diagnostic._classify(self.path, self.root), "PASS")

    def test_start_descriptor_identity_mask_is_bounded_and_non_sensitive(self):
        before = self.path.lstat()
        fake = types.SimpleNamespace(st_dev=before.st_dev, st_ino=before.st_ino + 1,
            st_mode=before.st_mode, st_nlink=before.st_nlink, st_size=before.st_size,
            st_mtime_ns=before.st_mtime_ns, st_ctime_ns=before.st_ctime_ns)
        with patch.object(diagnostic.os, "fstat", return_value=fake):
            label = diagnostic._classify(
                self.path, self.root,
                fingerprint=lambda *_: (_ for _ in ()).throw(ValueError("PRIVATE_INVOICE")))
        self.assertEqual(label, "START_MASK_2")
        self.assertIn("START_MASK_2", diagnostic.render("tests", {label: 1}))
        self.assertNotIn(str(before.st_ino + 1), label)

    def test_output_contains_no_private_values(self):
        with patch.object(diagnostic, "probe", side_effect=ValueError("PRIVATE_CSV_ROW")):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(diagnostic.main(), 0)
            output = stream.getvalue()
            self.assertIn("FVS_R101_RELEASE=HOLD_SOURCE_DIAGNOSTIC_ONLY", output)
            self.assertNotIn("PRIVATE", output)


def _sanitized_focus_main():
    """Only source-owned static method labels escape synthetic CI regressions."""
    with open(os.devnull, "w", encoding="utf-8") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(InventoryForensicsR101)
            result = unittest.TextTestRunner(stream=sink, verbosity=0).run(suite)
    if result.wasSuccessful():
        print("FVS_R101_SYNTHETIC:PASS")
        return 0
    # Never show tracebacks or private test data. Only immediate methods from
    # the named source-defined class may leave this trusted synthetic runner.
    safe = {n for n in vars(InventoryForensicsR101)
            if n.startswith("test_") and n.isascii() and n.replace("_", "").isalnum()}
    failures = sorted({getattr(test, "_testMethodName", "") for test, _ in
                       result.failures + result.errors})
    for name in failures:
        if name in safe:
            print("FVS_R101_SYNTHETIC_FAIL:" + name)
    print("FVS_R101_SYNTHETIC:BLOCKED")
    return 1


if __name__ == "__main__":
    raise SystemExit(_sanitized_focus_main())
