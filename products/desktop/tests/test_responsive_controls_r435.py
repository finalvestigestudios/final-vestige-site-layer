"""R435 headless Tk method tests: narrow wrapping and keyboard focus across widget families."""
from __future__ import annotations

import unittest
from unittest.mock import patch
from fvs_suite import scroll_access as scroll


class Node:
    def __init__(self, master=None):
        self.master = master


class Label:
    def __init__(self):
        self.wraps = []
    def configure(self, **kwargs):
        self.wraps.append(kwargs["wraplength"])
    def cget(self, _name):
        raise AssertionError("Must not read financial or label content")


class Canvas:
    def __init__(self):
        self.changed = []
        self.moves = []
    def itemconfigure(self, handle, **kwargs):
        self.changed.append((handle, kwargs))
    def winfo_height(self):
        return 200
    def canvasy(self, y):
        return y
    def yview_moveto(self, f):
        self.moves.append(f)


class Frame(Node):
    def winfo_height(self):
        return 1200
    def winfo_rooty(self):
        return 100


class Focusable(Node):
    def __init__(self, master, root, y=700):
        super().__init__(master)
        self.root = root
        self.y = y
    def winfo_toplevel(self):
        return self.root
    def winfo_rooty(self):
        return 100 + self.y
    def winfo_height(self):
        return 24
    def get(self):
        raise AssertionError("Must not read private widget value")


class ResponsiveControlsR435(unittest.TestCase):
    def setUp(self):
        self.root = Node()
        self.form = object.__new__(scroll.ScrollableForm)
        self.form.root = self.root
        self.form.viewport = Node(self.root)
        self.form.frame = Frame(self.form.viewport)
        self.form.canvas = Canvas()
        self.form.window = "canvas-window"
        self.label = Label()
        self.form.wrapping_labels = [self.label]

    def resize(self, width):
        class Event: pass
        event = Event()
        event.width = width
        self.form._canvas_resize(event)

    def focus(self, control, *, widget_type):
        class Event: pass
        event = Event()
        event.widget = control
        with patch.object(widget_type[0], widget_type[1], Focusable):
            self.form._focus_reveal(event)

    def test_narrow_widths_do_not_force_100_pixel_wrap(self):
        for width in (1, 24, 60, 72, 73, 80, 100, 171):
            with self.subTest(width=width):
                self.resize(width)
                self.assertEqual(self.label.wraps[-1], max(1, width - 72))
                self.assertLessEqual(self.label.wraps[-1], max(1, width - 72))

    def test_wide_width_retains_previous_wrap(self):
        self.resize(500)
        self.assertEqual(self.label.wraps, [428])
        self.assertEqual(self.form.canvas.changed, [("canvas-window", {"width": 500})])

    def test_zero_and_negative_width_do_not_modify_canvas(self):
        for width in (0, -1):
            self.resize(width)
        self.assertEqual(self.label.wraps, [])
        self.assertEqual(self.form.canvas.changed, [])

    def test_all_labels_track_same_narrow_width(self):
        extra = [Label(), Label()]
        self.form.wrapping_labels.extend(extra)
        self.resize(80)
        self.assertEqual([label.wraps for label in self.form.wrapping_labels], [[8], [8], [8]])

    def test_empty_tracked_labels_still_resize_canvas(self):
        self.form.wrapping_labels.clear()
        self.resize(90)
        self.assertEqual(self.form.canvas.changed, [("canvas-window", {"width": 90})])

    def test_width_changes_do_not_read_private_label_content(self):
        self.resize(70)
        self.resize(400)
        self.assertEqual(self.label.wraps, [1, 328])

    def test_combobox_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Combobox"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_checkbutton_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Checkbutton"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_radiobutton_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Radiobutton"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_spinbox_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Spinbox"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_treeview_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Treeview"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_classic_entry_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.tk, "Entry"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_classic_text_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.tk, "Text"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_classic_button_focus_revealed(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.tk, "Button"))
        self.assertEqual(len(self.form.canvas.moves), 1)

    def test_unrelated_root_sibling_cannot_move_viewport(self):
        self.focus(Focusable(Node(self.root), self.root), widget_type=(scroll.ttk, "Combobox"))
        self.assertEqual(self.form.canvas.moves, [])

    def test_child_dialog_cannot_move_viewport(self):
        self.focus(Focusable(self.form.frame, Node()), widget_type=(scroll.ttk, "Checkbutton"))
        self.assertEqual(self.form.canvas.moves, [])

    def test_unrecognized_node_cannot_move_viewport(self):
        class Event: pass
        event = Event()
        event.widget = Node(self.form.frame)
        self.form._focus_reveal(event)
        self.assertEqual(self.form.canvas.moves, [])

    def test_focus_never_reads_financial_cell(self):
        self.focus(Focusable(self.form.frame, self.root), widget_type=(scroll.ttk, "Combobox"))
        self.assertAlmostEqual(self.form.canvas.moves[0], 536/1200)


if __name__ == "__main__":
    unittest.main()
