"""R236 CSV financial output integrity: synthetic local bytes only."""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.csv_stage_integrity import CSVStagingWitness
from fvs_suite.atomic_reports import _BudgetedCSVTextSink, write_csv_report


class ShortWriteStream:
    def __init__(self, returned):
        self.returned = returned

    def write(self, text):
        return self.returned


class CSVStageIntegrityR236(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.target = self.root / "secret-customer-ledger.csv"
        self.lines = (b"\xef\xbb\xbfid,amount\r\nA,42.10\r\n")

    def witness_file(self, contents):
        fd, name = tempfile.mkstemp(dir=self.root)
        self.addCleanup(lambda: os.path.exists(name) and os.unlink(name))
        self.addCleanup(lambda: os.close(fd))
        os.write(fd, contents)
        w = CSVStagingWitness()
        w.record(b"id,amount\r\n")
        w.record(b"A,42.10\r\n")
        return w, fd

    def test_real_staged_file_matches_streamed_witness(self):
        witness, fd = self.witness_file(self.lines)
        witness.verify(fd)

    def test_same_length_first_byte_corruption_rejected(self):
        w, fd = self.witness_file(b"X" + self.lines[1:])
        with self.assertRaises(OSError): w.verify(fd)

    def test_same_length_last_byte_corruption_rejected(self):
        w, fd = self.witness_file(self.lines[:-1] + b"X")
        with self.assertRaises(OSError): w.verify(fd)

    def test_same_length_amount_corruption_rejected(self):
        w, fd = self.witness_file(self.lines.replace(b"42.10", b"99.99"))
        with self.assertRaises(OSError): w.verify(fd)

    def test_missing_bom_rejected(self):
        w, fd = self.witness_file(self.lines[3:])
        with self.assertRaises(OSError): w.verify(fd)

    def test_extra_byte_rejected(self):
        w, fd = self.witness_file(self.lines + b"X")
        with self.assertRaises(OSError): w.verify(fd)

    def test_truncated_file_rejected(self):
        w, fd = self.witness_file(self.lines[:-1])
        with self.assertRaises(OSError): w.verify(fd)

    def test_short_os_read_is_valid_and_streams_to_completion(self):
        w, fd = self.witness_file(self.lines)
        real_read = os.read
        with patch("fvs_suite.csv_stage_integrity.os.read", side_effect=lambda f, n: real_read(f, min(n, 2))):
            w.verify(fd)

    def test_early_eof_fails_closed(self):
        w, fd = self.witness_file(self.lines)
        with patch("fvs_suite.csv_stage_integrity.os.read", return_value=b""):
            with self.assertRaises(OSError): w.verify(fd)

    def test_read_oserror_is_fixed_text_without_path(self):
        w, fd = self.witness_file(self.lines)
        with patch("fvs_suite.csv_stage_integrity.os.read", side_effect=OSError(5, "sensitive", str(self.target))):
            with self.assertRaises(OSError) as context: w.verify(fd)
        self.assertEqual(str(context.exception), "[Errno 5] CSV report staging integrity check failed")
        self.assertEqual(context.exception.errno, errno.EIO)
        self.assertNotIn(str(self.target), str(context.exception))

    def test_fstat_failure_fixed_text(self):
        w, fd = self.witness_file(self.lines)
        with patch("fvs_suite.csv_stage_integrity.os.fstat", side_effect=OSError(2, "private", str(self.target))):
            with self.assertRaises(OSError) as context: w.verify(fd)
        self.assertNotIn(str(self.target), str(context.exception))

    def test_rejects_forged_mutable_byte_subclass(self):
        class Forged(bytes):
            pass
        with self.assertRaises(TypeError): CSVStagingWitness().record(Forged(b"unsafe"))

    def test_sink_rejects_short_text_write_without_recording(self):
        sink = _BudgetedCSVTextSink(ShortWriteStream(1))
        with self.assertRaises(OSError): sink.write("ABC")

    def test_sink_rejects_bool_text_write(self):
        sink = _BudgetedCSVTextSink(ShortWriteStream(True))
        with self.assertRaises(OSError): sink.write("X")

    def test_sink_accepts_valid_text_write_and_budget(self):
        sink = _BudgetedCSVTextSink(ShortWriteStream(3))
        self.assertEqual(sink.write("ABC"), 3)

    def test_end_to_end_multirow_unicode_bom(self):
        result = write_csv_report(self.target, ("id", "amount"), [{"id": "🧪", "amount": "42.10"}], str)
        self.assertEqual(result, self.target)
        self.assertEqual(self.target.read_bytes(), b"\xef\xbb\xbfid,amount\r\n" + "🧪".encode() + b",42.10\r\n")
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_corrupt_staged_bytes_prepublication_never_reach_output(self):
        original_fstat = os.fstat

        def corrupt(fd):
            status = original_fstat(fd)
            os.lseek(fd, -4, os.SEEK_END)
            os.write(fd, b"XXXX")
            return status

        with patch("fvs_suite.csv_stage_integrity.os.fstat", side_effect=corrupt):
            with self.assertRaises(OSError):
                write_csv_report(self.target, ("id", "amount"), [{"id": "A", "amount": "42.10"}], str)
        self.assertFalse(self.target.exists())
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_empty_data_rows_still_verify_header_and_bom(self):
        write_csv_report(self.target, ("id", "amount"), [], str)
        self.assertEqual(self.target.read_bytes(), b"\xef\xbb\xbfid,amount\r\n")


if __name__ == "__main__":
    unittest.main()
