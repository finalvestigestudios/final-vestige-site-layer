"""R315 synthetic custody checks for both packaged premium smoke paths.

Exercises pathname substitution with the same bytes and valid manifest changes.
Full AES-GCM integration and actual Windows executable acceptance remain separate.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fvs_suite.vault_smoke_scope import check_scoped_vault_roundtrip

_DENIED = "Encrypted evidence does not match this premium review product"


class PackagedVaultCustodyR315(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="labs-r315-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.archive = self.root / "synthetic.fvault"
        self.archive.write_bytes(b"synthetic ciphertext only")
        self.report = self.root / "synthetic.csv"
        self.report.write_bytes(b"case,amount\nX,12.34\n")
        self.journal = self.root / "synthetic.jsonl"
        self.journal.write_bytes(b'{"decision":"needs_evidence"}\n')
        self.restored = self.root / "fvs-evidence-restored-synthetic"
        self.product = "grants"
        self.on_deny = lambda: None

    def _valid_restore(self):
        self.restored.mkdir()
        (self.restored / "exception-report.csv").write_bytes(self.report.read_bytes())
        (self.restored / "exception-report.review.jsonl").write_bytes(self.journal.read_bytes())
        manifest = {
            "schema": 1, "product": self.product,
            "sealed_utc": "2026-11-09T00:00:00+00:00",
            "report_filename": self.report.name,
            "report_sha256": hashlib.sha256(self.report.read_bytes()).hexdigest(),
            "journal_filename": self.journal.name,
            "journal_sha256": hashlib.sha256(self.journal.read_bytes()).hexdigest(),
            "journal_present": True, "review_event_count": 1,
        }
        (self.restored / "sealed-evidence-manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return self.restored

    def _restore(self, archive, root, password, *, expected_product):
        self.assertEqual((archive, root, password),
                         (self.archive, self.root, "Synthetic-Only-Secret"))
        if expected_product != self.product:
            self.on_deny()
            raise ValueError(_DENIED)
        return self._valid_restore()

    def _check(self, product, mutation=None):
        self.product = product
        self.on_deny = mutation or (lambda: None)
        return check_scoped_vault_roundtrip(
            self.archive, self.root, "Synthetic-Only-Secret", product,
            self.report, self.journal, self._restore)

    def _each_product(self, mutator, expected_error):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.setUp()
                with self.assertRaisesRegex(RuntimeError, expected_error):
                    self._check(product, mutator)

    def test_untouched_denial_preserves_grants_and_procurement(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.setUp()
                self.assertEqual(self._check(product), self.restored)

    def test_manifest_reformatted_but_semantically_valid(self):
        def change():
            p = self.restored / "sealed-evidence-manifest.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            p.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        self._each_product(change, "cross-product restore changed manifest bytes")

    def test_manifest_timestamp_changed_but_still_nonempty(self):
        def change():
            p = self.restored / "sealed-evidence-manifest.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["sealed_utc"] = "2026-11-09T01:00:00+00:00"
            p.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n",
                         encoding="utf-8")
        self._each_product(change, "cross-product restore changed manifest bytes")

    def test_identical_bytes_manifest_replacement(self):
        self._each_product(lambda: self._replace("sealed-evidence-manifest.json"),
                           "cross-product restore changed filesystem identity")

    def test_identical_bytes_report_replacement(self):
        self._each_product(lambda: self._replace("exception-report.csv"),
                           "cross-product restore changed filesystem identity")

    def test_identical_bytes_journal_replacement(self):
        self._each_product(lambda: self._replace("exception-report.review.jsonl"),
                           "cross-product restore changed filesystem identity")

    def test_identical_bytes_encrypted_archive_replacement(self):
        self._each_product(lambda: self._replace_source(self.archive),
                           "cross-product restore changed filesystem identity")

    def test_identical_bytes_original_report_replacement(self):
        self._each_product(lambda: self._replace_source(self.report),
                           "cross-product restore changed filesystem identity")

    def test_identical_bytes_original_journal_replacement(self):
        self._each_product(lambda: self._replace_source(self.journal),
                           "cross-product restore changed filesystem identity")

    def test_restored_directory_replaced_with_identical_tree(self):
        def change():
            replacement = self.root / "replacement"
            shutil.copytree(self.restored, replacement)
            shutil.rmtree(self.restored)
            replacement.rename(self.restored)
        self._each_product(change, "cross-product restore changed filesystem identity")

    def _replace(self, member):
        self._replace_source(self.restored / member)

    @staticmethod
    def _replace_source(path):
        original = path.read_bytes()
        path.unlink()
        path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
