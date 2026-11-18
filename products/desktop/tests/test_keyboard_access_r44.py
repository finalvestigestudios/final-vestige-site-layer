"""R44 GUI keyboard access, no Tk display, customer file or network required."""
from __future__ import annotations

import unittest
from fvs_suite.keyboard_access import install_shortcuts, format_keyboard_help


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


    # R531: on narrow/high-DPI forms the new F1 help must be read as short,
    # ordered lines, with no customer input or arbitrary/unbounded modal text.
    @staticmethod
    def _r531_static_legend():
        return (
            "Keyboard: Alt+1..1 focus an input; Ctrl+1..1 browse; "
            "numeric keypad 1..3 also supported (Num Lock on/off); "
            "Alt+O/Ctrl+O output; Alt+G/Ctrl+Enter generate; "
            "F1 opens keyboard help"
        )

    def test_r531_f1_help_has_short_separate_lines(self):
        out = format_keyboard_help(self._r531_static_legend())
        self.assertEqual(out.splitlines()[0], "Keyboard shortcuts:")
        self.assertEqual(len(out.splitlines()), 8)
        self.assertEqual(out.count("\n- "), 6)
        self.assertIn("- F1 opens keyboard help", out)
        self.assertTrue(all(len(line) <= 77 for line in out.splitlines()))

    def test_r531_f1_help_preserves_order(self):
        out = format_keyboard_help(self._r531_static_legend())
        self.assertLess(out.index("Alt+1..1"), out.index("Ctrl+1..1"))
        self.assertLess(out.index("Ctrl+1..1"), out.index("Alt+O/Ctrl+O"))
        self.assertLess(out.index("Alt+O/Ctrl+O"), out.index("Alt+G/Ctrl+Enter"))

    def test_r531_ledger_header_shortcuts_are_visible(self):
        legend = self._r531_static_legend().replace(
            "F1 opens keyboard help",
            "Alt+L left match, Alt+R right match; "
            "Alt+A left amount, Alt+M right amount (blank = automatic); "
            "F1 opens keyboard help")
        out = format_keyboard_help(legend)
        self.assertIn("- Alt+L left match, Alt+R right match", out)
        self.assertIn("- Alt+A left amount", out)

    def test_r531_invoice_window_shortcut_visible(self):
        legend = self._r531_static_legend().replace(
            "F1 opens keyboard help",
            "Alt+W near-match day window (0-365 days, default 7); "
            "F1 opens keyboard help")
        # The static legend uses a comma here to keep this one command intact.
        out = format_keyboard_help(legend)
        self.assertIn("- Alt+W near-match day window (0-365 days, default 7)", out)

    def test_r531_procurement_premium_controls_visible(self):
        legend = self._r531_static_legend().replace(
            "F1 opens keyboard help",
            "Alt+P optional policy; Ctrl+P browse policy; "
            "Alt+R review exceptions; F1 opens keyboard help")
        out = format_keyboard_help(legend)
        self.assertIn("- Alt+P optional policy", out)
        self.assertIn("- Ctrl+P browse policy", out)
        self.assertIn("- Alt+R review exceptions", out)

    def test_r531_f1_help_invocation_is_lazy_and_read_only(self):
        shown = []
        install_shortcuts(
            self.root, self.fields[:1], self.output, self.generate,
            help_action=lambda: shown.append(
                format_keyboard_help(self._r531_static_legend())))
        self.assertEqual(shown, [])
        self.assertEqual(self.root.press("<F1>"), "break")
        self.assertEqual(len(shown), 1)
        self.assertTrue(shown[0].startswith("Keyboard shortcuts:"))
        self.assertEqual(self.generate.invoked, 0)
        self.assertEqual(self.review.invoked, 0)

    def test_r531_help_rejects_subclasses_and_nontext(self):
        class StrSubclass(str):
            pass
        for bad in (None, True, 5, StrSubclass(self._r531_static_legend())):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaisesRegex(ValueError, "bounded static legend"):
                    format_keyboard_help(bad)

    def test_r531_help_rejects_control_characters(self):
        original = self._r531_static_legend()
        for bad in (original + "\n", original + "\r",
                    original + "\x00", original + "\x7f"):
            with self.subTest(bad=repr(bad[-2:])):
                with self.assertRaises(ValueError):
                    format_keyboard_help(bad)

    def test_r531_help_rejects_bad_delimiters_and_oversize(self):
        original = self._r531_static_legend()
        for bad in (original.replace("Keyboard: ", "Keys: "),
                    original.replace("; ", ";; "),
                    original.replace("F1 opens keyboard help", "x" * 76),
                    original + "x" * 1000,
                    original + "; x" * 8):
            with self.subTest(length=len(bad)):
                with self.assertRaises(ValueError):
                    format_keyboard_help(bad)

    def test_r531_help_is_deterministic_without_source_values(self):
        original = self._r531_static_legend()
        self.assertEqual(format_keyboard_help(original),
                         format_keyboard_help(original))
        for private in ("invoice.csv", r"C:\Users", "$100", "entitlement"):
            self.assertNotIn(private, format_keyboard_help(original))


if __name__ == "__main__":
    unittest.main()
