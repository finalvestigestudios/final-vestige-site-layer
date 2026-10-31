"""R80: test raw Unicode-control validation before human-review whitespace trimming.

Synthetic/offline fixtures only; Windows executable behavior is not attested.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import exception_review as review

TRIMMED_CONTROLS = (
    ("tab", "\t"), ("CR", "\r"), ("LF", "\n"), ("vertical tab", "\v"),
    ("form feed", "\f"), ("record separator", "\x1e"),
    ("next line", "\u0085"), ("line separator", "\u2028"),
    ("paragraph separator", "\u2029"),
)


class PremiumReviewTrimBoundaryR80(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r80-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "exceptions.csv"
        self.journal = self.root / "human-review.jsonl"

    def batch(self, product):
        with self.report.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            if product == "grants":
                writer.writerows((("id", "status"), ("CLM-1", "variance_review")))
            else:
                writer.writerows((("po", "line", "status"),
                                  ("PO-1", "2", "quantity_variance_review")))
        return review.read_cases(self.report, product)

    def append(self, batch, **changes):
        args = dict(case_id=batch.cases[0].case_id,
                    expected_report_sha256=batch.report_sha256,
                    reviewer="Human Reviewer", decision="needs_evidence",
                    rationale="Inspect supporting documents before any payment.")
        args.update(changes)
        return review.append_review(self.report, batch.product, self.journal, **args)

    def assert_no_write(self):
        self.assertFalse(self.journal.exists())
        self.assertFalse(Path(str(self.journal) + ".lock").exists())
        self.assertFalse(list(self.root.glob("review-register-*.csv")))

    def test_reviewer_prefix_raw_controls(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text(ch + "Human Reviewer", "Reviewer", 2, 80)

    def test_reviewer_suffix_raw_controls(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text("Human Reviewer" + ch, "Reviewer", 2, 80)

    def test_rationale_prefix_raw_controls(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text(ch + "Inspect evidence before a decision.", "Rationale", 12, 2000)

    def test_rationale_suffix_raw_controls(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text("Inspect evidence before a decision." + ch,
                                 "Rationale", 12, 2000)

    def test_controls_with_outer_spaces_not_silently_trimmed(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                for sample in ("  " + ch + "Human Reviewer  ",
                               "  Human Reviewer" + ch + "  "):
                    with self.assertRaisesRegex(ValueError, "hidden or control"):
                        review._text(sample, "Reviewer", 2, 80)

    def test_existing_internal_control_guard_remains(self):
        for label, ch in TRIMMED_CONTROLS:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text("Human" + ch + "Reviewer", "Reviewer", 2, 80)

    def test_plain_outer_spaces_still_trim(self):
        self.assertEqual(review._text("  José Reviewer  ", "Reviewer", 2, 80),
                         "José Reviewer")

    def test_multilingual_characters_and_combining_accents_still_work(self):
        self.assertEqual(review._text("A\u00a0e\u0301", "Reviewer", 2, 80),
                         "A\u00a0e\u0301")

    def test_length_and_type_still_enforced(self):
        with self.assertRaisesRegex(ValueError, "must be text"):
            review._text(42, "Reviewer", 2, 80)
        for sample in ("", "A", "B" * 81):
            with self.subTest(sample=repr(sample)):
                with self.assertRaises(ValueError):
                    review._text(sample, "Reviewer", 2, 80)

    def test_error_does_not_echo_private_identity(self):
        secret = "PRIVATE_SYNTHETIC_CLIENT_IDENTIFIER"
        with self.assertRaises(ValueError) as problem:
            review._text(secret + "\n", "Reviewer", 2, 80)
        self.assertNotIn(secret, str(problem.exception))
        self.assertIn("Reviewer", str(problem.exception))

    def test_both_products_reject_raw_reviewer_controls_before_write(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                before = self.report.read_bytes()
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    self.append(batch, reviewer="\tHuman Reviewer")
                self.assertEqual(before, self.report.read_bytes())
                self.assert_no_write()

    def test_both_products_reject_raw_rationale_controls_before_write(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    self.append(batch, rationale="Inspect source evidence before a decision.\n")
                self.assert_no_write()

    def test_both_products_reject_rehashed_boundary_controls_on_read_export(self):
        for product in ("grants", "procurement"):
            for field, injected in (("reviewer", "Human Reviewer\t"),
                                    ("rationale", "\nInspect source evidence before a decision.")):
                with self.subTest(product=product, field=field):
                    batch = self.batch(product)
                    event = self.append(batch)
                    event[field] = injected
                    event["event_hash"] = review._hex_hash(
                        review._json({name: event[name] for name in review.FIELDS}))
                    self.journal.write_bytes(review._json(event) + b"\n")
                    original = self.journal.read_bytes()
                    with self.assertRaisesRegex(ValueError, "hidden or control"):
                        review.read_journal(self.journal, batch)
                    with self.assertRaises(ValueError):
                        review.export_register(self.report, product, self.journal, self.root)
                    self.assertEqual(original, self.journal.read_bytes())
                    self.assertFalse(list(self.root.glob("review-register-*.csv")))
                    self.journal.unlink()

    def test_both_products_accept_plain_review_with_trimmed_spaces(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                event = self.append(batch, reviewer="  Human Reviewer  ",
                                    rationale="  Inspect source evidence before a decision.  ")
                self.assertEqual(event["reviewer"], "Human Reviewer")
                self.assertEqual(event["rationale"], "Inspect source evidence before a decision.")
                self.assertEqual(review.read_journal(self.journal, batch), [event])
                self.journal.unlink()


if __name__ == "__main__":
    unittest.main()
