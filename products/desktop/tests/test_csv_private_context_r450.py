"""R450 CSV publisher and staged-byte error privacy regressions; synthetic only."""
from __future__ import annotations

import errno
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_publish_guard import private_csv_failure
from fvs_suite.csv_stage_integrity import CSVStagingWitness

_SECRET = "CLIENT_SECRET_FINANCIAL_FILENAME_450"


class PrivateCSVContextR450(unittest.TestCase):
    def assert_private_error_absent(self, error: BaseException) -> None:
        self.assertNotIn(_SECRET, repr(error))
        self.assertIsNone(error.__context__, "retained private source context")
        self.assertIsNone(error.__cause__, "retained private source cause")

    def test_writer_sanitizes_os_error_without_private_context(self):
        original = OSError(errno.EACCES, _SECRET, "/private/" + _SECRET)
        with patch("fvs_suite.atomic_reports._write_csv_report", side_effect=original):
            with self.assertRaises(OSError) as raised:
                write_csv_report("ignored", (), (), str)
        self.assertEqual(raised.exception.errno, errno.EACCES)
        self.assertEqual(str(raised.exception), "[Errno 13] CSV report publication failed")
        self.assert_private_error_absent(raised.exception)

    def test_writer_sanitizes_collision_and_retains_no_filename(self):
        original = FileExistsError(errno.EEXIST, _SECRET, "/private/" + _SECRET)
        with patch("fvs_suite.atomic_reports._write_csv_report", side_effect=original):
            with self.assertRaises(FileExistsError) as raised:
                write_csv_report("ignored", (), (), str)
        self.assertEqual(str(raised.exception), "CSV report destination already exists")
        self.assert_private_error_absent(raised.exception)

    def test_writer_defaults_unknown_errno_to_eio(self):
        with patch("fvs_suite.atomic_reports._write_csv_report", side_effect=OSError(_SECRET)):
            with self.assertRaises(OSError) as raised:
                write_csv_report("ignored", (), (), str)
        self.assertEqual(raised.exception.errno, errno.EIO)
        self.assert_private_error_absent(raised.exception)

    def test_clean_builder_does_not_capture_source_exception(self):
        original = OSError(errno.EIO, _SECRET)
        result = private_csv_failure(original)
        self.assertIsInstance(result, OSError)
        self.assertIsNone(result.__context__)
        self.assertNotIn(_SECRET, str(result))

    def test_writer_propagates_non_os_validation_failures(self):
        with patch("fvs_suite.atomic_reports._write_csv_report", side_effect=ValueError("Invalid row")):
            with self.assertRaisesRegex(ValueError, "Invalid row"):
                write_csv_report("ignored", (), (), str)

    def _staged(self, actual=b"A", expected=b"A"):
        temporary = tempfile.TemporaryFile()
        self.addCleanup(temporary.close)
        temporary.write(b"\xef\xbb\xbf" + actual)
        temporary.flush()
        witness = CSVStagingWitness()
        witness.record(expected)
        return temporary.fileno(), witness

    def test_valid_stage_bytes_succeed(self):
        descriptor, witness = self._staged()
        witness.verify(descriptor)

    def test_staging_fstat_private_error_has_no_hidden_context(self):
        descriptor, witness = self._staged()
        with patch("fvs_suite.csv_stage_integrity.os.fstat", side_effect=OSError(errno.EIO, _SECRET)):
            with self.assertRaises(OSError) as raised:
                witness.verify(descriptor)
        self.assertEqual(raised.exception.errno, errno.EIO)
        self.assert_private_error_absent(raised.exception)

    def test_staging_lseek_private_error_has_no_hidden_context(self):
        descriptor, witness = self._staged()
        with patch("fvs_suite.csv_stage_integrity.os.lseek", side_effect=OSError(errno.EIO, _SECRET)):
            with self.assertRaises(OSError) as raised:
                witness.verify(descriptor)
        self.assert_private_error_absent(raised.exception)

    def test_staging_read_private_error_has_no_hidden_context(self):
        descriptor, witness = self._staged()
        with patch("fvs_suite.csv_stage_integrity.os.read", side_effect=OSError(errno.EIO, _SECRET)):
            with self.assertRaises(OSError) as raised:
                witness.verify(descriptor)
        self.assert_private_error_absent(raised.exception)

    def test_same_size_modified_stage_rejected(self):
        descriptor, witness = self._staged(actual=b"B", expected=b"A")
        with self.assertRaises(OSError) as raised:
            witness.verify(descriptor)
        self.assert_private_error_absent(raised.exception)

    def test_short_staging_file_rejected(self):
        descriptor, witness = self._staged(actual=b"", expected=b"A")
        with self.assertRaises(OSError) as raised:
            witness.verify(descriptor)
        self.assert_private_error_absent(raised.exception)

    def test_witness_does_not_accept_nonbytes(self):
        with self.assertRaises(TypeError):
            CSVStagingWitness().record(bytearray(b"A"))

if __name__ == "__main__":
    unittest.main()
