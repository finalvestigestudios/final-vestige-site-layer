"""Local-only, keyboard-revealing scroll form for scaled Tk desktop layouts.

Source-controlled visual accessibility aid, not an accessibility certification.
Never reads entry values, file paths, reports or customer financial information.
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from .wheel_modifiers import is_plain_vertical_wheel
from .wheel_edge_guard import wheel_points_outward


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
    if widget_height > visible_height - 2 * margin:
        # An oversized focused control cannot fit entirely in the viewport.
        # Reveal its start, never scroll the beginning out of sight while
        # trying to satisfy an impossible bottom-edge visibility request.
        if top + margin <= widget_y < top + visible_height - margin:
            return None
        desired = widget_y - margin
    elif widget_y < top + margin:
        desired = widget_y - margin
    elif widget_y + widget_height > top + visible_height - margin:
        desired = widget_y + widget_height + margin - visible_height
    else:
        return None
    maximum = max(total_height - visible_height, 0.0)
    return min(1.0, max(0.0, desired / max(total_height, 1.0),
                        )) if maximum else None


def wheel_scroll_units(*, delta=0, button=None):
    """Translate an OS wheel event into bounded Tk vertical scroll units.

    Windows/macOS generate MouseWheel delta events; X11 uses Button-4/5.
    Direction and magnitude use only native integers, never widget contents.
    Invalid event shapes are rejected without invoking application callbacks.
    """
    if button is not None:
        if type(button) is not int or button not in (4, 5):
            raise ValueError("Invalid mouse wheel button")
        return -3 if button == 4 else 3
    if type(delta) is not int:
        raise ValueError("Invalid mouse wheel delta")
    if delta == 0:
        return 0
    ticks = min(4, max(1, (abs(delta) + 119) // 120))
    return (-3 if delta > 0 else 3) * ticks


def precise_windows_wheel_units(delta, remainder=0):
    """Accumulate partial Win32 120-unit notches without amplifying trackpads.

    One physical notch moves three Tk units. Four 30-unit events equal one
    notch, opposing partial events cancel, and a single huge event is capped
    at four notches. Residual values cannot escape [-119, 119]. The function
    never inspects paths, widgets or financial data.
    """
    if (type(delta) is not int or type(remainder) is not int
            or not -120 < remainder < 120):
        raise ValueError("Invalid Windows wheel delta")
    total = delta + remainder
    if total == 0:
        return 0, 0
    direction = 1 if total > 0 else -1
    notches, residual = divmod(abs(total), 120)
    return -3 * direction * min(4, notches), direction * residual


class ScrollableForm:
    """Single root-owned vertical viewport; controls keep native Tk Tab order.

    The canvas and scrollbar are not keyboard-focus targets. Tab/shortcut
    focus still reveals obscured controls. Root-local wheel events scroll only
    this app's viewport, never a child dialog or another application window.
    Styles follow the current system window background instead of hard-coded
    foreground/background colors.
    """

    def __init__(self, root):
        self.root = root
        self._wheel_platform = root.tk.call("tk", "windowingsystem")
        self._wheel_remainder = 0
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
        # App-root bindings receive descendant Tk events via bindtags, without
        # process-global bind_all hooks or hijacking dialog wheel behavior.
        root.bind("<MouseWheel>", self._mouse_wheel, add="+")
        root.bind("<Button-4>", self._x11_wheel, add="+")
        root.bind("<Button-5>", self._x11_wheel, add="+")

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

    def _inside_viewport(self, widget):
        """Only descendants of our own viewport may scroll this canvas."""
        while widget is not None:
            if widget is self.viewport:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _scroll_wheel(self, event, *, button=None):
        if not self._inside_viewport(event.widget):
            return None
        # Leave Shift-wheel horizontal navigation and Ctrl/Alt wheel
        # gestures to native controls; do not change Win32 partial residual.
        if not is_plain_vertical_wheel(getattr(event, "state", 0)):
            return None
        lo, hi = self.canvas.yview()
        if lo <= 0.0 and hi >= 1.0:
            if getattr(self, "_wheel_platform", None) == "win32":
                self._wheel_remainder = 0
            return None
        # A wheel pushing beyond either canvas edge must not accumulate
        # unused Win32 fractions that cancel the user's first reverse move.
        if wheel_points_outward(lo, hi, delta=getattr(event, "delta", 0), button=button):
            if getattr(self, "_wheel_platform", None) == "win32":
                self._wheel_remainder = 0
            return None
        if button is None and getattr(self, "_wheel_platform", None) == "win32":
            units, self._wheel_remainder = precise_windows_wheel_units(
                getattr(event, "delta", 0), self._wheel_remainder)
        else:
            units = wheel_scroll_units(delta=getattr(event, "delta", 0), button=button)
        if not units:
            return None
        self.canvas.yview_scroll(units, "units")
        return "break"

    def _mouse_wheel(self, event):
        return self._scroll_wheel(event)

    def _x11_wheel(self, event):
        return self._scroll_wheel(event, button=event.num)

    def _focus_reveal(self, event):
        widget = event.widget
        if not isinstance(widget, (ttk.Entry, ttk.Button)):
            return
        if widget.winfo_toplevel() is not self.root:
            return
        # Root-local focus events can originate in sibling root-owned widgets.
        # Only descendants of this canvas may move its scroll position.
        if not self._inside_viewport(widget):
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
