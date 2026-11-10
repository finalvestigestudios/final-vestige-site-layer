"""R47: descriptor-bound premium human review reads and appends (synthetic only)."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.journal_io import read_regular_bytes, append_verified_event
from synthetic_windows_fs_r104 import altered_lstat, changed_stat


class DescriptorJournalR47Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-journal-r47-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.journal = self.root / "review.jsonl"
        self.other = self.root / "private.txt"
        self.other.write_bytes(b"UNRELATED-PRIVATE-DATA\n")
        self.first = b'{"review":"one"}\n'
        self.second = b'{"review":"two"}\n'

    def test_regular_read_uses_exact_bounded_bytes(self):
        self.journal.write_bytes(self.first)
        self.assertEqual(read_regular_bytes(self.journal, 64, "Review journal"), self.first)

    def test_new_journal_is_created_privately_and_verified(self):
        calls = []
        def verify():
            calls.append(self.journal.read_bytes())
        append_verified_event(self.journal, self.first, 64, verify)
        self.assertEqual(calls, [b""])
        self.assertEqual(self.journal.read_bytes(), self.first)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.journal.stat().st_mode), 0o600)

    def test_valid_second_event_preserves_first(self):
        self.journal.write_bytes(self.first)
        append_verified_event(self.journal, self.second, 64,
                              lambda: self.assertEqual(self.journal.read_bytes(), self.first))
        self.assertEqual(self.journal.read_bytes(), self.first + self.second)

    def test_failed_verification_preserves_empty_journal_for_manual_review(self):
        def reject():
            raise ValueError("source changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            append_verified_event(self.journal, self.first, 64, reject)
        self.assertTrue(self.journal.is_file())
        self.assertEqual(self.journal.read_bytes(), b"")

    def test_failed_existing_verification_does_not_append(self):
        self.journal.write_bytes(self.first)
        with self.assertRaises(ValueError):
            append_verified_event(self.journal, self.second, 64,
                                  lambda: (_ for _ in ()).throw(ValueError("bad chain")))
        self.assertEqual(self.journal.read_bytes(), self.first)

    def test_journal_exceeding_limit_rejected_before_write(self):
        self.journal.write_bytes(self.first)
        with self.assertRaisesRegex(ValueError, "size limit"):
            append_verified_event(self.journal, self.second, len(self.first) + 1, lambda: None)
        self.assertEqual(self.journal.read_bytes(), self.first)

    def test_oversize_and_missing_read_rejected(self):
        self.journal.write_bytes(self.first)
        with self.assertRaises(ValueError):
            read_regular_bytes(self.journal, len(self.first) - 1, "Journal")
        # Privacy boundary: missing customer paths are never retained in a raw OS error.
        with self.assertRaisesRegex(ValueError, "Review evidence cannot be read"):
            read_regular_bytes(self.root / "absent", 128, "Journal")

    def test_link_alias_cannot_read_or_extend(self):
        os.link(self.other, self.journal)
        with self.assertRaisesRegex(ValueError, "without aliases"):
            read_regular_bytes(self.journal, 128, "Review journal")
        with self.assertRaisesRegex(ValueError, "without aliases"):
            append_verified_event(self.journal, self.first, 128, lambda: None)
        self.assertEqual(self.other.read_bytes(), b"UNRELATED-PRIVATE-DATA\n")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_cannot_read_or_extend_unrelated_file(self):
        self.journal.symlink_to(self.other)
        with self.assertRaises(ValueError):
            read_regular_bytes(self.journal, 128, "Review journal")
        with self.assertRaises(ValueError):
            append_verified_event(self.journal, self.first, 128, lambda: None)
        self.assertEqual(self.other.read_bytes(), b"UNRELATED-PRIVATE-DATA\n")

    def test_directory_cannot_be_read_or_extended(self):
        self.journal.mkdir()
        with self.assertRaises(ValueError):
            read_regular_bytes(self.journal, 128, "Review journal")
        with self.assertRaises(ValueError):
            append_verified_event(self.journal, self.first, 128, lambda: None)

    def test_regular_file_replacement_between_stat_and_open_rejected_on_read(self):
        self.journal.write_bytes(self.first)
        original_open = os.open
        changed = False
        def racing_open(path, flags, *args):
            nonlocal changed
            if Path(path) == self.journal and not changed:
                changed = True
                self.journal.unlink()
                self.journal.write_bytes(self.first)
            return original_open(path, flags, *args)
        with patch("fvs_suite.journal_io.os.open", side_effect=racing_open):
            with self.assertRaisesRegex(ValueError, "changed before read"):
                read_regular_bytes(self.journal, 128, "Review journal")

    def test_replacement_between_stat_and_open_cannot_redirect_append(self):
        self.journal.write_bytes(self.first)
        stranger = self.root / "stranger.jsonl"
        stranger.write_bytes(b"SECRET\n")
        original_open = os.open
        swapped = False
        def racing_open(path, flags, *args):
            nonlocal swapped
            if Path(path) == self.journal and not swapped:
                swapped = True
                self.journal.unlink()
                os.link(stranger, self.journal)
            return original_open(path, flags, *args)
        with patch("fvs_suite.journal_io.os.open", side_effect=racing_open):
            with self.assertRaises(ValueError):
                append_verified_event(self.journal, self.second, 128, lambda: None)
        self.assertEqual(stranger.read_bytes(), b"SECRET\n")

    def test_change_during_validation_blocks_append(self):
        self.journal.write_bytes(self.first)
        if os.name == "nt":
            # NTFS may deny a second writer while our append descriptor is
            # live. Simulate descriptor metadata drift AFTER validation, and
            # require the exact production _unchanged check to reject it.
            real_fstat = os.fstat
            active = {"active": False}
            def modified():
                active["active"] = True
            def drift(fd):
                info = real_fstat(fd)
                return changed_stat(info, "st_size") if active["active"] else info
            with patch("fvs_suite.journal_io.os.fstat", side_effect=drift):
                with self.assertRaisesRegex(ValueError, "changed while validating"):
                    append_verified_event(self.journal, self.second, 128, modified)
            self.assertEqual(self.journal.read_bytes(), self.first)
            return
        def modified():
            self.journal.write_bytes(b'{"review":"bad"}\n')
        with self.assertRaisesRegex(ValueError, "changed while validating"):
            append_verified_event(self.journal, self.second, 128, modified)
        self.assertEqual(self.journal.read_bytes(), b'{"review":"bad"}\n')

    def test_replacement_during_validation_blocks_append(self):
        self.journal.write_bytes(self.first)
        if os.name == "nt":
            # A live Windows handle can prevent unlink; the adversarial
            # observation is the *different pathname inode*, not successful
            # platform-specific deletion.
            active = {"active": False}
            original_lstat = os.lstat
            def swap():
                active["active"] = True
            observer = altered_lstat(self.journal, active, original_lstat)
            with patch("fvs_suite.journal_io.os.lstat", side_effect=observer):
                with self.assertRaises(ValueError):
                    append_verified_event(self.journal, self.second, 128, swap)
            self.assertEqual(self.journal.read_bytes(), self.first)
        else:
            def swap():
                self.journal.unlink()
                os.link(self.other, self.journal)
            with self.assertRaises(ValueError):
                append_verified_event(self.journal, self.second, 128, swap)
        self.assertEqual(self.other.read_bytes(), b"UNRELATED-PRIVATE-DATA\n")

    def test_validation_of_single_newline_event(self):
        for invalid in (b"", b"{}", b"{}\n{}\n", b"{}\x00\n", "{}\n", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    append_verified_event(self.journal, invalid, 128, lambda: None)
                self.assertFalse(self.journal.exists())

    def test_detect_replacement_after_read_before_return(self):
        self.journal.write_bytes(self.first)
        actual_fdopen = os.fdopen
        race_once = False
        if os.name == "nt":
            active = {"active": False}
            original_lstat = os.lstat
            def redirect_fdopen(*args, **kwargs):
                nonlocal race_once
                if not race_once:
                    race_once = True
                    active["active"] = True
                return actual_fdopen(*args, **kwargs)
            observer = altered_lstat(self.journal, active, original_lstat)
            with patch("fvs_suite.journal_io.os.lstat", side_effect=observer):
                with patch("fvs_suite.journal_io.os.fdopen", side_effect=redirect_fdopen):
                    with self.assertRaisesRegex(ValueError, "path changed"):
                        read_regular_bytes(self.journal, 128, "Review journal")
            self.assertEqual(self.journal.read_bytes(), self.first)
            return
        def redirect_fdopen(*args, **kwargs):
            nonlocal race_once
            if not race_once:
                race_once = True
                self.journal.unlink()
                self.journal.write_bytes(self.first)
            return actual_fdopen(*args, **kwargs)
        with patch("fvs_suite.journal_io.os.fdopen", side_effect=redirect_fdopen):
            with self.assertRaises(ValueError):
                read_regular_bytes(self.journal, 128, "Review journal")

    def test_failed_fsync_leaves_detectable_but_not_silent_journal(self):
        self.journal.write_bytes(self.first)
        with patch("fvs_suite.journal_io.os.fsync", side_effect=OSError("disk error")):
            with self.assertRaisesRegex(ValueError, "Review journal I/O failed"):
                append_verified_event(self.journal, self.second, 128, lambda: None)
        # An append may have reached the OS before fsync failed: do not claim it
        # was rolled back, and never manufacture a success acknowledgment.
        self.assertIn(self.journal.read_bytes(), (self.first, self.first + self.second))


if __name__ == "__main__":
    unittest.main()
