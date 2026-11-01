"""Local-only, keyboard-revealing scroll form for scaled Tk desktop layouts.

Source-controlled visual accessibility aid, not an accessibility certification.
Never reads entry values, file paths, reports or customer financial information.
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk


def focus_scroll_fraction(total_height, visible_height, top, widget_y, widget_height):
    """Return a bounded scroll fraction when a focused control is out of view.

    Values are Tk widget geometry, never file paths or customer input. The
    calculation is deterministic, independent of display scaling, and does not
    use `assert` (it remains enforced under optimized Python).
    """
    values = (total_height, visible_height, top, widget_y, widget_height)
    if any(type(value) not in (int, float) or not math.isfinite(value)
           for value in values):
        raise ValueError("Invalid scroll geometry")
    if total_height <= 0 or visible_height <= 0 or widget_height <= 0:
        raise ValueError("Nonpositive scroll geometry")
    if total_height <= visible_height:
        return None
    top = min(max(0.0, top), total_height - visible_height)
    margin = min(12.0, visible_height / 4)
    if widget_y < top + margin:
        desired = widget_y - margin
    elif widget_y + widget_height > top + visible_height - margin:
        desired = widget_y + widget_height + margin - visible_height
    else:
        return None
    maximum = max(total_height - visible_height, 0.0)
    return min(1.0, max(0.0, desired / max(total_height, 1.0),
                        )) if maximum else None


class ScrollableForm:
    """Single root-owned vertical viewport; controls keep native Tk Tab order.

    The canvas and scrollbar are not keyboard-focus targets. When the user Tabs
    to a field/button below the viewport, the focused control scrolls into view.
    Styles follow the current system window background instead of hard-coded
    foreground/background colors.
    """

    def __init__(self, root):
        self.root = root
        self.viewport = ttk.Frame(root)
        self.viewport.grid(row=0, column=0, sticky="nsew")
        self.viewport.rowconfigure(0, weight=1)
        self.viewport.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            self.viewport, borderwidth=0, highlightthickness=0,
            takefocus=0, background=root.cget("background"))
        self.scrollbar = ttk.Scrollbar(
            self.viewport, orient="vertical", takefocus=0,
            command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.frame = ttk.Frame(self.canvas, padding=24)
        self.window = self.canvas.create_window(
            (0, 0), window=self.frame, anchor="nw")
        self.frame.columnconfigure(1, weight=1)
        self.wrapping_labels = []
        self.frame.bind("<Configure>", self._content_resize, add="+")
        self.canvas.bind("<Configure>", self._canvas_resize, add="+")
        root.bind("<FocusIn>", self._focus_reveal, add="+")

    def track_label(self, label):
        """Responsive wrap without inspecting or recording text contents."""
        self.wrapping_labels.append(label)
        return label

    def _content_resize(self, _event):
        box = self.canvas.bbox("all")
        if box:
            self.canvas.configure(scrollregion=box)

    def _canvas_resize(self, event):
        if event.width < 1:
            return
        self.canvas.itemconfigure(self.window, width=event.width)
        wraplength = max(100, event.width - 72)
        for widget in self.wrapping_labels:
            widget.configure(wraplength=wraplength)

    def _focus_reveal(self, event):
        widget = event.widget
        if not isinstance(widget, (ttk.Entry, ttk.Button)):
            return
        if widget.winfo_toplevel() is not self.root:
            return
        total = self.frame.winfo_height()
        visible = self.canvas.winfo_height()
        if total < 2 or visible < 2:
            return
        widget_y = widget.winfo_rooty() - self.frame.winfo_rooty()
        fraction = focus_scroll_fraction(
            total, visible, self.canvas.canvasy(0), widget_y,
            widget.winfo_height())
        if fraction is not None:
            self.canvas.yview_moveto(fraction)
