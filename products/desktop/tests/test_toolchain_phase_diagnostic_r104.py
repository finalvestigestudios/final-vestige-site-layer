"""R104 synthetic-only privacy and fail-closed toolchain diagnostic tests."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import re
import unittest
from unittest.mock import patch

from scripts import diagnose_windows_toolchain_r104 as diag


class ToolchainPhaseDiagnosticR104(unittest.TestCase):
    def test_exact_static_phase_inventory(self):
        self.assertEqual(diag.PHASES,
            ("runtime_file", "distribution_file", "distribution_inventory",
             "snapshot", "evidence_preflight", "evidence_atomic_publish",
             "capture", "verify"))
        self.assertEqual(len(set(diag.PHASES)), len(diag.PHASES))

    def test_synthetic_diagnostic_has_no_release_authorization(self):
        result = diag.diagnose()
        self.assertEqual(set(result), set(diag.PHASES))
        self.assertTrue(all(value in ("PASS", "BLOCKED") for value in result.values()))

    def test_output_contains_only_fixed_static_phase_values(self):
        capture = io.StringIO()
        with redirect_stdout(capture):
            result = diag.main()
        self.assertEqual(result, 0)
        lines = capture.getvalue().splitlines()
        self.assertEqual(len(lines), len(diag.PHASES) + 1)
        self.assertEqual(lines[-1], "FVS_R104_RELEASE=HOLD_READ_ONLY_SOURCE_DIAGNOSTIC")
        for name, line in zip(diag.PHASES, lines):
            self.assertRegex(line, "^FVS_R104_TOOLCHAIN:" + re.escape(name) + "=(PASS|BLOCKED)$")

    def test_private_exception_text_and_absolute_paths_never_escape(self):
        secret = "CUSTOMER-PRIVATE-PATH-INTERNAL"
        capture = io.StringIO()
        with patch.object(diag.gate, "_file_record", side_effect=ValueError(secret)):
            with redirect_stdout(capture):
                self.assertEqual(diag.main(), 0)
        output = capture.getvalue()
        self.assertNotIn(secret, output)
        self.assertIn("FVS_R104_TOOLCHAIN:runtime_file=BLOCKED", output)
        self.assertIn("FVS_R104_RELEASE=HOLD_READ_ONLY_SOURCE_DIAGNOSTIC", output)


if __name__ == "__main__":
    unittest.main()
