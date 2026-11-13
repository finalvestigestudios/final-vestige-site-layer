"""R97: human-visible source citations in LedgerDiff and both GrantAudit modes.

All examples are synthetic. Escaped report labels are HUMAN DISPLAY strings;
original verified inputs and SHA-256 remain the authoritative source evidence.
"""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
from pathlib import Path
import tempfile
import unittest

from fvs_suite.review import (
    labels_for_report,
    normalized_collision,
    raw_values,
    reconciliation_status,
)


class SourceLabelVisibilityR97(unittest.TestCase):
    @staticmethod
    def labels(*values, field="id"):
        return labels_for_report([{field: value} for value in values], field)

    def test_plain_identifier_unchanged(self):
        self.assertEqual(self.labels("PO-101"), "PO-101")

    def test_order_compatible_with_existing_casefold_sort(self):
        self.assertEqual(self.labels("z-2", "A-1", "a-2"), "A-1; a-2; z-2")

    def test_absent_and_empty_identifiers_remain_absent(self):
        self.assertEqual(self.labels("", ""), "")

    def test_literal_space_only_identifier_remains_visible_for_review(self):
        # R398 preserves original source spellings rather than trimming them.
        # A whitespace-only source is not an absent field or a safe match.
        self.assertEqual(self.labels("", " ", ""), r"\u0020")

    def test_repeated_label_deduplication(self):
        self.assertEqual(self.labels("A-1", "A-1"), "A-1")

    def test_semicolon_is_not_a_source_separator(self):
        self.assertEqual(self.labels("INV; 4"), r"INV\u003B 4")

    def test_multiple_labels_distinguish_original_semicolon(self):
        self.assertEqual(self.labels("AB;C", "XYZ"), r"AB\u003BC; XYZ")

    def test_source_literal_unicode_escape_stays_distinct(self):
        self.assertEqual(self.labels(r"INV\u202E4"), r"INV\\u202E4")

    def test_actual_bidi_is_visibly_escaped(self):
        self.assertEqual(self.labels("INV\u202e4"), r"INV\u202E4")

    def test_actual_bidi_and_typed_escape_remain_distinct(self):
        actual = self.labels("INV\u202e4")
        typed = self.labels(r"INV\u202E4")
        self.assertNotEqual(actual, typed)

    def test_carriage_return_inside_label_is_visible(self):
        self.assertEqual(self.labels("X\rY"), r"X\u000DY")

    def test_line_feed_inside_label_is_visible(self):
        self.assertEqual(self.labels("X\nY"), r"X\u000AY")

    def test_tab_inside_label_is_visible(self):
        self.assertEqual(self.labels("X\tY"), r"X\u0009Y")

    def test_nbsp_inside_program_label_is_visible(self):
        self.assertEqual(self.labels("GR\u00a0A", field="program"), r"GR\u00A0A")

    def test_braille_blank_is_not_invisible(self):
        self.assertEqual(self.labels("A\u2800B"), r"A\u2800B")

    def test_standard_variation_selector_is_visible(self):
        self.assertEqual(self.labels("A\ufe0fB"), r"A\uFE0FB")

    def test_supplementary_variation_selector_is_visible(self):
        self.assertEqual(self.labels("A\U000E0100B"), r"A\U000E0100B")

    def test_original_backslash_is_escaped(self):
        self.assertEqual(self.labels("INV\\A"), r"INV\\A")

    def test_mixed_separator_bidi_and_backslash(self):
        self.assertEqual(self.labels("A;\u202e\\B"), r"A\u003B\u202E\\B")

    def test_inputs_remain_unmodified(self):
        rows = [{"id": "X;\u202e"}, {"id": r"\u202E"}]
        original = [dict(row) for row in rows]
        self.assertEqual(labels_for_report(rows, "id"),
                         labels_for_report(tuple(reversed(rows)), "id"))
        self.assertEqual(rows, original)

    def test_raw_values_preserve_matching_inputs(self):
        rows = [{"id": "A;B"}, {"id": "A\u202eB"}]
        original = raw_values(rows, "id")
        self.assertEqual(set(original), {"A;B", "A\u202eB"})
        self.assertTrue(normalized_collision(rows, "id"))
        self.assertIn(r"\u003B", labels_for_report(rows, "id"))

    def test_ascii_case_identity_logic_unchanged(self):
        rows = [{"id": "AbC"}, {"id": "aBc"}]
        self.assertFalse(normalized_collision(rows, "id"))
        self.assertEqual(self.labels("AbC", "aBc"), "AbC; aBc")

    def test_difference_still_triggers_human_review(self):
        left = [{"id": "INV-1"}]
        right = [{"id": "INV\u202e1"}]
        status = reconciliation_status(
            left, right, Decimal("7.00"), Decimal("7.00"),
            missing_left="missing_left", missing_right="missing_right")
        self.assertEqual(status, "normalized_id_review")

    def test_semicolon_identity_still_triggers_human_review(self):
        rows = [{"id": "A;1"}, {"id": "A1"}]
        self.assertTrue(normalized_collision(rows, "id"))

    def test_report_label_fields_use_same_display_rule(self):
        for field in ("id", "program", "ledger_reference",
                      "related_claim", "document_id"):
            with self.subTest(field=field):
                self.assertEqual(self.labels("A;\u202e1", field=field),
                                 r"A\u003B\u202E1")

    def test_10k_labels_deterministic(self):
        rows = [{"id": "INV-" + str(n).zfill(5)}
                for n in reversed(range(10_000))]
        first = labels_for_report(rows, "id")
        self.assertEqual(first, labels_for_report(reversed(rows), "id"))
        self.assertEqual(len(first.split("; ")), 10_000)
        self.assertTrue(first.startswith("INV-00000; INV-00001; "))


