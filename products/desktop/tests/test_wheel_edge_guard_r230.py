"""R230: precision-wheel boundary isolation; synthetic geometry, no user data."""
import ast
import inspect
import types
import unittest

from fvs_suite.scroll_access import ScrollableForm
from fvs_suite.wheel_edge_guard import wheel_points_outward


class WheelBoundaryMathR230(unittest.TestCase):
    def test_top_outward_delta(self):
        self.assertTrue(wheel_points_outward(0.0, 0.4, delta=120))

    def test_bottom_outward_delta(self):
        self.assertTrue(wheel_points_outward(0.6, 1.0, delta=-30))

    def test_top_reverse_remains_permitted(self):
        self.assertFalse(wheel_points_outward(0.0, 0.4, delta=-30))

    def test_bottom_reverse_remains_permitted(self):
        self.assertFalse(wheel_points_outward(0.6, 1.0, delta=30))

    def test_middle_both_directions(self):
        for delta in (-120, -1, 0, 1, 120):
            with self.subTest(delta=delta):
                self.assertFalse(wheel_points_outward(0.2, 0.8, delta=delta))

    def test_x11_button_four_top_blocked(self):
        self.assertTrue(wheel_points_outward(0, 0.2, button=4))

    def test_x11_button_five_bottom_blocked(self):
        self.assertTrue(wheel_points_outward(0.8, 1, button=5))

    def test_x11_buttons_reverse_allowed(self):
        self.assertFalse(wheel_points_outward(0, 0.3, button=5))
        self.assertFalse(wheel_points_outward(0.7, 1, button=4))

    def test_native_types_only_and_no_conversion_hooks(self):
        class Poison:
            def __float__(self): raise AssertionError("float hook invoked")
            def __int__(self): raise AssertionError("int hook invoked")
            def __str__(self): raise AssertionError("string hook invoked")
        for value in (True, False, None, 1.0, 'C:\\private\\data.csv', Poison()):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    wheel_points_outward(0.1, 0.5, delta=value)
        for value in (True, None, Poison(), float('nan'), float('inf'), -0.1, 1.1):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    wheel_points_outward(value, 0.5)

    def test_reversed_or_oversized_geometry_rejected(self):
        for lo, hi in ((0.6, 0.4), (-1, 1), (0, 2), (0, float('-inf'))):
            with self.subTest(lo=lo, hi=hi):
                with self.assertRaises(ValueError):
                    wheel_points_outward(lo, hi, delta=-30)

    def test_invalid_buttons_cannot_be_coerced(self):
        for value in (0, 6, True, '5', 5.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    wheel_points_outward(0.2, 0.8, button=value)

    def test_large_integer_delta_stays_bounded(self):
        self.assertTrue(wheel_points_outward(0, 0.5, delta=10**300))
        self.assertTrue(wheel_points_outward(0.5, 1, delta=-(10**300)))

    def test_optimized_python_does_not_erase_guards(self):
        tree = ast.parse(inspect.getsource(wheel_points_outward))
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(tree)))


class Widget:
    def __init__(self, master=None): self.master = master
    def get(self): raise AssertionError("Private input value accessed")


class Canvas:
    def __init__(self, view):
        self.view = view
        self.calls = []
    def yview(self): return self.view
    def yview_scroll(self, units, kind): self.calls.append((units, kind))


def make_form(view=(0.0, 0.4), platform='win32'):
    form = ScrollableForm.__new__(ScrollableForm)
    form.viewport = Widget()
    form.canvas = Canvas(view)
    form._wheel_platform = platform
    form._wheel_remainder = 0
    return form


def wheel(form, delta, state=0, widget=None):
    return form._mouse_wheel(types.SimpleNamespace(
        widget=widget or Widget(form.viewport), delta=delta, state=state))


class WheelBoundaryScopeR230(unittest.TestCase):
    def test_bottom_outward_win32_wheel_keeps_canvas_still(self):
        form = make_form((0.6, 1.0))
        self.assertIsNone(wheel(form, -120))
        self.assertEqual(form.canvas.calls, [])

    def test_top_outward_win32_wheel_keeps_canvas_still(self):
        form = make_form()
        self.assertIsNone(wheel(form, 120))
        self.assertEqual(form.canvas.calls, [])

    def test_blocked_outward_delta_clears_stale_precision_fraction(self):
        form = make_form((0.3, 0.8))
        self.assertIsNone(wheel(form, -80))
        self.assertEqual(form._wheel_remainder, -80)
        form.canvas.view = (0.6, 1.0)
        self.assertIsNone(wheel(form, -30))
        self.assertEqual(form._wheel_remainder, 0)
        self.assertEqual(form.canvas.calls, [])
        self.assertIsNone(wheel(form, 30))
        self.assertEqual(form._wheel_remainder, 30)
        self.assertEqual(wheel(form, 90), 'break')
        self.assertEqual(form.canvas.calls, [(-3, 'units')])

    def test_non_scrollable_view_clears_residual(self):
        form = make_form((0.2, 0.7))
        wheel(form, -40)
        form.canvas.view = (0.0, 1.0)
        self.assertIsNone(wheel(form, -20))
        self.assertEqual(form._wheel_remainder, 0)
        self.assertEqual(form.canvas.calls, [])

    def test_modified_event_does_not_clear_residual_at_boundary(self):
        form = make_form((0.3, 0.9))
        wheel(form, -30)
        form.canvas.view = (0.6, 1.0)
        self.assertIsNone(wheel(form, -120, state=1))
        self.assertIsNone(wheel(form, -120, state=4))
        self.assertIsNone(wheel(form, -120, state=8))
        self.assertEqual(form._wheel_remainder, -30)

    def test_dialog_event_does_not_clear_residual(self):
        form = make_form((0.3, 0.9))
        wheel(form, -30)
        form.canvas.view = (0.6, 1.0)
        self.assertIsNone(wheel(form, -120, widget=Widget()))
        self.assertEqual(form._wheel_remainder, -30)

    def test_non_win32_edges_are_not_intercepted(self):
        for platform in ('aqua', 'x11'):
            with self.subTest(platform=platform):
                form = make_form((0.6, 1), platform)
                self.assertIsNone(wheel(form, -1))
                self.assertEqual(form.canvas.calls, [])
                self.assertEqual(wheel(form, 1), 'break')

    def test_x11_button_top_and_bottom(self):
        form = make_form((0.0, 0.4), 'x11')
        entry = Widget(form.viewport)
        self.assertIsNone(form._x11_wheel(types.SimpleNamespace(widget=entry, num=4)))
        self.assertEqual(form._x11_wheel(types.SimpleNamespace(widget=entry, num=5)), 'break')
        form.canvas.view = (0.6, 1.0)
        self.assertIsNone(form._x11_wheel(types.SimpleNamespace(widget=entry, num=5)))
        self.assertEqual(form.canvas.calls, [(3, 'units')])

    def test_center_existing_notch_math_untouched(self):
        form = make_form((0.2, 0.8))
        self.assertEqual(wheel(form, -120), 'break')
        self.assertEqual(form.canvas.calls, [(3, 'units')])

    def test_invalid_geometry_fails_without_private_echo(self):
        form = make_form((float('nan'), 1.0))
        with self.assertRaisesRegex(ValueError, '^Invalid vertical scroll view$'):
            wheel(form, -20)
        self.assertEqual(form.canvas.calls, [])


if __name__ == '__main__':
    unittest.main()
