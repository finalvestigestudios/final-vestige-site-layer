"""Prevent form-level wheel events from stealing native control scrolling.

This check is strictly about Tk widget identity/type. It neither calls widget
methods nor inspects text, financial values, paths or application state.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


_NATIVE_WHEEL_CONTROLS = (
    tk.Text, tk.Listbox, tk.Spinbox, tk.Scale, tk.Scrollbar,
    ttk.Treeview, ttk.Combobox, ttk.Spinbox, ttk.Scale,
    ttk.Scrollbar, ttk.Notebook,
)


def native_wheel_owner(widget, form_canvas):
    """Return True for a native wheel recipient other than the form canvas.

    Nested canvases keep their own scroll gestures, but the form canvas must
    retain the existing viewport gesture. No Tk display or content getter is
    needed to make this decision.
    """
    if widget is form_canvas:
        return False
    return isinstance(widget, (tk.Canvas,) + _NATIVE_WHEEL_CONTROLS)
