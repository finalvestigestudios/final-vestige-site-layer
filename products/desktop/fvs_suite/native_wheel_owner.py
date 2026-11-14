"""Prevent form-level wheel events from stealing native control scrolling.

This check is strictly about Tk widget identity/type and parentage. It neither
calls widget content methods nor inspects text, financial values or file paths.
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
    """Whether a native wheel owner exists below the form canvas.

    A label, editor child or embedded widget inside a native Text, Treeview or
    nested Canvas belongs to that native wheel owner too. Do not traverse
    beyond the form canvas: every ordinary form input is its descendant.
    Ancestry checks do not call Tk methods or read customer content.
    """
    seen = set()
    while widget is not None and widget is not form_canvas:
        identity = id(widget)
        if identity in seen:
            return False  # Fail closed on malformed cyclic synthetic ancestry.
        seen.add(identity)
        if isinstance(widget, (tk.Canvas,) + _NATIVE_WHEEL_CONTROLS):
            return True
        try:
            # Bypass tkinter.Misc.__getattr__, which may try to call an absent
            # interpreter on displayless widget proxies used by tests.
            widget = object.__getattribute__(widget, "master")
        except AttributeError:
            return False
    return False
