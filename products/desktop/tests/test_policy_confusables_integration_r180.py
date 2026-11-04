"""R180 Policy Delta real-file integration: synthetic content, never user files."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicyConfusableIntegrationR180(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-policy-r180-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"
        self.report = self.root / "report.txt"

    def compare(self, before, after):
        old, new = before.encode("utf-8"), after.encode("utf-8")
        self.before.write_bytes(old)
        self.after.write_bytes(new)
        self.assertEqual(policy_diff.compare_policy_files(
            self.before, self.after, self.root, lambda *_: self.report), [self.report])
        body = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(old).hexdigest(), body)
        self.assertIn(hashlib.sha256(new).hexdigest(), body)
        self.assertEqual(self.before.read_bytes(), old)
        self.assertEqual(self.after.read_bytes(), new)
        return body

    def test_before_after_source_coordinates_and_codepoints(self):
        body = self.compare("PAYMENT\n", "PАYMENT\n")
        self.assertIn("Look-alike hunk 001: before L1; after L1;", body)
        self.assertIn("column 2 U+0041->U+0410", body)

    def test_mixed_substantive_revision_still_cites_local_pair(self):
        body = self.compare("PAYMENT\nOwner Old\n", "PАYMENT\nOwner New\n")
        self.assertIn("Look-alike hunk 001: before L1; after L1;", body)
        self.assertIn("-Owner Old", body)
        self.assertIn("+Owner New", body)

    def test_disjoint_hunks_have_correct_physical_coordinates(self):
        old = "COST\n" + ("same\n" * 9) + "RATE\n"
        new = "CОST\n" + ("same\n" * 9) + "RАTE\n"
        body = self.compare(old, new)
        self.assertIn("Look-alike hunk 001: before L1; after L1;", body)
        self.assertIn("Look-alike hunk 002: before L11; after L11;", body)

    def test_ambiguous_duplicate_lines_never_paired(self):
        body = self.compare("PAY\nPAY\n", "PАY\nPАY\n")
        self.assertNotIn("Look-alike hunk", body)

    def test_regular_substantive_change_not_mislabeled(self):
        body = self.compare("Limit 5\n", "Limit 6\n")
        self.assertNotIn("Look-alike hunk", body)

    def test_no_overwrite_of_existing_evidence(self):
        body = self.compare("PAY\n", "PАY\n")
        with self.assertRaises(FileExistsError):
            self.compare("PAY\n", "PАY\n")
        self.assertEqual(self.report.read_text(encoding="utf-8"), body)

    def test_failing_unsafe_input_creates_no_report(self):
        self.before.write_text("PAY\n", encoding="utf-8")
        self.after.write_text("PАY\u202e\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
