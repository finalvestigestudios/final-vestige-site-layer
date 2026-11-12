"""R21: evidence from synthetic source smokes must never imply verified EXEs."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "source_smoke_gate.py"
SPEC = importlib.util.spec_from_file_location("source_smoke_gate_r21", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class SourceSmokeGateR21Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r21-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        package = self.root / "products" / "desktop" / "fvs_suite"
        launchers = self.root / "products" / "desktop" / "launchers"
        package.mkdir(parents=True)
        launchers.mkdir()
        (package / "smoke.py").write_text("# synthetic mock engine\n", encoding="utf-8")
        for name, _ in gate.APPS:
            (launchers / (name + ".py")).write_text("# launcher fixture\n", encoding="utf-8")

    def test_six_distinct_apps_and_tier_names(self):
        self.assertEqual(len(gate.APPS), 6)
        self.assertEqual(len(set(gate.APPS)), 6)
        self.assertEqual([n for n, _ in gate.APPS][-2:],
                         ["GrantAuditStudioPro", "ProcureGuardStudioPro"])

    def test_inventory_is_stable_and_sha256_changes_with_source(self):
        before = gate.source_inventory(self.root)
        self.assertEqual(len(before), 7)
        self.assertEqual(before, gate.source_inventory(self.root))
        p = self.root / "products" / "desktop" / "fvs_suite" / "smoke.py"
        p.write_text("# mutated source\n", encoding="utf-8")
        after = gate.source_inventory(self.root)
        self.assertNotEqual(before, after)
        self.assertTrue(all(len(x["sha256"]) == 64 for x in before))

    def test_missing_launcher_fails_closed(self):
        (self.root / "products" / "desktop" / "launchers" / "PolicyDeltaDesk.py").unlink()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            gate.source_inventory(self.root)

    def test_symlinked_source_rejected(self):
        file = self.root / "products" / "desktop" / "launchers" / "LedgerDiffLite.py"
        file.unlink()
        try:
            file.symlink_to(self.root / "products" / "desktop" / "fvs_suite" / "smoke.py")
        except OSError:
            self.skipTest("Symlinks not available on this system")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            gate.source_inventory(self.root)

    def test_all_six_called_and_marked_source_only(self):
        calls = []
        def fake(app):
            calls.append(app)
            # All six real smoke contracts have fixed report multiplicity.
            from scripts.smoke_receipt_contract_r387 import EXPECTED_REPORT_COUNTS
            return [Path(f"report-{i}.csv") for i in range(EXPECTED_REPORT_COUNTS[app])]
        data = gate.report_data(self.root, fake, commit="abc123")
        self.assertEqual(calls, [app for _, app in gate.APPS])
        self.assertTrue(data["all_six_passed"])
        self.assertFalse(data["released"])
        self.assertFalse(data["qd_approved"])
        self.assertIn("NOT_WINDOWS_BINARY", data["scope"])
        self.assertEqual(len(data["application_results"]), 6)

    def test_empty_smoke_result_fails_without_success_evidence(self):
        with self.assertRaisesRegex(RuntimeError, "no source-smoke outputs"):
            gate.report_data(self.root, lambda app: [] if app == "spend" else [Path("ok.csv")])

    def test_exception_from_app_propagates_and_stops_further_work(self):
        calls = []
        def fake(app):
            calls.append(app)
            if app == "invoices":
                raise ValueError("Synthetic smoke failure")
            return [Path("report.csv")]
        with self.assertRaisesRegex(ValueError, "Synthetic smoke failure"):
            gate.report_data(self.root, fake)
        self.assertEqual(calls, ["ledger", "invoices"])

    def test_reject_absolute_or_nested_smoke_results(self):
        for result in ([Path("/tmp/unsafe.csv")], [Path("nested/file.csv")]):
            with self.subTest(result=result):
                with self.assertRaisesRegex(RuntimeError, "unsafe"):
                    gate.verify_smokes(lambda app: result)


if __name__ == "__main__":
    unittest.main()
