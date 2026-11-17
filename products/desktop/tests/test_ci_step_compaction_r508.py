"""R508: preserve fail-closed CI guards while restoring the reviewed workflow budget.

Static source checks only. These tests do not execute an EXE, publish assets,
approve QD, assert runner availability, or replace release validation.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from ci_workflow_budget_r292 import MAX_WORKFLOW_BYTES

WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/desktop-build.yml"


class DesktopCIBudgetR508(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = WORKFLOW.read_bytes()
        cls.text = cls.raw.decode("utf-8")

    def test_reviewed_224_kib_limit_is_restored_without_relaxation(self):
        self.assertEqual(MAX_WORKFLOW_BYTES, 224 * 1024)
        self.assertGreater(len(self.raw), 192 * 1024)
        self.assertLessEqual(len(self.raw), MAX_WORKFLOW_BYTES)

    def test_both_job_boundaries_and_action_pins_remain(self):
        for expected in (
            "  source-tests:",
            "  windows-build:",
            "actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8",
            "actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c",
        ):
            self.assertIn(expected, self.text)

    def test_inherited_python_regressions_are_not_pruned(self):
        self.assertGreaterEqual(
            self.text.count("-m unittest discover -s products/desktop/tests"), 816
        )
        self.assertGreaterEqual(len(re.findall(r"(?m)^\s*- name: ", self.text)), 492)

    def test_native_nonzero_exit_guards_remain(self):
        self.assertGreaterEqual(
            self.text.count("if ($LASTEXITCODE -ne 0)"), 566
        )
        self.assertNotIn("continue-on-error: true", self.text)

    def test_shorter_messages_still_throw_and_identify_revision(self):
        failures = re.findall(
            r'(?m)^\s*if \(\$LASTEXITCODE -ne 0\) '
            r'\{ throw "R\d+ test FAILED" \}$',
            self.text,
        )
        self.assertGreaterEqual(len(failures), 521)

    def test_critical_release_and_premium_holds_stay_explicit(self):
        for expected in (
            'throw "R9 binary integrity/smoke gate failed"',
            'throw "R118 actual-six-EXE private roundtrip FAILED; HOLD"',
            'throw "R105 GUI or premium lock unavailable; release HOLD"',
            "dist/SHA256SUMS.txt",
            "run: python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml",
        ):
            self.assertIn(expected, self.text)

    def test_unsafe_input_is_not_introduced_by_compression(self):
        self.assertNotIn(b"\x00", self.raw)
        self.assertNotIn(b"\t", self.raw)


if __name__ == "__main__":
    unittest.main()
