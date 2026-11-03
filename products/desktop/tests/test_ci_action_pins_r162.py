"""R162 synthetic provenance tests: immutable action references, no executable upload."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import ci_action_pin_guard as guard


CHECKOUT = "actions/checkout@" + guard.APPROVED["actions/checkout"]
PYTHON = "actions/setup-python@" + guard.APPROVED["actions/setup-python"]
UPLOAD = "actions/upload-artifact@" + guard.APPROVED["actions/upload-artifact"]
GOOD = ("name: Internal desktop suite\n"
        "jobs:\n"
        "  source-tests:\n"
        "    steps:\n"
        f"      - uses: {CHECKOUT}\n"
        f"      - uses: {PYTHON}\n"
        f"      - name: Evidence only\n        uses: {UPLOAD}\n"
        "  windows-build:\n"
        "    steps:\n"
        f"      - uses: {CHECKOUT}\n"
        f"      - uses: {PYTHON}\n"
        f"      - name: Evidence only\n        uses: {UPLOAD}\n")


class ActionPinR162(unittest.TestCase):
    def rejected(self, candidate):
        with self.assertRaises(guard.ActionPinError):
            guard.verify_action_pins(candidate)

    def test_six_exact_refs_accepted(self):
        self.assertEqual(guard.verify_action_pins(GOOD), 6)

    def test_pinned_actions_not_mutable_names(self):
        for value in guard.APPROVED.values():
            self.assertRegex(value, r"^[0-9a-f]{40}$")

    def test_all_six_calls_are_required(self):
        self.rejected(GOOD.replace(f"uses: {UPLOAD}", "run: echo offline", 1))

    def test_duplicate_upload_is_denied(self):
        self.rejected(GOOD + f"      - uses: {UPLOAD}\n")

    def test_unknown_action_is_denied(self):
        self.rejected(GOOD + "      - uses: unknown/diagnostics@0123456789012345678901234567890123456789\n")

    def test_mutable_checkout_major_tag_denied(self):
        self.rejected(GOOD.replace(CHECKOUT, "actions/checkout@v4"))

    def test_mutable_python_major_tag_denied(self):
        self.rejected(GOOD.replace(PYTHON, "actions/setup-python@v5"))

    def test_mutable_upload_major_tag_denied(self):
        self.rejected(GOOD.replace(UPLOAD, "actions/upload-artifact@v4"))

    def test_mutable_main_branch_denied(self):
        self.rejected(GOOD.replace(CHECKOUT, "actions/checkout@main"))

    def test_action_ref_sha_substitution_denied(self):
        self.rejected(GOOD.replace(guard.APPROVED["actions/checkout"],
                                   "0" * 40))

    def test_expression_action_ref_denied(self):
        self.rejected(GOOD.replace(CHECKOUT, "actions/checkout@${{ vars.CHECKOUT_SHA }}"))

    def test_multiple_at_symbols_denied(self):
        self.rejected(GOOD.replace(CHECKOUT, CHECKOUT + "@main"))

    def test_missing_at_symbol_denied(self):
        self.rejected(GOOD.replace(CHECKOUT, "actions/checkout"))

    def test_comment_does_not_satisfy_missing_action(self):
        self.rejected(GOOD.replace(f"uses: {UPLOAD}", "run: echo offline", 1)
                      + f"      # uses: {UPLOAD}\n")

    def test_legitimate_comment_is_ignored(self):
        self.assertEqual(guard.verify_action_pins(GOOD + "      # uses: fabricated/action@v1\n"), 6)

    def test_any_additional_action_denied(self):
        self.rejected(GOOD + "      - name: injected\n        uses: actions/upload-artifact@v4\n")

    def test_oversized_workflow_denied(self):
        self.rejected(GOOD + "#" * guard.MAX_WORKFLOW_BYTES)

    def test_nul_or_tabs_denied(self):
        for suffix in ("\x00", "\t"):
            with self.subTest(suffix=repr(suffix)):
                self.rejected(GOOD + suffix)

    def test_cli_privacy_hold(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            self.assertEqual(guard.main(["/private/client/annual-ledger.yml"]), 1)
        self.assertNotIn("annual-ledger", out.getvalue())
        self.assertNotIn("/private", out.getvalue())

    def test_cli_success(self):
        with tempfile.TemporaryDirectory(prefix="fvs-actions-r162-") as tmp:
            file = Path(tmp) / "workflow.yml"
            file.write_text(GOOD, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(guard.main([str(file)]), 0)
            self.assertIn("NOT a release", out.getvalue())

    def test_actual_workflow_all_refs_pinned(self):
        workflow = Path(__file__).resolve().parents[3] / ".github/workflows/desktop-build.yml"
        self.assertTrue(workflow.is_file(), "Full CI checkout required for action provenance")
        self.assertEqual(guard.verify_action_pins(workflow.read_text(encoding="utf-8")), 6)


if __name__ == "__main__":
    unittest.main()
