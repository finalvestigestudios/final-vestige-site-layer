import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from packet_integrity import (
    attachment_inventory, ensure_fresh, hash_file, input_fingerprints,
    packet_snapshot, write_report,
)


class PacketIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.attachments = self.root / 'evidence'
        self.attachments.mkdir()
        self.claims = self.root / 'claims.csv'
        self.support = self.root / 'support.csv'
        self.claims.write_text('vendor,invoice,amount\nA,1,10.00\n', encoding='utf-8')
        self.support.write_text('vendor,invoice,amount,file\nA,1,10.00,receipt.pdf\n', encoding='utf-8')
        (self.attachments / 'receipt.pdf').write_bytes(b'%PDF-1.4')

    def test_snapshot_is_stable(self):
        before = packet_snapshot(self.claims, self.support, self.attachments)
        ensure_fresh(before, self.claims, self.support, self.attachments)
        self.assertEqual(len(before['attachments']['files']), 1)
        self.assertEqual(before['attachments']['errors'], [])

    def test_changed_claims_detected(self):
        before = packet_snapshot(self.claims, self.support, self.attachments)
        self.claims.write_text('vendor,invoice,amount\nA,1,11.00\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed since analysis'):
            ensure_fresh(before, self.claims, self.support, self.attachments)

    def test_changed_evidence_detected(self):
        before = packet_snapshot(self.claims, self.support, self.attachments)
        (self.attachments / 'receipt.pdf').write_bytes(b'altered')
        with self.assertRaisesRegex(ValueError, 'changed since analysis'):
            ensure_fresh(before, self.claims, self.support, self.attachments)

    def test_new_evidence_detected(self):
        before = packet_snapshot(self.claims, self.support, self.attachments)
        (self.attachments / 'extra.pdf').write_bytes(b'added')
        with self.assertRaisesRegex(ValueError, 'changed since analysis'):
            ensure_fresh(before, self.claims, self.support, self.attachments)

    def test_report_never_overwrites(self):
        snapshot = packet_snapshot(self.claims, self.support, self.attachments)
        output = self.root / 'review.html'
        write_report(output, '<p>okay</p>', self.claims, self.support,
                     self.attachments, snapshot)
        with self.assertRaises(FileExistsError):
            write_report(output, 'hacked', self.claims, self.support,
                         self.attachments, snapshot)
        self.assertEqual(output.read_text(), '<p>okay</p>')

    def test_report_cannot_modify_evidence(self):
        snapshot = packet_snapshot(self.claims, self.support, self.attachments)
        with self.assertRaisesRegex(ValueError, 'outside the attachment'):
            write_report(self.attachments / 'review.html', 'body', self.claims,
                         self.support, self.attachments, snapshot)
        with self.assertRaises(ValueError):
            write_report(self.claims, 'body', self.claims, self.support,
                         self.attachments, snapshot)

    def test_report_rejects_stale_inputs_without_writing(self):
        snapshot = packet_snapshot(self.claims, self.support, self.attachments)
        (self.attachments / 'receipt.pdf').unlink()
        output = self.root / 'review.json'
        with self.assertRaisesRegex(ValueError, 'changed since analysis'):
            write_report(output, '{}', self.claims, self.support,
                         self.attachments, snapshot)
        self.assertFalse(output.exists())

    def test_reject_same_csv_file(self):
        with self.assertRaisesRegex(ValueError, 'different files'):
            input_fingerprints(self.claims, self.claims)

    def test_attachment_byte_limit_aborts(self):
        with patch('packet_integrity.MAX_ATTACHMENT_BYTES', 3):
            with self.assertRaisesRegex(ValueError, 'scan limit'):
                attachment_inventory(self.attachments, self.claims, self.support)

    def test_symlink_is_scan_error(self):
        if not hasattr(Path, 'symlink_to'):
            self.skipTest('no symlink support')
        link = self.attachments / 'alias.pdf'
        try:
            link.symlink_to(self.attachments / 'receipt.pdf')
        except (OSError, NotImplementedError):
            self.skipTest('symlink privileges unavailable')
        inventory = attachment_inventory(self.attachments, self.claims, self.support)
        self.assertTrue(any(x['path'] == 'alias.pdf' for x in inventory['errors']))


if __name__ == '__main__':
    unittest.main()
