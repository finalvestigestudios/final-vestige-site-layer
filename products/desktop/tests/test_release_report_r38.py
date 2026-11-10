"""R38: atomic and exclusive release-gate JSON evidence, no real EXE execution."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence
from report_evidence import ReportEvidenceError, prepare_report_path, publish_report


class ReleaseReportR38Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r38-report-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.reports = self.root / "reports"
        self.reports.mkdir()
        self.payload = {"schema": 1, "release_authorized": False, "premium_entitlement_verified": False,
                        "status": "integrity_only", "artifacts": [{"name": "LedgerDiffLite.exe", "sha256": "a"*64}]}

    def target(self, name="candidate.json"):
        return self.reports / name

    def test_preflight_valid_outside(self):
        accepted = prepare_report_path(self.target(), self.dist)
        # Windows temporary directories may resolve through volume junctions,
        # short names or differently cased drive paths. Verify the *actual*
        # existing parent directory, rather than its textual spelling.
        self.assertTrue(os.path.samefile(accepted.parent, self.reports))
        self.assertEqual(accepted.name, self.target().name)
        self.assertFalse(os.path.lexists(accepted))

    def test_atomic_complete_json_is_readable(self):
        dest = prepare_report_path(self.target(), self.dist)
        publish_report(dest, self.payload)
        self.assertEqual(json.loads(dest.read_text(encoding="utf-8")), self.payload)
        self.assertTrue(dest.read_bytes().endswith(b"\n"))
        self.assertEqual(len(list(self.reports.glob(".fvs-candidate-report-*"))), 1)

    def test_byte_determinism(self):
        first, second = self.target("first.json"), self.target("second.json")
        publish_report(first, self.payload)
        publish_report(second, self.payload)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_reject_report_inside_candidate(self):
        with self.assertRaisesRegex(ReportEvidenceError, "outside"):
            prepare_report_path(self.dist / "report.json", self.dist)

    def test_reject_nested_candidate_directory(self):
        nested = self.dist / "subdir"
        nested.mkdir()
        with self.assertRaisesRegex(ReportEvidenceError, "outside"):
            prepare_report_path(nested / "report.json", self.dist)

    def test_reject_dotdot_resolving_into_candidate(self):
        with self.assertRaisesRegex(ReportEvidenceError, "outside"):
            prepare_report_path(self.reports / ".." / "dist" / "proof.json", self.dist)

    def test_reject_symlink_parent_into_candidate(self):
        link = self.root / "alias"
        try:
            link.symlink_to(self.dist, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("Directory links not supported")
        with self.assertRaisesRegex(ReportEvidenceError, "outside"):
            prepare_report_path(link / "proof.json", self.dist)

    def test_reject_existing_report_even_if_empty(self):
        dest = self.target()
        dest.touch()
        with self.assertRaisesRegex(ReportEvidenceError, "already exists"):
            prepare_report_path(dest, self.dist)

    def test_reject_existing_symlink_even_if_dangling(self):
        dest = self.target()
        try:
            dest.symlink_to(self.root / "missing")
        except (NotImplementedError, OSError):
            self.skipTest("File links not supported")
        with self.assertRaisesRegex(ReportEvidenceError, "already exists"):
            prepare_report_path(dest, self.dist)

    def test_race_destination_creation_never_overwrites(self):
        dest = prepare_report_path(self.target(), self.dist)
        dest.write_text("original", encoding="utf-8")
        with self.assertRaises(ReportEvidenceError):
            publish_report(dest, self.payload)
        self.assertEqual(dest.read_text(encoding="utf-8"), "original")
        self.assertEqual(len(list(self.reports.glob(".fvs-candidate-report-*"))), 1)

    def test_exclusive_publish_twice_rejected_without_changes(self):
        dest = self.target()
        publish_report(dest, self.payload)
        original = dest.read_bytes()
        with self.assertRaises(ReportEvidenceError):
            publish_report(dest, {"modified": True})
        self.assertEqual(dest.read_bytes(), original)

    def test_invalid_evidence_never_creates_file(self):
        for evidence in ({"not_json": object()}, {"nan": float("nan")}):
            with self.subTest(evidence=evidence):
                with self.assertRaises(ReportEvidenceError):
                    publish_report(self.target(), evidence)
                self.assertFalse(self.target().exists())

    def test_flush_failure_retains_private_stage_without_final(self):
        with patch.object(report_evidence.os, "fsync", side_effect=OSError("private path")):
            with self.assertRaises(ReportEvidenceError) as caught:
                publish_report(self.target(), self.payload)
        self.assertFalse(self.target().exists())
        self.assertNotIn("private path", str(caught.exception))
        self.assertEqual(len(list(self.reports.glob(".fvs-candidate-report-*"))), 1)

    def test_hardlink_failure_retains_private_stage_without_final(self):
        with patch.object(report_evidence.os, "link", side_effect=OSError("sensitive")):
            with self.assertRaises(ReportEvidenceError) as caught:
                publish_report(self.target(), self.payload)
        self.assertFalse(self.target().exists())
        self.assertNotIn("sensitive", str(caught.exception))
        self.assertEqual(len(list(self.reports.glob(".fvs-candidate-report-*"))), 1)

    def test_missing_parent_rejected(self):
        with self.assertRaises(ReportEvidenceError):
            prepare_report_path(self.root / "missing" / "report.json", self.dist)

    def test_parent_file_not_directory_rejected(self):
        self.target().write_text("not a folder")
        with self.assertRaises(ReportEvidenceError):
            prepare_report_path(self.target() / "report.json", self.dist)

    def test_private_posix_permissions(self):
        if os.name == "nt":
            self.skipTest("POSIX mode bits do not map to NTFS ACLs")
        publish_report(self.target(), self.payload)
        self.assertEqual(self.target().stat().st_mode & 0o077, 0)

    def test_privacy_no_path_in_error(self):
        private = self.reports / "Client Name Hidden.json"
        private.touch()
        with self.assertRaises(ReportEvidenceError) as caught:
            prepare_report_path(private, self.dist)
        self.assertNotIn("Client Name", str(caught.exception))
        self.assertNotIn(str(self.root), str(caught.exception))


if __name__ == "__main__":
    unittest.main()
