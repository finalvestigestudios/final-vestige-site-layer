"""R132 source-owned Linux/Windows regressions for native LedgerDiff mapping controls.

No customer paths, network, dialogs or premium editors. Actual Tk event/scale
coverage remains mandatory in the Windows native R106/R107/R108 CI steps.
"""
from __future__ import annotations

import unittest

from scripts import native_keyboard_probe_r106 as keyboard
from scripts import native_scale_probe_r107 as scale
from scripts import native_shortcut_events_r108 as events


def observed_ledger():
    labels = ("Left ledger CSV", "Right ledger CSV")
    return dict(
        window_title=keyboard.FREE["ledger"][1],
        entry_count=7,
        traversal=keyboard._expected_order(2, ledger_keys=True),
        cycle_closed=True,
        bindings=keyboard._expected_bindings(2),
        first_focus=True,
        static_labels=labels + keyboard.LEDGER_KEY_LABELS + keyboard.LEDGER_AMOUNT_LABELS + (
            "Output folder",
            "Local-first review tools. Findings are not audit, legal, or fraud determinations.",
            "Keyboard: Alt+1..2 focus; Ctrl+1..2 browse; Alt+G/Ctrl+Enter generate",
        ),
        source_input_labels=labels,
    )


def scaled_ledger(scale_value=2.0):
    return dict(scale=scale_value, entries=7, browse=3, generate=1,
                scrollable=True, focus_revealed=True, labels_wrapped=True,
                controls_nonfocus=True, system_background=True)


