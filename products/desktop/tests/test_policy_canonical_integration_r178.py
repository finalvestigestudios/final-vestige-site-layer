"""R178 Policy Delta end-to-end synthetic file/sha/report checks (CI suite)."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicyCanonicalIntegrationR178(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-policy-r178-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"
        self.report = self.root / "report.txt"

    def compare(self, old, new):
        old_bytes, new_bytes = old.encode("utf-8"), new.encode("utf-8")
        self.before.write_bytes(old_bytes)
        self.after.write_bytes(new_bytes)
        result = policy_diff.compare_policy_files(
            self.before, self.after, self.root, lambda *_: self.report)
        self.assertEqual(result, [self.report])
        body = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(old_bytes).hexdigest(), body)
        self.assertIn(hashlib.sha256(new_bytes).hexdigest(), body)
        self.assertEqual(self.before.read_bytes(), old_bytes)
        self.assertEqual(self.after.read_bytes(), new_bytes)
        return body

    def test_mixed_canonical_and_substantive_change_one_hunk(self):
        report = self.compare("Café\nOwner Old\n", "Cafe\u0301\nOwner New\n")
        self.assertIn("Canonical hunk 001: before L1; after L1; NFC-only candidate", report)
        self.assertNotIn("NFC-normalization-equivalent;", report)
        self.assertIn("-Owner Old\n+Owner New", report)

    def test_mixed_edit_separated_hunks(self):
        old = "Café\n" + ("same\n" * 9) + "Owner Old\n"
        new = "Cafe\u0301\n" + ("same\n" * 9) + "Owner New\n"
        report = self.compare(old, new)
        self.assertIn("Canonical hunk 001: before L1; after L1", report)
        self.assertIn("Hunk 002:", report)

    def test_ambiguous_duplicate_lines_not_paired(self):
        report = self.compare("Café\nCafé\n", "Cafe\u0301\nCafe\u0301\n")
        self.assertNotIn("Canonical hunk", report)

    def test_nfkc_only_not_falsely_called_canonical(self):
        report = self.compare("Limit ⑩\n", "Limit 10\n")
        self.assertNotIn("Canonical hunk", report)
        self.assertIn("LOCAL REVIEW: NFKC-only", report)

    def test_crlf_only_not_false_canonical(self):
        report = self.compare("Café\r\n", "Café\n")
        self.assertNotIn("Canonical hunk", report)
        self.assertIn("-Café\\r", report)

    def test_replay_deterministic_and_no_overwrite(self):
        first = self.compare("Café\nOwner Old\n", "Cafe\u0301\nOwner New\n")
        with self.assertRaises(FileExistsError):
            self.compare("Café\nOwner Old\n", "Cafe\u0301\nOwner New\n")
        self.assertEqual(first, self.report.read_text(encoding="utf-8"))
        self.report.unlink()
        second = self.compare("Café\nOwner Old\n", "Cafe\u0301\nOwner New\n")
        self.assertEqual(first, second)

    def test_reject_unsafe_text_without_report(self):
        self.before.write_text("good\n", encoding="utf-8")
        self.after.write_text("hidden\u202e\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
