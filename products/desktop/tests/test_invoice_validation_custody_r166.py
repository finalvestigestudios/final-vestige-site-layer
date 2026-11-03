"""R166 Invoice Twin Scout: validate the owned source snapshot, never split-view dict.get.

Synthetic offline-only adversarial records; no private financial data or approval.
The public direct engine accepts dict subclasses, whose .get may disagree with
the stored mapping and therefore cannot be trusted for audit validation.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.invoice_match import candidate_pairs, review_flags


def source(row="2", v="ACME", inv="INV1", amt=Decimal("12.00"), dt=date(2026, 1, 1)):
    return {"row": row, "v": v, "inv": inv, "amt": amt, "dt": dt,
            "vendor": "Acme Original", "invoice_number": "INV1"}


class SplitView(dict):
    """In-memory subclass that supplies forged answers to record.get()."""

    def __init__(self, held, claimed=None):
        super().__init__(held)
        self.claimed = dict(source()) if claimed is None else claimed
        self.get_calls = 0

    def get(self, key, default=None):
        self.get_calls += 1
        return self.claimed.get(key, default)


class ForbiddenGet(dict):
    def get(self, key, default=None):
        raise AssertionError("untrusted caller get() must not execute")


class InvoiceValidationCustodyR166(unittest.TestCase):
    def reject_held(self, message, **changes):
        held = source()
        held.update(changes)
        row = SplitView(held)
        with self.assertRaisesRegex(ValueError, message):
            candidate_pairs([row])
        self.assertEqual(row.get_calls, 0)
        return row

    def test_reject_unstored_malformed_physical_line(self):
        self.reject_held("canonical physical CSV row", row="not-a-line")

    def test_reject_unstored_header_line(self):
        self.reject_held("canonical physical CSV row", row="1")

    def test_reject_unstored_leading_zero_line(self):
        self.reject_held("canonical physical CSV row", row="02")

    def test_reject_unstored_unicode_digit_line(self):
        self.reject_held("canonical physical CSV row", row="２")

    def test_reject_unstored_too_large_line(self):
        self.reject_held("canonical physical CSV row", row="12345678901")

    def test_reject_duplicate_held_physical_rows(self):
        first = source(row="2")
        second = source(row="2", inv="INV2")
        fake = source(row="3", inv="INV2")
        row = SplitView(second, claimed=fake)
        with self.assertRaisesRegex(ValueError, "Duplicate invoice physical CSV row"):
            candidate_pairs([first, row])
        self.assertEqual(row.get_calls, 0)

    def test_reject_unstored_date_text(self):
        self.reject_held("parsed calendar date", dt="2026-01-01")

    def test_reject_unstored_datetime(self):
        self.reject_held("parsed calendar date", dt=datetime(2026, 1, 1))

    def test_reject_unstored_float_money(self):
        self.reject_held("finite exact Decimal", amt=12.0)

    def test_reject_unstored_nonfinite_money(self):
        self.reject_held("finite exact Decimal", amt=Decimal("NaN"))

    def test_reject_unstored_infinite_money(self):
        self.reject_held("finite exact Decimal", amt=Decimal("Infinity"))

    def test_reject_unstored_excess_money(self):
        self.reject_held("permitted range", amt=Decimal("1000000000001"))

    def test_reject_unstored_precision_money(self):
        self.reject_held("permitted precision", amt=Decimal("0.123456789"))

    def test_reject_unstored_vendor_case(self):
        self.reject_held("normalized ASCII", v="acme")

    def test_reject_unstored_vendor_unicode(self):
        self.reject_held("normalized ASCII", v="ACMÉ")

    def test_reject_unstored_invoice_punctuation(self):
        self.reject_held("normalized ASCII", inv="INV-1")

    def test_reject_unstored_empty_invoice(self):
        self.reject_held("normalized ASCII", inv="")

    def test_reject_unstored_missing_key(self):
        held = source()
        del held["v"]
        deceptive = SplitView(held)
        with self.assertRaisesRegex(ValueError, "normalized ASCII"):
            candidate_pairs([deceptive])
        self.assertEqual(deceptive.get_calls, 0)

    def test_valid_stored_row_ignores_forged_get(self):
        held = source()
        forged = source(row="garbled", v="lowercase", dt="bad")
        deceptive = SplitView(held, claimed=forged)
        self.assertEqual(candidate_pairs([deceptive]), [])
        self.assertEqual(deceptive.get_calls, 0)

    def test_no_get_side_effect_invoked(self):
        row = ForbiddenGet(source())
        self.assertEqual(candidate_pairs([row]), [])

    def test_two_row_pair_binds_stored_values(self):
        first = SplitView(source(), claimed=source(row="999", v="BETA", inv="OTHER"))
        second = SplitView(source(row="3", inv="INV2"), claimed=source(row="998"))
        pairs = candidate_pairs([first, second])
        self.assertEqual([(a["row"], b["row"], label) for a, b, label, _ in pairs],
                         [("2", "3", "review_possible_duplicate")])
        self.assertEqual((first.get_calls, second.get_calls), (0, 0))
        self.assertEqual(pairs[0][0]["amt"], Decimal("12.00"))

    def test_owned_copy_not_input_alias(self):
        first = SplitView(source())
        second = source(row="3", inv="INV2")
        pairs = candidate_pairs([first, second])
        self.assertIsNot(pairs[0][0], first)
        first["row"] = "777"
        first["amt"] = Decimal("0")
        self.assertEqual((pairs[0][0]["row"], pairs[0][0]["amt"]),
                         ("2", Decimal("12.00")))

    def test_private_bad_value_not_in_error(self):
        private_value = "PRIVATE-ACCOUNT-DO-NOT-LOG"
        held = source(v=private_value)
        with self.assertRaises(ValueError) as ctx:
            candidate_pairs([SplitView(held)])
        self.assertNotIn(private_value, str(ctx.exception))

    def test_hostile_decimal_context_remains_exact(self):
        first = SplitView(source(amt=Decimal("0.00000001")))
        second = source(row="3", inv="INV2", amt=Decimal("0.00000001"))
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            pairs = candidate_pairs([first, second])
        self.assertEqual([x["amt"] for x in pairs[0][:2]],
                         [Decimal("0.00000001")] * 2)

    def test_valid_normal_input_regression(self):
        first = source()
        second = source(row="3", inv="INV1", amt=Decimal("13.00"))
        pairs = candidate_pairs([first, second])
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][2], "exact_invoice_key")
        self.assertIn("amount_variance_review", review_flags(*pairs[0][:3]))

    def test_no_partial_result_on_late_spoof(self):
        rows = [source(), source(row="3", inv="INV2"),
                SplitView(source(row="invalid", inv="INV3"))]
        with self.assertRaisesRegex(ValueError, "canonical physical CSV row"):
            candidate_pairs(iter(rows))


if __name__ == "__main__":
    unittest.main()
