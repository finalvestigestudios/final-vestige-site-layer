"""R437: full ScrollableForm routing, synthetic Tk ancestry, no display."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import types
import unittest

from fvs_suite.scroll_access import ScrollableForm


class Node:
    def __init__(self, master=None):
        self.master = master


class FakeCanvas(Node):
    def __init__(self, master=None, view=(0.1, 0.5)):
        super().__init__(master)
        self.view = view
        self.scrolls = []

    def yview(self):
        return self.view

    def yview_scroll(self, units, kind):
        self.scrolls.append((units, kind))


def fake_widget(cls, master):
    widget = object.__new__(cls)
    widget.master = master
    widget.get = lambda *_a, **_kw: (_ for _ in ()).throw(
        AssertionError('private financial value read'))
    return widget


def form():
    value = object.__new__(ScrollableForm)
    value.root = Node()
    value.viewport = Node(value.root)
    value.canvas = FakeCanvas(value.viewport)
    value.frame = Node(value.canvas)
    value._wheel_platform = 'win32'
    value._wheel_remainder = 37
    return value


class NativeWheelAncestryIntegrationR437(unittest.TestCase):
    def test_embedded_label_in_text_retains_windows_wheel(self):
        app = form()
        text = fake_widget(tk.Text, app.frame)
        child = fake_widget(ttk.Label, text)
        self.assertIsNone(app._mouse_wheel(types.SimpleNamespace(
            widget=child, delta=-120, state=0)))
        self.assertEqual(app.canvas.scrolls, [])
        self.assertEqual(app._wheel_remainder, 37)

    def test_embedded_frame_in_treeview_retains_windows_wheel(self):
        app = form()
        tree = fake_widget(ttk.Treeview, app.frame)
        child = fake_widget(ttk.Button, fake_widget(ttk.Frame, tree))
        self.assertIsNone(app._mouse_wheel(types.SimpleNamespace(
            widget=child, delta=30, state=0)))
        self.assertEqual(app.canvas.scrolls, [])
        self.assertEqual(app._wheel_remainder, 37)

    def test_nested_canvas_child_retains_x11_wheel(self):
        app = form()
        app._wheel_platform = 'x11'
        canvas = fake_widget(tk.Canvas, app.frame)
        child = fake_widget(ttk.Label, canvas)
        self.assertIsNone(app._x11_wheel(types.SimpleNamespace(
            widget=child, num=5, state=0)))
        self.assertEqual(app.canvas.scrolls, [])

    def test_descendant_of_regular_form_frame_still_scrolls(self):
        app = form()
        app._wheel_remainder = 0
        source = fake_widget(ttk.Label, fake_widget(ttk.Frame, app.frame))
        self.assertEqual(app._mouse_wheel(types.SimpleNamespace(
            widget=source, delta=-120, state=0)), 'break')
        self.assertEqual(app.canvas.scrolls, [(3, 'units')])

    def test_form_canvas_owns_form_gesture(self):
        app = form()
        app._wheel_remainder = 0
        self.assertEqual(app._mouse_wheel(types.SimpleNamespace(
            widget=app.canvas, delta=-120, state=0)), 'break')
        self.assertEqual(app.canvas.scrolls, [(3, 'units')])

    def test_native_child_outside_viewport_ignored(self):
        app = form()
        child = fake_widget(ttk.Label, fake_widget(tk.Text, Node(app.root)))
        self.assertIsNone(app._mouse_wheel(types.SimpleNamespace(
            widget=child, delta=-120, state=0)))
        self.assertEqual(app.canvas.scrolls, [])

    def test_native_descendant_malformed_delta_never_inspected(self):
        app = form()
        child = fake_widget(ttk.Label, fake_widget(tk.Listbox, app.frame))
        self.assertIsNone(app._mouse_wheel(types.SimpleNamespace(
            widget=child, delta='confidential cell', state=0)))
        self.assertEqual(app.canvas.scrolls, [])
        self.assertEqual(app._wheel_remainder, 37)

    def test_native_descendant_ignores_modifier_inspection(self):
        app = form()
        child = fake_widget(ttk.Label, fake_widget(ttk.Combobox, app.frame))
        self.assertIsNone(app._mouse_wheel(types.SimpleNamespace(
            widget=child, delta=-120, state='untrusted'))) 
        self.assertEqual(app.canvas.scrolls, [])
        self.assertEqual(app._wheel_remainder, 37)


if __name__ == '__main__':
    unittest.main()
