"""R44 GUI keyboard access, no Tk display, customer file or network required."""
from __future__ import annotations

import unittest
from fvs_suite.keyboard_access import install_shortcuts


class Widget:
    def __init__(self, name):
        self.name = name
        self.focus_count = 0
        self.invoked = 0
        self.command = None
        self.enabled = True

    def focus_set(self):
        self.focus_count += 1

    def invoke(self):
        if self.enabled:
            self.invoked += 1
            if self.command:
                self.command()


class FakeRoot:
    def __init__(self):
        self.bindings = {}

    def bind(self, key, handler, add=None):
        if key in self.bindings:
            raise AssertionError("Duplicate key combination")
        if add != "+":
            raise AssertionError("Existing application bindings must be preserved")
        self.bindings[key] = handler
        return f"fake-callback-{len(self.bindings)}"

    def press(self, key):
        return self.bindings[key](object())


class KeyboardAccessR44(unittest.TestCase):
    def setUp(self):
        self.root = FakeRoot()
        self.fields = [(Widget(f"entry{i}"), Widget(f"browse{i}")) for i in range(3)]
        self.output = (Widget("output"), Widget("outputBrowse"))
        self.generate = Widget("generate")
        self.review = Widget("review")

    def bind(self, n=3, premium=False):
        return install_shortcuts(self.root, self.fields[:n], self.output,
                                 self.generate, review=self.review if premium else None)

    def test_single_input_acceptance(self):
        self.assertEqual(len(self.bind(1)), 10)

    def test_two_input_acceptance(self):
        self.assertEqual(len(self.bind(2)), 16)

    def test_three_input_acceptance(self):
        self.assertEqual(len(self.bind(3)), 22)

    def test_four_inputs_rejected(self):
        with self.assertRaises(ValueError):
            install_shortcuts(self.root, self.fields + [(Widget("x"), Widget("y"))],
                              self.output, self.generate)

    def test_no_inputs_rejected(self):
        with self.assertRaises(ValueError):
            install_shortcuts(self.root, [], self.output, self.generate)

    def test_shared_controls_rejected(self):
        with self.assertRaises(ValueError):
            install_shortcuts(self.root, [(self.output[0], Widget("other"))],
                              self.output, self.generate)

    def test_malformed_pair_rejected(self):
        with self.assertRaises(ValueError):
            install_shortcuts(self.root, [(Widget("only"),)], self.output, self.generate)

    def test_all_inputs_focused_independently(self):
        self.bind()
        for i in (1, 2, 3):
            self.assertEqual(self.root.press(f"<Alt-Key-{i}>"), "break")
        self.assertEqual([e.focus_count for e, _ in self.fields], [1, 1, 1])
        self.assertEqual([b.invoked for _, b in self.fields], [0, 0, 0])

    def test_browse_uses_existing_commands(self):
        observed = []
        for _, button in self.fields:
            button.command = lambda b=button: observed.append(b.name)
        self.bind()
        for i in (1, 2, 3):
            self.root.press(f"<Control-Key-{i}>")
        self.assertEqual(observed, ["browse0", "browse1", "browse2"])

    def test_output_focus_and_browse(self):
        self.bind()
        self.root.press("<Alt-Key-o>")
        self.root.press("<Control-Key-o>")
        self.assertEqual(self.output[0].focus_count, 1)
        self.assertEqual(self.output[1].invoked, 1)

    def test_generate_alt_and_ctrl_return_share_original_command(self):
        observed = []
        self.generate.command = lambda: observed.append("existing-validation")
        self.bind()
        self.root.press("<Alt-Key-g>")
        self.root.press("<Control-Return>")
        self.assertEqual(observed, ["existing-validation", "existing-validation"])

    def test_disabled_generate_is_not_bypassed(self):
        self.generate.enabled = False
        self.generate.command = lambda: self.fail("Disabled command invoked")
        self.bind()
        self.root.press("<Control-Return>")
        self.assertEqual(self.generate.invoked, 0)

    def test_free_app_does_not_bind_review(self):
        self.bind()
        self.assertNotIn("<Alt-Key-r>", self.root.bindings)

    def test_premium_review_uses_existing_entitlement_command(self):
        observed = []
        self.review.command = lambda: observed.append("entitlement-check")
        self.bind(3, premium=True)
        self.assertEqual(self.root.press("<Alt-Key-r>"), "break")
        self.assertEqual(observed, ["entitlement-check"])

    def test_disabled_review_is_not_bypassed(self):
        self.review.enabled = False
        self.review.command = lambda: self.fail("Reviewer gate bypassed")
        self.bind(premium=True)
        self.root.press("<Alt-Key-r>")
        self.assertEqual(self.review.invoked, 0)

    def test_binding_is_toplevel_only(self):
        self.bind()
        self.assertFalse(hasattr(self.root, "bind_all"))
        self.assertEqual(len(self.root.bindings), 22)

    def test_shortcut_order_deterministic(self):
        first = self.bind(2)
        root2 = FakeRoot()
        second = install_shortcuts(root2, self.fields[:2], self.output, self.generate)
        self.assertEqual(first, second)
        self.assertEqual(len(second), len(set(second)))

    def test_premium_adds_only_review_shortcut(self):
        free = self.bind(2)
        premium = install_shortcuts(FakeRoot(), self.fields[:2], self.output,
                                    self.generate, review=self.review)
        self.assertEqual(set(premium) - set(free), {"<Alt-Key-r>"})


    # R530: a keyboard-only user can discover shortcuts at any scroll position.
    # The handler is opt-in so historical headless integrations remain stable.
    def test_r530_existing_callers_do_not_gain_f1(self):
        self.bind(1)
        self.assertNotIn("<F1>", self.root.bindings)

    def test_r530_invalid_help_action_fails_before_binding(self):
        for bad in (False, 1, "", object()):
            root = FakeRoot()
            with self.subTest(value=type(bad).__name__), self.assertRaisesRegex(
                    ValueError, "Keyboard help action"):
                install_shortcuts(root, self.fields[:1], self.output,
                                  self.generate, help_action=bad)
            self.assertEqual(root.bindings, {})

    def test_r530_help_is_not_invoked_during_registration(self):
        shown = []
        keys = install_shortcuts(
            self.root, self.fields[:1], self.output, self.generate,
            help_action=lambda: shown.append("static legend"))
        self.assertIn("<F1>", keys)
        self.assertEqual(keys[-1], "<F1>")
        self.assertEqual(shown, [])

    def test_r530_f1_dispatches_help_without_generate(self):
        shown = []
        install_shortcuts(self.root, self.fields[:1], self.output,
                          self.generate, help_action=lambda: shown.append("help"))
        self.assertEqual(self.root.press("<F1>"), "break")
        self.assertEqual(shown, ["help"])
        self.assertEqual(self.generate.invoked, 0)
        self.assertEqual(self.output[1].invoked, 0)

    def test_r530_f1_does_not_bypass_premium_review(self):
        shown = []
        install_shortcuts(self.root, self.fields, self.output, self.generate,
                          review=self.review,
                          help_action=lambda: shown.append("help"))
        self.root.press("<F1>")
        self.assertEqual(shown, ["help"])
        self.assertEqual(self.review.invoked, 0)
        self.assertEqual(self.generate.invoked, 0)
        self.assertIn("<Alt-Key-r>", self.root.bindings)

    def test_r530_all_form_counts_bind_a_single_help_key(self):
        for count in (1, 2, 3):
            root = FakeRoot()
            keys = install_shortcuts(
                root, self.fields[:count], self.output, self.generate,
                help_action=lambda: None)
            with self.subTest(count=count):
                self.assertEqual(keys.count("<F1>"), 1)
                self.assertEqual(len(keys), len(set(keys)))

    def test_r530_help_registration_order_is_deterministic(self):
        orders = []
        for _ in range(2):
            root = FakeRoot()
            orders.append(install_shortcuts(
                root, self.fields[:2], self.output, self.generate,
                help_action=lambda: None))
        self.assertEqual(orders[0], orders[1])
        self.assertEqual(orders[0][-1], "<F1>")

    def test_r530_failed_f1_registration_is_inert(self):
        class UncertainHelpRoot(FakeRoot):
            def bind(self, key, handler, add=None):
                ack = super().bind(key, handler, add)
                return "" if key == "<F1>" else ack

        root = UncertainHelpRoot()
        shown = []
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install_shortcuts(root, self.fields[:1], self.output,
                              self.generate,
                              help_action=lambda: shown.append("help"))
        # The failing registration can leave an orphan in Tk; it cannot act.
        self.assertEqual(root.press("<F1>"), "break")
        self.assertEqual(shown, [])

if __name__ == "__main__":
    unittest.main()
