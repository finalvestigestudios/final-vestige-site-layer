"""R394: private offline release-evidence failures have no retained exception chain.

Synthetic-only, filesystem-local evidence; never executes or releases a binary.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence as publisher
import report_link_witness_r338 as witness

PRIVATE = "PRIVATE_VENDOR_SPEND_ACCOUNT_394_DO_NOT_EXPOSE"


class EvidencePrivateExceptionR394(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.candidate = self.base / "candidate"
        self.candidate.mkdir()
        self.out = self.base / "evidence.json"

    def assert_private_rejection(self, func, cls, *args, **kwargs):
        with self.assertRaises(cls) as caught:
            func(*args, **kwargs)
        err = caught.exception
        self.assertNotIn(PRIVATE, str(err))
        self.assertIsNone(err.__context__)
        self.assertIsNone(err.__cause__)
        return err

    def test_preflight_path_io_error_does_not_retain_private_context(self):
        with patch.object(publisher.Path, "resolve", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(publisher.prepare_report_path,
                                          publisher.ReportEvidenceError, self.out, self.candidate)

    def test_preflight_runtime_fault_does_not_retain_private_context(self):
        with patch.object(publisher.Path, "resolve", side_effect=RuntimeError(PRIVATE)):
            self.assert_private_rejection(publisher.prepare_report_path,
                                          publisher.ReportEvidenceError, self.out, self.candidate)

    def test_preflight_valid_destination_is_preserved(self):
        self.assertEqual(publisher.prepare_report_path(self.out, self.candidate), self.out)

    def test_preflight_refuses_existing_destination(self):
        self.out.write_text("prior evidence", encoding="utf-8")
        self.assert_private_rejection(publisher.prepare_report_path,
                                      publisher.ReportEvidenceError, self.out, self.candidate)
        self.assertEqual(self.out.read_text(), "prior evidence")

    def test_preflight_refuses_destination_inside_candidate(self):
        self.assert_private_rejection(publisher.prepare_report_path,
                                      publisher.ReportEvidenceError,
                                      self.candidate / "evidence.json", self.candidate)

    def test_fdopen_fault_closes_raw_descriptor_and_redacts_context(self):
        fd, name = tempfile.mkstemp(dir=self.base)
        with patch.object(publisher.os, "fdopen", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(publisher._write_verified_stage,
                                          publisher.ReportEvidenceError, fd, b"private")
        with self.assertRaises(OSError):
            os.fstat(fd)
        self.assertTrue(Path(name).exists())

    def test_fsync_fault_does_not_retain_private_context(self):
        fd, name = tempfile.mkstemp(dir=self.base)
        with patch.object(publisher.os, "fsync", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(publisher._write_verified_stage,
                                          publisher.ReportEvidenceError, fd, b"receipt")
        with self.assertRaises(OSError):
            os.fstat(fd)
        self.assertTrue(Path(name).exists())

    def test_fdopen_system_interrupt_propagates_and_fd_closed(self):
        fd, _ = tempfile.mkstemp(dir=self.base)
        with patch.object(publisher.os, "fdopen", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                publisher._write_verified_stage(fd, b"receipt")
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_short_write_is_rejected(self):
        fd, _ = tempfile.mkstemp(dir=self.base)
        class ShortWriter:
            def __enter__(self): return self
            def __exit__(self, *exc): return False
            def write(self, _): return 0
            def close(self): self.closed = True
        fake = ShortWriter()
        with patch.object(publisher.os, "fdopen", return_value=fake):
            self.assert_private_rejection(publisher._write_verified_stage,
                                          publisher.ReportEvidenceError, fd, b"receipt")
        os.close(fd)
        self.assertTrue(fake.closed)

    def test_json_error_redacted_before_creating_stage(self):
        with patch.object(publisher.json, "dumps", side_effect=TypeError(PRIVATE)):
            self.assert_private_rejection(publisher.publish_report,
                                          publisher.ReportEvidenceError, self.out, {"safe": True})
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.base.glob(".fvs-candidate-report-*")), [])

    def test_stage_creation_error_redacted(self):
        with patch.object(publisher.tempfile, "mkstemp", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(publisher.publish_report,
                                          publisher.ReportEvidenceError, self.out, {"safe": True})
        self.assertFalse(self.out.exists())

    def test_hardlink_error_redacted_and_never_overwrites(self):
        with patch.object(publisher.os, "link", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(publisher.publish_report,
                                          publisher.ReportEvidenceError, self.out, {"safe": True})
        self.assertFalse(self.out.exists())
        self.assertEqual(len(list(self.base.glob(".fvs-candidate-report-*"))), 1)

    def test_witness_fault_redacted_and_artifacts_retained_for_review(self):
        with patch.object(publisher, "verify_published_link",
                          side_effect=publisher.LinkWitnessError(PRIVATE)):
            self.assert_private_rejection(publisher.publish_report,
                                          publisher.ReportEvidenceError, self.out, {"safe": True})
        self.assertTrue(self.out.exists())
        self.assertEqual(len(list(self.base.glob(".fvs-candidate-report-*"))), 1)

    def test_atomic_publication_and_exact_byte_witness(self):
        data = {"offline": True, "approved": False}
        publisher.publish_report(self.out, data)
        expected = (json.dumps(data, sort_keys=True, indent=2,
                               ensure_ascii=True, allow_nan=False) + "\n").encode()
        self.assertEqual(self.out.read_bytes(), expected)
        stage = list(self.base.glob(".fvs-candidate-report-*"))
        self.assertEqual(len(stage), 1)
        witness.verify_published_link(stage[0], self.out, expected)
        self.assertEqual(os.stat(stage[0]).st_ino, os.stat(self.out).st_ino)

    def test_atomic_publication_never_overwrites_existing_report(self):
        self.out.write_text("original", encoding="utf-8")
        self.assert_private_rejection(publisher.publish_report,
                                      publisher.ReportEvidenceError, self.out, {"safe": True})
        self.assertEqual(self.out.read_text(encoding="utf-8"), "original")

    def test_witness_metadata_fault_discards_private_chain(self):
        with patch.object(witness.os, "stat", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(witness.verify_published_link,
                                          witness.LinkWitnessError, self.out, self.out, b"receipt")

    def test_witness_read_fault_discards_private_chain(self):
        self.out.write_bytes(b"receipt")
        with patch.object(witness.os, "read", side_effect=OSError(PRIVATE)):
            self.assert_private_rejection(witness.verify_published_link,
                                          witness.LinkWitnessError, self.out, self.out, b"receipt")

    def test_witness_rejects_mismatched_bytes(self):
        self.out.write_bytes(b"incorrect")
        self.assert_private_rejection(witness.verify_published_link,
                                      witness.LinkWitnessError, self.out, self.out, b"receipt")

    def test_witness_invalid_payload_type_rejected(self):
        self.assert_private_rejection(witness.verify_published_link,
                                      witness.LinkWitnessError, self.out, self.out, "not-bytes")


if __name__ == "__main__":
    unittest.main()
