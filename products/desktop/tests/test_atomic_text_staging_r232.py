"""R232: real local staging custody for policy/grant TXT; synthetic data only."""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


class TextStagingCustodyR232(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "customer-private-grant-9912.txt"

    def assert_no_partials(self):
        self.assertEqual(list(self.root.glob("*.partial")), [])
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_existing_regular_file_is_rejected_before_staging(self):
        self.target.write_bytes(b"canonical evidence")
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaisesRegex(FileExistsError, "^Text report destination already exists$"):
                publish_text(self.target, "confidential new text")
        self.assertEqual(self.target.read_bytes(), b"canonical evidence")
        self.assert_no_partials()

    def test_existing_empty_file_is_rejected_before_staging(self):
        self.target.touch()
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(FileExistsError):
                publish_text(self.target, "new")
        self.assertEqual(self.target.read_bytes(), b"")
        self.assert_no_partials()

    def test_existing_symlink_rejected_without_staging(self):
        private = self.root / "source.txt"
        private.write_bytes(b"original")
        try:
            self.target.symlink_to(private)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(FileExistsError):
                publish_text(self.target, "replacement")
        self.assertEqual(private.read_bytes(), b"original")
        self.assertTrue(self.target.is_symlink())
        self.assert_no_partials()

    def test_dangling_symlink_rejected_without_staging(self):
        try:
            self.target.symlink_to(self.root / "absent.txt")
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        self.assertFalse(self.target.exists())
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(FileExistsError):
                publish_text(self.target, "replacement")
        self.assertTrue(self.target.is_symlink())
        self.assert_no_partials()

    def test_existing_directory_rejected_without_staging(self):
        self.target.mkdir()
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(FileExistsError):
                publish_text(self.target, "new")
        self.assertTrue(self.target.is_dir())
        self.assert_no_partials()

    def test_stage_prefix_never_contains_private_destination_name(self):
        original_mkstemp = tempfile.mkstemp
        captured = []
        def observe(*a, **kw):
            captured.append(kw.get("prefix"))
            return original_mkstemp(*a, **kw)
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=observe):
            publish_text(self.target, "approved\r\nexact UTF-8 🧪")
        self.assertEqual(captured, [".fvs-text-"])
        self.assertEqual(self.target.read_bytes(), "approved\r\nexact UTF-8 🧪".encode("utf-8"))
        self.assert_no_partials()

    def test_prefix_is_constant_across_distinct_private_names(self):
        original_mkstemp = tempfile.mkstemp
        prefixes = []
        def observe(*a, **kw):
            prefixes.append(kw.get("prefix"))
            return original_mkstemp(*a, **kw)
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=observe):
            publish_text(self.target, "first")
            publish_text(self.root / "second-secret-claim.txt", "second")
        self.assertEqual(prefixes, [".fvs-text-", ".fvs-text-"])
        self.assert_no_partials()

    def test_fdopen_failure_closes_native_descriptor(self):
        original_mkstemp = tempfile.mkstemp
        created = []
        def tracked(*a, **kw):
            fd, name = original_mkstemp(*a, **kw)
            created.append(fd)
            return fd, name
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=tracked):
            with patch("fvs_suite.atomic_text.os.fdopen", side_effect=OSError("synthetic fdopen failure")):
                with self.assertRaises(OSError):
                    publish_text(self.target, "private data")
        self.assertEqual(len(created), 1)
        try:
            os.fstat(created[0])
        except OSError as exc:
            self.assertEqual(exc.errno, errno.EBADF)
        else:
            os.close(created[0])
            self.fail("staging file descriptor was leaked")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_fdopen_keyboard_interrupt_also_closes_descriptor(self):
        original_mkstemp = tempfile.mkstemp
        created = []
        def tracked(*a, **kw):
            fd, name = original_mkstemp(*a, **kw)
            created.append(fd)
            return fd, name
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=tracked):
            with patch("fvs_suite.atomic_text.os.fdopen", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    publish_text(self.target, "private data")
        try:
            os.fstat(created[0])
        except OSError as exc:
            self.assertEqual(exc.errno, errno.EBADF)
        else:
            os.close(created[0])
            self.fail("interrupted staging file descriptor was leaked")
        self.assert_no_partials()

    def test_race_collision_still_refuses_overwrite(self):
        original_link = os.link
        original_rename = os.rename
        def race(src, dst):
            Path(dst).write_bytes(b"racing owner evidence")
            if os.name == "nt":
                return original_rename(src, dst)
            return original_link(src, dst)
        operation = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + operation, side_effect=race):
            with self.assertRaises((FileExistsError, OSError)):
                publish_text(self.target, "must not replace")
        self.assertEqual(self.target.read_bytes(), b"racing owner evidence")
        self.assert_no_partials()

    def test_missing_parent_does_not_stage(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(ValueError):
                publish_text(self.root / "missing" / "x.txt", "text")
        self.assert_no_partials()

    def test_nul_rejected_without_staging(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(ValueError):
                publish_text(self.target, "private\0value")
        self.assert_no_partials()

    def test_surrogate_rejected_without_staging(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=AssertionError("staged")):
            with self.assertRaises(ValueError):
                publish_text(self.target, "private\ud800value")
        self.assert_no_partials()

    def test_existing_target_error_does_not_include_private_filename(self):
        self.target.touch()
        with self.assertRaises(FileExistsError) as caught:
            publish_text(self.target, "customer content")
        self.assertNotIn("customer-private-grant", str(caught.exception))
        self.assert_no_partials()

    def test_normal_success_preserves_private_file_permissions_posix(self):
        if os.name == "nt":
            self.skipTest("POSIX-only mode check")
        publish_text(self.target, "hello")
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        self.assert_no_partials()


if __name__ == "__main__":
    unittest.main()
