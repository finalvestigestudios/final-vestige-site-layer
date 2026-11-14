"""R434: headless real method regressions for oversized Tk controls and viewport boundaries."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from fvs_suite import scroll_access as scroll

class Node:
    def __init__(self, master=None): self.master = master

class Frame(Node):
    def winfo_height(self): return 1200
    def winfo_rooty(self): return 100

class Canvas:
    def __init__(self, top=0): self.top=top; self.moves=[]
    def winfo_height(self): return 200
    def canvasy(self, y): return self.top+y
    def yview_moveto(self, fraction): self.moves.append(fraction)

class Focusable(Node):
    def __init__(self, master, root, y=700, height=24):
        super().__init__(master)
        self.root=root; self.y=y; self.height=height
    def winfo_toplevel(self): return self.root
    def winfo_rooty(self): return 100+self.y
    def winfo_height(self): return self.height

class FocusViewportR434(unittest.TestCase):
    def setUp(self):
        self.root=Node()
        self.form=object.__new__(scroll.ScrollableForm)
        self.form.root=self.root
        self.form.viewport=Node(self.root)
        self.form.frame=Frame(self.form.viewport)
        self.form.canvas=Canvas()

    def focus(self, widget):
        class E: pass
        event=E(); event.widget=widget
        with patch.object(scroll.ttk,'Entry',Focusable), patch.object(scroll.ttk,'Button',Focusable):
            self.form._focus_reveal(event)

    def test_oversize_from_far_below_reveals_start_not_end(self):
        self.assertAlmostEqual(scroll.focus_scroll_fraction(1200,200,0,700,320),688/1200)

    def test_oversize_if_top_visible_does_not_scroll_it_out_of_view(self):
        self.assertIsNone(scroll.focus_scroll_fraction(1200,200,600,620,320))

    def test_oversize_partly_above_reveals_top(self):
        self.assertAlmostEqual(scroll.focus_scroll_fraction(1200,200,600,500,320),488/1200)

    def test_short_visible_control_unchanged(self):
        self.assertIsNone(scroll.focus_scroll_fraction(1200,200,600,680,24))

    def test_short_offscreen_control_revealed_with_margin(self):
        self.assertAlmostEqual(scroll.focus_scroll_fraction(1200,200,0,700,24),536/1200)

    def test_exact_fit_content_never_scrolls(self):
        self.assertIsNone(scroll.focus_scroll_fraction(200,200,0,150,400))

    def test_root_sibling_focus_does_not_move_scroll(self):
        sibling=Focusable(Node(self.root),self.root)
        self.focus(sibling)
        self.assertEqual(self.form.canvas.moves,[])

    def test_nested_viewport_entry_is_revealed(self):
        entry=Focusable(Node(self.form.frame),self.root)
        self.focus(entry)
        self.assertEqual(len(self.form.canvas.moves),1)
        self.assertAlmostEqual(self.form.canvas.moves[0],536/1200)

    def test_child_dialog_focus_does_not_move_scroll(self):
        dialog=Focusable(Node(self.form.frame),Node())
        self.focus(dialog)
        self.assertEqual(self.form.canvas.moves,[])

    def test_non_entry_non_button_focus_does_not_move_scroll(self):
        self.focus(Node(self.form.frame))
        self.assertEqual(self.form.canvas.moves,[])

    def test_no_sensitive_value_access(self):
        class Private(Focusable):
            def get(self): raise AssertionError('private cell read')
        self.focus(Private(self.form.frame,self.root))
        self.assertEqual(len(self.form.canvas.moves),1)

if __name__=='__main__': unittest.main()
