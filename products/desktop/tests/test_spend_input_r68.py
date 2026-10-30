"""R68 focused SpendMap reusable-input safety tests; synthetic data only."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import math
import re
import unittest

from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import MAX_SPEND_ROWS, validated_spend_rows

SHA = "1" * 64
SECRET = "account=987654321\n\x1b[31mSECRET\x1b[0m"


def normalize(label: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", label.upper())


def parse_amount(raw: str) -> Decimal:
    return Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(amount: Decimal) -> str:
    return format(amount.quantize(Decimal("0.01")), ".2f")


def row(n=2, *, vendor="ACME", amount="10.00", date_text="2026-01-01", category="Parts"):
    return {"row": str(n), "vendor": vendor, "amount": amount,
            "date": date_text, "category": category}


def run(rows, **callbacks):
    return summarize_spend(rows, source_sha256=SHA,
                           normalize_vendor=callbacks.get("vendor", normalize),
                           parse_date=callbacks.get("day", date.fromisoformat),
                           parse_money=callbacks.get("money", parse_amount),
                           format_money=fmt)


class SpendInputR68(unittest.TestCase):
    def fail_private(self, rows, *, fragment="", **kwargs):
        with self.assertRaises(ValueError) as caught:
            run(rows, **kwargs)
        error = str(caught.exception)
        self.assertNotIn(SECRET, error)
        self.assertNotIn("987654321", error)
        self.assertNotIn("\x1b", error)
        if fragment:
            self.assertIn(fragment, error)

    def test_empty_valid_input(self):
        self.assertEqual(run([]), [])

    def test_plain_compatibility_row(self):
        item = run([row()])[0]
        self.assertEqual((item["amount"], item["source_rows"], item["source_sha256"]),
                         ("10.00", "2", SHA))

    def test_collision_and_monthly_spike_unchanged(self):
        rows = [row(i+2, amount="10.00", date_text=f"2026-{i+1:02d}-01")
                for i in range(3)]
        rows.append(row(5, vendor="A-CME", amount="20.00", date_text="2026-04-01"))
        report = run(rows)
        self.assertEqual(report[-1]["flag"],
                         "review_spike;normalized_vendor_collision_review")
        self.assertEqual(report[-1]["baseline_median"], "10.00")
        self.assertEqual(report[-1]["history_months"], "3")
        self.assertEqual(report[-1]["source_vendor_labels"], "A-CME")
        self.assertEqual(report[-1]["source_rows"], "5")

    def test_exact_half_cent_median_preserved(self):
        values = ("10.00", "10.01", "10.00", "10.02", "20.01")
        rows = [row(i+2, amount=value, date_text=f"2026-{i+1:02d}-01")
                for i, value in enumerate(values)]
        self.assertEqual(run(rows)[-1]["baseline_median"], "10.005")

    def test_refunds_have_exact_decimal_total(self):
        report = run([row(2, amount="0.10"), row(3, amount="0.20"),
                      row(4, amount="-0.05")])
        self.assertEqual(report[0]["amount"], "0.25")

    def test_original_source_order_not_renumbered(self):
        self.assertEqual(run([row(9), row(2), row(20)])[0]["source_rows"], "9;2;20")

    def test_malformed_physical_rows_rejected(self):
        for invalid in (None, 2, True, "", "0", "1", "02", "+2", " 2", "2\n" + SECRET,
                        "٢", "²", "2.0", "2e0", "99999999999"):
            with self.subTest(row=repr(invalid)):
                self.fail_private([dict(row(), row=invalid)],
                                  fragment="canonical physical CSV row")

    def test_duplicate_physical_row_rejected_without_report(self):
        self.fail_private([row(), row()], fragment="Duplicate spend physical CSV row")

    def test_duplicate_reference_even_when_record_data_changes(self):
        self.fail_private([row(2), row(2, amount="100")], fragment="Duplicate")

    def test_list_required(self):
        self.fail_private(iter([row()]), fragment="must be a list")

    def test_row_count_limit_before_parsing(self):
        self.assertEqual(MAX_SPEND_ROWS, 200_000)
        self.fail_private([row()] * (MAX_SPEND_ROWS + 1),
                          fragment="Too many spend source records")

    def test_record_mapping_shape(self):
        for invalid in (None, [], "not-a-record", 123):
            with self.subTest(value=repr(invalid)):
                self.fail_private([invalid], fragment="record must be a mapping")

    def test_raw_fields_must_be_text(self):
        for field, invalid in (("vendor", None), ("vendor", 2), ("date", False),
                               ("amount", 1.25), ("amount", Decimal("1.2")),
                               ("category", True), ("category", None)):
            with self.subTest(field=field, invalid=repr(invalid)):
                self.fail_private([dict(row(), **{field: invalid})],
                                  fragment=f"Spend {field} must be imported text")

    def test_missing_text_fields(self):
        for field in ("vendor", "date", "amount"):
            with self.subTest(field=field):
                entry = row()
                del entry[field]
                self.fail_private([entry], fragment=f"Spend {field} must be imported text")

    def test_legacy_missing_category_is_uncategorized(self):
        entry = row()
        del entry["category"]
        self.assertEqual(run([entry])[0]["category"], "Uncategorized")

    def test_empty_category_is_uncategorized(self):
        self.assertEqual(run([row(category="")])[0]["category"], "Uncategorized")

    def test_blank_normalized_vendor_preserves_r59_error(self):
        self.fail_private([row(vendor="!!!")], fragment="Blank vendor at row 2")

    def test_malformed_normalized_keys_rejected(self):
        for key in (None, 123, "acme", "A-CME", "A CME", "ÅCME", "A\x00", "A\n" + SECRET):
            with self.subTest(key=repr(key)):
                self.fail_private([row()], vendor=lambda _: key,
                                  fragment="Invalid normalized vendor key")

    def test_vendor_normalizer_failure_is_redacted(self):
        def bad(_):
            raise RuntimeError(SECRET)
        self.fail_private([row(vendor=SECRET)], vendor=bad,
                          fragment="Invalid vendor at physical row 2")

    def test_date_parser_failure_is_redacted(self):
        def bad(_):
            raise ValueError(SECRET)
        self.fail_private([row(date_text=SECRET)], day=bad,
                          fragment="Invalid spend date at physical row 2")

    def test_date_parser_must_return_actual_date(self):
        for invalid in (None, "2026-01-01", datetime(2026,1,1), 20260101, True):
            with self.subTest(value=repr(invalid)):
                self.fail_private([row()], day=lambda _: invalid,
                                  fragment="Spend date must be a calendar date")

    def test_money_parser_failure_is_redacted(self):
        def bad(_):
            raise ValueError(SECRET)
        self.fail_private([row(amount=SECRET)], money=bad,
                          fragment="Invalid spend amount at physical row 2")

    def test_money_parser_rejects_float_nonfinite_and_nondecimal(self):
        for invalid in (10, 1.5, "10", True, None, Decimal("NaN"),
                        Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")):
            with self.subTest(value=repr(invalid)):
                self.fail_private([row()], money=lambda _: invalid,
                                  fragment="finite exact Decimal")

    def test_no_partial_results_after_late_bad_record(self):
        self.fail_private([row(), row(3), row(4, amount=SECRET)],
                          fragment="Invalid spend amount at physical row 4")

    def test_source_digest_rejected_without_data_echo(self):
        with self.assertRaises(ValueError):
            summarize_spend([row()], source_sha256="ff\n" + SECRET,
                            normalize_vendor=normalize, parse_date=date.fromisoformat,
                            parse_money=parse_amount, format_money=fmt)

    def test_same_input_is_deterministic_and_not_mutated(self):
        rows = [row(2), row(3, vendor="A-CME", amount="1.00")]
        frozen = [dict(x) for x in rows]
        self.assertEqual(run(rows), run(rows))
        self.assertEqual(rows, frozen)

    def test_direct_helper_parses_each_input_once(self):
        calls = {"vendor": 0, "date": 0, "money": 0}
        def tracked_vendor(raw):
            calls["vendor"] += 1
            return normalize(raw)
        def tracked_date(raw):
            calls["date"] += 1
            return date.fromisoformat(raw)
        def tracked_money(raw):
            calls["money"] += 1
            return parse_amount(raw)
        prepared = list(validated_spend_rows([row(2), row(3)],
                           normalize_vendor=tracked_vendor,
                           parse_date=tracked_date, parse_money=tracked_money))
        self.assertEqual(calls, {"vendor": 2, "date": 2, "money": 2})
        self.assertEqual(prepared[0][1:], ("ACME", "2026-01", "Parts", Decimal("10.00")))

    def test_month_aggregation_deterministic_across_categories(self):
        rows = [row(2, amount="3.01", category="Parts"),
                row(3, amount="2.02", category="Travel")]
        report = run(rows)
        self.assertEqual({r["category"]:r["amount"] for r in report},
                         {"Parts": "3.01", "Travel": "2.02"})
        self.assertEqual({r["vendor_month_total"] for r in report}, {"5.03"})


if __name__ == "__main__":
    unittest.main()
