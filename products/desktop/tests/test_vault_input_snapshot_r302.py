"""R302 vault input: private, stable, bounded source snapshots (synthetic only)."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fvs_suite import vault_input_snapshot as snapshot

PRIVATE = "SYNTHETIC-CONFIDENTIAL-GRANTS-47912"


class VaultInputSnapshotR302Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r302-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / (PRIVATE + ".fvault")
        self.payload = b"Synthetic grant and procurement evidence\x00\xff"
        self.path.write_bytes(self.payload)

    def assert_private(self, fn, expected):
        try:
            fn()
        except ValueError as exc:
            self.assertEqual(str(exc), expected)
            self.assertIsNone(exc.__cause__)
            self.assertIsNone(exc.__context__)
            self.assertNotIn(PRIVATE, repr(exc))
        else:
            self.fail("Expected fixed-message ValueError")

    def test_reads_precisely_same_source_bytes(self):
        self.assertEqual(snapshot.read_vault_input(self.path, len(self.payload), "Encrypted archive"), self.payload)
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_empty_source(self):
        self.path.write_bytes(b"")
        self.assertEqual(snapshot.read_vault_input(self.path, 0, "Report"), b"")

    def test_one_byte_over_limit_refused(self):
        self.assert_private(lambda: snapshot.read_vault_input(self.path, len(self.payload) - 1, "Journal"),
                            "Journal exceeds the size limit")

    def test_missing_path_private(self):
        self.path.unlink()
        self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Report"),
                            "Report must be an existing regular file, not a symlink")

    def test_symlink_rejected_without_following(self):
        link = self.root / "linked.fvault"
        try:
            link.symlink_to(self.path)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")
        self.assert_private(lambda: snapshot.read_vault_input(link, 100, "Encrypted archive"),
                            "Encrypted archive must be an existing regular file, not a symlink")

    def test_directory_rejected(self):
        self.assert_private(lambda: snapshot.read_vault_input(self.root, 100, "Journal"),
                            "Journal must be an existing regular file, not a symlink")

    def test_no_untrusted_error_labels(self):
        self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, PRIVATE),
                            "Invalid vault input contract")

    def test_negative_or_noninteger_limit_refused(self):
        for invalid in (-1, 1.0, True):
            with self.subTest(invalid=invalid):
                self.assert_private(lambda: snapshot.read_vault_input(self.path, invalid, "Report"),
                                    "Invalid vault input contract")

    def test_lstat_permission_denied_no_context(self):
        with mock.patch.object(Path, "lstat", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Encrypted archive"),
                                "Cannot inspect encrypted archive source")

    def test_open_permission_denied_no_context(self):
        with mock.patch.object(snapshot.os, "open", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Report"),
                                "Cannot safely open report source")

    def test_descriptor_fstat_denied_no_context_and_closes_fd(self):
        real_close = os.close
        closed = []
        def close(fd):
            closed.append(fd)
            return real_close(fd)
        with mock.patch.object(snapshot.os, "fstat", side_effect=OSError(5, PRIVATE, str(self.path))), \
             mock.patch.object(snapshot.os, "close", side_effect=close):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Journal"),
                                "Cannot read journal source")
        self.assertEqual(len(closed), 1)

    def test_descriptor_read_failure_private_and_closed(self):
        real_close = os.close
        seen = []
        def close(fd):
            seen.append(fd)
            return real_close(fd)
        with mock.patch.object(snapshot.os, "read", side_effect=OSError(5, PRIVATE, str(self.path))), \
             mock.patch.object(snapshot.os, "close", side_effect=close):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Report"),
                                "Cannot read report source")
        self.assertEqual(len(seen), 1)

    def test_close_failure_private_not_masked(self):
        real_close = os.close
        def close_then_fail(fd):
            real_close(fd)
            raise OSError(5, PRIVATE, str(self.path))
        with mock.patch.object(snapshot.os, "close", side_effect=close_then_fail):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Journal"),
                                "Cannot read journal source")

    def test_path_swap_after_descriptor_open_detected(self):
        real_open = os.open
        def swap(path, flags):
            fd = real_open(path, flags)
            self.path.unlink()
            self.path.write_bytes(self.payload)
            return fd
        with mock.patch.object(snapshot.os, "open", side_effect=swap):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Report"),
                                "Report changed while opening")

    def test_file_growth_during_read_detected(self):
        real_read = os.read
        count = 0
        def mutate(fd, n):
            nonlocal count
            data = real_read(fd, n)
            count += 1
            if count == 1:
                with self.path.open("ab") as dest:
                    dest.write(b"changed")
            return data
        with mock.patch.object(snapshot.os, "read", side_effect=mutate):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Report"),
                                "Report changed while reading")

    def test_file_growth_over_limit_refused(self):
        real_read = os.read
        count = 0
        def grow(fd, n):
            nonlocal count
            count += 1
            if count == 1:
                with self.path.open("ab") as dest:
                    dest.write(b"z")
            return real_read(fd, n)
        with mock.patch.object(snapshot.os, "read", side_effect=grow):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, len(self.payload), "Report"),
                                "Report exceeds the size limit")

    def test_os_open_receives_no_follow_where_supported(self):
        real_open = os.open
        seen = []
        def watched(path, flags):
            seen.append(flags)
            return real_open(path, flags)
        with mock.patch.object(snapshot.os, "open", side_effect=watched):
            snapshot.read_vault_input(self.path, 100, "Report")
        self.assertEqual(len(seen), 1)
        if hasattr(os, "O_NOFOLLOW"):
            self.assertTrue(seen[0] & os.O_NOFOLLOW)

    def test_interrupt_is_not_swallowed_and_fd_is_closed(self):
        closed = []
        real_close = os.close
        def close(fd):
            closed.append(fd)
            return real_close(fd)
        with mock.patch.object(snapshot.os, "read", side_effect=KeyboardInterrupt), \
             mock.patch.object(snapshot.os, "close", side_effect=close):
            with self.assertRaises(KeyboardInterrupt):
                snapshot.read_vault_input(self.path, 100, "Report")
        self.assertEqual(len(closed), 1)

    def test_final_path_metadata_failure_keeps_path_private(self):
        real_lstat = Path.lstat
        count = 0
        def probe(path):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError(13, PRIVATE, str(path))
            return real_lstat(path)
        with mock.patch.object(Path, "lstat", autospec=True, side_effect=probe):
            self.assert_private(lambda: snapshot.read_vault_input(self.path, 100, "Journal"),
                                "Cannot inspect journal source")

    def test_read_does_not_modify_source_metadata(self):
        previous = self.path.stat()
        snapshot.read_vault_input(self.path, 100, "Report")
        latest = self.path.stat()
        self.assertEqual((previous.st_size, previous.st_mtime_ns), (latest.st_size, latest.st_mtime_ns))


if __name__ == "__main__":
    unittest.main()
