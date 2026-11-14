"""R437 native nested wheel ownership: headless, no customer data or display."""
import tkinter as tk
from tkinter import ttk
import unittest

from fvs_suite.native_wheel_owner import native_wheel_owner


class Node:
    def __init__(self, master=None):
        self.master = master


def widget(cls, master=None):
    value = object.__new__(cls)
    value.master = master
    return value


class NestedWheelOwnershipR437(unittest.TestCase):
    def test_children_inside_native_controls_keep_their_wheel(self):
        form = widget(tk.Canvas)
        native = (tk.Text, tk.Listbox, tk.Spinbox, tk.Scale, tk.Scrollbar,
                  ttk.Treeview, ttk.Combobox, ttk.Spinbox, ttk.Scale,
                  ttk.Scrollbar, ttk.Notebook, tk.Canvas)
        for cls in native:
            with self.subTest(cls=cls.__name__):
                owner = widget(cls, Node(form))
                child = widget(ttk.Label, owner)
                self.assertTrue(native_wheel_owner(child, form))

    def test_multilevel_embedding_preserves_native_owner(self):
        form = widget(tk.Canvas)
        text = widget(tk.Text, Node(form))
        child = Node(widget(ttk.Frame, widget(tk.Frame, text)))
        self.assertTrue(native_wheel_owner(child, form))

    def test_plain_child_in_regular_form_is_scrollable(self):
        form = widget(tk.Canvas)
        label = widget(ttk.Label, widget(ttk.Frame, form))
        self.assertFalse(native_wheel_owner(label, form))

    def test_form_canvas_is_not_a_native_owner(self):
        form = widget(tk.Canvas)
        self.assertFalse(native_wheel_owner(form, form))

    def test_stop_at_form_canvas_even_with_outer_native_parent(self):
        outer = widget(tk.Text)
        form = widget(tk.Canvas, outer)
        child = widget(ttk.Label, widget(ttk.Frame, form))
        self.assertFalse(native_wheel_owner(child, form))

    def test_source_native_owner_below_form_canvas(self):
        form = widget(tk.Canvas)
        native = widget(ttk.Treeview, widget(ttk.Frame, form))
        self.assertTrue(native_wheel_owner(native, form))

    def test_uninitialized_classic_controls_return_without_tk_calls(self):
        form = widget(tk.Canvas)
        for cls in (tk.Label, tk.Entry, ttk.Entry, ttk.Button, tk.Button):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(native_wheel_owner(object.__new__(cls), form))

    def test_cycles_cannot_hang(self):
        form = widget(tk.Canvas)
        a = Node()
        b = Node(a)
        a.master = b
        self.assertFalse(native_wheel_owner(a, form))

    def test_direct_native_wheel_owner_is_preserved(self):
        form = widget(tk.Canvas)
        self.assertTrue(native_wheel_owner(widget(tk.Text, form), form))

    def test_form_child_and_external_non_widgets_are_not_native(self):
        form = widget(tk.Canvas)
        for value in (None, object(), 'sensitive ledger cell', 42, False, Node(form)):
            with self.subTest(type=type(value).__name__):
                self.assertFalse(native_wheel_owner(value, form))

    def test_no_financial_read_or_geometry_calls(self):
        class ConfidentialLabel(ttk.Label):
            def get(self):
                raise AssertionError('must not read user data')
            def winfo_class(self):
                raise AssertionError('must not inspect Tcl')
        class ConfidentialText(tk.Text):
            def get(self, *_):
                raise AssertionError('must not read private text')
        form = widget(tk.Canvas)
        source = widget(ConfidentialLabel, widget(ConfidentialText, form))
        self.assertTrue(native_wheel_owner(source, form))

    def test_does_not_depend_on_optimizable_assert(self):
        import ast
        import inspect
        from fvs_suite import native_wheel_owner as target
        syntax = ast.parse(inspect.getsource(target.native_wheel_owner))
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(syntax)))


if __name__ == '__main__':
    unittest.main()
