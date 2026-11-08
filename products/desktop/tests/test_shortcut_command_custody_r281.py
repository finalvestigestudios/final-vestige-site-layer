"""R281: all six GUI shortcut command gates stay distinct; synthetic widgets only."""
from __future__ import annotations

import unittest
from fvs_suite.keyboard_access import install_shortcuts


class Widget:
    def __init__(self, name):
        self.name = name
        self.events = []
        self.enabled = True

    def focus_set(self):
        self.events.append("focus")

    def invoke(self):
        if self.enabled:
            self.events.append("invoke")


class Root:
    def __init__(self):
        self.bindings = {}

    def bind(self, key, callback, add=None):
        if key in self.bindings or add != "+":
            raise AssertionError("Duplicate or replacement shortcut")
        self.bindings[key] = callback

    def press(self, key):
        return self.bindings[key](None)


def fixture(app):
    counts = {"LedgerDiffLite": 2, "InvoiceTwinScout": 1,
              "SpendMapLite": 1, "PolicyDeltaDesk": 2,
              "GrantAuditStudioPro": 3, "ProcureGuardStudioPro": 3}
    w = Widget
    root = Root()
    fields = [(w(f"source-{i}"), w(f"browse-{i}"))
              for i in range(counts[app])]
    output = (w("out"), w("out-browse"))
    generate, review = w("generate"), w("review")
    kw = {}
    if app == "LedgerDiffLite":
        kw["ledger_headers"] = [w(f"header-{i}") for i in range(4)]
    if app == "InvoiceTwinScout":
        kw["invoice_window"] = w("invoice-window")
    if app == "GrantAuditStudioPro":
        kw["review"] = review
    if app == "ProcureGuardStudioPro":
        kw.update(review=review, policy_rules=(w("policy"), w("policy-browse")))
    return root, fields, output, generate, review, kw


class ShortcutCommandCustodyR281(unittest.TestCase):
    def reject(self, app, *, generate_as=None, review_as=None):
        root, fields, output, generate, review, kw = fixture(app)
        pool = [w for pair in (*fields, output) for w in pair]
        if app == "LedgerDiffLite":
            pool += list(kw["ledger_headers"])
        if app == "InvoiceTwinScout":
            pool += [kw["invoice_window"]]
        if app == "ProcureGuardStudioPro":
            pool += list(kw["policy_rules"])
        if generate_as is not None:
            generate = pool[generate_as]
        if review_as is not None:
            kw["review"] = generate if review_as == "generate" else pool[review_as]
        with self.assertRaisesRegex(ValueError, "independent command buttons"):
            install_shortcuts(root, fields, output, generate, **kw)
        self.assertEqual(root.bindings, {}, "invalid controls must leave no partial bindings")
        self.assertFalse(any(w.events for w in pool), "validation must never execute widgets")

    def test_all_six_valid_widgets_still_install_keyboard_shortcuts(self):
        for app in ("LedgerDiffLite", "InvoiceTwinScout", "SpendMapLite",
                    "PolicyDeltaDesk", "GrantAuditStudioPro", "ProcureGuardStudioPro"):
            with self.subTest(app=app):
                root, fields, output, generate, review, kw = fixture(app)
                shortcuts = install_shortcuts(root, fields, output, generate, **kw)
                self.assertEqual(len(root.bindings), len(shortcuts))
                self.assertEqual(root.press("<Control-Return>"), "break")
                self.assertEqual(generate.events, ["invoke"])
                self.assertFalse(review.events)
                if "review" in kw:
                    self.assertEqual(root.press("<Alt-Key-r>"), "break")
                    self.assertEqual(review.events, ["invoke"])

    def test_generate_must_not_alias_any_source_or_browse_control(self):
        for app in ("LedgerDiffLite", "InvoiceTwinScout", "SpendMapLite",
                    "PolicyDeltaDesk", "GrantAuditStudioPro", "ProcureGuardStudioPro"):
            root, fields, output, generate, review, kw = fixture(app)
            controls = [w for pair in (*fields, output) for w in pair]
            if app == "LedgerDiffLite": controls += list(kw["ledger_headers"])
            if app == "InvoiceTwinScout": controls.append(kw["invoice_window"])
            if app == "ProcureGuardStudioPro": controls += list(kw["policy_rules"])
            for index in range(len(controls)):
                with self.subTest(app=app, control=index):
                    self.reject(app, generate_as=index)

    def test_premium_review_must_not_alias_any_input_or_output_control(self):
        for app in ("GrantAuditStudioPro", "ProcureGuardStudioPro"):
            _, fields, output, _, _, kw = fixture(app)
            length = 2 * (len(fields) + 1) + (2 if "policy_rules" in kw else 0)
            for index in range(length):
                with self.subTest(app=app, control=index):
                    self.reject(app, review_as=index)

    def test_review_cannot_alias_generate(self):
        for app in ("GrantAuditStudioPro", "ProcureGuardStudioPro"):
            with self.subTest(app=app):
                self.reject(app, review_as="generate")

    def test_missing_or_noncommand_generate_rejected_without_partial_binding(self):
        for bad in (None, object(), "generate"):
            root, fields, output, _, _, kw = fixture("SpendMapLite")
            with self.subTest(type=type(bad).__name__), self.assertRaises(ValueError):
                install_shortcuts(root, fields, output, bad, **kw)
            self.assertEqual(root.bindings, {})

    def test_invalid_premium_review_rejected_without_partial_binding(self):
        for bad in (object(), "review", 0):
            root, fields, output, generate, _, kw = fixture("ProcureGuardStudioPro")
            kw["review"] = bad
            with self.subTest(type=type(bad).__name__), self.assertRaises(ValueError):
                install_shortcuts(root, fields, output, generate, **kw)
            self.assertEqual(root.bindings, {})

    def test_disabled_generate_never_invoked_by_shortcut(self):
        root, fields, output, generate, _, kw = fixture("GrantAuditStudioPro")
        generate.enabled = False
        install_shortcuts(root, fields, output, generate, **kw)
        root.press("<Alt-Key-g>")
        root.press("<Control-Return>")
        self.assertEqual(generate.events, [])

    def test_disabled_premium_review_never_invoked_by_shortcut(self):
        root, fields, output, generate, review, kw = fixture("ProcureGuardStudioPro")
        review.enabled = False
        install_shortcuts(root, fields, output, generate, **kw)
        root.press("<Alt-Key-r>")
        self.assertEqual(review.events, [])

    def test_browse_shortcut_never_invokes_generate_or_premium_review(self):
        root, fields, output, generate, review, kw = fixture("ProcureGuardStudioPro")
        install_shortcuts(root, fields, output, generate, **kw)
        root.press("<Control-Key-1>")
        root.press("<Control-Key-o>")
        root.press("<Control-Key-p>")
        self.assertEqual(generate.events, [])
        self.assertEqual(review.events, [])
        self.assertEqual(fields[0][1].events, ["invoke"])


    def test_keypad_and_optional_shortcut_counts_for_all_six(self):
        expected = {"LedgerDiffLite": 20, "InvoiceTwinScout": 11,
                    "SpendMapLite": 10, "PolicyDeltaDesk": 16,
                    "GrantAuditStudioPro": 23, "ProcureGuardStudioPro": 25}
        for app, count in expected.items():
            with self.subTest(app=app):
                root, fields, output, generate, _, kw = fixture(app)
                installed = install_shortcuts(root, fields, output, generate, **kw)
                self.assertEqual(len(installed), count)
                self.assertEqual(len(root.bindings), count)
                self.assertEqual(len(set(installed)), count)


if __name__ == "__main__":
    unittest.main()
