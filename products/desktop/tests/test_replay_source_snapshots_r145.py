"""R145 offline source-custody regressions; all inputs synthetic."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fvs_suite import engine, replay_verify
from fvs_suite.replay_verify import verify_report, main

SECRET = "secret-family-office-payroll-2026"


class SourceSnapshotR145(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r145-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.out = self.root / "published"
        self.out.mkdir()

    def source(self, name, headers, rows, folder=None):
        root = folder or self.root
        root.mkdir(parents=True, exist_ok=True)
        path = root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def spend(self, name="spend.csv"):
        path = self.source(name, ("vendor", "amount", "date", "category"),
                           (("ACME", "150.00", "2026-01-01", "Parts"),
                            ("ACME", "-140.00", "2026-01-02", "Parts")))
        return path, engine.spend_map(path, self.out)[0]

    def ledger(self, same_name=False):
        first = self.source("ledger.csv" if same_name else "a.csv",
                            ("transaction_id", "amount"), (("A", "1.25"),),
                            self.root / "first" if same_name else None)
        second = self.source("ledger.csv" if same_name else "b.csv",
                             ("transaction_id", "amount"), (("A", "1.25"),),
                             self.root / "second" if same_name else None)
        return first, second, engine.ledger_diff(first, second, self.out)[0]

    def invoice(self, window=7):
        src = self.source("invoices.csv",
                          ("vendor", "invoice_number", "amount", "date"),
                          (("ACME", "INV1", "20.00", "2026-01-01"),
                           ("ACME", "INV1", "-20.00", "2026-01-03")))
        return src, engine.invoice_twins(src, self.out, window_days=window)[0]

    def policy(self, same_name=False, bom=False):
        first = self.root / ("original/policy.txt" if same_name else "old.txt")
        second = self.root / ("revised/policy.txt" if same_name else "new.txt")
        first.parent.mkdir(parents=True, exist_ok=True)
        second.parent.mkdir(parents=True, exist_ok=True)
        first.write_bytes((b"\xef\xbb\xbf" if bom else b"") + b"Section\nBefore\n")
        second.write_bytes((b"\xef\xbb\xbf" if bom else b"") + b"Section\nAfter\n")
        return first, second, engine.policy_delta(first, second, self.out)[0]

    def test_spend_reads_independent_private_copy(self):
        source, report = self.spend()
        original = engine.spend_map
        seen = []
        def observer(path, folder):
            seen.append(Path(path))
            self.assertNotEqual(Path(path), source)
            self.assertEqual(Path(path).name, source.name)
            self.assertEqual(Path(path).read_bytes(), source.read_bytes())
            return original(path, folder)
        with mock.patch.object(engine, "spend_map", side_effect=observer):
            receipt = verify_report("spend-map", report, [source])
        self.assertEqual(len(seen), 1)
        self.assertEqual(receipt.source_sha256,
                         (hashlib.sha256(source.read_bytes()).hexdigest(),))

    def test_ledger_reads_two_distinct_copy_directories(self):
        a, b, report = self.ledger()
        original = engine.ledger_diff
        seen = []
        def observer(left, right, folder, **opts):
            seen.extend((Path(left), Path(right)))
            self.assertNotEqual(Path(left), a)
            self.assertNotEqual(Path(right), b)
            self.assertNotEqual(Path(left).parent, Path(right).parent)
            return original(left, right, folder, **opts)
        with mock.patch.object(engine, "ledger_diff", side_effect=observer):
            self.assertEqual(verify_report("ledger-diff", report, [a,b]).kind,
                             "ledger-diff")
        self.assertEqual(len(seen), 2)

    def test_invoice_reads_copy_not_original(self):
        src, report = self.invoice()
        original = engine.invoice_twins
        seen = []
        def observer(path, folder, **opts):
            seen.append(Path(path))
            return original(path, folder, **opts)
        with mock.patch.object(engine, "invoice_twins", side_effect=observer):
            verify_report("invoice-twins", report, [src])
        self.assertEqual(len(seen), 1)
        self.assertNotEqual(seen[0], src)

    def test_policy_copy_preserves_filenames(self):
        a, b, report = self.policy()
        original = engine.policy_delta
        seen = []
        def observer(left, right, folder):
            seen.extend((Path(left), Path(right)))
            return original(left, right, folder)
        with mock.patch.object(engine, "policy_delta", side_effect=observer):
            verify_report("policy-delta", report, [a,b])
        self.assertEqual([p.name for p in seen], [a.name, b.name])
        self.assertNotEqual(seen[0], a)

    def test_policy_same_basename_across_directories(self):
        a, b, report = self.policy(same_name=True)
        self.assertEqual(verify_report("policy-delta", report, [a,b]).kind,
                         "policy-delta")

    def test_ledger_same_basename_across_directories(self):
        a, b, report = self.ledger(same_name=True)
        self.assertEqual(verify_report("ledger-diff", report, [a,b]).kind,
                         "ledger-diff")

    def test_policy_bom_bytes_preserved(self):
        a, b, report = self.policy(bom=True)
        receipt = verify_report("policy-delta", report, [a,b])
        self.assertEqual(receipt.source_sha256,
                         tuple(hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (a,b)))

    def test_spend_snapshot_mismatched_digest_holds_before_engine(self):
        src, report = self.spend()
        with mock.patch.object(replay_verify, "read_csv_snapshot",
                               return_value=b"vendor,amount,date\nEVIL,900,2026-01-01\n"):
            with mock.patch.object(engine, "spend_map") as forbidden:
                with self.assertRaisesRegex(ValueError, "changed before replay"):
                    verify_report("spend-map", report, [src])
                forbidden.assert_not_called()

    def test_policy_snapshot_mismatched_digest_holds_before_engine(self):
        a, b, report = self.policy()
        read = replay_verify.read_csv_snapshot
        def tamper(path, cap):
            return b"INJECTED\n" if Path(path) == b else read(path, cap)
        with mock.patch.object(replay_verify, "read_csv_snapshot", side_effect=tamper):
            with mock.patch.object(engine, "policy_delta") as forbidden:
                with self.assertRaises(ValueError):
                    verify_report("policy-delta", report, [a,b])
                forbidden.assert_not_called()

    def test_copy_corrupted_after_write_holds_before_engine(self):
        src, report = self.spend()
        write = Path.write_bytes
        def corrupt(path, payload):
            return write(path, payload + b"unexpected")
        with mock.patch.object(Path, "write_bytes", new=corrupt):
            with mock.patch.object(engine, "spend_map") as forbidden:
                with self.assertRaisesRegex(ValueError, "Private replay source"):
                    verify_report("spend-map", report, [src])
                forbidden.assert_not_called()

    def test_original_changes_during_replay_holds(self):
        src, report = self.spend()
        original = engine.spend_map
        raw = src.read_bytes()
        def mutate(path, folder):
            self.assertNotEqual(Path(path), src)
            src.write_bytes(raw + b"\n")
            return original(path, folder)
        with mock.patch.object(engine, "spend_map", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Evidence changed"):
                verify_report("spend-map", report, [src])

    def test_report_tamper_holds(self):
        src, report = self.spend()
        report.write_bytes(report.read_bytes() + b"altered\n")
        with self.assertRaises(ValueError):
            verify_report("spend-map", report, [src])

    def test_sources_and_report_preserved(self):
        src, report = self.spend()
        before = (src.read_bytes(), report.read_bytes(),
                  src.stat().st_mtime_ns, report.stat().st_mtime_ns)
        verify_report("spend-map", report, [src])
        self.assertEqual(before, (src.read_bytes(), report.read_bytes(),
                                  src.stat().st_mtime_ns, report.stat().st_mtime_ns))

    def test_published_folder_has_no_new_files(self):
        a, b, report = self.ledger()
        names = sorted(path.name for path in self.out.iterdir())
        verify_report("ledger-diff", report, [a,b])
        self.assertEqual(names, sorted(path.name for path in self.out.iterdir()))

    def test_temp_copy_removed_after_success(self):
        src, report = self.spend()
        original = tempfile.TemporaryDirectory
        observed = []
        def tracked(*args, **kwargs):
            obj = original(*args, **kwargs)
            observed.append(Path(obj.name))
            return obj
        with mock.patch.object(replay_verify.tempfile, "TemporaryDirectory",
                               side_effect=tracked):
            verify_report("spend-map", report, [src])
        self.assertEqual(len(observed), 1)
        self.assertFalse(observed[0].exists())

    def test_temp_copy_removed_after_failure(self):
        src, report = self.spend()
        report.write_bytes(report.read_bytes() + b"tamper")
        original = tempfile.TemporaryDirectory
        observed = []
        def tracked(*args, **kwargs):
            obj = original(*args, **kwargs)
            observed.append(Path(obj.name))
            return obj
        with mock.patch.object(replay_verify.tempfile, "TemporaryDirectory",
                               side_effect=tracked):
            with self.assertRaises(ValueError):
                verify_report("spend-map", report, [src])
        self.assertEqual(len(observed), 1)
        self.assertFalse(observed[0].exists())

    def test_ledger_custom_decimal_and_columns(self):
        a = self.source("cash.csv", ("L Ref", "Debit Value"), (("A", "-8.25"),))
        b = self.source("books.csv", ("R Ref", "Credit Value"), (("A", "-8.25"),))
        options = dict(left_match_column="L Ref", right_match_column="R Ref",
                       left_amount_column="Debit Value",
                       right_amount_column="Credit Value")
        report = engine.ledger_diff(a,b,self.out,**options)[0]
        self.assertEqual(verify_report("ledger-diff", report, [a,b], **options).kind,
                         "ledger-diff")

    def test_invoice_window_still_bound(self):
        src, report = self.invoice(window=3)
        verify_report("invoice-twins", report, [src], window_days=3)
        with self.assertRaises(ValueError):
            verify_report("invoice-twins", report, [src], window_days=0)

    def test_header_only_financial_report_still_holds(self):
        a = self.source("empty-a.csv", ("transaction_id","amount"), ())
        b = self.source("empty-b.csv", ("transaction_id","amount"), ())
        report = engine.ledger_diff(a,b,self.out)[0]
        with self.assertRaisesRegex(ValueError, "No source-bound"):
            verify_report("ledger-diff", report, [a,b])

    def test_premium_kind_rejected_before_snapshot(self):
        src, report = self.spend()
        with mock.patch.object(replay_verify, "read_csv_snapshot") as forbidden:
            with self.assertRaises(ValueError):
                verify_report("grant-audit", report, [src])
            forbidden.assert_not_called()

    def test_snapshot_failure_cli_redacts_confidential_value(self):
        src, report = self.spend(SECRET + ".csv")
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.object(replay_verify, "read_csv_snapshot",
                               side_effect=ValueError(SECRET)):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                code = main(["--kind","spend-map","--report",str(report),
                             "--source",str(src)])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(errors.getvalue(),
                         "REPLAY HOLD: selected report and sources cannot be verified "
                         "under the current local engine.\n")
        self.assertNotIn(SECRET, errors.getvalue())

    def test_repeated_replays_have_identical_receipts(self):
        src, report = self.spend()
        self.assertEqual(verify_report("spend-map", report, [src]),
                         verify_report("spend-map", report, [src]))

    def test_directory_masquerading_as_csv_rejected(self):
        src, report = self.spend()
        fake = self.root / "fake.csv"
        fake.mkdir()
        with self.assertRaises((ValueError, OSError)):
            verify_report("spend-map", report, [fake])


if __name__ == "__main__":
    unittest.main()