class SourceLabelFullPipelineR97(unittest.TestCase):
    """Repository integration tests; only meaningful inside a complete checkout."""

    @staticmethod
    def _write(path: Path, content: str):
        path.write_text(content, encoding="utf-8", newline="")
        return path.read_bytes()

    def test_ledger_full_csv_keeps_bytes_sha_and_review_labels(self):
        from fvs_suite import engine
        with tempfile.TemporaryDirectory(prefix="fvs-r97-ledger-") as tmp:
            root = Path(tmp)
            data = ("transaction_id,amount\n"
                    "A\u202e-1,1.00\n"
                    "B;2,2.00\n")
            left, right = root / "left.csv", root / "right.csv"
            originals = [self._write(p, data) for p in (left, right)]
            paths = engine.ledger_diff(str(left), str(right), str(root))
            self.assertEqual(len(paths), 1)
            with paths[0].open(encoding="utf-8-sig", newline="") as fh:
                report = list(csv.DictReader(fh))
            labels = {row["id"]: row for row in report}
            self.assertEqual(labels["A1"]["left_ids"], r"A\u202E-1")
            self.assertEqual(labels["B2"]["right_ids"], r"B\u003B2")
            self.assertEqual(labels["A1"]["status"], "matched")
            self.assertEqual(labels["A1"]["left_amount"], "1.00")
            self.assertEqual(labels["A1"]["right_amount"], "1.00")
            self.assertEqual(labels["A1"]["left_source_sha256"],
                             hashlib.sha256(originals[0]).hexdigest())
            self.assertEqual([left.read_bytes(), right.read_bytes()], originals)

    def test_grant_legacy_csv_and_manifest_preserve_originals(self):
        from fvs_suite import engine
        with tempfile.TemporaryDirectory(prefix="fvs-r97-grant-") as tmp:
            root = Path(tmp)
            inputs = (
                ("claims.csv",
                 "transaction_id,amount,program\nX\u202e1,1.00,GR;A\n"),
                ("ledger.csv",
                 "transaction_id,amount,program\nX\u202e1,1.00,GR;A\n"),
                ("budgets.csv", "program,budget\nGR;A,2.00\n"),
            )
            paths = [root / name for name, _ in inputs]
            originals = [self._write(root / name, content)
                         for name, content in inputs]
            output = engine.grant_audit(*(str(p) for p in paths), str(root))
            self.assertEqual(len(output), 3)
            report_file = next(p for p in output if p.name.startswith("grant-audit-exceptions"))
            budget_file = next(p for p in output if p.name.startswith("grant-budget-check"))
            with report_file.open(encoding="utf-8-sig", newline="") as fh:
                report = list(csv.DictReader(fh))
            with budget_file.open(encoding="utf-8-sig", newline="") as fh:
                budgets = list(csv.DictReader(fh))
            self.assertEqual(len(report), 1)
            self.assertEqual(report[0]["claim_ids"], r"X\u202E1")
            self.assertEqual(report[0]["ledger_ids"], r"X\u202E1")
            self.assertEqual(report[0]["claim_programs"], r"GR\u003BA")
            self.assertEqual(report[0]["status"], "matched")
            self.assertEqual(budgets[0]["source_programs"], r"GR\u003BA")
            self.assertTrue(any(p.name.startswith("evidence-manifest") for p in output))
            self.assertEqual([p.read_bytes() for p in paths], originals)

    def test_grant_linked_label_contract_retains_literal_source_escape(self):
        rows = [
            {"ledger_reference": "LED\u202e1", "related_claim": r"C\u003B"},
            {"ledger_reference": r"LED\u202E1", "related_claim": "C;B"},
        ]
        self.assertEqual(labels_for_report(rows, "ledger_reference"),
                         r"LED\\u202E1; LED\u202E1")
        self.assertEqual(labels_for_report(rows, "related_claim"),
                         r"C\u003BB; C\\u003B")


if __name__ == "__main__":
    unittest.main()
