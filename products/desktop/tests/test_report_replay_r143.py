"""R143 private-source replay verifier: synthetic fixtures only; no telemetry."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.replay_verify import ReplayReceipt, main, verify_report


class LocalReportReplayR143(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory(prefix="fvs-r143-")
        self.addCleanup(fixture.cleanup)
        self.root = Path(fixture.name)
        self.published = self.root / "published"
        self.published.mkdir()

    def csv_source(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def ledger(self):
        a = self.csv_source("left.csv", ("transaction_id", "amount"),
                            (("A", "10.00"), ("B", "-5.00")))
        b = self.csv_source("right.csv", ("transaction_id", "amount"),
                            (("A", "10.00"), ("B", "-5.00")))
        return a, b, engine.ledger_diff(a, b, self.published)[0]

    def invoice(self, *, gap=1, window_days=7):
        a = self.csv_source("invoices.csv",
                            ("vendor", "invoice_number", "amount", "date"),
                            (("ACME", "A", "10.00", "2026-01-01"),
                             ("ACME", "B", "10.00", f"2026-01-{gap+1:02d}")))
        return a, engine.invoice_twins(a, self.published, window_days=window_days)[0]

    def spend(self):
        a = self.csv_source("spend.csv", ("vendor", "amount", "date", "category"),
                            (("ACME", "150", "2026-01-01", "Parts"),
                             ("ACME", "-140", "2026-01-02", "Parts")))
        return a, engine.spend_map(a, self.published)[0]

    def policy(self):
        a = self.root / "old.txt"
        b = self.root / "new.txt"
        a.write_text("Policy Section 1\nBefore\n", encoding="utf-8")
        b.write_text("Policy Section 1\nAfter\n", encoding="utf-8")
        return a, b, engine.policy_delta(a, b, self.published)[0]

    @staticmethod
    def tamper(path):
        path.write_bytes(path.read_bytes() + b"UNEXPECTED TAMPER\n")

    def test_ledger_replay_and_receipt(self):
        a, b, report = self.ledger()
        receipt = verify_report("ledger-diff", report, (a, b))
        self.assertIsInstance(receipt, ReplayReceipt)
        self.assertEqual(receipt.report_sha256, hashlib.sha256(report.read_bytes()).hexdigest())
        self.assertEqual(receipt.source_sha256, tuple(hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)))

    def test_ledger_custom_columns_require_matching_options(self):
        a = self.csv_source("ledger-a.csv", ("L Ref", "Debit Value"), (("A", "3.25"),))
        b = self.csv_source("ledger-b.csv", ("R Ref", "Credit Value"), (("A", "3.25"),))
        opts = dict(left_match_column="L Ref", right_match_column="R Ref",
                    left_amount_column="Debit Value", right_amount_column="Credit Value")
        report = engine.ledger_diff(a, b, self.published, **opts)[0]
        self.assertEqual(verify_report("ledger-diff", report, (a,b), **opts).kind, "ledger-diff")
        with self.assertRaises(ValueError):
            verify_report("ledger-diff", report, (a,b))

    def test_ledger_report_tamper_holds(self):
        a,b,report=self.ledger()
        self.tamper(report)
        with self.assertRaises(ValueError):
            verify_report("ledger-diff", report, (a,b))

    def test_ledger_source_tamper_holds(self):
        a,b,report=self.ledger()
        self.tamper(a)
        with self.assertRaises(ValueError):
            verify_report("ledger-diff", report, (a,b))

    def test_ledger_header_only_holds(self):
        a=self.csv_source("empty-left.csv", ("transaction_id","amount"), ())
        b=self.csv_source("empty-right.csv", ("transaction_id","amount"), ())
        report=engine.ledger_diff(a,b,self.published)[0]
        with self.assertRaisesRegex(ValueError, "No source-bound"):
            verify_report("ledger-diff", report, (a,b))

    def test_invoice_replay_candidate_and_digest(self):
        a,report=self.invoice()
        receipt=verify_report("invoice-twins", report, (a,))
        self.assertEqual(receipt.source_sha256, (hashlib.sha256(a.read_bytes()).hexdigest(),))

    def test_invoice_review_window_bound(self):
        a,report=self.invoice(gap=8,window_days=9)
        self.assertEqual(verify_report("invoice-twins", report, [a], window_days=9).kind,
                         "invoice-twins")
        with self.assertRaises(ValueError):
            verify_report("invoice-twins", report, [a], window_days=7)

    def test_invoice_report_tamper_holds(self):
        a,report=self.invoice()
        self.tamper(report)
        with self.assertRaises(ValueError):
            verify_report("invoice-twins", report, [a])

    def test_invoice_source_tamper_holds(self):
        a,report=self.invoice()
        self.tamper(a)
        with self.assertRaises(ValueError):
            verify_report("invoice-twins", report, [a])

    def test_invoice_zero_candidates_holds(self):
        a=self.csv_source("one-invoice.csv",
                          ("vendor","invoice_number","amount","date"),
                          (("ACME","A","10.00","2026-01-01"),))
        report=engine.invoice_twins(a,self.published)[0]
        with self.assertRaisesRegex(ValueError, "No source-bound"):
            verify_report("invoice-twins", report, [a])

    def test_spend_replay_offset_report(self):
        a,report=self.spend()
        self.assertEqual(verify_report("spend-map", report, [a]).kind, "spend-map")

    def test_spend_report_tamper_holds(self):
        a,report=self.spend()
        self.tamper(report)
        with self.assertRaises(ValueError):
            verify_report("spend-map", report, [a])

    def test_spend_source_tamper_holds(self):
        a,report=self.spend()
        self.tamper(a)
        with self.assertRaises(ValueError):
            verify_report("spend-map", report, [a])

    def test_policy_replay_exact(self):
        a,b,report=self.policy()
        receipt=verify_report("policy-delta", report, [a,b])
        self.assertEqual(receipt.source_sha256, tuple(
            hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)))

    def test_policy_reverse_sources_holds(self):
        a,b,report=self.policy()
        with self.assertRaises(ValueError):
            verify_report("policy-delta", report, (b,a))

    def test_policy_report_tamper_holds(self):
        a,b,report=self.policy()
        self.tamper(report)
        with self.assertRaises(ValueError):
            verify_report("policy-delta", report, [a,b])

    def test_missing_report_holds(self):
        a,report=self.spend()
        report.unlink()
        with self.assertRaises((ValueError, OSError)):
            verify_report("spend-map", report, [a])

    def test_invalid_kind_and_premium_holds(self):
        a,report=self.spend()
        for kind in ("grant-audit", "procure-guard", "", "private-pro", 123):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify_report(kind, report, [a])

    def test_wrong_source_count_holds(self):
        a,b,report=self.ledger()
        for sources in ([a], [a,b,a], [], "not-a-sequence-of-paths"):
            with self.subTest(sources=str(type(sources))), self.assertRaises(ValueError):
                verify_report("ledger-diff", report, sources)

    def test_cross_product_options_holds(self):
        a,report=self.spend()
        for options in ({"window_days":0}, {"left_amount_column":"amount"},
                        {"window_days":True}, {"window_days":366}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                verify_report("spend-map", report, [a], **options)

    def test_cli_verified_digest_no_filename(self):
        a,report=self.spend()
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=main(["--kind","spend-map","--report",str(report),"--source",str(a)])
        self.assertEqual(code,0)
        self.assertIn(hashlib.sha256(report.read_bytes()).hexdigest(),out.getvalue())
        self.assertNotIn(str(a),out.getvalue())
        self.assertEqual(err.getvalue(),"")

    def test_cli_hold_redacts_private_filename(self):
        a,report=self.spend()
        secret=a.rename(self.root/"private-client-payroll-secret.csv")
        self.tamper(secret)
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=main(["--kind","spend-map","--report",str(report),
                       "--source",str(self.root/"private-client-payroll-secret.csv")])
        self.assertEqual(code,1)
        self.assertEqual(out.getvalue(),"")
        self.assertIn("REPLAY HOLD",err.getvalue())
        self.assertNotIn("private-client-payroll-secret",err.getvalue())

    def test_verifier_leaves_original_folder_intact(self):
        a,b,report=self.ledger()
        before=sorted(p.name for p in self.published.iterdir())
        sources_before=(a.read_bytes(),b.read_bytes())
        verify_report("ledger-diff",report,[a,b])
        self.assertEqual(sorted(p.name for p in self.published.iterdir()),before)
        self.assertEqual((a.read_bytes(),b.read_bytes()),sources_before)


if __name__ == "__main__":
    unittest.main()
