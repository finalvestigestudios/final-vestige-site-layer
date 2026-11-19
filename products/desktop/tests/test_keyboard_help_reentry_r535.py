"""R535: F1 must work inside the independent help Toplevel, not just the form.

All tests use the shared helper used by the six Windows apps. Native Tk tests
skip only when no display is available; the headless tests remain mandatory.
No customer records, license keys, network calls, report writes, or compliance
decisions are involved.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import MagicMock, patch

import fvs_suite.keyboard_access as help_module


LEGEND = (
    "Keyboard: Alt+1 focus input; Ctrl+1 browse file; "
    "Alt+G generate report; F1 opens help"
)


class R535HeadlessDialogReentry(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        self.root._fvs_help_dialog = None
        self.root.winfo_screenwidth.return_value = 1200
        self.root.winfo_screenheight.return_value = 800
        self.previous = MagicMock()
        self.previous.winfo_exists.return_value = True
        self.root.focus_get.return_value = self.previous
        self.dialog = MagicMock()
        self.dialog.winfo_exists.return_value = True
        self.instructions = MagicMock()
        self.instructions.winfo_exists.return_value = True
        self.patches = [
            patch.object(help_module.tk, "Toplevel", return_value=self.dialog),
            patch.object(help_module.tk, "Text", return_value=self.instructions),
            patch.object(help_module.ttk, "Frame", return_value=MagicMock()),
            patch.object(help_module.ttk, "Scrollbar", return_value=MagicMock()),
            patch.object(help_module.ttk, "Button", return_value=MagicMock()),
        ]
        self.ctors = [p.start() for p in self.patches]
        self.addCleanup(lambda: [p.stop() for p in reversed(self.patches)])
        help_module.show_keyboard_help(self.root, LEGEND)

    def f1(self):
        bindings = [call.args[1] for call in self.dialog.bind.call_args_list
                    if call.args[0] == "<F1>"]
        self.assertEqual(len(bindings), 1)
        return bindings[0]

    def test_r535_f1_is_bound_only_on_dialog(self):
        self.f1()
        self.root.bind.assert_not_called()
        self.assertEqual([c.args[0] for c in self.dialog.bind.call_args_list],
                         ["<F1>", "<Escape>"])

    def test_r535_repeat_f1_returns_break_and_refocuses_text(self):
        self.instructions.focus_set.reset_mock()
        self.assertEqual(self.f1()(object()), "break")
        self.dialog.lift.assert_called_once()
        self.instructions.focus_set.assert_called_once()
        self.ctors[0].assert_called_once_with(self.root)
        self.root.get.assert_not_called()

    def test_r535_multiple_f1_presses_keep_single_window(self):
        handler = self.f1()
        self.assertEqual(handler(object()), "break")
        self.assertEqual(handler(object()), "break")
        self.ctors[0].assert_called_once_with(self.root)
        self.assertEqual(self.instructions.focus_set.call_count, 3)

    def test_r535_f1_rebuilds_externally_destroyed_help_text(self):
        successor = MagicMock()
        self.ctors[0].return_value = successor
        self.instructions.winfo_exists.return_value = False
        self.assertEqual(self.f1()(object()), "break")
        self.assertEqual(self.ctors[0].call_count, 2)
        self.dialog.destroy.assert_called_once()
        self.assertIs(self.root._fvs_help_dialog, successor)
        self.assertIs(successor._fvs_former_focus, self.previous)


class R535NativeDialogReentry(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Native Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.entry = ttk.Entry(self.root)
        self.entry.pack()
        self.root.update()
        self.root.focus_force()
        self.entry.focus_set()
        self.root.update()
        help_module.show_keyboard_help(self.root, LEGEND)
        self.root.update()
        self.dialog = self.root._fvs_help_dialog
        self.text = self.dialog._fvs_help_text

    def close_button(self):
        frame, = self.dialog.winfo_children()
        buttons = [widget for widget in frame.winfo_children()
                   if isinstance(widget, ttk.Button)]
        self.assertEqual(len(buttons), 1)
        return buttons[0]

    def test_r535_native_f1_inside_text_does_not_create_extra_dialog(self):
        self.text.focus_force()
        self.root.update()
        self.text.event_generate("<F1>")
        self.root.update()
        self.assertIs(self.root._fvs_help_dialog, self.dialog)
        self.assertTrue(self.text.winfo_exists())
        self.assertIs(self.root.focus_get(), self.text)

    def test_r535_native_f1_inside_close_button_returns_focus_to_help(self):
        button = self.close_button()
        button.focus_force()
        self.root.update()
        self.assertIs(self.root.focus_get(), button)
        button.event_generate("<F1>")
        self.root.update()
        self.assertIs(self.root._fvs_help_dialog, self.dialog)
        self.assertIs(self.root.focus_get(), self.text)

    def test_r535_native_f1_recovers_destroyed_text_from_close_button(self):
        button = self.close_button()
        button.focus_force()
        self.text.destroy()
        self.root.update()
        button.event_generate("<F1>")
        self.root.update()
        rebuilt = self.root._fvs_help_dialog
        self.assertIsNot(rebuilt, self.dialog)
        self.assertFalse(self.dialog.winfo_exists())
        self.assertTrue(rebuilt._fvs_help_text.winfo_exists())
        self.assertEqual(rebuilt._fvs_help_text.cget("state"), "disabled")
        self.assertIs(rebuilt._fvs_former_focus, self.entry)

    def test_r535_native_escape_after_f1_restores_form(self):
        button = self.close_button()
        button.focus_force()
        self.root.update()
        button.event_generate("<F1>")
        self.root.update()
        self.text.event_generate("<Escape>")
        self.root.update()
        self.assertIsNone(self.root._fvs_help_dialog)
        self.assertIs(self.root.focus_get(), self.entry)

    def test_r535_native_f1_is_not_rebound_globally_to_root(self):
        root_f1 = []
        self.root.bind("<F1>", lambda event: root_f1.append(event))
        button = self.close_button()
        button.focus_force()
        self.root.update()
        button.event_generate("<F1>")
        self.root.update()
        self.assertEqual(root_f1, [])
        self.assertIs(self.root._fvs_help_dialog, self.dialog)


if __name__ == "__main__":
    unittest.main()
