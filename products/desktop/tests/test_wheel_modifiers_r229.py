"""R229: modifier-aware wheel routing; no customer records, no UI side effects."""
import ast
import inspect
import types
import unittest

from fvs_suite.scroll_access import ScrollableForm, precise_windows_wheel_units
from fvs_suite.wheel_modifiers import is_plain_vertical_wheel


class RoutingMathR229(unittest.TestCase):
    def test_plain_event_allowed(self):
        self.assertTrue(is_plain_vertical_wheel(0))

    def test_shift_is_not_vertical(self):
        self.assertFalse(is_plain_vertical_wheel(0x0001))

    def test_ctrl_is_not_vertical(self):
        self.assertFalse(is_plain_vertical_wheel(0x0004))

    def test_alt_is_not_vertical(self):
        self.assertFalse(is_plain_vertical_wheel(0x0008))

    def test_all_modifier_combinations_are_reserved(self):
        for bits in (3, 5, 9, 12, 13, 0x100 | 0x4, 0x10 | 0x8):
            with self.subTest(bits=bits):
                self.assertFalse(is_plain_vertical_wheel(bits))

    def test_lock_and_mouse_flags_allow_normal_scrolling(self):
        for bits in (0x2, 0x10, 0x20, 0x100, 0x200, 0x400, 0x1000):
            with self.subTest(bits=bits):
                self.assertTrue(is_plain_vertical_wheel(bits))

    def test_invalid_event_values_rejected_without_hooks(self):
        class Poison:
            def __int__(self): raise AssertionError("native int hook executed")
            def __index__(self): raise AssertionError("index hook executed")
            def __str__(self): raise AssertionError("string hook executed")
        for value in (True, False, None, 1.0, "C:\\secrets\\ledger.csv", -1, Poison()):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    is_plain_vertical_wheel(value)

    def test_big_native_mask_safe_and_deterministic(self):
        flags = 1 << 500
        self.assertTrue(is_plain_vertical_wheel(flags))
        self.assertFalse(is_plain_vertical_wheel(flags | 4))

    def test_optimized_python_guard_has_no_assert(self):
        body = ast.parse(inspect.getsource(is_plain_vertical_wheel))
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(body)))


class Widget:
    def __init__(self, master=None): self.master = master
    def get(self): raise AssertionError("private field was inspected")


class Canvas:
    def __init__(self, view=(0.0, 0.4)):
        self.view = view
        self.calls = []
    def yview(self): return self.view
    def yview_scroll(self, steps, unit): self.calls.append((steps, unit))


def make_form(platform="win32"):
    obj = ScrollableForm.__new__(ScrollableForm)
    obj.viewport = Widget()
    obj.canvas = Canvas()
    obj._wheel_platform = platform
    obj._wheel_remainder = 0
    return obj


def wheel(form, *, state=0, delta=-120):
    return form._mouse_wheel(types.SimpleNamespace(
        widget=Widget(form.viewport), delta=delta, state=state))


class ScopedRoutingR229(unittest.TestCase):
    def test_normal_win32_wheel_preserved(self):
        form = make_form()
        self.assertEqual(wheel(form), "break")
        self.assertEqual(form.canvas.calls, [(3, "units")])

    def test_shift_wheel_does_not_move_viewport(self):
        form = make_form()
        self.assertIsNone(wheel(form, state=1))
        self.assertEqual(form.canvas.calls, [])

    def test_ctrl_wheel_does_not_move_viewport(self):
        form = make_form()
        self.assertIsNone(wheel(form, state=4))
        self.assertEqual(form.canvas.calls, [])

    def test_alt_wheel_does_not_move_viewport(self):
        form = make_form()
        self.assertIsNone(wheel(form, state=8))
        self.assertEqual(form.canvas.calls, [])

    def test_partial_win32_residual_untouched_by_modified_wheel(self):
        form = make_form()
        self.assertIsNone(wheel(form, delta=-30))
        self.assertEqual(form._wheel_remainder, -30)
        for state in (1, 4, 8, 13):
            self.assertIsNone(wheel(form, state=state, delta=-120))
            self.assertEqual(form._wheel_remainder, -30)
        self.assertEqual(wheel(form, delta=-90), "break")
        self.assertEqual(form.canvas.calls, [(3, "units")])
        self.assertEqual(form._wheel_remainder, 0)

    def test_aqua_wheel_is_not_hijacked_when_modified(self):
        form = make_form("aqua")
        self.assertIsNone(wheel(form, state=1, delta=-1))
        self.assertEqual(form.canvas.calls, [])
        self.assertEqual(wheel(form, delta=-1), "break")

    def test_x11_button_gestures_respect_modifiers(self):
        form = make_form("x11")
        entry = Widget(form.viewport)
        self.assertIsNone(form._x11_wheel(
            types.SimpleNamespace(widget=entry, num=5, state=4)))
        self.assertEqual(form._x11_wheel(
            types.SimpleNamespace(widget=entry, num=5, state=0)), "break")
        self.assertEqual(form.canvas.calls, [(3, "units")])

    def test_dialog_outside_viewport_remains_isolated(self):
        form = make_form()
        self.assertIsNone(form._mouse_wheel(types.SimpleNamespace(
            widget=Widget(), delta=-120, state=0)))
        self.assertEqual(form.canvas.calls, [])

    def test_legacy_synthetic_events_without_state_continue(self):
        form = make_form()
        self.assertEqual(form._mouse_wheel(types.SimpleNamespace(
            widget=Widget(form.viewport), delta=-120)), "break")

    def test_malformed_state_blocks_scroll_and_unchanged_residual(self):
        form = make_form()
        wheel(form, delta=-40)
        with self.assertRaises(ValueError):
            wheel(form, state="customer.csv", delta=-120)
        self.assertEqual(form._wheel_remainder, -40)
        self.assertEqual(form.canvas.calls, [])

    def test_ctrl_and_shift_on_non_scrollable_forms_remain_passive(self):
        form = make_form()
        form.canvas.view = (0.0, 1.0)
        self.assertIsNone(wheel(form, state=5))
        self.assertEqual(form._wheel_remainder, 0)

    def test_precision_math_unchanged(self):
        self.assertEqual(precise_windows_wheel_units(-90, -30), (3, 0))


if __name__ == "__main__":
    unittest.main()
