"""Synthetic failure injections for privacy-safe read-only Windows phase receipts."""
from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import diagnose_windows_source_r100 as probe


class WindowsSourceStageR100(unittest.TestCase):
    def test_all_phases_are_static_and_no_private_exception_leaks(self):
        results = {}
        stdout = io.StringIO()

        def pass_stage():
            print("PRIVATE_ACCOUNT_NUMBER")
            return {"synthetic": 1}

        def fail_stage():
            print("PRIVATE_CUSTOMER_PATH")
            raise ValueError("PRIVATE_CSV_INVOICE_DO_NOT_ECHO")

        with contextlib.redirect_stdout(stdout):
            results["inventory"] = probe._quiet_stage("inventory", pass_stage)
            results["normal_tests"] = probe._quiet_stage("normal_tests", fail_stage)
        transcript = stdout.getvalue()
        self.assertIn("FVS_WIN_SOURCE_STAGE:inventory=PASS", transcript)
        self.assertIn("FVS_WIN_SOURCE_STAGE:normal_tests=BLOCKED", transcript)
        self.assertTrue(results["inventory"][0])
        self.assertFalse(results["normal_tests"][0])
        self.assertNotIn("PRIVATE", transcript)
        self.assertNotIn("INVOICE", transcript)

    def test_unknown_user_supplied_diagnostic_phase_rejected(self):
        with self.assertRaises(ValueError):
            probe._quiet_stage("customer-secret", lambda: None)

    def test_blocked_inventory_does_not_run_source_tests_or_engine_smokes(self):
        from scripts import offline_source_gate as gate
        stdout = io.StringIO()
        with patch.object(gate, "_snapshot", side_effect=ValueError("PRIVATE_CUSTOMER")), \
             patch.object(gate, "_child_suite") as child, \
             patch.object(gate.source_gate, "report_data") as smoke, \
             contextlib.redirect_stdout(stdout):
            states = probe.probe(Path("synthetic"))
        self.assertFalse(states["inventory"])
        self.assertFalse(states["normal_tests"])
        self.assertFalse(states["optimized_tests"])
        self.assertFalse(states["engine_smokes"])
        child.assert_not_called()
        smoke.assert_not_called()
        self.assertIn("NOT_RUN_INVENTORY_BLOCKED", stdout.getvalue())
        self.assertNotIn("PRIVATE", stdout.getvalue())

    def test_independent_phase_receipts_and_no_release_claim(self):
        from scripts import offline_source_gate as gate
        stdout = io.StringIO()
        with patch.object(gate, "_snapshot", return_value=([], [], [], [])), \
             patch.object(gate, "_child_suite", side_effect=ValueError("PRIVATE_TRACEBACK")), \
             patch.object(gate.source_gate, "report_data", return_value={"all_six_passed": True}), \
             contextlib.redirect_stdout(stdout):
            results = probe.probe(Path("synthetic"))
        for phase, expected in {
            "root_paths": False,
            "checked_test_dir": False, "scan_test_tree": False,
            "fingerprint_test": False, "fingerprint_engine": False,
            "source_inventory": False, "test_inventory": False,
            "source_metadata": False,
            "inventory": True, "normal_tests": False,
            "optimized_tests": False, "engine_smokes": True,
        }.items():
            self.assertEqual(results[phase], expected, phase)
        rendered = stdout.getvalue()
        self.assertNotIn("PRIVATE", rendered)
        self.assertIn("FVS_WIN_SOURCE_STAGE:read_only_no_release=TRUE", rendered)


if __name__ == "__main__":
    unittest.main()
