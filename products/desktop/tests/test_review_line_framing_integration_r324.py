"""R324: genuine premium report-bound journal reader integration (full checkout)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from fvs_suite.exception_review import read_cases, read_journal, _json, _hex_hash


class PremiumReviewJournalFramingIntegrationR324(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r324-synthetic-")
        self.addCleanup(tmp.cleanup)
        self.report = Path(tmp.name) / "exceptions.csv"
        self.journal = Path(tmp.name) / "review.jsonl"
        self.report.write_bytes(b"id,status\nSYNTHETIC-01,exception\n")
        self.batch = read_cases(self.report, "grants")
        self.case = self.batch.cases[0]

    def _events(self):
        previous = "0" * 64
        records = []
        for index in range(2):
            payload = {
                "schema": 1, "product": "grants",
                "report_sha256": self.batch.report_sha256,
                "case_id": self.case.case_id, "report_row": self.case.report_row,
                "flags": self.case.flags,
                "decision": "needs_evidence" if index == 0 else "escalated",
                "reviewer": "Synthetic Reviewer",
                "rationale": "Synthetic record for local-only chain testing.",
                "created_utc": (datetime(2026, 11, 9, 10, 5, tzinfo=timezone.utc) +
                                timedelta(minutes=index)).isoformat(timespec="seconds"),
                "previous_hash": previous,
            }
            previous = _hex_hash(_json(payload))
            records.append(_json({**payload, "event_hash": previous}))
        return records

    def test_normal_lf_valid_hash_chain(self):
        records = self._events()
        self.journal.write_bytes(b"\n".join(records) + b"\n")
        self.assertEqual(len(read_journal(self.journal, self.batch)), 2)

    def test_optional_crlf_valid_hash_chain(self):
        records = self._events()
        self.journal.write_bytes(b"\r\n".join(records) + b"\r\n")
        self.assertEqual(len(read_journal(self.journal, self.batch)), 2)

    def test_bare_cr_separator_valid_events_must_hold(self):
        records = self._events()
        # Old bytes.splitlines() treated this as two legitimate records.
        raw = records[0] + b"\r" + records[1] + b"\n"
        self.assertEqual(raw.splitlines(), records)
        self.journal.write_bytes(raw)
        with self.assertRaises(ValueError):
            read_journal(self.journal, self.batch)

    def test_raw_cr_in_json_whitespace_must_hold(self):
        records = self._events()
        self.journal.write_bytes(records[0].replace(b':1', b':\r1', 1) + b"\n")
        with self.assertRaises(ValueError):
            read_journal(self.journal, self.batch)

    def test_source_report_not_modified_by_reader(self):
        records = self._events()
        self.journal.write_bytes(records[0] + b"\n")
        report_before, journal_before = self.report.read_bytes(), self.journal.read_bytes()
        self.assertEqual(len(read_journal(self.journal, self.batch)), 1)
        self.assertEqual(self.report.read_bytes(), report_before)
        self.assertEqual(self.journal.read_bytes(), journal_before)

    def test_missing_journal_still_means_no_events(self):
        self.assertEqual(read_journal(self.journal, self.batch), [])


if __name__ == "__main__":
    unittest.main()
