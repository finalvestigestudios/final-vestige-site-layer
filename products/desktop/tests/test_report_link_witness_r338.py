"""R338: six-application report evidence requires post-publication readback.

Only synthetic JSON and real temporary filesystem links; no Windows EXE executed.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from report_link_witness_r338 import LinkWitnessError, verify_published_link
import report_link_witness_r338 as witness


class ReportLinkWitnessR338(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="r338-private-ledger-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.stage = self.folder / "stage.tmp"
        self.target = self.folder / "verification.json"
        self.payload = b'{"release_authorized": false}\n'
        self.stage.write_bytes(self.payload)

    def publish(self):
        os.link(self.stage, self.target)

    def check(self):
        verify_published_link(self.stage, self.target, self.payload)

    def rejects(self):
        with self.assertRaises(LinkWitnessError) as ctx:
            self.check()
        self.assertNotIn(str(self.folder), str(ctx.exception))
        self.assertNotIn("PRIVATE_CLIENT", str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)

    def test_genuine_hardlink_and_exact_bytes_pass(self):
        self.publish()
        self.check()
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_zero_length_evidence_link_can_be_witnessed(self):
        self.stage.write_bytes(b"")
        self.publish()
        verify_published_link(self.stage, self.target, b"")

    def test_missing_final_target_fails(self):
        self.rejects()

    def test_separate_copy_even_with_same_bytes_fails_identity(self):
        self.target.write_bytes(self.payload)
        self.rejects()

    def test_corrupted_same_length_copy_fails(self):
        self.target.write_bytes(b"X" + self.payload[1:])
        self.rejects()

    def test_short_copy_fails(self):
        self.target.write_bytes(self.payload[:-1])
        self.rejects()

    def test_extra_byte_in_link_fails(self):
        self.publish()
        self.target.write_bytes(self.payload + b"!")
        self.rejects()

    def test_inplace_same_size_mutation_of_link_fails(self):
        self.publish()
        self.target.write_bytes(b"X" + self.payload[1:])
        self.rejects()

    def test_replaced_staging_path_fails_even_if_target_was_original(self):
        self.publish()
        self.stage.unlink()
        self.stage.write_bytes(self.payload)
        self.rejects()
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_final_symlink_fails_even_with_matching_contents(self):
        try:
            self.target.symlink_to(self.stage)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        self.rejects()

    def test_staging_symlink_fails(self):
        original = self.folder / "original.tmp"
        self.stage.rename(original)
        try:
            self.stage.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        self.target.write_bytes(self.payload)
        self.rejects()

    def test_invalid_expected_payload_fails_closed(self):
        self.publish()
        for bad in (None, "hello", bytearray(self.payload), True):
            with self.subTest(bad=type(bad).__name__), self.assertRaises(LinkWitnessError):
                verify_published_link(self.stage, self.target, bad)

    def test_unexpected_open_exception_redacted(self):
        self.publish()
        with patch.object(witness.os, 'open', side_effect=OSError('PRIVATE_CLIENT')):
            self.rejects()

    def test_unexpected_read_exception_closes_descriptor(self):
        self.publish()
        captured = []
        real_open = os.open
        def recording_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            captured.append(fd)
            return fd
        with patch.object(witness.os, 'open', side_effect=recording_open), \
             patch.object(witness.os, 'read', side_effect=OSError('PRIVATE_CLIENT')):
            self.rejects()
        self.assertEqual(len(captured), 1)
        with self.assertRaises(OSError):
            os.fstat(captured[0])

    def test_closed_descriptor_when_read_returns_wrong_type(self):
        self.publish()
        with patch.object(witness.os, 'read', return_value=None):
            self.rejects()

    def test_existing_destination_witness_does_not_delete_or_modify(self):
        self.target.write_bytes(b'CUSTOMER_EVIDENCE')
        original = self.target.read_bytes()
        self.rejects()
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(self.stage.read_bytes(), self.payload)

    def test_unexpected_fstat_exception_redacted(self):
        self.publish()
        with patch.object(witness.os, 'fstat', side_effect=OSError('PRIVATE_CLIENT')):
            self.rejects()

    def test_mismatch_does_not_unlink_valid_or_invalid_evidence(self):
        self.publish()
        self.target.write_bytes(b"X" + self.payload[1:])
        self.rejects()
        self.assertTrue(self.stage.exists())
        self.assertTrue(self.target.exists())


if __name__ == '__main__':
    unittest.main()
