"""R81 register rendering with synthetic source snapshots and test-only I/O stubs.

The real CI integration tests exercise actual premium CSV parsing/atomic writer.
"""
from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from fvs_suite import review_register

FIELDS = ("case_id", "source_row", "source_key", "original_flags",
          "review_state", "reviewer", "rationale", "reviewed_utc", "report_sha256")


def cell(value):
    data = str(value)
    return "'" + data if data.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else data


class AuditRegisterRenderR81(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r81-register-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cases = [
            SimpleNamespace(case_id="cid-a", report_row=2,
                            source_key="INV\u202E-1", flags="needs\u200B_evidence"),
            SimpleNamespace(case_id="cid-b", report_row=3,
                            source_key=r"INV\u202E-1", flags="variance"),
        ]
        self.batch = SimpleNamespace(product="grants", report_sha256="d" * 64,
                                     cases=self.cases)
        self.events = [{"case_id": "cid-a", "decision": "reviewed",
                        "reviewer": "Analyst", "rationale": "Inspect original source.",
                        "created_utc": "2026-10-31T00:00:00+00:00"}]
        self.calls = []

    def read_cases(self, report, product):
        self.calls.append("read_cases")
        return self.batch

    def read_journal(self, journal, batch):
        self.calls.append("read_journal")
        self.assertIs(batch, self.batch)
        return list(self.events)

    def export(self):
        return review_register.publish_review_register(
            "report.csv", "grants", "journal.jsonl", self.root,
            read_cases=self.read_cases, read_journal=self.read_journal,
            columns=FIELDS, cell=cell, expected_report_sha256="d" * 64)

    def test_export_distinguishes_hidden_and_literal_source(self):
        path = self.export()
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["source_key"], r"INV\u202E-1")
        self.assertEqual(rows[1]["source_key"], r"INV\\u202E-1")
        self.assertEqual(rows[0]["original_flags"], r"needs\u200B_evidence")
        self.assertEqual(rows[0]["review_state"], "reviewed")
        self.assertEqual(rows[1]["review_state"], "pending")
        self.assertEqual(rows[0]["case_id"], "cid-a")
        self.assertEqual(rows[1]["source_row"], "3")
        self.assertEqual(rows[0]["report_sha256"], "d" * 64)
        self.assertEqual(self.calls,
                         ["read_cases", "read_journal", "read_cases", "read_journal"])
        self.assertEqual(self.cases[0].source_key, "INV\u202E-1")
        self.assertEqual(self.cases[0].flags, "needs\u200B_evidence")

    def test_formula_prefix_remains_escaped_by_csv_guard(self):
        self.cases[0].source_key = "=SUM(A1:A2)"
        path = self.export()
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["source_key"], "'=SUM(A1:A2)")

    def test_changed_source_before_publication_rejected(self):
        class Changed:
            def __init__(self, batch):
                self.batch = batch
                self.count = 0

            def __call__(self, report, product):
                self.count += 1
                if self.count == 2:
                    return SimpleNamespace(report_sha256="e" * 64,
                                           cases=self.batch.cases,
                                           product=self.batch.product)
                return self.batch

        with self.assertRaises(ValueError):
            review_register.publish_review_register(
                "report.csv", "grants", "journal.jsonl", self.root,
                read_cases=Changed(self.batch), read_journal=self.read_journal,
                columns=FIELDS, cell=cell, expected_report_sha256="d" * 64)
        self.assertEqual(list(self.root.glob("review-register-*.csv")), [])

    def test_expected_source_hash_mismatch_fails_closed(self):
        with self.assertRaises(ValueError):
            review_register.publish_review_register(
                "report.csv", "grants", "journal.jsonl", self.root,
                read_cases=self.read_cases, read_journal=self.read_journal,
                columns=FIELDS, cell=cell, expected_report_sha256="wrong")
        self.assertEqual(list(self.root.glob("review-register-*.csv")), [])


if __name__ == "__main__":
    unittest.main()
