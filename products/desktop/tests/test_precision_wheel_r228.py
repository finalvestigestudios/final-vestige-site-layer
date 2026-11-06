"""R228: Win32 precision wheel accumulation; source values never read."""
import types
import unittest

from fvs_suite.scroll_access import (
    ScrollableForm, precise_windows_wheel_units, wheel_scroll_units,
)


class PrecisionMathR228(unittest.TestCase):
    def test_four_partial_events_are_one_notch(self):
        remainder = 0
        outputs = []
        for _ in range(4):
            units, remainder = precise_windows_wheel_units(-30, remainder)
            outputs.append(units)
        self.assertEqual(outputs, [0, 0, 0, 3])
        self.assertEqual(remainder, 0)

    def test_reverse_partial_events_cancel(self):
        self.assertEqual(precise_windows_wheel_units(30, -30), (0, 0))
        self.assertEqual(precise_windows_wheel_units(-90, 60), (0, -30))

    def test_native_notches_keep_old_direction(self):
        for delta in (-240, -120, 120, 240):
            with self.subTest(delta=delta):
                self.assertEqual(precise_windows_wheel_units(delta),
                                 (wheel_scroll_units(delta=delta), 0))

    def test_signed_residual_both_directions(self):
        self.assertEqual(precise_windows_wheel_units(121), (-3, 1))
        self.assertEqual(precise_windows_wheel_units(-121), (3, -1))

    def test_residual_carries_across_single_notch(self):
        self.assertEqual(precise_windows_wheel_units(80, 70), (-3, 30))
        self.assertEqual(precise_windows_wheel_units(-80, -70), (3, -30))

    def test_extreme_delta_is_bounded(self):
        for delta in (10**200, -(10**200)):
            units, remain = precise_windows_wheel_units(delta)
            self.assertEqual(abs(units), 12)
            self.assertLess(abs(remain), 120)

    def test_invalid_delta_and_remainder_rejected(self):
        invalid = (True, 1.2, None, "customer-finance.csv", float("nan"))
        for value in invalid:
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    precise_windows_wheel_units(value)
                with self.assertRaises(ValueError):
                    precise_windows_wheel_units(120, value)
        for remainder in (-120, 120, 121, -(10**200)):
            with self.assertRaises(ValueError):
                precise_windows_wheel_units(120, remainder)

    def test_no_untrusted_conversion(self):
        class Poison:
            def __int__(self): raise AssertionError("untrusted int called")
            def __str__(self): raise AssertionError("untrusted string called")
        with self.assertRaises(ValueError):
            precise_windows_wheel_units(Poison())


class FakeWidget:
    def __init__(self, master=None): self.master = master
    def get(self): raise AssertionError("private entry accessed")


class FakeCanvas:
    def __init__(self, yview=(0.0, 0.4)):
        self.view = yview
        self.calls = []
    def yview(self): return self.view
    def yview_scroll(self, units, kind): self.calls.append((units, kind))


def make_form(platform="win32", *, visible=(0.0, 0.4)):
    obj = ScrollableForm.__new__(ScrollableForm)
    obj.viewport = FakeWidget()
    obj.canvas = FakeCanvas(visible)
    obj._wheel_platform = platform
    obj._wheel_remainder = 0
    return obj


class PrecisionScopeR228(unittest.TestCase):
    def test_nested_events_accumulate_before_moving(self):
        form = make_form()
        entry = FakeWidget(form.viewport)
        results = [form._mouse_wheel(types.SimpleNamespace(widget=entry, delta=-30))
                   for _ in range(4)]
        self.assertEqual(results, [None, None, None, "break"])
        self.assertEqual(form.canvas.calls, [(3, "units")])
        self.assertEqual(form._wheel_remainder, 0)

    def test_unrelated_dialog_does_not_change_residual(self):
        form = make_form()
        in_scope = FakeWidget(form.viewport)
        elsewhere = FakeWidget()
        self.assertIsNone(form._mouse_wheel(
            types.SimpleNamespace(widget=in_scope, delta=-50)))
        self.assertIsNone(form._mouse_wheel(
            types.SimpleNamespace(widget=elsewhere, delta=-120)))
        self.assertEqual(form._wheel_remainder, -50)
        self.assertEqual(form.canvas.calls, [])

    def test_non_scrollable_form_ignores_partial_wheel(self):
        form = make_form(visible=(0, 1))
        self.assertIsNone(form._mouse_wheel(
            types.SimpleNamespace(widget=FakeWidget(form.viewport), delta=-30)))
        self.assertEqual(form._wheel_remainder, 0)

    def test_x11_button_remains_independent_of_win32_residual(self):
        form = make_form()
        entry = FakeWidget(form.viewport)
        form._mouse_wheel(types.SimpleNamespace(widget=entry, delta=-60))
        self.assertEqual(form._x11_wheel(types.SimpleNamespace(widget=entry, num=5)), "break")
        self.assertEqual(form._wheel_remainder, -60)
        self.assertEqual(form.canvas.calls, [(3, "units")])

    def test_non_windows_mac_events_remain_immediate(self):
        form = make_form("aqua")
        entry = FakeWidget(form.viewport)
        self.assertEqual(form._mouse_wheel(
            types.SimpleNamespace(widget=entry, delta=-1)), "break")
        self.assertEqual(form.canvas.calls, [(3, "units")])

    def test_inherited_r227_uninitialized_fake_form_keeps_working(self):
        form = ScrollableForm.__new__(ScrollableForm)
        form.viewport = FakeWidget()
        form.canvas = FakeCanvas()
        entry = FakeWidget(form.viewport)
        self.assertEqual(form._mouse_wheel(
            types.SimpleNamespace(widget=entry, delta=-120)), "break")
        self.assertEqual(form.canvas.calls, [(3, "units")])

    def test_completed_partial_reversal_does_not_scroll(self):
        form = make_form()
        entry = FakeWidget(form.viewport)
        form._mouse_wheel(types.SimpleNamespace(widget=entry, delta=-80))
        form._mouse_wheel(types.SimpleNamespace(widget=entry, delta=80))
        self.assertEqual(form.canvas.calls, [])
        self.assertEqual(form._wheel_remainder, 0)

    def test_malformed_in_scope_event_fails_without_scroll(self):
        form = make_form()
        with self.assertRaises(ValueError):
            form._mouse_wheel(types.SimpleNamespace(widget=FakeWidget(form.viewport), delta=True))
        self.assertEqual(form.canvas.calls, [])

    def test_optimized_python_does_not_bypass_guards(self):
        import inspect, ast
        self.assertFalse(any(isinstance(node, ast.Assert)
                             for node in ast.walk(ast.parse(inspect.getsource(precise_windows_wheel_units)))))


if __name__ == "__main__":
    unittest.main()
