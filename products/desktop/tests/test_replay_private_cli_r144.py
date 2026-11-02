"""R144 adversarial privacy tests: malformed offline replay CLI values must never leak.

All data is synthetic. These tests do not authenticate sources or release builds.
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

from fvs_suite import engine
from fvs_suite.replay_verify import main


SECRET = "private-client-payroll-987654"
GENERIC_HOLD = (
    "REPLAY HOLD: selected report and sources cannot be verified "
    "under the current local engine.\n"
)


class ReplayPrivateCliR144(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r144-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / (SECRET + ".csv")
        self.report = self.root / "private-salary-report.csv"

    def base(self):
        return ["--kind", "spend-map", "--report", str(self.report),
                "--source", str(self.source)]

    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(args)
        return status, out.getvalue(), err.getvalue()

    def assert_hold(self, args, *private_values):
        status, out, err = self.invoke(args)
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, GENERIC_HOLD)
        for value in (SECRET, str(self.source), str(self.report), *private_values):
            self.assertNotIn(value, err)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("usage:", err)

    def create_real_spend(self):
        with self.source.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(("vendor", "amount", "date", "category"))
            writer.writerows((("ACME", "150.00", "2026-01-01", "Parts"),
                              ("ACME", "-140.00", "2026-01-02", "Parts")))
        folder = self.root / "exports"
        folder.mkdir()
        return engine.spend_map(self.source, folder)[0]

    def test_invalid_product_value_redacted(self):
        args = self.base()
        args[1] = SECRET
        self.assert_hold(args)

    def test_invalid_integer_window_redacted(self):
        self.assert_hold(self.base() + ["--window-days", SECRET])

    def test_unknown_option_name_redacted(self):
        self.assert_hold(self.base() + ["--" + SECRET, "123"])

    def test_unknown_option_value_redacted(self):
        self.assert_hold(self.base() + ["--not-valid", SECRET])

    def test_orphan_positional_value_redacted(self):
        self.assert_hold(self.base() + [SECRET])

    def test_missing_product_redacted(self):
        self.assert_hold(self.base()[2:])

    def test_missing_report_redacted(self):
        self.assert_hold(["--kind", "spend-map", "--source", str(self.source)])

    def test_missing_source_redacted(self):
        self.assert_hold(["--kind", "spend-map", "--report", str(self.report)])

    def test_source_option_missing_value_redacted(self):
        self.assert_hold(self.base() + ["--source"])

    def test_option_shaped_source_value_redacted(self):
        self.assert_hold(["--kind", "spend-map", "--report", str(self.report),
                          "--source", "--" + SECRET])

    def test_premium_product_name_redacted(self):
        args = self.base()
        args[1] = "grant-audit-" + SECRET
        self.assert_hold(args, "grant-audit-" + SECRET)

    def test_unicode_control_value_redacted(self):
        suspicious = SECRET + "\u202e" + "confidential"
        self.assert_hold(self.base() + ["--window-days", suspicious], suspicious)

    def test_noninteger_boolean_text_window_redacted(self):
        self.assert_hold(self.base() + ["--window-days", "True"])

    def test_integer_outside_window_bound_holds(self):
        self.assert_hold(self.base() + ["--window-days", "366"])

    def test_inapplicable_mapping_option_holds(self):
        self.assert_hold(self.base() + ["--left-amount-column", SECRET])

    def test_empty_argument_list_holds_without_usage(self):
        self.assert_hold([])

    def test_double_dash_stray_private_position_holds(self):
        self.assert_hold(self.base() + ["--", SECRET])

    def test_bad_arguments_leave_original_bytes_unchanged(self):
        original_report = self.create_real_spend()
        before = (self.source.read_bytes(), original_report.read_bytes())
        self.assert_hold(["--kind", "spend-map", "--report", str(original_report),
                          "--source", str(self.source), "--window-days", SECRET])
        self.assertEqual((self.source.read_bytes(), original_report.read_bytes()), before)

    def test_valid_spend_replay_keeps_success_contract(self):
        original_report = self.create_real_spend()
        status, out, err = self.invoke(["--kind", "spend-map",
            "--report", str(original_report), "--source", str(self.source)])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertIn("LOCAL REPLAY VERIFIED", out)
        self.assertIn(hashlib.sha256(original_report.read_bytes()).hexdigest(), out)
        self.assertNotIn(SECRET, out)
        self.assertNotIn(str(self.source), out)

    def test_native_python_module_invalid_option_redacted(self):
        env = os.environ.copy()
        desktop = str(Path(__file__).resolve().parents[1])
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (desktop, env.get("PYTHONPATH", "")) if part)
        command = [sys.executable, "-m", "fvs_suite.replay_verify", *self.base(),
                   "--window-days", SECRET]
        result = subprocess.run(command, cwd=str(self.root), env=env,
                                text=True, capture_output=True, timeout=35,
                                check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, GENERIC_HOLD)
        self.assertNotIn(SECRET, result.stderr)


if __name__ == "__main__":
    unittest.main()
