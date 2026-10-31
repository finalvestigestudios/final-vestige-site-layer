"""R79: premium human-review text custody; all files and identities synthetic.

These are source/regression tests, not an attestation of Windows executables.
"""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unicodedata
import unittest
from pathlib import Path

from fvs_suite import exception_review as review


# Important: these are Python source escapes, not copy/pasted invisible glyphs.
UNSAFE = (
    ("C0 newline", "\n"),
    ("C0 tab", "\t"),
    ("C1 next-line", "\u0085"),
    ("C1 control", "\u009b"),
    ("RTL override", "\u202e"),
    ("LTR override", "\u202d"),
    ("bidi isolate", "\u2066"),
    ("bidi pop", "\u2069"),
    ("right-to-left mark", "\u200f"),
    ("zero-width space", "\u200b"),
    ("zero-width joiner", "\u200d"),
    ("word joiner", "\u2060"),
    ("BOM", "\ufeff"),
    ("line separator", "\u2028"),
    ("paragraph separator", "\u2029"),
    ("combining grapheme joiner", "\u034f"),
    ("Mongolian selector", "\u180b"),
    ("emoji variation selector", "\ufe0f"),
    ("supplementary variation selector", "\U000e0100"),
    ("lone surrogate", "\ud800"),
)


class PremiumReviewUnicodeCustodyR79(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r79-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "synthetic-exceptions.csv"
        self.journal = self.root / "human-review.jsonl"

    def batch(self, product):
        with self.report.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            if product == "grants":
                writer.writerow(("id", "status"))
                writer.writerow(("CLAIM-1", "amount_variance_review"))
            else:
                writer.writerow(("po", "line", "status"))
                writer.writerow(("PO-1", "3", "quantity_variance_review"))
        return review.read_cases(self.report, product)

    def append(self, batch, **overrides):
        params = dict(
            case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Human Reviewer",
            decision="needs_evidence",
            rationale="Verify original documents before any financial action.",
        )
        params.update(overrides)
        return review.append_review(
            self.report, batch.product, self.journal, **params)

    def assert_no_review_write(self):
        self.assertFalse(self.journal.exists())
        self.assertFalse(Path(str(self.journal) + ".lock").exists())
        self.assertFalse(list(self.root.glob("review-register-*.csv")))

    def test_hidden_characters_rejected_in_reviewer(self):
        for label, character in UNSAFE:
            with self.subTest(character=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text("A" + character + "Reviewer", "Reviewer", 2, 80)

    def test_hidden_characters_rejected_in_rationale(self):
        for label, character in UNSAFE:
            with self.subTest(character=label):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review._text(
                        "Supporting" + character + " evidence required for review.",
                        "Rationale", 12, 2000)

    def test_accepted_multilingual_letters_unchanged(self):
        examples = ("Élodie Méndez", "王 小明", "أحمد منصور", "Μαρία Δημητρίου",
                    "Renée O'Connor", "Decomposed e\u0301 name")
        for name in examples:
            with self.subTest(name=name):
                self.assertEqual(review._text(name, "Reviewer", 2, 80), name)

    def test_review_narrative_preserves_plain_multilingual_text(self):
        narratives = (
            "Pièce justificative reçue; vérifier les montants.",
            "書類を確認し、支払承認は別途判断する。",
            "בדיקת המסמכים נדרשת לפני תשלום.",
            "Reviewed 2.50 and 3.75; no auto-approval.",
        )
        for note in narratives:
            with self.subTest(note=note):
                self.assertEqual(review._text(note, "Rationale", 12, 2000), note)

    def test_valid_text_is_trimmed_without_unicode_normalization(self):
        self.assertEqual(review._text("  José  ", "Reviewer", 2, 80), "José")
        self.assertNotEqual("é", "e\u0301")
        self.assertEqual(review._text("e\u0301 audit", "Reviewer", 2, 80), "e\u0301 audit")

    def test_ordinary_non_ascii_spacing_inside_text_is_not_deleted(self):
        self.assertEqual(review._text("A\u00a0B", "Reviewer", 2, 80), "A\u00a0B")

    def test_existing_minimum_length_and_maximum_limits_stay_enforced(self):
        for invalid in ("", "X", "A" * 81):
            with self.subTest(value=repr(invalid)):
                with self.assertRaises(ValueError):
                    review._text(invalid, "Reviewer", 2, 80)
        with self.assertRaisesRegex(ValueError, "must be text"):
            review._text(42, "Reviewer", 2, 80)

    def test_reject_surrogate_before_json_encoding(self):
        with self.assertRaisesRegex(ValueError, "hidden or control"):
            review._text("Reviewer\udfff Name", "Reviewer", 2, 80)

    def test_unicode_format_category_is_disallowed(self):
        for character in ("\u200b", "\u202e", "\u2060", "\ufeff"):
            with self.subTest(character=hex(ord(character))):
                self.assertEqual(unicodedata.category(character), "Cf")
                self.assertTrue(review._unsafe_review_character(character))

    def test_combining_accents_allowed_but_invisible_variants_rejected(self):
        self.assertFalse(review._unsafe_review_character("\u0301"))
        for character in ("\u034f", "\ufe0f", "\U000e0100", "\u180b"):
            with self.subTest(character=hex(ord(character))):
                self.assertTrue(review._unsafe_review_character(character))

    def test_both_premium_apps_reject_invalid_reviewer_without_writing(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                source = self.report.read_bytes()
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    self.append(batch, reviewer="Manager\u202e Operator")
                self.assertEqual(self.report.read_bytes(), source)
                self.assert_no_review_write()

    def test_both_premium_apps_reject_hidden_rationale_without_writing(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    self.append(batch, rationale="Need\u200b to verify original receipts.")
                self.assert_no_review_write()

    def test_hash_valid_forged_journal_with_hidden_reviewer_fails_closed(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                event = self.append(batch)
                event["reviewer"] = "Auditor\u202e Supervisor"
                event["event_hash"] = review._hex_hash(
                    review._json({field: event[field] for field in review.FIELDS}))
                self.journal.write_bytes(review._json(event) + b"\n")
                original_journal = self.journal.read_bytes()
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review.read_journal(self.journal, batch)
                with self.assertRaises(ValueError):
                    review.export_register(self.report, product, self.journal, self.root)
                self.assertEqual(self.journal.read_bytes(), original_journal)
                self.assertFalse(list(self.root.glob("review-register-*.csv")))
                self.journal.unlink()

    def test_hash_valid_forged_journal_with_hidden_rationale_fails_closed(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                event = self.append(batch)
                event["rationale"] = "Verify supporting\u200d invoices before payment."
                event["event_hash"] = review._hex_hash(
                    review._json({field: event[field] for field in review.FIELDS}))
                self.journal.write_bytes(review._json(event) + b"\n")
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review.read_journal(self.journal, batch)
                self.journal.unlink()

    def test_valid_review_events_remain_readable_for_both_premium_apps(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.batch(product)
                before = self.report.read_bytes()
                event = self.append(
                    batch, reviewer="Élodie Méndez",
                    rationale="Pièce reçue; confirm with supporting documents.")
                self.assertEqual(review.read_journal(self.journal, batch), [event])
                self.assertEqual(self.report.read_bytes(), before)
                self.assertEqual(event["decision"], "needs_evidence")
                self.journal.unlink()

    def test_all_failures_keep_privacy_no_user_value_echo(self):
        secret = "CLIENT_2047_BENEFICIARY_PRIVATE"
        with self.assertRaises(ValueError) as trapped:
            review._text(secret + "\u202e", "Reviewer", 2, 80)
        self.assertNotIn(secret, str(trapped.exception))
        self.assertIn("Reviewer", str(trapped.exception))


if __name__ == "__main__":
    unittest.main()