class LedgerNativeAccessibilityR132(unittest.TestCase):
    def test_ledger_has_two_visible_key_entry_tab_stops(self):
        self.assertEqual(keyboard._expected_order(2, ledger_keys=True), (
            "input_1", "browse_1", "input_2", "browse_2",
            "ledger_left_key", "ledger_right_key",
            "ledger_left_amount", "ledger_right_amount", "output", "browse_output",
            "generate"))

    def test_original_free_app_tab_order_unchanged(self):
        for count in (1, 2, 3):
            with self.subTest(count=count):
                self.assertEqual(
                    keyboard._expected_order(count),
                    tuple(item for pair in
                          ((f"input_{i}", f"browse_{i}") for i in range(1, count+1))
                          for item in pair) + ("output", "browse_output", "generate"))

    def test_ledger_five_entry_native_snapshot_is_valid(self):
        keyboard._verify_snapshot("ledger", **observed_ledger())

    def test_legacy_ledger_tab_order_is_no_longer_sufficient(self):
        sample = observed_ledger()
        sample["traversal"] = keyboard._expected_order(2)
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_reversed_ledger_match_key_tab_order_blocks(self):
        sample = observed_ledger()
        sequence = list(sample["traversal"])
        sequence[4:6] = reversed(sequence[4:6])
        sample["traversal"] = tuple(sequence)
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_missing_optional_ledger_entry_blocks(self):
        sample = observed_ledger()
        sample["entry_count"] = 8
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_extra_ledger_entry_blocks(self):
        sample = observed_ledger()
        sample["entry_count"] = 8
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_missing_left_key_label_blocks(self):
        sample = observed_ledger()
        sample["static_labels"] = tuple(
            s for s in sample["static_labels"] if s != keyboard.LEDGER_KEY_LABELS[0])
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_missing_right_key_label_blocks(self):
        sample = observed_ledger()
        sample["static_labels"] = tuple(
            s for s in sample["static_labels"] if s != keyboard.LEDGER_KEY_LABELS[1])
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_ledger_key_labels_do_not_leak_into_other_free_apps(self):
        sample = observed_ledger()
        sample["window_title"] = keyboard.FREE["policy"][1]
        sample["entry_count"] = 3
        sample["traversal"] = keyboard._expected_order(2)
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("policy", **sample)

    def test_source_owned_ledger_shortcuts_remain_required(self):
        sample = observed_ledger()
        sample["bindings"] = frozenset(
            key for key in sample["bindings"] if key != "<Control-Key-2>")
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("ledger", **sample)

    def test_scaled_ledger_five_entries_three_browse_at_both_scales(self):
        for factor in scale.SCALES:
            with self.subTest(factor=factor):
                scale.verify_snapshot("ledger", **scaled_ledger(factor))

    def test_scaled_ledger_rejects_old_three_entry_inventory(self):
        sample = scaled_ledger()
        sample["entries"] = 3
        with self.assertRaises(scale.ScaleBlocked):
            scale.verify_snapshot("ledger", **sample)

    def test_scaled_ledger_rejects_missing_browse(self):
        sample = scaled_ledger()
        sample["browse"] = 2
        with self.assertRaises(scale.ScaleBlocked):
            scale.verify_snapshot("ledger", **sample)

    def test_scaled_other_free_apps_still_need_one_output_entry(self):
        for app_id, required in scale.FREE_INPUTS.items():
            if app_id == "ledger":
                continue
            for factor in scale.SCALES:
                with self.subTest(app_id=app_id, factor=factor):
                    sample = scaled_ledger(factor)
                    # R134 adds a keyboard-focusable review-window entry to
                    # Invoice Twin only; do not relax any native scale gate.
                    sample["entries"] = required + 1 + (1 if app_id == "invoices" else 0)
                    sample["browse"] = required + 1
                    scale.verify_snapshot(app_id, **sample)

    def test_scaled_entry_bool_is_not_a_count(self):
        sample = scaled_ledger()
        sample["entries"] = True
        with self.assertRaises(scale.ScaleBlocked):
            scale.verify_snapshot("ledger", **sample)

    def test_ledger_cancel_events_still_require_no_engine_calls(self):
        sample = dict(input_focus=2, input_cancels=2, output_focus=True,
                      output_cancel=True, blocked_generates=2, warnings=2,
                      engine_calls=0, files_selected=0, extra_dialogs=0,
                      premium_opened=False)
        events.verify_snapshot("ledger", **sample)
        sample["engine_calls"] = 1
        with self.assertRaises(events.ShortcutBlocked):
            events.verify_snapshot("ledger", **sample)

    def test_premium_apps_rejected_by_all_three_native_contracts(self):
        sample = observed_ledger()
        with self.assertRaises(keyboard.KeyboardBlocked):
            keyboard._verify_snapshot("grants", **sample)
        with self.assertRaises(scale.ScaleBlocked):
            scale.verify_snapshot("procurement", **scaled_ledger())
        with self.assertRaises(events.ShortcutBlocked):
            events.verify_snapshot(
                "grants", input_focus=0, input_cancels=0, output_focus=True,
                output_cancel=True, blocked_generates=0, warnings=0,
                engine_calls=0, files_selected=0, extra_dialogs=0,
                premium_opened=False)


    def test_scaled_access_failure_reports_only_fixed_reason_code(self):
        sample = scaled_ledger()
        sample["focus_revealed"] = False
        with self.assertRaises(scale.ScaleBlocked) as caught:
            scale.verify_snapshot("ledger", **sample)
        message = scale.safe_failure("ledger", 4.0, caught.exception)
        self.assertIn("app=ledger", message)
        self.assertIn("zoom=400%", message)
        self.assertIn("check=focus", message)

    def test_private_exception_text_never_reaches_native_diagnostic(self):
        marker = "customer-account-0001234"
        for exception in (ValueError(marker), RuntimeError(marker),
                          scale.ScaleBlocked(marker)):
            with self.subTest(kind=type(exception).__name__):
                text = scale.safe_failure("ledger", 2.0, exception)
                self.assertIn("check=unexpected", text)
                self.assertNotIn(marker, text)

    def test_unknown_diagnostic_scope_fails_without_private_details(self):
        marker = "private-financial-98765"
        result = scale.safe_failure("grants", 4.0, scale.ScaleBlocked(marker))
        self.assertEqual(result, scale.ERROR)
        self.assertNotIn(marker, result)
        result = scale.safe_failure("ledger", 3.0, scale.ScaleBlocked(marker))
        self.assertEqual(result, scale.ERROR)


if __name__ == "__main__":
    unittest.main()
