"""R225: deterministic, headless LedgerDiff optional-header keyboard tests."""
import unittest
from fvs_suite.keyboard_access import install_shortcuts


class Root:
    def __init__(self):
        self.bindings = {}
        self.modes = {}

    def bind(self, key, callback, add=None):
        if key in self.bindings:
            raise AssertionError("duplicate binding")
        self.bindings[key] = callback
        self.modes[key] = add

    def press(self, key):
        return self.bindings[key](object())


class Widget:
    def __init__(self, label, calls):
        self.label, self.calls = label, calls

    def focus_set(self):
        self.calls.append((self.label, "focus"))

    def invoke(self):
        self.calls.append((self.label, "invoke"))


def fixture(count=2):
    calls = []
    root = Root()
    def widget(label):
        return Widget(label, calls)
    inputs = [(widget("input" + str(i)), widget("browse" + str(i)))
              for i in range(count)]
    output = (widget("output"), widget("output-picker"))
    generate, review = widget("generate"), widget("review")
    headers = tuple(widget(s) for s in ("left-key", "right-key",
                                        "left-amount", "right-amount"))
    return root, calls, inputs, output, generate, review, headers


class LedgerHeadersR225(unittest.TestCase):
    def prepare(self, count=2, **options):
        root, calls, inputs, output, generate, review, headers = fixture(count)
        keys = install_shortcuts(root, inputs, output, generate, **options)
        return root, calls, keys

    def test_four_header_keys_focus_correct_entries(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        keys = install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        for key, name in zip(("l", "r", "a", "m"),
                             ("left-key", "right-key", "left-amount", "right-amount")):
            with self.subTest(key=key):
                sequence = "<Alt-Key-" + key + ">"
                self.assertIn(sequence, keys)
                self.assertEqual(root.press(sequence), "break")
                self.assertEqual(calls[-1], (name, "focus"))

    def test_no_actions_during_install(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        self.assertEqual(calls, [])

    def test_optional_headers_do_not_generate_or_review(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        for key in ("l", "r", "a", "m"):
            root.press("<Alt-Key-" + key + ">")
        self.assertEqual([action for _, action in calls], ["focus"] * 4)

    def test_required_source_focus_and_browse_preserved(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        for key, result in (("<Alt-Key-1>", ("input0", "focus")),
                            ("<Control-Key-1>", ("browse0", "invoke")),
                            ("<Alt-Key-2>", ("input1", "focus")),
                            ("<Control-Key-2>", ("browse1", "invoke"))):
            root.press(key)
            self.assertEqual(calls[-1], result)

    def test_output_focus_and_browse_preserved(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        root.press("<Alt-Key-o>")
        root.press("<Control-Key-o>")
        self.assertEqual(calls, [("output", "focus"), ("output-picker", "invoke")])

    def test_generate_uses_existing_button(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        root.press("<Alt-Key-g>")
        root.press("<Control-Return>")
        self.assertEqual(calls, [("generate", "invoke")] * 2)

    def test_no_header_browse_or_extra_policy_bindings(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        keys = install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        for key in ("l", "r", "a", "m"):
            self.assertNotIn("<Control-Key-" + key + ">", keys)
        self.assertNotIn("<Alt-Key-p>", keys)
        self.assertNotIn("<Alt-Key-w>", keys)

    def test_window_bindings_are_additive(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        install_shortcuts(root, inputs, output, generate, ledger_headers=headers)
        self.assertTrue(all(mode == "+" for mode in root.modes.values()))

    def test_shortcut_order_deterministic(self):
        sequences = []
        for _ in range(3):
            root, calls, inputs, output, generate, review, headers = fixture()
            sequences.append(install_shortcuts(root, inputs, output, generate,
                                               ledger_headers=headers))
        self.assertEqual(sequences[0], sequences[1])
        self.assertEqual(sequences[1], sequences[2])

    def test_no_ledger_bindings_for_other_apps(self):
        for count in (1, 2, 3):
            root, calls, inputs, output, generate, review, headers = fixture(count)
            keys = install_shortcuts(root, inputs, output, generate)
            for key in ("l", "r", "a", "m"):
                self.assertNotIn("<Alt-Key-" + key + ">", keys)

    def test_invoice_optional_window_unchanged(self):
        root, calls, inputs, output, generate, review, headers = fixture(1)
        window = Widget("near-match", calls)
        keys = install_shortcuts(root, inputs, output, generate, invoice_window=window)
        self.assertIn("<Alt-Key-w>", keys)
        self.assertNotIn("<Alt-Key-l>", keys)
        root.press("<Alt-Key-w>")
        self.assertEqual(calls, [("near-match", "focus")])

    def test_procurement_policy_and_review_unchanged(self):
        root, calls, inputs, output, generate, review, headers = fixture(3)
        policy = (Widget("policy", calls), Widget("picker", calls))
        install_shortcuts(root, inputs, output, generate,
                          policy_rules=policy, review=review)
        for key, result in (("<Alt-Key-p>", ("policy", "focus")),
                            ("<Control-Key-p>", ("picker", "invoke")),
                            ("<Alt-Key-r>", ("review", "invoke"))):
            root.press(key)
            self.assertEqual(calls[-1], result)

    def test_reject_malformed_header_collection_before_binding(self):
        for bad in ("text", {"a": 1}, object(), (), (object(),), (1, 2, 3),
                    (1, 2, 3, 4, 5)):
            root, calls, inputs, output, generate, review, headers = fixture()
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                install_shortcuts(root, inputs, output, generate, ledger_headers=bad)
            self.assertFalse(root.bindings)

    def test_reject_ledger_with_wrong_input_count(self):
        for count in (1, 3):
            root, calls, inputs, output, generate, review, headers = fixture(count)
            with self.subTest(count=count), self.assertRaises(ValueError):
                install_shortcuts(root, inputs, output, generate,
                                  ledger_headers=headers)
            self.assertFalse(root.bindings)

    def test_reject_ledger_with_other_optional_controls(self):
        for opt in ("review", "invoice_window", "policy_rules"):
            root, calls, inputs, output, generate, review, headers = fixture()
            kwargs = {"review": review,
                      "invoice_window": Widget("window", calls),
                      "policy_rules": (Widget("policy", calls), Widget("picker", calls))}
            with self.subTest(option=opt), self.assertRaises(ValueError):
                install_shortcuts(root, inputs, output, generate,
                                  ledger_headers=headers, **{opt: kwargs[opt]})
            self.assertFalse(root.bindings)

    def test_reject_ledger_widget_aliases(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        for bad in ((headers[0], headers[0], headers[2], headers[3]),
                    (inputs[0][0], *headers[1:]),
                    (*headers[:3], output[1])):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                install_shortcuts(root, inputs, output, generate,
                                  ledger_headers=bad)
            self.assertFalse(root.bindings)

    def test_missing_header_focus_method_fails_before_binding(self):
        root, calls, inputs, output, generate, review, headers = fixture()
        with self.assertRaises(AttributeError):
            install_shortcuts(root, inputs, output, generate,
                              ledger_headers=(headers[0], object(), *headers[2:]))
        self.assertFalse(root.bindings)


if __name__ == "__main__":
    unittest.main()
