"""R339: private six-EXE report staging path is never auto-unlinked.

Synthetic evidence, genuine local temp directories and links. No EXE execution.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence as report


class ReportStageRetentionR339(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r339-private-audit-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "verification.json"
        self.evidence = {"release_authorized": False, "status": "integrity_only"}
        self.expected = (json.dumps(self.evidence, sort_keys=True, indent=2,
                                    ensure_ascii=True, allow_nan=False) + "\n").encode()

    def stages(self):
        return list(self.root.glob(".fvs-candidate-report-*.tmp"))

    def failed(self):
        with self.assertRaises(report.ReportEvidenceError) as ctx:
            report.publish_report(self.target, self.evidence)
        self.assertNotIn(str(self.root), str(ctx.exception))
        self.assertNotIn("PRIVATE_CLIENT", str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)

    def test_success_keeps_private_stage_with_identical_contents(self):
        report.publish_report(self.target, self.evidence)
        self.assertEqual(self.target.read_bytes(), self.expected)
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.stages()[0].read_bytes(), self.expected)

    def test_success_stage_and_final_share_inode(self):
        report.publish_report(self.target, self.evidence)
        a, b = self.stages()[0].stat(), self.target.stat()
        self.assertEqual((a.st_dev, a.st_ino), (b.st_dev, b.st_ino))

    def test_posix_stage_and_target_not_world_readable(self):
        if os.name == "nt":
            self.skipTest("Windows permission bits do not express NTFS ACLs")
        report.publish_report(self.target, self.evidence)
        self.assertEqual(self.target.stat().st_mode & 0o077, 0)
        self.assertEqual(self.stages()[0].stat().st_mode & 0o077, 0)

    def test_repeat_publication_creates_distinct_evidence_and_stages(self):
        report.publish_report(self.target, self.evidence)
        second = self.root / "second.json"
        report.publish_report(second, self.evidence)
        self.assertEqual(self.target.read_bytes(), second.read_bytes())
        self.assertEqual(len(self.stages()), 2)

    def test_existing_destination_kept_and_new_private_stage_retained(self):
        self.target.write_bytes(b"PREVIOUS_PRIVATE_CLIENT")
        self.failed()
        self.assertEqual(self.target.read_bytes(), b"PREVIOUS_PRIVATE_CLIENT")
        self.assertEqual(len(self.stages()), 1)

    def test_non_json_value_never_creates_stage(self):
        self.evidence = {"not_json": object()}
        self.failed()
        self.assertFalse(self.target.exists())
        self.assertFalse(self.stages())

    def test_nonfinite_float_never_creates_stage(self):
        self.evidence = {"bad_money": float("nan")}
        self.failed()
        self.assertFalse(self.stages())

    def test_fsync_failure_preserves_private_stage(self):
        with patch.object(report.os, "fsync", side_effect=OSError("PRIVATE_CLIENT")):
            self.failed()
        self.assertFalse(self.target.exists())
        self.assertEqual(len(self.stages()), 1)

    def test_fdopen_failure_preserves_private_stage(self):
        with patch.object(report.os, "fdopen", side_effect=OSError("PRIVATE_CLIENT")):
            self.failed()
        self.assertFalse(self.target.exists())
        self.assertEqual(len(self.stages()), 1)

    def test_link_failure_before_publication_preserves_stage(self):
        with patch.object(report.os, "link", side_effect=OSError("PRIVATE_CLIENT")):
            self.failed()
        self.assertFalse(self.target.exists())
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.stages()[0].read_bytes(), self.expected)

    def test_link_creates_target_then_raises_preserves_both(self):
        real_link = os.link
        def link_then_raise(stage, dest):
            real_link(stage, dest)
            raise OSError("PRIVATE_CLIENT")
        with patch.object(report.os, "link", side_effect=link_then_raise):
            self.failed()
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.target.read_bytes(), self.expected)

    def test_link_creates_wrong_bytes_then_raises_preserves_both(self):
        def bad_link(stage, dest):
            Path(dest).write_bytes(b"X" + Path(stage).read_bytes()[1:])
            raise OSError("PRIVATE_CLIENT")
        with patch.object(report.os, "link", side_effect=bad_link):
            self.failed()
        self.assertEqual(len(self.stages()), 1)
        self.assertTrue(self.target.read_bytes().startswith(b"X"))

    def test_missing_final_target_on_false_success_retains_stage(self):
        with patch.object(report.os, "link", return_value=None):
            self.failed()
        self.assertEqual(len(self.stages()), 1)
        self.assertFalse(self.target.exists())

    def test_suspect_copy_final_rejected_and_retained(self):
        def copy_not_link(stage, dest):
            Path(dest).write_bytes(Path(stage).read_bytes())
        with patch.object(report.os, "link", side_effect=copy_not_link):
            self.failed()
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.target.read_bytes(), self.expected)

    def test_injected_stage_path_swap_does_not_delete_other_owner_file(self):
        sentinel = self.root / "other-owner-private.txt"
        sentinel.write_bytes(b"DO_NOT_DELETE_PRIVATE_CLIENT")
        real_link = os.link
        def swap_then_raise(stage, dest):
            os.unlink(stage)
            real_link(sentinel, stage)
            raise OSError("PRIVATE_CLIENT")
        with patch.object(report.os, "link", side_effect=swap_then_raise):
            self.failed()
        self.assertEqual(sentinel.read_bytes(), b"DO_NOT_DELETE_PRIVATE_CLIENT")
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual(self.stages()[0].read_bytes(), sentinel.read_bytes())

    def test_stage_swap_after_hardlink_fails_witness_and_keeps_foreign_file(self):
        sentinel = self.root / "foreign-evidence.bin"
        sentinel.write_bytes(b"PRIVATE_CLIENT_DATA")
        real_link = os.link
        def link_then_swap(stage, dest):
            real_link(stage, dest)
            os.unlink(stage)
            real_link(sentinel, stage)
        with patch.object(report.os, "link", side_effect=link_then_swap):
            self.failed()
        self.assertEqual(sentinel.read_bytes(), b"PRIVATE_CLIENT_DATA")
        self.assertEqual(self.stages()[0].read_bytes(), sentinel.read_bytes())
        self.assertEqual(self.target.read_bytes(), self.expected)

    def test_unlink_not_called_even_after_normal_success(self):
        with patch.object(Path, "unlink", side_effect=AssertionError("unsafe delete")):
            report.publish_report(self.target, self.evidence)
        self.assertEqual(len(self.stages()), 1)

    def test_unlink_not_called_after_link_failure(self):
        with patch.object(report.os, "link", side_effect=OSError("PRIVATE_CLIENT")), \
             patch.object(Path, "unlink", side_effect=AssertionError("unsafe delete")):
            self.failed()
        self.assertEqual(len(self.stages()), 1)


if __name__ == "__main__":
    unittest.main()
