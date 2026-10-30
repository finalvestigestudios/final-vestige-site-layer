"""R66 complete-engine GrantAudit confidential-claim-type regressions.

These tests require the full private fvs_suite checkout and are not equivalent
in coverage to the separately executable pure-helper tests.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class GrantClaimPrivacyIntegrationR66Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-grant-private-r66-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "output"
        self.output.mkdir()
        self.claims = self.root / "claims.csv"
        self.ledger = self.root / "ledger.csv"
        self.budget = self.root / "budget.csv"
        self._csv(self.ledger, ("id", "amount", "program"), [("T1", "100.00", "G1")])
        self._csv(self.budget, ("program", "budget"), [("G1", "200.00")])

    @staticmethod
    def _csv(path, headers, records):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(records)

    def _claims(self, records, *, with_type=True):
        headers = ("claim_id", "amount", "program", "ledger_reference")
        if with_type:
            headers += ("claim_type", "related_claim")
        self._csv(self.claims, headers, records)

    def _run(self):
        return engine.grant_audit(str(self.claims), str(self.ledger),
                                  str(self.budget), str(self.output))

    def _no_partial_outputs(self):
        self.assertEqual(list(self.output.rglob("*")), [])

    def test_private_claim_type_is_not_raised_or_written(self):
        secret = "beneficiary-acct-7733"
        self._claims([("C1", "100.00", "G1", "T1", secret, "")])
        with self.assertRaises(ValueError) as caught:
            self._run()
        self.assertEqual(str(caught.exception),
                         "Unsupported claim_type at claim CSV physical row 2; use claim or credit")
        self.assertNotIn(secret, str(caught.exception))
        self._no_partial_outputs()

    def test_multiline_claim_type_preserves_physical_start_row(self):
        secret = "private\nsecond line\x1b[31m"
        self._claims([("C1", "100.00", "G1", "T1", secret, "")])
        with self.assertRaises(ValueError) as caught:
            self._run()
        self.assertIn("physical row 2", str(caught.exception))
        self.assertNotIn("private", str(caught.exception))
        self.assertNotIn("second line", str(caught.exception))
        self.assertNotIn("\x1b", str(caught.exception))
        self._no_partial_outputs()

    def test_casefolded_credit_preserves_exact_reversal_math(self):
        self._claims([("C1", "120.00", "G1", "T1", " Claim ", ""),
                      ("CR1", "20.00", "G1", "T1", " CREDIT ", "C1")])
        paths = self._run()
        with Path(paths[0]).open(newline="", encoding="utf-8-sig") as stream:
            record = list(csv.DictReader(stream))[0]
        self.assertEqual(record["gross_claim_amount"], "120.00")
        self.assertEqual(record["credit_amount"], "20.00")
        self.assertEqual(record["net_claim_amount"], "100.00")
        self.assertIn("credit_memo_review", record["status"])

    def test_omitted_claim_type_still_defaults_to_claim(self):
        self._claims([("C1", "100.00", "G1", "T1")], with_type=False)
        paths = self._run()
        with Path(paths[0]).open(newline="", encoding="utf-8-sig") as stream:
            record = list(csv.DictReader(stream))[0]
        self.assertEqual(record["claim_amount"], "100.00")
        self.assertEqual(record["status"], "matched")

    def test_error_on_second_row_does_not_publish_first_valid_claim(self):
        self._claims([("C1", "40.00", "G1", "T1", "claim", ""),
                      ("C2", "60.00", "G1", "T1", "personal data", "")])
        with self.assertRaises(ValueError) as caught:
            self._run()
        self.assertIn("physical row 3", str(caught.exception))
        self.assertNotIn("personal data", str(caught.exception))
        self._no_partial_outputs()


if __name__ == "__main__":
    unittest.main()
