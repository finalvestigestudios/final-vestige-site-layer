"""R257: fail-closed SHA inventory descriptor adoption and proven normal hashing.

Uses the real manifest guard, descriptor helper and CSV signature modules with
synthetic local files. Does not test an executable or native Windows GUI.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import manifest_guard as subject


class ManifestStreamAdoptionR257(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'confidential-source.csv'
        self.source.write_bytes(b'Invoice,Amount\nINV-1,12.30\n')

    def track_opened_descriptor(self, fault):
        """Inject fdopen failure while recording the genuine opened OS handle."""
        opened = []
        original_open = os.open

        def traced_open(*args, **kwargs):
            fd = original_open(*args, **kwargs)
            opened.append(fd)
            return fd

        with (patch('fvs_suite.premium_link_custody.os.open', side_effect=traced_open),
              patch('fvs_suite.premium_link_custody.os.fdopen', side_effect=fault)):
            with self.assertRaises(type(fault)) if isinstance(fault, BaseException) and not isinstance(fault, Exception) else self.assertRaises(ValueError) as caught:
                subject._hash_regular(self.source, subject.MAX_INPUT_BYTES)
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])
        return caught.exception

    def test_real_sha256_matches_file_bytes(self):
        digest, metadata = subject._hash_regular(self.source, subject.MAX_INPUT_BYTES)
        self.assertEqual(digest, hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(metadata[2], self.source.stat().st_size)

    def test_inventory_text_covers_source_and_report(self):
        report = self.root / 'report.csv'
        report.write_bytes(b'Status\nreview\n')
        expected = hashlib.sha256(self.source.read_bytes()).hexdigest()
        inventory = subject.inventory_text([self.source], [report], expected_input_digests={self.source: expected})
        self.assertIn(f'{self.source.name}\t{expected}\n', inventory)
        self.assertIn(f'{report.name}\t{hashlib.sha256(report.read_bytes()).hexdigest()}\n', inventory)
        self.assertEqual(len(inventory.splitlines()), 3)

    def test_wrong_source_snapshot_digest_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Source bytes changed'):
            subject.inventory_text([self.source], [], expected_input_digests={self.source: '0' * 64})

    def test_missing_digest_coverage_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'coverage mismatch'):
            subject.inventory_text([self.source], [], expected_input_digests={})

    def test_adoption_oserror_closes_real_descriptor_and_redacts_path(self):
        error = self.track_opened_descriptor(OSError('/private/customer/ledger.csv'))
        self.assertNotIn('customer', str(error))
        self.assertNotIn('ledger.csv', str(error))

    def test_adoption_runtimeerror_closes_real_descriptor_and_redacts_path(self):
        error = self.track_opened_descriptor(RuntimeError('/private/customer/ledger.csv'))
        self.assertNotIn('customer', str(error))
        self.assertNotIn('ledger.csv', str(error))

    def test_adoption_keyboardinterrupt_closes_real_descriptor(self):
        self.track_opened_descriptor(KeyboardInterrupt())

    def test_adoption_systemexit_closes_real_descriptor(self):
        self.track_opened_descriptor(SystemExit(5))

    def test_os_open_error_never_attempts_stream_adoption(self):
        with (patch('fvs_suite.premium_link_custody.os.open', side_effect=PermissionError('/private/customer.csv')),
              patch('fvs_suite.premium_link_custody.os.fdopen') as adopt):
            with self.assertRaises(ValueError) as caught:
                subject._hash_regular(self.source, subject.MAX_INPUT_BYTES)
            adopt.assert_not_called()
        self.assertNotIn('customer.csv', str(caught.exception))

    def test_disappearing_file_during_open_has_safe_missing_message(self):
        with patch('fvs_suite.premium_link_custody.os.open', side_effect=FileNotFoundError('/private/customer.csv')):
            with self.assertRaises(FileNotFoundError) as caught:
                subject._hash_regular(self.source, subject.MAX_INPUT_BYTES)
        self.assertNotIn('customer.csv', str(caught.exception))

    def test_oversized_data_is_rejected_before_open(self):
        with patch('fvs_suite.premium_link_custody.os.open') as opener:
            with self.assertRaisesRegex(ValueError, 'file-size limit'):
                subject._hash_regular(self.source, 2)
            opener.assert_not_called()

    def test_symlink_is_rejected_before_open(self):
        link = self.root / 'source-link.csv'
        try:
            link.symlink_to(self.source)
        except (NotImplementedError, OSError) as e:
            self.skipTest(f'Symlinks unsupported: {type(e).__name__}')
        with patch('fvs_suite.premium_link_custody.os.open') as opener:
            with self.assertRaisesRegex(ValueError, 'regular file'):
                subject._hash_regular(link, subject.MAX_INPUT_BYTES)
            opener.assert_not_called()
        self.assertEqual(self.source.read_bytes(), b'Invoice,Amount\nINV-1,12.30\n')

    def test_success_closes_descriptor(self):
        opened = []
        original_open = os.open
        def trace(*args, **kwargs):
            fd = original_open(*args, **kwargs)
            opened.append(fd)
            return fd
        with patch('fvs_suite.premium_link_custody.os.open', side_effect=trace):
            subject._hash_regular(self.source, subject.MAX_INPUT_BYTES)
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])

    def test_hardlinked_input_output_are_rejected_in_same_inventory(self):
        alias = self.root / 'hardlinked-report.csv'
        try:
            os.link(self.source, alias)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f'Hardlinks unsupported: {type(exc).__name__}')
        with self.assertRaisesRegex(ValueError, 'distinct'):
            subject.inventory_text([self.source], [alias])

    def test_ambiguous_basename_is_rejected_before_open(self):
        other = self.root / 'sub'
        other.mkdir()
        duplicate = other / self.source.name
        duplicate.write_bytes(b'synthetic\n')
        with patch('fvs_suite.premium_link_custody.os.open') as opener:
            with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                subject.inventory_text([self.source], [duplicate])
            opener.assert_not_called()


if __name__ == '__main__':
    unittest.main()
