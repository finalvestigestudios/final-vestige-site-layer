"""Source-only adversarial R106 keyboard preflight tests: no Tk display needed."""
import contextlib
import io
import unittest

from scripts import native_keyboard_probe_r106 as audit


def fixture(app_id="ledger"):
    count, title = audit.FREE[app_id]
    labels = tuple(f"Required input {n}" for n in range(1, count + 1))
    ledger = app_id == "ledger"
    invoices = app_id == "invoices"
    return dict(
        window_title=title,
        entry_count=count + 1 + (4 if ledger else 1 if invoices else 0),
        traversal=audit._expected_order(count, ledger_keys=ledger,
                                        invoice_window=invoices),
        cycle_closed=True,
        bindings=audit._expected_bindings(count),
        first_focus=True,
        static_labels=labels + (audit.LEDGER_KEY_LABELS + audit.LEDGER_AMOUNT_LABELS if ledger else ())
                      + ((audit.INVOICE_WINDOW_LABEL,) if invoices else ()) + (
            "Output folder",
            "Local-first review tools. Findings are not audit, legal, or fraud determinations.",
            "Keyboard: Alt+1..3 focus input; Ctrl+1..3 browse; Alt+O/Ctrl+O output; "
            "Alt+G/Ctrl+Enter generate",
        ),
        source_input_labels=labels,
    )


class NativeKeyboardContractR106(unittest.TestCase):
    def check_blocked(self, app_id="ledger", **alterations):
        payload = fixture(app_id)
        payload.update(alterations)
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verify_snapshot(app_id, **payload)

    def test_all_four_free_ui_contracts_accepted(self):
        for app_id in audit.FREE:
            with self.subTest(app=app_id):
                audit._verify_snapshot(app_id, **fixture(app_id))

    def test_inventory_excludes_both_premium_products(self):
        self.assertEqual(set(audit.FREE), {"ledger", "invoices", "spend", "policy"})
        self.check_blocked("ledger", entry_count=0)
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verify_snapshot("grants", **fixture())

    def test_invalid_order_length_rejected(self):
        self.check_blocked(traversal=audit._expected_order(2)[:-1])

    def test_invalid_tab_order_rejected(self):
        order = list(audit._expected_order(2, ledger_keys=True))
        order[0], order[1] = order[1], order[0]
        self.check_blocked(traversal=tuple(order))

    def test_duplicate_focus_target_rejected(self):
        order = list(audit._expected_order(2, ledger_keys=True))
        order[1] = order[0]
        self.check_blocked(traversal=tuple(order))

    def test_unexpected_focus_target_rejected(self):
        order = list(audit._expected_order(2, ledger_keys=True))
        order[2] = "<unverified>"
        self.check_blocked(traversal=tuple(order))

    def test_tab_cycle_must_return_to_first_field(self):
        self.check_blocked(cycle_closed=False)

    def test_first_field_must_receive_focus(self):
        self.check_blocked(first_focus=False)

    def test_wrong_main_window_title_rejected(self):
        self.check_blocked(window_title="Impostor LedgerDiff Lite")

    def test_missing_required_entry_rejected(self):
        self.check_blocked(entry_count=2)

    def test_non_integer_entry_count_rejected(self):
        self.check_blocked(entry_count=True)

    def test_missing_numeric_focus_accelerator(self):
        keys = set(audit._expected_bindings(2))
        keys.remove("<Alt-Key-1>")
        self.check_blocked(bindings=frozenset(keys))

    def test_missing_numeric_browse_accelerator(self):
        keys = set(audit._expected_bindings(2))
        keys.remove("<Control-Key-2>")
        self.check_blocked(bindings=frozenset(keys))

    def test_missing_output_accelerator(self):
        keys = set(audit._expected_bindings(2))
        keys.remove("<Control-Key-o>")
        self.check_blocked(bindings=frozenset(keys))

    def test_missing_generate_accelerator(self):
        keys = set(audit._expected_bindings(2))
        keys.remove("<Control-Return>")
        self.check_blocked(bindings=frozenset(keys))

    def test_premium_shortcut_on_free_app_refused(self):
        keys = audit._expected_bindings(2) | {"<Alt-Key-r>"}
        self.check_blocked(bindings=frozenset(keys))

    def test_bindings_must_be_a_frozenset(self):
        self.check_blocked(bindings=set(audit._expected_bindings(2)))

    def test_missing_input_label_rejected(self):
        labels = tuple(item for item in fixture()["static_labels"]
                       if item != "Required input 1")
        self.check_blocked(static_labels=labels)

    def test_missing_output_label_rejected(self):
        labels = tuple(item for item in fixture()["static_labels"]
                       if item != "Output folder")
        self.check_blocked(static_labels=labels)

    def test_missing_visible_shortcut_hint_rejected(self):
        labels = tuple(item for item in fixture()["static_labels"]
                       if not item.startswith("Keyboard:"))
        self.check_blocked(static_labels=labels)

    def test_missing_disclaimer_rejected(self):
        labels = tuple(item for item in fixture()["static_labels"]
                       if not item.startswith("Local-first review tools"))
        self.check_blocked(static_labels=labels)

    def test_untrusted_nonstring_labels_rejected(self):
        self.check_blocked(static_labels=("Required input 1", 12, "Output folder"))

    def test_source_input_label_count_matters(self):
        self.check_blocked(source_input_labels=("Required input 1",))

    def test_unsupported_expected_order_refuses_both_modes(self):
        for count in (0, 4, False, "2"):
            with self.subTest(count=count):
                with self.assertRaises(audit.KeyboardBlocked):
                    audit._expected_order(count)

    def test_explicit_invalid_cli_refuses_without_private_details(self):
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured):
            code = audit.main(["--unexpected"])
        self.assertEqual(code, 1)
        self.assertEqual(captured.getvalue().strip(), audit.ERROR)


    def test_source_scheduled_first_focus_is_accepted(self):
        class Input:
            def focus_set(self):
                pass
        root = object()
        entry = Input()
        self.assertEqual(audit._verified_initial_focus(
            [(root, entry.focus_set, ())], root, entry).__name__, "focus_set")

    def test_missing_or_multiple_focus_schedules_rejected(self):
        class Input:
            def focus_set(self):
                pass
        root, entry = object(), Input()
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([], root, entry)
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([
                (root, entry.focus_set, ()), (root, entry.focus_set, ())
            ], root, entry)

    def test_unrelated_window_focus_schedule_rejected(self):
        class Input:
            def focus_set(self):
                pass
        root, entry = object(), Input()
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([(object(), entry.focus_set, ())], root, entry)

    def test_wrong_widget_or_unbound_callback_rejected(self):
        class Input:
            def focus_set(self):
                pass
        root, entry, other = object(), Input(), Input()
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([(root, other.focus_set, ())], root, entry)
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([(root, lambda: None, ())], root, entry)

    def test_focus_schedule_arguments_and_command_rejected(self):
        class Input:
            def focus_set(self):
                pass
            def focus_force(self):
                pass
        root, entry = object(), Input()
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([(root, entry.focus_set, ("unsafe",))], root, entry)
        with self.assertRaises(audit.KeyboardBlocked):
            audit._verified_initial_focus([(root, entry.focus_force, ())], root, entry)



if __name__ == "__main__":
    unittest.main()
