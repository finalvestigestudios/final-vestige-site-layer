"""R436: local-first native widget wheel ownership; runnable without Tk display."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import unittest

from fvs_suite.native_wheel_owner import native_wheel_owner


class NativeWheelOwnerR436(unittest.TestCase):
    def test_native_widgets_keep_their_wheel(self):
        native = (tk.Text, tk.Listbox, tk.Spinbox, tk.Scale, tk.Scrollbar,
                  ttk.Treeview, ttk.Combobox, ttk.Spinbox, ttk.Scale,
                  ttk.Scrollbar, ttk.Notebook, tk.Canvas)
        for cls in native:
            with self.subTest(cls=f"{cls.__module__}.{cls.__name__}"):
                widget = object.__new__(cls)
                self.assertTrue(native_wheel_owner(widget, object()))

    def test_form_canvas_remains_scrollable(self):
        canvas = object.__new__(tk.Canvas)
        self.assertFalse(native_wheel_owner(canvas, canvas))

    def test_nested_canvas_is_native_owner(self):
        form = object.__new__(tk.Canvas)
        nested = object.__new__(tk.Canvas)
        self.assertTrue(native_wheel_owner(nested, form))

    def test_regular_form_controls_do_not_consume_wheel(self):
        for cls in (tk.Frame, ttk.Frame, tk.Label, ttk.Label,
                    tk.Button, ttk.Button, tk.Entry, ttk.Entry,
                    tk.Checkbutton, ttk.Checkbutton):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(native_wheel_owner(object.__new__(cls), object()))

    def test_none_and_non_widget_values_cannot_claim_scroll(self):
        for value in (None, False, 1, 'private path', (), object()):
            with self.subTest(kind=type(value).__name__):
                self.assertFalse(native_wheel_owner(value, object()))

    def test_does_not_read_private_text_or_geometry(self):
        class FinancialText(tk.Text):
            def get(self, *_args):
                raise AssertionError('private financial contents read')
            def winfo_class(self):
                raise AssertionError('native Tk method must not run')
            def winfo_height(self):
                raise AssertionError('geometry not required')
        self.assertTrue(native_wheel_owner(object.__new__(FinancialText), object()))

    def test_regular_entry_does_not_read_private_text(self):
        class FinancialEntry(ttk.Entry):
            def get(self, *_args):
                raise AssertionError('private contents read')
        self.assertFalse(native_wheel_owner(object.__new__(FinancialEntry), object()))

    def test_overrides_do_not_depend_on_optimizable_assert(self):
        import ast
        import inspect
        from fvs_suite import native_wheel_owner as guard
        tree = ast.parse(inspect.getsource(guard.native_wheel_owner))
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main()
