"""R224: headless optional-field keyboard access without bypassing real actions."""
import unittest
from fvs_suite.keyboard_access import install_shortcuts


class FakeRoot:
    def __init__(self):
        self.handlers = {}
        self.mode = {}

    def bind(self, sequence, callback, add=None):
        if sequence in self.handlers:
            raise AssertionError("Duplicate binding")
        self.handlers[sequence] = callback
        self.mode[sequence] = add

    def press(self, sequence):
        return self.handlers[sequence](object())


class FakeWidget:
    def __init__(self, label, calls):
        self.label = label
        self.calls = calls

    def focus_set(self):
        self.calls.append((self.label, "focus"))

    def invoke(self):
        self.calls.append((self.label, "invoke"))


def controls(count):
    calls = []
    root = FakeRoot()
    fields = [(FakeWidget(f"input{i}", calls), FakeWidget(f"picker{i}", calls))
              for i in range(1, count + 1)]
    output = (FakeWidget("output", calls), FakeWidget("output-picker", calls))
    generate = FakeWidget("generate", calls)
    review = FakeWidget("review", calls)
    return root, calls, fields, output, generate, review


class OptionalShortcutsR224(unittest.TestCase):
    def test_one_input_no_optional_shortcuts(self):
        root, calls, fields, output, generate, review = controls(1)
        bindings = install_shortcuts(root, fields, output, generate)
        self.assertEqual(bindings, ("<Alt-Key-1>", "<Control-Key-1>",
                                    "<Alt-Key-o>", "<Control-Key-o>",
                                    "<Alt-Key-g>", "<Control-Return>"))
        self.assertFalse(calls)
        self.assertTrue(all(v == "+" for v in root.mode.values()))

    def test_three_input_existing_hotkeys_unchanged(self):
        root, calls, fields, output, generate, review = controls(3)
        install_shortcuts(root, fields, output, generate)
        for seq, expected in (("<Alt-Key-3>", ("input3", "focus")),
                              ("<Control-Key-3>", ("picker3", "invoke")),
                              ("<Alt-Key-o>", ("output", "focus")),
                              ("<Control-Key-o>", ("output-picker", "invoke")),
                              ("<Alt-Key-g>", ("generate", "invoke")),
                              ("<Control-Return>", ("generate", "invoke"))):
            with self.subTest(seq=seq):
                self.assertEqual(root.press(seq), "break")
                self.assertEqual(calls[-1], expected)

    def test_invoice_window_focus_is_not_an_action(self):
        root, calls, fields, output, generate, review = controls(1)
        win = FakeWidget("window", calls)
        bindings = install_shortcuts(root, fields, output, generate,
                                     invoice_window=win)
        self.assertIn("<Alt-Key-w>", bindings)
        self.assertNotIn("<Control-Key-w>", bindings)
        self.assertNotIn("<Alt-Key-p>", bindings)
        self.assertEqual(root.press("<Alt-Key-w>"), "break")
        self.assertEqual(calls, [("window", "focus")])

    def test_invoice_generate_uses_existing_button(self):
        root, calls, fields, output, generate, review = controls(1)
        win = FakeWidget("window", calls)
        install_shortcuts(root, fields, output, generate, invoice_window=win)
        root.press("<Control-Return>")
        self.assertEqual(calls, [("generate", "invoke")])

    def test_procurement_optional_policy_focus_and_picker(self):
        root, calls, fields, output, generate, review = controls(3)
        policy = (FakeWidget("policy", calls), FakeWidget("policy-picker", calls))
        bindings = install_shortcuts(root, fields, output, generate,
                                     review=review, policy_rules=policy)
        self.assertIn("<Alt-Key-p>", bindings)
        self.assertIn("<Control-Key-p>", bindings)
        self.assertNotIn("<Alt-Key-w>", bindings)
        for seq, event in (("<Alt-Key-p>", ("policy", "focus")),
                           ("<Control-Key-p>", ("policy-picker", "invoke"))):
            self.assertEqual(root.press(seq), "break")
            self.assertEqual(calls[-1], event)
        self.assertEqual(len(calls), 2)

    def test_premium_review_remains_existing_gated_button(self):
        root, calls, fields, output, generate, review = controls(3)
        install_shortcuts(root, fields, output, generate, review=review)
        root.press("<Alt-Key-r>")
        self.assertEqual(calls, [("review", "invoke")])

    def test_free_apps_do_not_gain_premium_binding(self):
        root, calls, fields, output, generate, review = controls(2)
        install_shortcuts(root, fields, output, generate)
        self.assertNotIn("<Alt-Key-r>", root.handlers)

    def test_no_callbacks_invoked_during_binding(self):
        root, calls, fields, output, generate, review = controls(3)
        policy = (FakeWidget("policy", calls), FakeWidget("policy-picker", calls))
        install_shortcuts(root, fields, output, generate, review=review,
                          policy_rules=policy)
        self.assertEqual(calls, [])

    def test_reject_mixed_invoice_and_policy_without_binding(self):
        root, calls, fields, output, generate, review = controls(1)
        with self.assertRaisesRegex(ValueError, "optional controls"):
            install_shortcuts(root, fields, output, generate,
                              invoice_window=FakeWidget("win", calls),
                              policy_rules=(FakeWidget("p", calls),
                                            FakeWidget("b", calls)))
        self.assertFalse(root.handlers)

    def test_reject_policy_bad_pair_without_binding(self):
        for bad in ((), (object(),), (object(), object(), object()),
                    "bad", {"a": 1, "b": 2}):
            root, calls, fields, output, generate, review = controls(3)
            with self.subTest(policy=repr(bad)), self.assertRaises(ValueError):
                install_shortcuts(root, fields, output, generate, policy_rules=bad)
            self.assertFalse(root.handlers)

    def test_reject_reused_invoice_widget(self):
        root, calls, fields, output, generate, review = controls(1)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, generate,
                              invoice_window=fields[0][0])
        self.assertFalse(root.handlers)

    def test_reject_reused_policy_widget(self):
        root, calls, fields, output, generate, review = controls(3)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, generate,
                              policy_rules=(fields[0][0], FakeWidget("browse", calls)))
        self.assertFalse(root.handlers)

    def test_reject_reused_required_widget(self):
        root, calls, fields, output, generate, review = controls(1)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, (fields[0][0], output[1]), generate)
        self.assertFalse(root.handlers)

    def test_reject_wrong_input_count(self):
        for n in (0, 4):
            root, calls, fields, output, generate, review = controls(n)
            with self.subTest(n=n), self.assertRaises(ValueError):
                install_shortcuts(root, fields, output, generate)
            self.assertFalse(root.handlers)

    def test_reject_bad_required_pair(self):
        root, calls, fields, output, generate, review = controls(2)
        with self.assertRaises(ValueError):
            install_shortcuts(root, [(fields[0][0],)], output, generate)
        self.assertFalse(root.handlers)

    def test_binding_deterministic_with_optional_controls(self):
        keys = []
        for _ in range(2):
            root, calls, fields, output, generate, review = controls(3)
            policy = (FakeWidget("policy", calls), FakeWidget("policy-picker", calls))
            keys.append(install_shortcuts(root, fields, output, generate,
                                          policy_rules=policy, review=review))
        self.assertEqual(keys[0], keys[1])
        self.assertEqual(keys[0][-5:], ("<Alt-Key-p>", "<Control-Key-p>",
                                       "<Alt-Key-g>", "<Control-Return>", "<Alt-Key-r>"))


if __name__ == "__main__":
    unittest.main()
