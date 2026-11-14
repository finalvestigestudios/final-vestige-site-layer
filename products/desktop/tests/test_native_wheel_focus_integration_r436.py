"""R436: real scroll module, synthetic native Tk widgets; no display or user files."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import types
import unittest

from fvs_suite.scroll_access import ScrollableForm


class Node:
    def __init__(self, master=None):
        self.master = master


class Frame(Node):
    def winfo_height(self):
        return 1200
    def winfo_rooty(self):
        return 100


class Canvas(Node):
    def __init__(self, master=None, view=(0.1, 0.5)):
        super().__init__(master)
        self.view = view
        self.scrolls = []
        self.moves = []
    def yview(self):
        return self.view
    def yview_scroll(self, units, kind):
        self.scrolls.append((units, kind))
    def winfo_height(self):
        return 200
    def canvasy(self, y):
        return y
    def yview_moveto(self, fraction):
        self.moves.append(fraction)


def native(cls, master, root=None):
    control = object.__new__(cls)  # avoid Tk display; retain real widget type
    control.master = master
    control.winfo_toplevel = lambda: root
    control.winfo_rooty = lambda: 800
    control.winfo_height = lambda: 24
    control.get = lambda *_a, **_kw: (_ for _ in ()).throw(
        AssertionError('financial widget contents accessed'))
    return control


def form():
    result = object.__new__(ScrollableForm)
    result.root = Node()
    result.viewport = Node(result.root)
    result.frame = Frame(result.viewport)
    result.canvas = Canvas(result.viewport)
    result._wheel_platform = 'win32'
    result._wheel_remainder = 37
    return result


class NativeWheelRoutingR436(unittest.TestCase):
    def test_nested_native_widgets_cannot_double_scroll_form(self):
        controls = (tk.Text, tk.Listbox, tk.Spinbox, tk.Scale, tk.Scrollbar,
                    ttk.Treeview, ttk.Combobox, ttk.Spinbox, ttk.Scale,
                    ttk.Scrollbar, ttk.Notebook, tk.Canvas)
        for cls in controls:
            with self.subTest(cls=f"{cls.__module__}.{cls.__name__}"):
                obj = form()
                source = native(cls, obj.frame)
                result = obj._mouse_wheel(types.SimpleNamespace(
                    widget=source, delta=-120, state=0))
                self.assertIsNone(result)
                self.assertEqual(obj.canvas.scrolls, [])
                self.assertEqual(obj._wheel_remainder, 37)

    def test_x11_native_controls_keep_widget_wheel(self):
        obj = form()
        obj._wheel_platform = 'x11'
        source = native(tk.Text, obj.frame)
        self.assertIsNone(obj._x11_wheel(types.SimpleNamespace(
            widget=source, num=5, state=0)))
        self.assertEqual(obj.canvas.scrolls, [])

    def test_generic_child_still_scrolls_form(self):
        obj = form()
        obj._wheel_remainder = 0
        source = Node(obj.frame)
        self.assertEqual(obj._mouse_wheel(types.SimpleNamespace(
            widget=source, delta=-120, state=0)), 'break')
        self.assertEqual(obj.canvas.scrolls, [(3, 'units')])

    def test_the_form_canvas_still_scrolls(self):
        obj = form()
        obj._wheel_remainder = 0
        self.assertEqual(obj._mouse_wheel(types.SimpleNamespace(
            widget=obj.canvas, delta=-120, state=0)), 'break')
        self.assertEqual(obj.canvas.scrolls, [(3, 'units')])

    def test_native_outside_own_viewport_ignored(self):
        obj = form()
        source = native(ttk.Treeview, Node(obj.root))
        self.assertIsNone(obj._mouse_wheel(types.SimpleNamespace(
            widget=source, delta=-120, state=0)))
        self.assertEqual(obj.canvas.scrolls, [])

    def test_parent_wheel_keeps_existing_modifier_routing(self):
        obj = form()
        for state in (1, 4, 8, 13):
            with self.subTest(state=state):
                self.assertIsNone(obj._mouse_wheel(types.SimpleNamespace(
                    widget=Node(obj.frame), delta=-120, state=state)))
        self.assertEqual(obj.canvas.scrolls, [])
        self.assertEqual(obj._wheel_remainder, 37)

    def test_nested_owner_ignored_before_malformed_delta_inspection(self):
        obj = form()
        source = native(tk.Listbox, obj.frame)
        self.assertIsNone(obj._mouse_wheel(types.SimpleNamespace(
            widget=source, delta='private ledger cell', state=0)))
        self.assertEqual(obj.canvas.scrolls, [])


class NativeKeyboardRevealR436(unittest.TestCase):
    def test_additional_native_keyboard_targets_reveal_hidden_controls(self):
        targets = (tk.Listbox, tk.Spinbox, tk.Checkbutton, tk.Radiobutton,
                   tk.Scale, ttk.Scale, ttk.Notebook)
        for cls in targets:
            with self.subTest(cls=cls.__name__):
                obj = form()
                source = native(cls, obj.frame, obj.root)
                obj._focus_reveal(types.SimpleNamespace(widget=source))
                self.assertEqual(len(obj.canvas.moves), 1)
                self.assertAlmostEqual(obj.canvas.moves[0], 536 / 1200)

    def test_unrelated_root_sibling_cannot_reveal_scrolled_form(self):
        obj = form()
        source = native(tk.Listbox, Node(obj.root), obj.root)
        obj._focus_reveal(types.SimpleNamespace(widget=source))
        self.assertEqual(obj.canvas.moves, [])

    def test_child_dialog_cannot_reveal_scrolled_form(self):
        obj = form()
        source = native(ttk.Notebook, obj.frame, Node())
        obj._focus_reveal(types.SimpleNamespace(widget=source))
        self.assertEqual(obj.canvas.moves, [])

    def test_unknown_object_focus_is_not_intercepted(self):
        obj = form()
        obj._focus_reveal(types.SimpleNamespace(widget=Node(obj.frame)))
        self.assertEqual(obj.canvas.moves, [])

    def test_focus_only_consumes_geometry_not_private_values(self):
        obj = form()
        source = native(tk.Spinbox, obj.frame, obj.root)
        obj._focus_reveal(types.SimpleNamespace(widget=source))
        self.assertEqual(len(obj.canvas.moves), 1)


if __name__ == '__main__':
    unittest.main()
