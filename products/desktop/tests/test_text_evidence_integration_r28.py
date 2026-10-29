"""R28 engine integrations: policy report + grant hash manifest are complete.

All financial and policy test data is synthetic. The full repository suite and
native Windows candidate still require trusted-runner verification.
"""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class TextEvidenceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = self.root / "old.txt"
        self.after = self.root / "new.txt"
        self.before.write_bytes(b"Rule A\n")
        self.after.write_bytes(b"Rule B\n")

    def assert_clean(self):
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_policy_engine_retains_fingerprints_and_change_markers(self):
        output, = engine.policy_delta(self.before, self.after, self.root)
        body = output.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(b"Rule A\n").hexdigest(), body)
        self.assertIn(hashlib.sha256(b"Rule B\n").hexdigest(), body)
        self.assertIn("-Rule A", body)
        self.assertIn("+Rule B", body)
        self.assertIn("Not legal advice", body)
        self.assert_clean()

    def test_policy_output_collision_never_overwrites(self):
        target = self.root / "policy-fixed.txt"
        target.write_bytes(b"previous official evidence")
        with patch("fvs_suite.engine.outpath", return_value=target):
            with self.assertRaises(FileExistsError):
                engine.policy_delta(self.before, self.after, self.root)
        self.assertEqual(target.read_bytes(), b"previous official evidence")
        self.assert_clean()

    def test_policy_publish_failure_removes_staging(self):
        operation = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + operation,
                   side_effect=OSError("no exclusive publish")):
            with self.assertRaises(OSError):
                engine.policy_delta(self.before, self.after, self.root)
        self.assertEqual(list(self.root.glob("policy-delta-*.txt")), [])
        self.assert_clean()

    def test_manifest_hashes_exact_input_and_report_bytes(self):
        report = self.root / "grant-audit-exceptions.csv"
        report.write_bytes(b"claim,amount\nA,0.01\n")
        output = engine.manifest(self.root, [self.before, self.after], [report])
        lines = output.read_text(encoding="utf-8").splitlines()
        self.assertIn("SHA-256", lines[0])
        self.assertEqual(len(lines), 4)
        expected = [(p.name, hashlib.sha256(p.read_bytes()).hexdigest())
                    for p in [self.before, self.after, report]]
        self.assertEqual([tuple(line.split("\t")) for line in lines[1:]], expected)
        self.assert_clean()

    def test_manifest_output_collision_never_overwrites(self):
        target = self.root / "existing.txt"
        target.write_bytes(b"trusted original")
        with patch("fvs_suite.engine.outpath", return_value=target):
            with self.assertRaises(FileExistsError):
                engine.manifest(self.root, [self.before], [self.after])
        self.assertEqual(target.read_bytes(), b"trusted original")
        self.assert_clean()

    def test_manifest_unreadable_source_cannot_publish_partial(self):
        missing = self.root / "missing.csv"
        with self.assertRaises(FileNotFoundError):
            engine.manifest(self.root, [self.before, missing], [self.after])
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])
        self.assert_clean()

    def test_manifest_fsync_failure_prevents_visible_manifest(self):
        with patch("fvs_suite.atomic_text.os.fsync", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                engine.manifest(self.root, [self.before], [self.after])
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])
        self.assert_clean()

    @unittest.skipIf(os.name == "nt", "Windows disallows control characters in filenames")
    def test_manifest_escapes_injected_filename_controls_and_bidi(self):
        injected = self.root / "claim\tforged\nline\u202e.csv"
        injected.write_bytes(b"synthetic")
        output = engine.manifest(self.root, [injected], [])
        lines = output.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn(r"claim\tforged\nline\u202e.csv", lines[1])
        self.assertNotIn("\u202e", lines[1])
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
