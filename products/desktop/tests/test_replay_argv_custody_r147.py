"""R147 synthetic adversarial replay CLI ambiguity, privacy and continuity tests.

The offline verifier must never silently accept a replacement report, product,
window, or ledger mapping. All fixtures are synthetic. Verification is only
reproducibility, not source authenticity or a compliance decision.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fvs_suite import engine, replay_verify

SECRET = "CONFIDENTIAL-CLIENT-PAYROLL-2026-ALPHA"
HOLD = ("REPLAY HOLD: selected report and sources cannot be verified "
        "under the current local engine.\n")


class ReplayArgvCustodyR147(unittest.TestCase):
    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="fvs-r147-")
        self.addCleanup(private.cleanup)
        self.root = Path(private.name)
        self.out = self.root / "reports"
        self.out.mkdir()
        self.source = self.root / (SECRET + ".csv")
        self.report = self.out / "spend-map.csv"

    def base(self):
        return ["--kind", "spend-map", "--report", str(self.report),
                "--source", str(self.source)]

    def _invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = replay_verify.main(args)
        return status, stdout.getvalue(), stderr.getvalue()

    def _hold_before_dispatch(self, args):
        with mock.patch.object(replay_verify, "verify_report",
                               side_effect=AssertionError("invalid argv reached sources")) as verified:
            status, out, err = self._invoke(args)
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, HOLD)
        self.assertNotIn(SECRET, err)
        self.assertNotIn("usage:", err.lower())
        self.assertNotIn("Traceback", err)
        verified.assert_not_called()

    def _spend_fixture(self):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category"))
            writer.writerow(("Acme", "150.00", "2026-01-01", "Supplies"))
            writer.writerow(("Acme", "-140.00", "2026-01-02", "Supplies"))
        return engine.spend_map(self.source, self.out)[0]

    def _ledger_fixture(self):
        first = self.root / "left.csv"
        second = self.root / "right.csv"
        for path, amount in ((first, "5.25"), (second, "5.25")):
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(("transaction_id", "amount"))
                writer.writerow(("TX-001", amount))
        return first, second, engine.ledger_diff(first, second, self.out)[0]

    def test_duplicate_kind_flag_rejected(self):
        self._hold_before_dispatch(self.base() + ["--kind", "invoice-twins"])

    def test_duplicate_kind_equals_rejected(self):
        self._hold_before_dispatch(self.base() + ["--kind=" + SECRET])

    def test_duplicate_report_flag_rejected(self):
        self._hold_before_dispatch(self.base() + ["--report", SECRET])

    def test_duplicate_report_equals_rejected(self):
        self._hold_before_dispatch(self.base() + ["--report=" + SECRET])

    def test_duplicate_window_days_rejected(self):
        self._hold_before_dispatch(self.base() + ["--window-days", "7", "--window-days", SECRET])

    def test_duplicate_left_match_mapping_rejected(self):
        self._hold_before_dispatch(self.base() + ["--left-match-column", "A",
                                                   "--left-match-column", SECRET])

    def test_duplicate_right_match_mapping_rejected(self):
        self._hold_before_dispatch(self.base() + ["--right-match-column", "B",
                                                   "--right-match-column", SECRET])

    def test_duplicate_left_amount_mapping_rejected(self):
        self._hold_before_dispatch(self.base() + ["--left-amount-column", "C",
                                                   "--left-amount-column", SECRET])

    def test_duplicate_right_amount_mapping_rejected(self):
        self._hold_before_dispatch(self.base() + ["--right-amount-column", "D",
                                                   "--right-amount-column", SECRET])

    def test_mixed_equals_first_report_rejected(self):
        self._hold_before_dispatch(["--kind", "spend-map", "--report=" + SECRET,
                                    "--source", str(self.source),
                                    "--report", str(self.report)])

    def test_mixed_equals_second_kind_rejected(self):
        self._hold_before_dispatch(["--kind=spend-map", "--report", str(self.report),
                                    "--source", str(self.source), "--kind", SECRET])

    def test_abbreviated_kind_rejected(self):
        self._hold_before_dispatch(["--ki", "spend-map"] + self.base()[2:])

    def test_abbreviated_report_rejected(self):
        self._hold_before_dispatch(["--kind", "spend-map", "--rep", SECRET,
                                    "--source", str(self.source)])

    def test_abbreviated_source_rejected(self):
        self._hold_before_dispatch(self.base()[:-2] + ["--sou", SECRET])

    def test_abbreviated_window_rejected(self):
        self._hold_before_dispatch(self.base() + ["--window", SECRET])

    def test_abbreviated_left_match_rejected(self):
        self._hold_before_dispatch(self.base() + ["--left-match", SECRET])

    def test_abbreviated_left_amount_rejected(self):
        self._hold_before_dispatch(self.base() + ["--left-amount", SECRET])

    def test_secret_unknown_option_redacted(self):
        self._hold_before_dispatch(self.base() + ["--" + SECRET, "PRIVATE"])

    def test_mixed_long_help_with_secret_rejected(self):
        self._hold_before_dispatch(self.base() + ["--help", SECRET])

    def test_mixed_short_help_with_secret_rejected(self):
        self._hold_before_dispatch(["-h", "--report", SECRET])

    def test_double_dash_separator_rejected(self):
        self._hold_before_dispatch(self.base() + ["--", SECRET])

    def test_nonstr_argument_rejected(self):
        self._hold_before_dispatch(self.base() + [object()])

    def test_standalone_help_is_static_without_source_reads(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(replay_verify, "verify_report") as forbidden:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                with self.assertRaises(SystemExit) as caught:
                    replay_verify.main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("--source", out.getvalue())
        self.assertNotIn(SECRET, out.getvalue())
        self.assertEqual(err.getvalue(), "")
        forbidden.assert_not_called()

    def test_two_explicit_sources_still_dispatch_for_ledger(self):
        second = self.root / "independent.csv"
        receipt = replay_verify.ReplayReceipt("ledger-diff", "a" * 64, ("b" * 64, "c" * 64))
        args = ["--kind", "ledger-diff", "--report", str(self.report),
                "--source", str(self.source), "--source", str(second)]
        with mock.patch.object(replay_verify, "verify_report", return_value=receipt) as verify:
            status, out, err = self._invoke(args)
        self.assertEqual(status, 0)
        self.assertIn("source_count=2", out)
        self.assertEqual(err, "")
        self.assertNotIn(SECRET, out)
        verify.assert_called_once_with("ledger-diff", str(self.report),
            [str(self.source), str(second)], window_days=7,
            left_match_column=None, right_match_column=None,
            left_amount_column=None, right_amount_column=None)

    def test_three_sources_for_spend_map_hold_before_engine(self):
        args = self.base() + ["--source", str(self.root / "second.csv"),
                              "--source=" + str(self.root / "third.csv")]
        with mock.patch.object(engine, "spend_map",
                               side_effect=AssertionError("must not run")) as forbidden:
            status, out, err = self._invoke(args)
        self.assertEqual((status, out, err), (1, "", HOLD))
        forbidden.assert_not_called()

    def test_real_spend_replay_valid_after_parser_hardening(self):
        report = self._spend_fixture()
        status, out, err = self._invoke(["--kind", "spend-map", "--report", str(report),
                                         "--source", str(self.source)])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertIn(hashlib.sha256(report.read_bytes()).hexdigest(), out)
        self.assertNotIn(SECRET, out)

    def test_real_ledger_replay_allows_two_sources(self):
        left, right, report = self._ledger_fixture()
        status, out, err = self._invoke(["--kind", "ledger-diff", "--report", str(report),
                                         "--source=" + str(left), "--source", str(right)])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertIn("kind=ledger-diff", out)
        self.assertIn("source_count=2", out)

    def test_real_policy_replay_allows_two_sources(self):
        left = self.root / "before.txt"
        right = self.root / "after.txt"
        left.write_text("Policy one\n", encoding="utf-8")
        right.write_text("Policy two\n", encoding="utf-8")
        report = engine.policy_delta(left, right, self.out)[0]
        status, out, err = self._invoke(["--kind", "policy-delta",
                                         "--report", str(report),
                                         "--source", str(left), "--source", str(right)])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertIn("kind=policy-delta", out)

    def test_rejected_duplicate_does_not_modify_originals(self):
        report = self._spend_fixture()
        original = (self.source.read_bytes(), report.read_bytes(),
                    self.source.stat().st_mtime_ns, report.stat().st_mtime_ns)
        with mock.patch.object(replay_verify, "verify_report",
                               side_effect=AssertionError("must not verify")) as forbidden:
            status, out, err = self._invoke(
                ["--kind", "spend-map", "--report", str(report),
                 "--source", str(self.source), "--report=" + SECRET])
        self.assertEqual((status, out, err), (1, "", HOLD))
        forbidden.assert_not_called()
        self.assertEqual((self.source.read_bytes(), report.read_bytes(),
                          self.source.stat().st_mtime_ns, report.stat().st_mtime_ns), original)

    def test_real_subprocess_duplicate_report_does_not_leak(self):
        env = os.environ.copy()
        desktop = str(Path(__file__).resolve().parents[1])
        env["PYTHONPATH"] = os.pathsep.join(
            piece for piece in (desktop, env.get("PYTHONPATH", "")) if piece)
        call = [sys.executable, "-m", "fvs_suite.replay_verify",
                *self.base(), "--report=" + SECRET]
        result = subprocess.run(call, cwd=self.root, env=env, text=True,
                                capture_output=True, timeout=40, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, HOLD)
        self.assertNotIn(SECRET, result.stderr)

    def test_parser_exception_never_contains_private_choice(self):
        parser = replay_verify._PrivateArgumentParser(add_help=False)
        parser.add_argument("--report", required=True)
        with self.assertRaises(ValueError) as captured:
            parser.parse_args(["--report", SECRET, "--not-valid=" + SECRET])
        self.assertNotIn(SECRET, str(captured.exception))

    def test_premium_kind_rejected_before_verifier(self):
        self._hold_before_dispatch(["--kind", "grant-audit", "--report", SECRET,
                                    "--source", str(self.source)])

    def test_missing_kind_never_reaches_verifier(self):
        self._hold_before_dispatch(self.base()[2:])


if __name__ == "__main__":
    unittest.main()
