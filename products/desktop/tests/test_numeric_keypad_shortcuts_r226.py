"""R226: six-app numeric keypad mnemonics remain focus/Browse only."""
import unittest

from fvs_suite.keyboard_access import install_shortcuts


KEYSYMS = (("KP_1", "KP_End"), ("KP_2", "KP_Down"), ("KP_3", "KP_Next"))


class FakeRoot:
    def __init__(self):
        self.bindings = {}
        self.add_modes = {}

    def bind(self, sequence, handler, add=None):
        if sequence in self.bindings:
            raise AssertionError("Duplicate keybinding")
        self.bindings[sequence] = handler
        self.add_modes[sequence] = add

    def press(self, sequence):
        return self.bindings[sequence](None)


class FakeWidget:
    def __init__(self, name, actions):
        self.name, self.actions = name, actions

    def focus_set(self):
        self.actions.append((self.name, "focus"))

    def invoke(self):
        self.actions.append((self.name, "invoke"))


def fixture(count=3, *, optional=None):
    calls = []
    root = FakeRoot()
    def w(name):
        return FakeWidget(name, calls)
    inputs = [(w(f"entry-{i}"), w(f"browse-{i}")) for i in range(1, count+1)]
    output = (w("output"), w("output-browse"))
    generate = w("generate")
    kw = {}
    if optional == "ledger":
        kw["ledger_headers"] = tuple(w("header-" + str(i)) for i in range(4))
    elif optional == "invoice":
        kw["invoice_window"] = w("invoice-window")
    elif optional == "procurement":
        kw["policy_rules"] = (w("policy-entry"), w("policy-browse"))
        kw["review"] = w("human-review")
    elif optional == "grants":
        kw["review"] = w("human-review")
    return root, calls, inputs, output, generate, kw


class KeypadShortcutR226(unittest.TestCase):
    def test_alt_keypad_digit_and_navigation_focus_each_source(self):
        for count in (1, 2, 3):
            root, calls, inputs, output, generate, kw = fixture(count)
            actions = install_shortcuts(root, inputs, output, generate, **kw)
            for index in range(count):
                for keysym in KEYSYMS[index]:
                    with self.subTest(count=count, keysym=keysym):
                        seq = f"<Alt-Key-{keysym}>"
                        self.assertIn(seq, actions)
                        self.assertEqual(root.press(seq), "break")
                        self.assertEqual(calls[-1], (f"entry-{index+1}", "focus"))

    def test_control_keypad_browse_invokes_only_own_source(self):
        for count in (1, 2, 3):
            root, calls, inputs, output, generate, kw = fixture(count)
            actions = install_shortcuts(root, inputs, output, generate, **kw)
            for index in range(count):
                for keysym in KEYSYMS[index]:
                    with self.subTest(count=count, keysym=keysym):
                        seq = f"<Control-Key-{keysym}>"
                        self.assertIn(seq, actions)
                        self.assertEqual(root.press(seq), "break")
                        self.assertEqual(calls[-1], (f"browse-{index+1}", "invoke"))

    def test_unconfigured_source_has_no_keypad_binding(self):
        for count in (1, 2):
            root, calls, inputs, output, generate, kw = fixture(count)
            actions = install_shortcuts(root, inputs, output, generate, **kw)
            for keysyms in KEYSYMS[count:]:
                for keysym in keysyms:
                    with self.subTest(count=count, keysym=keysym):
                        self.assertNotIn(f"<Alt-Key-{keysym}>", actions)
                        self.assertNotIn(f"<Control-Key-{keysym}>", actions)

    def test_neither_keypad_mode_generates_or_reviews(self):
        for opt, count in (("ledger", 2), ("invoice", 1),
                           ("procurement", 3), ("grants", 3)):
            root, calls, inputs, output, generate, kw = fixture(count, optional=opt)
            install_shortcuts(root, inputs, output, generate, **kw)
            for symbols in KEYSYMS[:count]:
                for sym in symbols:
                    root.press(f"<Alt-Key-{sym}>")
            self.assertTrue(calls)
            self.assertTrue(all(action == "focus" for _, action in calls))
            self.assertFalse(any(name in {"generate", "human-review"} for name, _ in calls))

    def test_normal_keyboard_shortcuts_remain_present_and_equivalent(self):
        root, calls, inputs, output, generate, kw = fixture()
        actions = install_shortcuts(root, inputs, output, generate)
        for i in (1, 2, 3):
            root.press(f"<Alt-Key-{i}>")
            self.assertEqual(calls[-1], (f"entry-{i}", "focus"))
            root.press(f"<Control-Key-{i}>")
            self.assertEqual(calls[-1], (f"browse-{i}", "invoke"))
        self.assertIn("<Control-Return>", actions)
        self.assertIn("<Alt-Key-g>", actions)
        self.assertIn("<Alt-Key-o>", actions)

    def test_keypad_does_not_shadow_ledger_headers(self):
        root, calls, inputs, output, generate, kw = fixture(2, optional="ledger")
        actions = install_shortcuts(root, inputs, output, generate, **kw)
        for letter, name in zip("lram", ("header-0", "header-1", "header-2", "header-3")):
            self.assertIn(f"<Alt-Key-{letter}>", actions)
            root.press(f"<Alt-Key-{letter}>")
            self.assertEqual(calls[-1], (name, "focus"))
        self.assertNotIn("<Control-Key-l>", actions)

    def test_invoice_and_procurement_optional_fields_intact(self):
        for opt, count, key, expected in (
            ("invoice", 1, "<Alt-Key-w>", ("invoice-window", "focus")),
            ("procurement", 3, "<Alt-Key-p>", ("policy-entry", "focus")),
            ("procurement", 3, "<Control-Key-p>", ("policy-browse", "invoke")),
            ("procurement", 3, "<Alt-Key-r>", ("human-review", "invoke"))
        ):
            root, calls, inputs, output, generate, kw = fixture(count, optional=opt)
            install_shortcuts(root, inputs, output, generate, **kw)
            root.press(key)
            self.assertEqual(calls[-1], expected)

    def test_binds_additively_and_in_deterministic_order(self):
        observed = []
        for _ in range(4):
            root, calls, inputs, output, generate, kw = fixture(3)
            observed.append(install_shortcuts(root, inputs, output, generate, **kw))
            self.assertTrue(all(mode == "+" for mode in root.add_modes.values()))
        self.assertEqual(observed, [observed[0]] * 4)
        self.assertEqual(len(observed[0]), len(set(observed[0])))

    def test_invalid_inventory_cannot_install_partial_bindings(self):
        for count in (0, 4):
            root, calls, inputs, output, generate, kw = fixture(count)
            with self.assertRaises(ValueError):
                install_shortcuts(root, inputs, output, generate)
            self.assertEqual(root.bindings, {})

    def test_keypad_focus_does_not_read_input_values(self):
        class NoValueWidget(FakeWidget):
            def get(self):
                raise AssertionError("Private entry value accessed")
        root, calls, inputs, output, generate, kw = fixture(1)
        inputs[0] = (NoValueWidget("entry-1", calls), inputs[0][1])
        install_shortcuts(root, inputs, output, generate)
        root.press("<Alt-Key-KP_End>")
        self.assertEqual(calls[-1], ("entry-1", "focus"))

    def test_no_operations_or_content_reads_during_install(self):
        root, calls, inputs, output, generate, kw = fixture(3, optional="procurement")
        install_shortcuts(root, inputs, output, generate, **kw)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
