"""R28 synthetic, local-only text-evidence publication regression tests."""
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


class AtomicTextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "policy-delta.txt"

    def assert_no_partials(self):
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_round_trip_exact_bytes_and_line_endings(self):
        content = "évidence\nRule A\r\nRule B\n"
        self.assertEqual(publish_text(self.target, content), self.target)
        self.assertEqual(self.target.read_bytes(), content.encode("utf-8"))
        self.assert_no_partials()

    def test_zero_length_evidence_is_still_a_complete_file(self):
        publish_text(self.target, "")
        self.assertEqual(self.target.read_bytes(), b"")
        self.assert_no_partials()

    def test_collision_preserves_existing_evidence(self):
        self.target.write_bytes(b"trusted report")
        with self.assertRaises(FileExistsError):
            publish_text(self.target, "replacement")
        self.assertEqual(self.target.read_bytes(), b"trusted report")
        self.assert_no_partials()

    def test_symlink_cannot_be_followed_or_replaced(self):
        private = self.root / "private.txt"
        private.write_bytes(b"private data")
        try:
            self.target.symlink_to(private)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(FileExistsError):
            publish_text(self.target, "overwrite")
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(private.read_bytes(), b"private data")
        self.assert_no_partials()

    def test_no_directory_no_staging(self):
        with self.assertRaises(ValueError):
            publish_text(self.root / "missing" / "report.txt", "test")
        self.assert_no_partials()

    def test_invalid_content_rejected_before_staging(self):
        with self.assertRaises(TypeError):
            publish_text(self.target, b"bytes")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_invalid_utf8_payload_rejected_before_staging(self):
        with self.assertRaisesRegex(ValueError, '^Invalid text report content
            publish_text(self.target, "unpaired surrogate \ud800")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_fsync_error_cleans_partial_without_report(self):
        with patch("fvs_suite.atomic_text.os.fsync", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                publish_text(self.target, "private test")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_publication_error_cleans_partial_without_report(self):
        operation = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + operation,
                   side_effect=OSError("unsupported filesystem")):
            with self.assertRaises(OSError):
                publish_text(self.target, "private test")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_only_final_report_is_visible_after_success(self):
        publish_text(self.target, "complete")
        self.assertEqual([p.name for p in self.root.iterdir()], [self.target.name])
        self.assert_no_partials()

    def test_unicode_report_text_without_bom(self):
        publish_text(self.target, "Γραμμή\n日本語\n")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "Γραμμή\n日本語\n")
        self.assertFalse(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))

    @unittest.skipIf(os.name == "nt", "POSIX mode only")
    def test_private_owner_permissions_posix(self):
        publish_text(self.target, "financial evidence")
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
):
            publish_text(self.target, "unpaired surrogate \ud800")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_fsync_error_cleans_partial_without_report(self):
        with patch("fvs_suite.atomic_text.os.fsync", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                publish_text(self.target, "private test")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_publication_error_cleans_partial_without_report(self):
        operation = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + operation,
                   side_effect=OSError("unsupported filesystem")):
            with self.assertRaises(OSError):
                publish_text(self.target, "private test")
        self.assertFalse(self.target.exists())
        self.assert_no_partials()

    def test_only_final_report_is_visible_after_success(self):
        publish_text(self.target, "complete")
        self.assertEqual([p.name for p in self.root.iterdir()], [self.target.name])
        self.assert_no_partials()

    def test_unicode_report_text_without_bom(self):
        publish_text(self.target, "Γραμμή\n日本語\n")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "Γραμμή\n日本語\n")
        self.assertFalse(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))

    @unittest.skipIf(os.name == "nt", "POSIX mode only")
    def test_private_owner_permissions_posix(self):
        publish_text(self.target, "financial evidence")
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
