"""R108 strict Tk event/cancellation evidence tests; no GUI or filesystem needed."""
from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import native_shortcut_events_r108 as probe


def sample(app_id="ledger"):
    required = probe.FREE_INPUTS[app_id]
    return dict(input_focus=required, input_cancels=required, output_focus=True,
                output_cancel=True, blocked_generates=2, warnings=2,
                engine_calls=0, files_selected=0, extra_dialogs=0,
                premium_opened=False)


class NativeShortcutEventsR108(unittest.TestCase):
    def reject(self, **changes):
        observed = sample()
        observed.update(changes)
        with self.assertRaises(probe.ShortcutBlocked):
            probe.verify_snapshot("ledger", **observed)

    def test_exact_four_free_product_inventory(self):
        self.assertEqual(probe.FREE_INPUTS, {"ledger": 2, "invoices": 1,
                                            "spend": 1, "policy": 2})

    def test_four_complete_event_contracts(self):
        for app_id in probe.FREE_INPUTS:
            with self.subTest(app=app_id):
                probe.verify_snapshot(app_id, **sample(app_id))

    def test_premium_access_cannot_enter_free_probe(self):
        with self.assertRaises(probe.ShortcutBlocked):
            probe.verify_snapshot("grants", **sample())
        with self.assertRaises(probe.ShortcutBlocked):
            probe.verify_snapshot("procurement", **sample())

    def test_unknown_app_rejected(self):
        with self.assertRaises(probe.ShortcutBlocked):
            probe.verify_snapshot("unknown", **sample())

    def test_missing_input_focus_rejected(self):
        self.reject(input_focus=1)

    def test_extra_input_focus_rejected(self):
        self.reject(input_focus=3)

    def test_cancelled_input_picker_must_run(self):
        self.reject(input_cancels=1)

    def test_replayed_cancelled_picker_rejected(self):
        self.reject(input_cancels=3)

    def test_output_focus_must_be_actual_boolean(self):
        self.reject(output_focus=False)
        self.reject(output_focus=1)

    def test_output_cancel_must_be_actual_boolean(self):
        self.reject(output_cancel=False)
        self.reject(output_cancel=1)

    def test_generate_requires_two_distinct_warning_events(self):
        self.reject(warnings=1)
        self.reject(blocked_generates=1)

    def test_generate_extra_warning_rejected(self):
        self.reject(warnings=3)

    def test_engine_must_never_run_on_empty_inputs(self):
        self.reject(engine_calls=1)

    def test_browse_must_never_select_a_file(self):
        self.reject(files_selected=1)

    def test_other_dialogs_are_forbidden(self):
        self.reject(extra_dialogs=1)

    def test_premium_editor_must_not_be_opened(self):
        self.reject(premium_opened=True)
        self.reject(premium_opened=0)

    def test_truthy_and_negative_counts_rejected(self):
        self.reject(input_cancels=True)
        self.reject(engine_calls=False)
        self.reject(warnings=-1)

    def test_extra_cli_argument_denied_without_details(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertEqual(probe.main(["--customer-path=/private.csv"]), 1)
        self.assertEqual(output.getvalue().strip(), probe.ERROR)
        self.assertNotIn("private.csv", output.getvalue())

    def test_linux_native_probe_cannot_claim_pass(self):
        if sys.platform == "win32":
            self.skipTest("Native runner tests handled by Windows CI")
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertEqual(probe.main([]), 1)
        self.assertEqual(output.getvalue().strip(), probe.ERROR)

    def test_no_assert_bypass_in_check_logic(self):
        import ast
        source = (SCRIPTS / "native_shortcut_events_r108.py").read_text(encoding="utf-8")
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(source))))


if __name__ == "__main__":
    unittest.main()
