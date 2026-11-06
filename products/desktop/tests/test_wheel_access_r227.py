"""R227: local-first wheel scroll, bounded and root-scoped, across six Tk forms."""
import types
import unittest
from fvs_suite.scroll_access import ScrollableForm, wheel_scroll_units


class WheelMathR227(unittest.TestCase):
    def test_windows_and_mac_deltas(self):
        self.assertEqual([wheel_scroll_units(delta=d) for d in (120, -120, 240, -240, 1, -1, 0)],
                         [-3, 3, -6, 6, -3, 3, 0])

    def test_x11_button_events(self):
        self.assertEqual(wheel_scroll_units(button=4), -3)
        self.assertEqual(wheel_scroll_units(button=5), 3)

    def test_huge_deltas_bounded(self):
        self.assertEqual(wheel_scroll_units(delta=10**200), -12)
        self.assertEqual(wheel_scroll_units(delta=-(10**200)), 12)

    def test_invalid_and_bool_rejected(self):
        for value in (True, False, 1.25, 'private/path', float('nan'), None):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(ValueError):
                    wheel_scroll_units(delta=value)
        for button in (True, 0, 3, 6, '4', None):
            if button is None:
                continue
            with self.assertRaises(ValueError):
                wheel_scroll_units(button=button)

    def test_no_user_callbacks_from_units(self):
        class Poison:
            def __int__(self): raise AssertionError('called conversion')
            def __str__(self): raise AssertionError('called str')
        with self.assertRaises(ValueError):
            wheel_scroll_units(delta=Poison())


class FakeWidget:
    def __init__(self, master=None): self.master = master


class FakeCanvas:
    def __init__(self, yview=(0, 0.4)):
        self.calls = []
        self.view = yview
    def yview(self): return self.view
    def yview_scroll(self, units, kind): self.calls.append((units, kind))


def form(yview=(0, .4)):
    obj = ScrollableForm.__new__(ScrollableForm)
    obj.viewport = FakeWidget()
    obj.canvas = FakeCanvas(yview)
    return obj


class ScopedWheelR227(unittest.TestCase):
    def test_nested_field_scrolls_without_reading_value(self):
        obj = form()
        class PrivateEntry(FakeWidget):
            def get(self): raise AssertionError('private value read')
        field = PrivateEntry(FakeWidget(obj.viewport))
        event = types.SimpleNamespace(widget=field, delta=-120)
        self.assertEqual(obj._mouse_wheel(event), 'break')
        self.assertEqual(obj.canvas.calls, [(3, 'units')])

    def test_x11_nested_field_both_directions(self):
        obj = form()
        field = FakeWidget(obj.viewport)
        for n in (4, 5):
            self.assertEqual(obj._x11_wheel(types.SimpleNamespace(widget=field, num=n)), 'break')
        self.assertEqual(obj.canvas.calls, [(-3, 'units'), (3, 'units')])

    def test_root_and_modal_dialog_events_ignored(self):
        obj = form()
        external = FakeWidget(FakeWidget())
        for widget in (external, FakeWidget(), None):
            self.assertIsNone(obj._mouse_wheel(types.SimpleNamespace(widget=widget, delta=-120)))
        self.assertEqual(obj.canvas.calls, [])

    def test_fitting_content_is_not_intercepted(self):
        obj = form((0, 1))
        event = types.SimpleNamespace(widget=FakeWidget(obj.viewport), delta=-120)
        self.assertIsNone(obj._mouse_wheel(event))
        self.assertEqual(obj.canvas.calls, [])

    def test_zero_delta_is_not_intercepted(self):
        obj = form()
        self.assertIsNone(obj._mouse_wheel(types.SimpleNamespace(widget=FakeWidget(obj.viewport), delta=0)))
        self.assertEqual(obj.canvas.calls, [])

    def test_invalid_in_scope_delta_fails_closed(self):
        obj = form()
        with self.assertRaises(ValueError):
            obj._mouse_wheel(types.SimpleNamespace(widget=FakeWidget(obj.viewport), delta='secret'))
        self.assertEqual(obj.canvas.calls, [])

    def test_no_asserts_in_release_validations(self):
        import ast, inspect
        source = inspect.getsource(wheel_scroll_units)
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(source))))


if __name__ == '__main__':
    unittest.main()
