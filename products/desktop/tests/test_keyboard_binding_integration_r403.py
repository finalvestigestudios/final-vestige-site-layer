"""R403: real six-launcher keyboard registration exercises the preflight."""
from __future__ import annotations

import unittest
from fvs_suite.keyboard_access import install_shortcuts


class Entry:
    def __init__(self):
        self.focused = 0
    def focus_set(self):
        self.focused += 1


class Button:
    def __init__(self):
        self.called = 0
    def invoke(self):
        self.called += 1


class Broken:
    pass


class Root:
    def __init__(self):
        self.handlers = {}
    def bind(self, key, handler, add=None):
        if add != "+" or key in self.handlers:
            raise AssertionError("Invalid shortcut registration")
        self.handlers[key] = handler
        return "callback-" + str(len(self.handlers))
    def unbind(self, key, callback_id):
        self.handlers.pop(key)


def parts(n):
    return Root(), [(Entry(), Button()) for _ in range(n)], (Entry(), Button()), Button()


class RealKeyboardBindingR403(unittest.TestCase):
    def install(self, n, **kwargs):
        root, fields, output, go = parts(n)
        keys = install_shortcuts(root, fields, output, go, **kwargs)
        self.assertEqual(set(keys), set(root.handlers))
        self.assertEqual(go.called, 0)
        return root

    def test_all_six_app_control_shapes(self):
        for name, n, extra in (
            ("ledger", 2, {"ledger_headers": tuple(Entry() for _ in range(4))}),
            ("invoices", 1, {"invoice_window": Entry()}),
            ("spend", 1, {}),
            ("policy", 2, {}),
            ("grants", 3, {"review": Button()}),
            ("procurement", 3, {"review": Button(), "policy_rules": (Entry(), Button())}),
        ):
            with self.subTest(product=name):
                self.install(n, **extra)

    def test_bad_input_browse_never_partially_binds(self):
        root, fields, output, go = parts(3)
        fields[1] = (fields[1][0], Broken())
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go)
        self.assertEqual(root.handlers, {})

    def test_bad_output_focus_never_partially_binds(self):
        root, fields, output, go = parts(2)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, (Broken(), output[1]), go)
        self.assertEqual(root.handlers, {})

    def test_bad_generate_never_binds(self):
        root, fields, output, _ = parts(1)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, Broken())
        self.assertEqual(root.handlers, {})

    def test_bad_premium_review_never_binds(self):
        root, fields, output, go = parts(3)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go, review=Broken())
        self.assertEqual(root.handlers, {})

    def test_bad_policy_browse_never_binds(self):
        root, fields, output, go = parts(3)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go, policy_rules=(Entry(), Broken()))
        self.assertEqual(root.handlers, {})

    def test_bad_ledger_header_never_binds(self):
        root, fields, output, go = parts(2)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go,
                              ledger_headers=(Entry(), Broken(), Entry(), Entry()))
        self.assertEqual(root.handlers, {})

    def test_bad_invoice_window_never_binds(self):
        root, fields, output, go = parts(1)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go, invoice_window=Broken())
        self.assertEqual(root.handlers, {})

    def test_real_existing_generate_command_still_used(self):
        root, fields, output, go = parts(1)
        install_shortcuts(root, fields, output, go)
        self.assertEqual(root.handlers["<Control-Return>"](object()), "break")
        self.assertEqual(go.called, 1)

    def test_duplicate_install_is_rejected_without_new_bindings(self):
        root, fields, output, go = parts(1)
        install_shortcuts(root, fields, output, go)
        before = tuple(root.handlers)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, go)
        self.assertEqual(tuple(root.handlers), before)


if __name__ == "__main__":
    unittest.main()
