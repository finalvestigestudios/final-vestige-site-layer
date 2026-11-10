"""R340: unexpected report I/O faults must fail closed, privately and without deletion.

Genuine local temp files; synthetic JSON only. Never starts a Windows executable.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence as report


class ReportRuntimeFaultR340(unittest.TestCase):
    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="r340-private-customer-ledger-")
        self.addCleanup(private.cleanup)
        self.root = Path(private.name)
        self.target = self.root / "verification.json"
        self.payload = {"release_authorized": False, "status": "integrity_only"}
        self.expected = (json.dumps(self.payload, sort_keys=True, indent=2,
                                    ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")

    def stages(self):
        return list(self.root.glob(".fvs-candidate-report-*.tmp"))

    def reject_privately(self):
        with self.assertRaises(report.ReportEvidenceError) as err:
            report.publish_report(self.target, self.payload)
        self.assertNotIn("PRIVATE_CLIENT", str(err.exception))
        self.assertNotIn(str(self.root), str(err.exception))
        self.assertIsNone(err.exception.__cause__)

    def assert_retained(self, *, target=True):
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.stages()[0].read_bytes(), self.expected)
        self.assertEqual(self.target.exists(), target)
        if target:
            self.assertEqual(self.target.read_bytes(), self.expected)

    def test_link_runtimeerror_before_publication_redacted(self):
        with patch.object(report.os, "link", side_effect=RuntimeError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained(target=False)

    def test_link_runtimeerror_after_publication_preserves_both(self):
        real_link = os.link
        def write_then_fail(src, dst):
            real_link(src, dst)
            raise RuntimeError("PRIVATE_CLIENT")
        with patch.object(report.os, "link", side_effect=write_then_fail):
            self.reject_privately()
        self.assert_retained()
        self.assertTrue(os.path.samefile(self.target, self.stages()[0]))

    def test_link_runtimeerror_after_wrong_destination_keeps_both_for_review(self):
        def copy_then_fail(src, dst):
            Path(dst).write_bytes(b"OTHER_EVIDENCE")
            raise RuntimeError("PRIVATE_CLIENT")
        with patch.object(report.os, "link", side_effect=copy_then_fail):
            self.reject_privately()
        self.assertEqual(self.target.read_bytes(), b"OTHER_EVIDENCE")
        self.assert_retained_wrong_dest()

    def assert_retained_wrong_dest(self):
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.stages()[0].read_bytes(), self.expected)

    def test_mkstemp_runtimeerror_redacted_without_stage(self):
        with patch.object(report.tempfile, "mkstemp", side_effect=RuntimeError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assertEqual(self.stages(), [])
        self.assertFalse(self.target.exists())

    def test_mkstemp_typeerror_redacted_without_stage(self):
        with patch.object(report.tempfile, "mkstemp", side_effect=TypeError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assertEqual(self.stages(), [])
        self.assertFalse(self.target.exists())

    def test_witness_runtimeerror_redacted_and_evidence_retained(self):
        with patch.object(report, "verify_published_link", side_effect=RuntimeError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained()

    def test_witness_oserror_redacted_and_evidence_retained(self):
        with patch.object(report, "verify_published_link", side_effect=OSError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained()

    def test_witness_valueerror_redacted_and_evidence_retained(self):
        with patch.object(report, "verify_published_link", side_effect=ValueError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained()

    def test_fsync_runtimeerror_redacted_and_stage_retained(self):
        with patch.object(report.os, "fsync", side_effect=RuntimeError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained(target=False)

    def test_link_permissionerror_redacted_stage_retained(self):
        with patch.object(report.os, "link", side_effect=PermissionError("PRIVATE_CLIENT")):
            self.reject_privately()
        self.assert_retained(target=False)

    def test_destination_existing_remains_untouched(self):
        self.target.write_bytes(b"EXISTING_CUSTOMER_EVIDENCE")
        with self.assertRaises(report.ReportEvidenceError):
            report.publish_report(self.target, self.payload)
        self.assertEqual(self.target.read_bytes(), b"EXISTING_CUSTOMER_EVIDENCE")
        self.assert_retained_wrong_dest()

    def test_no_autodelete_after_unexpected_link_fault(self):
        with patch.object(report.os, "link", side_effect=RuntimeError("PRIVATE_CLIENT")), \
             patch.object(Path, "unlink", side_effect=AssertionError("unsafe auto-delete")):
            self.reject_privately()
        self.assert_retained(target=False)

    def test_no_autodelete_after_witness_fault(self):
        with patch.object(report, "verify_published_link", side_effect=RuntimeError("PRIVATE_CLIENT")), \
             patch.object(Path, "unlink", side_effect=AssertionError("unsafe auto-delete")):
            self.reject_privately()
        self.assert_retained()

    def test_interrupt_in_link_not_swallowed(self):
        with patch.object(report.os, "link", side_effect=KeyboardInterrupt()), \
             self.assertRaises(KeyboardInterrupt):
            report.publish_report(self.target, self.payload)
        self.assert_retained(target=False)

    def test_interrupt_in_witness_not_swallowed(self):
        with patch.object(report, "verify_published_link", side_effect=KeyboardInterrupt()), \
             self.assertRaises(KeyboardInterrupt):
            report.publish_report(self.target, self.payload)
        self.assert_retained()

    def test_interrupt_in_stage_creator_not_swallowed(self):
        with patch.object(report.tempfile, "mkstemp", side_effect=KeyboardInterrupt()), \
             self.assertRaises(KeyboardInterrupt):
            report.publish_report(self.target, self.payload)
        self.assertEqual(self.stages(), [])
        self.assertFalse(self.target.exists())

    def test_deterministic_canonical_bytes_still_publish(self):
        report.publish_report(self.target, self.payload)
        self.assert_retained()
        second = self.root / "second.json"
        report.publish_report(second, self.payload)
        self.assertEqual(second.read_bytes(), self.expected)
        self.assertEqual(len(self.stages()), 2)

    def test_nonfinite_evidence_cannot_create_stage(self):
        with self.assertRaises(report.ReportEvidenceError):
            report.publish_report(self.target, {"amount": float("nan")})
        self.assertEqual(self.stages(), [])
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
