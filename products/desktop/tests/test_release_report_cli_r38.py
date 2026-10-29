"""R38 CLI integration: never smoke for an invalid evidence destination."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import release_gate as gate
from report_evidence import ReportEvidenceError


class ReleaseReportCliR38Tests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="fvs-r38-cli-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.out = self.root / "evidence.json"
        self.sample = {"schema": 1, "status": "integrity_only", "release_authorized": False,
                       "premium_entitlement_verified": False, "artifacts": []}

    def test_cli_publishes_outside_candidate_and_never_authorizes_release(self):
        with patch.object(gate, "verify", return_value=self.sample) as verify:
            self.assertEqual(gate.main([str(self.dist), "--report", str(self.out)]), 0)
        verify.assert_called_once_with(str(self.dist), smoke=False)
        self.assertEqual(json.loads(self.out.read_text()), self.sample)
        self.assertEqual(list(self.dist.iterdir()), [])

    def test_inside_candidate_fails_without_executing_verifier(self):
        with patch.object(gate, "verify") as verify:
            self.assertEqual(gate.main([str(self.dist), "--smoke", "--report",
                                        str(self.dist / "fake.json")]), 1)
        verify.assert_not_called()
        self.assertEqual(list(self.dist.iterdir()), [])

    def test_existing_destination_fails_before_verification(self):
        self.out.write_text("preserve")
        with patch.object(gate, "verify") as verify:
            self.assertEqual(gate.main([str(self.dist), "--smoke", "--report", str(self.out)]), 1)
        verify.assert_not_called()
        self.assertEqual(self.out.read_text(), "preserve")

    def test_report_link_failure_keeps_candidate_unchanged(self):
        with patch.object(gate, "verify", return_value=self.sample), \
             patch.object(gate, "publish_report", side_effect=ReportEvidenceError("failed")):
            self.assertEqual(gate.main([str(self.dist), "--report", str(self.out)]), 1)
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.dist.iterdir()), [])

    def test_cli_without_report_retains_old_behavior(self):
        with patch.object(gate, "verify", return_value=self.sample) as verify:
            self.assertEqual(gate.main([str(self.dist)]), 0)
        verify.assert_called_once()


if __name__ == "__main__":
    unittest.main()
