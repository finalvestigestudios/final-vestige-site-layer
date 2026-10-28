"""Synthetic R8 archive regression tests; never use confidential account data."""
from __future__ import annotations
import csv
import json
from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fvs_suite import evidence_vault as vault
from fvs_suite import exception_review as review

PASSWORD = "correct horse battery staple: 2026"


class EvidenceVaultR8Tests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="fvs-evidence-r8-")
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.report = self.root / "grant-audit-exceptions-synthetic.csv"
        self.journal = self.root / "grant-audit-exceptions-synthetic.review.jsonl"
        self.write_report("grants")

    def write_report(self, product):
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            w = csv.writer(stream)
            if product == "grants":
                w.writerow(("id", "status", "amount"))
                w.writerow(("CLAIM-A", "split_allocation_review", "120.45"))
                w.writerow(("CLAIM-B", "matched", "20.00"))
            else:
                w.writerow(("po", "line", "status"))
                w.writerow(("PO-1", "1", "price_variance_above_policy"))
                w.writerow(("PO-2", "2", "matched"))

    def record(self, product="grants"):
        batch = review.read_cases(self.report, product)
        return review.append_review(
            self.report, product, self.journal,
            case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Human Reviewer", decision="needs_evidence",
            rationale="Obtain source approval and supporting documentation.")

    def seal(self, product="grants", password=PASSWORD):
        return vault.seal_evidence(self.report, product, self.journal, self.root, password)

    def test_sealed_grant_roundtrip_authenticated_and_no_plaintext_leak(self):
        self.record()
        original_report, original_journal = self.report.read_bytes(), self.journal.read_bytes()
        destination = self.seal()
        self.assertEqual(destination.suffix, ".fvault")
        blob = destination.read_bytes()
        self.assertTrue(blob.startswith(vault.MAGIC))
        self.assertNotIn(b"CLAIM-A", blob)
        self.assertNotIn(b"Human Reviewer", blob)
        self.assertNotIn(PASSWORD.encode(), blob)
        restored = vault.restore_evidence(destination, self.root, PASSWORD)
        self.assertEqual((restored / "exception-report.csv").read_bytes(), original_report)
        self.assertEqual((restored / "review-journal.jsonl").read_bytes(), original_journal)
        manifest = json.loads((restored / "sealed-evidence-manifest.json").read_text())
        self.assertEqual(manifest["review_event_count"], 1)
        self.assertEqual(manifest["product"], "grants")
        self.assertEqual(self.report.read_bytes(), original_report)
        self.assertEqual(self.journal.read_bytes(), original_journal)

    def test_no_review_journal_still_seals_report_without_approval(self):
        self.assertFalse(self.journal.exists())
        destination = self.seal()
        restored = vault.restore_evidence(destination, self.root, PASSWORD)
        self.assertTrue((restored / "exception-report.csv").exists())
        self.assertFalse((restored / "review-journal.jsonl").exists())
        self.assertFalse(self.journal.exists())
        self.assertEqual(json.loads((restored / "sealed-evidence-manifest.json").read_text())["review_event_count"], 0)

    def test_procurement_roundtrip(self):
        self.report = self.root / "procurement-three-way-synthetic.csv"
        self.write_report("procurement")
        self.record("procurement")
        archive = self.seal("procurement")
        output = vault.restore_evidence(archive, self.root, PASSWORD)
        self.assertEqual(review.read_cases(output / "exception-report.csv", "procurement").cases[0].flags,
                         "price_variance_above_policy")

    def test_wrong_passphrase_writes_nothing(self):
        archive = self.seal()
        before = set(self.root.iterdir())
        with self.assertRaisesRegex(ValueError, "Wrong passphrase or.*altered"):
            vault.restore_evidence(archive, self.root, "this is a different long password")
        self.assertEqual(set(self.root.iterdir()), before)

    def test_tamper_ciphertext_and_nonce_fail_without_files(self):
        archive = self.seal()
        for index in (-3, len(vault.MAGIC) + 17):
            original = archive.read_bytes()
            modified = bytearray(original)
            modified[index] ^= 1
            archive.write_bytes(modified)
            before = set(self.root.iterdir())
            with self.assertRaisesRegex(ValueError, "Wrong passphrase or.*altered"):
                vault.restore_evidence(archive, self.root, PASSWORD)
            self.assertEqual(set(self.root.iterdir()), before)
            archive.write_bytes(original)

    def test_truncated_header_fails_closed(self):
        archive = self.seal()
        archive.write_bytes(archive.read_bytes()[:len(vault.MAGIC) + 2])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            vault.restore_evidence(archive, self.root, PASSWORD)

    def test_wrong_format_and_weak_passphrase_rejected(self):
        with self.assertRaisesRegex(ValueError, "16 to 1024"):
            self.seal(password="short")
        fake = self.root / "wrong.zip"
        fake.write_bytes(b"data")
        with self.assertRaisesRegex(ValueError, r"\.fvault"):
            vault.restore_evidence(fake, self.root, PASSWORD)
        self.assertFalse(list(self.root.glob("*.fvault")))

    def test_stale_report_with_existing_review_refused(self):
        self.record()
        original = self.report.read_text(encoding="utf-8-sig")
        self.report.write_text(original.replace("120.45", "120.46"), encoding="utf-8-sig")
        with self.assertRaisesRegex(ValueError, "different report snapshot"):
            self.seal()
        self.assertFalse(list(self.root.glob("*.fvault")))

    def test_corrupt_journal_refused(self):
        self.record()
        original = self.journal.read_text(encoding="utf-8")
        self.journal.write_text(original.replace("needs_evidence", "reviewed"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.seal()
        self.assertFalse(list(self.root.glob("*.fvault")))

    def test_collision_preserves_prior_vault(self):
        with mock.patch.object(vault.secrets, "token_hex", return_value="0000000000"), \
             mock.patch.object(vault, "datetime") as fixed_clock:
            fixed_clock.now.return_value = datetime(2026, 10, 28, 1, 0, tzinfo=timezone.utc)
            first = self.seal()
            original = first.read_bytes()
            with self.assertRaises(FileExistsError):
                self.seal()
        self.assertEqual(first.read_bytes(), original)

    def test_source_symlink_is_rejected(self):
        alternate = self.root / "linked.csv"
        try:
            alternate.symlink_to(self.report)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not supported")
        with self.assertRaises(ValueError):
            vault.seal_evidence(alternate, "grants", self.journal, self.root, PASSWORD)

    def test_decrypt_creates_distinct_folders_without_overwrite(self):
        archive = self.seal()
        first = vault.restore_evidence(archive, self.root, PASSWORD)
        second = vault.restore_evidence(archive, self.root, PASSWORD)
        self.assertNotEqual(first, second)
        self.assertEqual((first / "exception-report.csv").read_bytes(), self.report.read_bytes())
        self.assertEqual((second / "exception-report.csv").read_bytes(), self.report.read_bytes())


if __name__ == "__main__":
    unittest.main()
