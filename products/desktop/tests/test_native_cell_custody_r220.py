"""R220 native CSV evidence custody; synthetic fixtures only, offline, no premium assets."""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
from decimal import Decimal
from fvs_suite.csv_native_cell import native_report_text
from fvs_suite.atomic_reports import MAX_REPORT_CELL_CHARS

class Contract(unittest.TestCase):
 def test_native_str(self): self.assertEqual(native_report_text("=SUM(A1)"), "=SUM(A1)")
 def test_precise_decimal(self): self.assertEqual(native_report_text(Decimal('-123.4500')),'-123.4500')
 def test_negative_int(self): self.assertEqual(native_report_text(-123),'-123')
 def test_zero_decimal(self): self.assertEqual(native_report_text(Decimal('-0.00')),'-0.00')
 def test_big_but_bounded_str(self): self.assertEqual(len(native_report_text('A' * MAX_REPORT_CELL_CHARS)), MAX_REPORT_CELL_CHARS)
 def test_overlong_str(self):
  with self.assertRaisesRegex(ValueError,'size limit'): native_report_text('A' * (MAX_REPORT_CELL_CHARS+1))
 def test_huge_int(self):
  with self.assertRaisesRegex(ValueError,'Invalid native'): native_report_text(2**270)
 def test_int_boundary(self): self.assertEqual(native_report_text(2**268),str(2**268))
 def test_non_finite(self):
  for v in ('NaN','sNaN','Infinity','-Infinity'):
   with self.subTest(v=v),self.assertRaisesRegex(ValueError,'Invalid native'):native_report_text(Decimal(v))
 def test_float(self):
  with self.assertRaises(ValueError): native_report_text(0.1)
 def test_bool(self):
  with self.assertRaises(ValueError): native_report_text(True)
 def test_none(self):
  with self.assertRaises(ValueError): native_report_text(None)
 def test_bytes(self):
  with self.assertRaises(ValueError): native_report_text(b'=HYPERLINK(A1)')
 def test_unsafe_obj_never_str(self):
  class Fraud:
   calls=0
   def __str__(self):
    self.calls+=1
    return 'APPROVED'
  f=Fraud()
  with self.assertRaisesRegex(ValueError,'Invalid native'):native_report_text(f)
  self.assertEqual(f.calls,0)
 def test_str_subclass_never_coerced(self):
  class Fraud(str):
   calls=0
   def __str__(self):
    self.calls+=1
    return 'APPROVED'
  f=Fraud('=HYPERLINK(A1)')
  with self.assertRaises(ValueError):native_report_text(f)
  self.assertEqual(f.calls,0)
 def test_int_subclass_never_coerced(self):
  class Fraud(int):
   def __str__(self): raise RuntimeError('SECRET')
  with self.assertRaisesRegex(ValueError,'Invalid native'):native_report_text(Fraud(12))
 def test_decimal_subclass_never_coerced(self):
  class Fraud(Decimal):
   def __str__(self): raise RuntimeError('SECRET')
  with self.assertRaisesRegex(ValueError,'Invalid native'):native_report_text(Fraud('1.20'))
 def test_private_error_context_empty(self):
  class Fraud:
   def __str__(self):raise ValueError('CLIENT_000_SECRET')
  try:native_report_text(Fraud())
  except ValueError as ex:
   self.assertEqual(str(ex),'Invalid native CSV report cell')
   self.assertIsNone(ex.__context__)
  else:self.fail('did not reject')


class EngineIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r220-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _files(self):
        return list(self.root.iterdir())

    def _rows(self, report):
        with report.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_default_sanitizer_rejects_forged_text_subclass(self):
        from fvs_suite import engine
        calls = []
        class Forged(str):
            def __str__(self):
                calls.append("forged")
                return "APPROVED"
        with self.assertRaisesRegex(ValueError, "Invalid native CSV report cell"):
            engine.safe_cell(Forged("=HYPERLINK(A1)"))
        self.assertEqual(calls, [])

    def test_default_sanitizer_never_invokes_forged_object(self):
        from fvs_suite import engine
        calls = []
        class Forged:
            def __str__(self):
                calls.append("forged")
                return "PAID"
        with self.assertRaisesRegex(ValueError, "Invalid native CSV report cell"):
            engine.safe_cell(Forged())
        self.assertEqual(calls, [])

    def test_default_save_forged_second_row_rolls_back(self):
        from fvs_suite import engine
        class Forged:
            def __str__(self):
                raise RuntimeError("PRIVATE_CLIENT_ID_IN_EXCEPTION")
        def rows():
            yield {"id": "legit", "amount": Decimal("-0.01")}
            yield {"id": Forged(), "amount": Decimal("0.10")}
        with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed") as ctx:
            engine.save(self.root, "evidence", ("id", "amount"), rows())
        self.assertNotIn("PRIVATE_CLIENT_ID", str(ctx.exception))
        self.assertIsNone(ctx.exception.__context__)
        self.assertEqual(self._files(), [])

    def test_default_save_ignored_extra_object_must_fail(self):
        from fvs_suite import engine
        class Forged:
            def __str__(self):
                return "AUDIT_APPROVED"
        with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed"):
            engine.save(self.root, "extra", ("id",), [{"id": "A", "extra": Forged()}])
        self.assertEqual(self._files(), [])

    def test_default_save_rejects_float_and_bool(self):
        from fvs_suite import engine
        for amount in (0.1, True):
            with self.subTest(amount=amount):
                with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed"):
                    engine.save(self.root, "money", ("amount",), [{"amount": amount}])
                self.assertEqual(self._files(), [])

    def test_default_save_keeps_money_and_formula_custody(self):
        from fvs_suite import engine
        report = engine.save(self.root, "safe", ("id", "amount", "count"),
                             [{"id": "＝SUM(A1)", "amount": Decimal("-0.0100"), "count": 2}])
        self.assertEqual(self._rows(report),
                         [{"id": "'＝SUM(A1)", "amount": "-0.0100", "count": "2"}])
        self.assertTrue(report.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_existing_destination_is_not_overwritten(self):
        from fvs_suite import engine
        existing = self.root / "private.csv"
        existing.write_bytes(b"PRIOR_AUDIT_EVIDENCE")
        with patch("fvs_suite.engine.outpath", return_value=existing):
            with self.assertRaises(FileExistsError):
                engine.save(self.root, "private", ("id",), [{"id": "A"}])
        self.assertEqual(existing.read_bytes(), b"PRIOR_AUDIT_EVIDENCE")
        self.assertEqual(self._files(), [existing])


if __name__ == "__main__":
    unittest.main()
