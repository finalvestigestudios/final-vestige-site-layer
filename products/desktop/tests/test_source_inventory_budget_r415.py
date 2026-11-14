"""R415: a finite offline source tree is a prerequisite for six-app receipts.

Fixtures are synthetic, not full financial engines or native Windows builds.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class OfflineSourceInventoryBudgetR415(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "desktop"
        self.desktop.mkdir()
        (self.desktop / "fvs_suite").mkdir()
        (self.desktop / "launchers").mkdir()
        (self.desktop / "fvs_suite" / "__init__.py").write_text("# synthetic\n", encoding="utf-8")
        (self.desktop / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(8)\n", encoding="utf-8")
        (self.desktop / "offline_source_smoke_r408.py").write_bytes(
            Path(gate.__file__).read_bytes())
        for app, name in gate.PRODUCTS:
            (self.desktop / "launchers" / name).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")

    def _asset(self, name, *, folder="fvs_suite", size=1):
        path = self.desktop / folder / name
        path.write_bytes(b"x" * size)
        return path

    def _assert_held_before_child(self):
        with patch.object(gate.subprocess, "run") as spawned:
            with self.assertRaisesRegex(gate.SourceGateError,
                                        "Desktop source inventory exceeds safe bounds") as caught:
                gate.run_gate(self.desktop)
        spawned.assert_not_called()
        return str(caught.exception)

    def test_six_apps_still_pass_both_modes_under_budget(self):
        result = gate.run_gate(self.desktop)
        self.assertEqual(result["required"], 12)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(len(result["tests"]), 6)
        self.assertFalse(result["release_authorized"])

    def test_count_limit_rejects_before_any_child(self):
        for index in range(gate.MAX_IMPORT_FILES):
            self._asset(f"padding_{index:04}.json")
        self._assert_held_before_child()

    def test_count_budget_includes_both_import_roots(self):
        for index in range(260):
            self._asset(f"data_{index:04}.json", folder="launchers")
        for index in range(260):
            self._asset(f"data_{index:04}.json", folder="fvs_suite")
        self._assert_held_before_child()

    def test_many_empty_subdirectories_rejected_before_child(self):
        for index in range(gate.MAX_IMPORT_DIRS):
            (self.desktop / "fvs_suite" / f"nested_{index:04}").mkdir()
        self._assert_held_before_child()

    def test_deep_directory_count_includes_grandchildren(self):
        for index in range(65):
            parent = self.desktop / "fvs_suite" / f"parent_{index:04}"
            parent.mkdir()
            (parent / "child").mkdir()
        self._assert_held_before_child()

    def test_total_source_bytes_bounded_before_any_child(self):
        for index in range(9):
            self._asset(f"large_{index}.json", size=1_900_000)
        self._assert_held_before_child()

    def test_total_bytes_accumulate_across_import_roots(self):
        for index in range(5):
            self._asset(f"large_{index}.json", folder="fvs_suite", size=1_900_000)
            self._asset(f"large_{index}.json", folder="launchers", size=1_900_000)
        self._assert_held_before_child()

    def test_single_large_asset_rejected_before_materialization(self):
        self._asset("oversized.dat", size=gate.MAX_SOURCE_BYTES + 1)
        self._assert_held_before_child()

    def test_zero_byte_extra_asset_is_not_attested(self):
        self._asset("empty.csv", size=0)
        self._assert_held_before_child()

    def test_private_filename_is_never_in_budget_diagnostic(self):
        secret = "CONFIDENTIAL_CLIENT_BUDGET_Z91"
        self._asset(secret + ".csv", size=gate.MAX_SOURCE_BYTES + 1)
        message = self._assert_held_before_child()
        self.assertNotIn(secret, message)
        self.assertNotIn(str(self.desktop), message)

    def test_budget_resets_between_independent_checks(self):
        temp = self._asset("too-big.txt", size=gate.MAX_SOURCE_BYTES + 1)
        self._assert_held_before_child()
        temp.unlink()
        with patch.object(
                gate.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0)) as run:
            receipt = gate.run_gate(self.desktop)
        self.assertEqual(receipt["passed"], 12)
        self.assertEqual(run.call_count, 12)

    def test_source_digest_is_stable_for_a_small_nonempty_asset(self):
        self._asset("provenance.json", size=37)
        self.assertEqual(gate.source_digest(self.desktop), gate.source_digest(self.desktop))


if __name__ == "__main__":
    unittest.main()
