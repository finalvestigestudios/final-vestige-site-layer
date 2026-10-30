"""R67 direct-engine exact-money and physical-row boundary tests (synthetic)."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
import unittest
from unittest.mock import patch

from fvs_suite import invoice_match
from fvs_suite.invoice_match import candidate_pairs


class InvoiceBoundaryR67(unittest.TestCase):
    @staticmethod
    def row(line=2, inv="A", amt=Decimal("10.00"), dt=date(2026, 1, 1), vendor="ACME"):
        return {"row": str(line), "v": vendor, "inv": inv, "amt": amt,
                "dt": dt, "vendor": vendor, "invoice_number": inv}

    def test_exact_pair_preserves_anchor_and_status(self):
        a, b = self.row(2), self.row(3)
        result = candidate_pairs([a, b])
        self.assertEqual([(x["row"], y["row"], s) for x, y, s, _ in result],
                         [("2", "3", "exact_invoice_key")])

    def test_near_window_includes_day_seven_and_excludes_day_eight(self):
        a = self.row(2, "A")
        b = self.row(3, "B", dt=date(2026, 1, 8))
        c = self.row(4, "C", dt=date(2026, 1, 9))
        pairs = candidate_pairs([c, a, b])
        self.assertEqual([(x["row"], y["row"]) for x, y, *_ in pairs],
                         [("2", "3"), ("3", "4")])

    def test_half_cent_preserved_without_float_coercion(self):
        a = self.row(2, "A", Decimal("0.005"))
        b = self.row(3, "B", Decimal("0.005"))
        self.assertEqual(len(candidate_pairs([a, b])), 1)
        self.assertEqual(a["amt"], Decimal("0.005"))

    def test_floating_point_and_booleans_rejected(self):
        for bad in (10.0, float("nan"), float("inf"), True, False, 10, "10.00"):
            with self.subTest(value=type(bad).__name__):
                with self.assertRaisesRegex(ValueError, "finite exact Decimal"):
                    candidate_pairs([self.row(amt=bad)])

    def test_nonfinite_decimal_rejected(self):
        for bad in (Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")):
            with self.subTest(value=str(bad).replace("NaN", "nan")):
                with self.assertRaisesRegex(ValueError, "finite exact Decimal"):
                    candidate_pairs([self.row(amt=bad)])

    def test_missing_amount_rejected_without_private_values(self):
        item = self.row()
        del item["amt"]
        with self.assertRaisesRegex(ValueError, "finite exact Decimal"):
            candidate_pairs([item])

    def test_datetime_not_accepted_as_calendar_date(self):
        for bad in (datetime(2026, 1, 1), "2026-01-01", None, 0):
            with self.subTest(value=type(bad).__name__), self.assertRaisesRegex(ValueError, "calendar date"):
                candidate_pairs([self.row(dt=bad)])

    def test_bad_row_citations_rejected(self):
        for bad in ("1", "0", "00", "02", "+2", "-2", "2.0", " 2", "2 ",
                    "２", "²", "2\nPRIVATE", "A", "1"*20, ""):
            with self.subTest(value=bad), self.assertRaisesRegex(ValueError, "physical CSV row"):
                candidate_pairs([self.row(line=bad)])

    def test_missing_physical_row_is_rejected(self):
        item = self.row()
        del item["row"]
        with self.assertRaisesRegex(ValueError, "physical CSV row"):
            candidate_pairs([item])

    def test_duplicate_physical_row_rejected_even_if_invoice_differs(self):
        a = self.row(2, "A")
        b = self.row(2, "B")
        with self.assertRaisesRegex(ValueError, "Duplicate invoice physical CSV row"):
            candidate_pairs([a, b])

    def test_keys_reject_noncanonical_or_missing_identifiers(self):
        for field in ("v", "inv"):
            for bad in (None, "", "A-B", "a", "Ａ", "A B", "A\nPRIVATE", True, 5, []):
                with self.subTest(field=field, bad=repr(bad)):
                    item = self.row()
                    item[field] = bad
                    with self.assertRaisesRegex(ValueError, "normalized ASCII"):
                        candidate_pairs([item])

    def test_key_missing_fails_closed(self):
        for field in ("v", "inv"):
            item = self.row()
            del item[field]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "normalized ASCII"):
                candidate_pairs([item])

    def test_bad_record_type_fails_closed(self):
        for bad in (None, False, [], "private", 5):
            with self.subTest(bad=type(bad).__name__), self.assertRaisesRegex(ValueError, "source record"):
                candidate_pairs([bad])

    def test_bool_policy_controls_fail_closed(self):
        for bad in (True, False, 1.0, "7", -1, 366):
            with self.subTest(window=repr(bad)), self.assertRaisesRegex(ValueError, "window"):
                candidate_pairs([], window_days=bad)
        for bad in (True, False, 1.0, "100", 0, -1):
            with self.subTest(limit=repr(bad)), self.assertRaisesRegex(ValueError, "positive integer"):
                candidate_pairs([], max_candidates=bad)

    def test_empty_records_remain_empty(self):
        self.assertEqual(candidate_pairs([]), [])
        self.assertEqual(candidate_pairs(iter([])), [])

    def test_candidate_cap_remains_fail_closed(self):
        records = [self.row(i, chr(65 + i)) for i in range(2, 8)]
        with self.assertRaisesRegex(ValueError, "no incomplete report was saved"):
            candidate_pairs(records, max_candidates=2)

    def test_record_cap_works_for_generators_without_reading_extra(self):
        def records():
            for i in range(2, 7):
                yield self.row(i, chr(65 + i))
            raise AssertionError("generator should be stopped at limit")
        with patch.object(invoice_match, "MAX_RECORDS", 4):
            with self.assertRaisesRegex(ValueError, "Too many invoice source records"):
                candidate_pairs(records())

    def test_input_rows_not_mutated(self):
        rows = [self.row(2, "A"), self.row(3, "B")]
        before = deepcopy(rows)
        candidate_pairs(rows)
        self.assertEqual(rows, before)

    def test_privacy_message_does_not_reflect_untrusted_cells(self):
        item = self.row()
        item["inv"] = "PRIVATE_ACCOUNT_123\npassword"
        with self.assertRaises(ValueError) as ctx:
            candidate_pairs([item])
        self.assertNotIn("PRIVATE_ACCOUNT", str(ctx.exception))
        self.assertNotIn("password", str(ctx.exception))

    def test_validation_happens_before_any_candidates_returned(self):
        rows = [self.row(2, "A"), self.row(3, "B"), self.row(4, "C", amt=5.0)]
        with self.assertRaises(ValueError):
            candidate_pairs(rows)


if __name__ == "__main__":
    unittest.main()
