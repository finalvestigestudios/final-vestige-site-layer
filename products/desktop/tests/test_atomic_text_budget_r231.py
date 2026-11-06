"""R231 private local TXT/manifest publication custody; synthetic fixtures only."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


class AtomicTextBudgetR231(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.target = self.folder / "report.txt"

    def clean(self):
        self.assertEqual(list(self.folder.glob(".*.partial")), [])

    def test_ascii_exact_byte_budget(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 10):
            publish_text(self.target, '0123456789')
        self.assertEqual(self.target.read_bytes(), b'0123456789')
        self.clean()

    def test_utf8_exact_byte_budget(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 8):
            publish_text(self.target, 'é' * 4)
        self.assertEqual(self.target.read_bytes(), ('é'*4).encode('utf-8'))
        self.clean()

    def test_utf8_expansion_above_byte_budget_rejected_pre_staging(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 7):
            with self.assertRaisesRegex(ValueError, '^Text report byte limit exceeded$'):
                publish_text(self.target, 'é' * 4)
        self.assertFalse(self.target.exists())
        self.clean()

    def test_ascii_above_byte_budget_rejected_pre_staging(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 4):
            with self.assertRaisesRegex(ValueError, '^Text report byte limit exceeded$'):
                publish_text(self.target, 'abcde')
        self.assertFalse(self.target.exists())
        self.clean()

    def test_zero_budget_allows_empty_document(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 0):
            publish_text(self.target, '')
        self.assertEqual(self.target.read_bytes(), b'')
        self.clean()

    def test_zero_budget_rejects_one_byte(self):
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 0):
            with self.assertRaises(ValueError):
                publish_text(self.target, 'a')
        self.clean()

    def test_no_nul_in_plaintext_report(self):
        with self.assertRaisesRegex(ValueError, '^Invalid text report content$'):
            publish_text(self.target, 'approval\x00hidden text')
        self.assertFalse(self.target.exists())
        self.clean()

    def test_unpaired_surrogate_fails_with_fixed_error(self):
        with self.assertRaisesRegex(ValueError, '^Invalid text report content$'):
            publish_text(self.target, 'private \ud800')
        self.assertFalse(self.target.exists())
        self.clean()

    def test_reject_str_subclass_without_calling_overrides(self):
        class ForgedText(str):
            def encode(self, *args, **kwargs): raise AssertionError('encode hook called')
            def __len__(self): raise AssertionError('len hook called')
            def __str__(self): raise AssertionError('str hook called')
        with self.assertRaisesRegex(TypeError, '^Text report content must be a plain string$'):
            publish_text(self.target, ForgedText('pretend official evidence'))
        self.assertFalse(self.target.exists())
        self.clean()

    def test_invalid_payload_cannot_replace_existing_report(self):
        self.target.write_bytes(b'official evidence')
        with self.assertRaises(ValueError):
            publish_text(self.target, 'bad\0payload')
        self.assertEqual(self.target.read_bytes(), b'official evidence')
        self.clean()

    def test_over_budget_cannot_replace_existing_report(self):
        self.target.write_bytes(b'official evidence')
        with patch('fvs_suite.atomic_text.MAX_TEXT_REPORT_BYTES', 1):
            with self.assertRaises(ValueError):
                publish_text(self.target, 'invalid')
        self.assertEqual(self.target.read_bytes(), b'official evidence')
        self.clean()

    def test_unicode_line_endings_stay_byte_identical(self):
        contents = 'Rule A\r\nRule B\nΓραμμή\n'
        publish_text(self.target, contents)
        self.assertEqual(self.target.read_bytes(), contents.encode('utf-8'))
        self.clean()

    def test_allows_valid_supplementary_unicode(self):
        publish_text(self.target, 'A\U0001F9EA B')
        self.assertEqual(self.target.read_bytes(), 'A\U0001F9EA B'.encode('utf-8'))
        self.clean()

    def test_staging_failure_cleans_partial(self):
        with patch('fvs_suite.atomic_text.os.fsync', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                publish_text(self.target, 'test')
        self.assertFalse(self.target.exists())
        self.clean()

    def test_existing_file_never_replaced(self):
        self.target.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            publish_text(self.target, 'new')
        self.assertEqual(self.target.read_bytes(), b'original')
        self.clean()

    def test_existing_symlink_never_replaced(self):
        private = self.folder / 'private.txt'
        private.write_bytes(b'private')
        try:
            self.target.symlink_to(private)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        with self.assertRaises(FileExistsError):
            publish_text(self.target, 'new')
        self.assertEqual(private.read_bytes(), b'private')
        self.clean()


if __name__ == '__main__':
    unittest.main()
