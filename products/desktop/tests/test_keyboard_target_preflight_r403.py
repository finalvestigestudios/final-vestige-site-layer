"""R403: six-app keyboard access fails before binding broken controls."""
from __future__ import annotations

import unittest
from fvs_suite.shortcut_targets_r403 import validate_shortcut_targets


class Entry:
    def __init__(self):
        self.focused = 0
    def focus_set(self):
        self.focused += 1


class Button:
    def __init__(self, command=None, enabled=True):
        self.command = command
        self.enabled = enabled
        self.calls = 0
    def invoke(self):
        if self.enabled:
            self.calls += 1
            if self.command:
                self.command()


class Missing:
    pass


class BrokenFocus:
    focus_set = None


class BrokenInvoke:
    invoke = False


def good(n):
    return [(Entry(), Button()) for _ in range(n)], (Entry(), Button()), Button()


class PreflightR403(unittest.TestCase):
    def valid(self, n, **options):
        fields, out, go = good(n)
        self.assertIsNone(validate_shortcut_targets(fields, out, go, **options))
        self.assertEqual(go.calls, 0)
        self.assertEqual(sum(x.focused for x, _ in fields), 0)
        return fields, out, go

    def test_ledger_configuration(self):
        self.valid(2, ledger_headers=tuple(Entry() for _ in range(4)))

    def test_invoice_configuration(self):
        self.valid(1, invoice_window=Entry())

    def test_spend_configuration(self):
        self.valid(1)

    def test_policy_configuration(self):
        self.valid(2)

    def test_grant_premium_configuration(self):
        self.valid(3, review=Button())

    def test_procure_premium_policy_configuration(self):
        self.valid(3, review=Button(), policy_rules=(Entry(), Button()))

    def test_missing_input_entry_focus(self):
        fields, output, go = good(2)
        fields[0] = (BrokenFocus(), fields[0][1])
        with self.assertRaisesRegex(ValueError, "unavailable"):
            validate_shortcut_targets(fields, output, go)
        self.assertEqual(go.calls, 0)

    def test_missing_second_input_browse(self):
        fields, output, go = good(3)
        fields[1] = (fields[1][0], BrokenInvoke())
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go)

    def test_missing_output_entry_focus(self):
        fields, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, (Missing(), output[1]), go)

    def test_missing_output_browse(self):
        fields, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, (output[0], Missing()), go)

    def test_generate_invoker_missing(self):
        fields, output, _ = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, Missing())

    def test_premium_review_invoker_missing(self):
        fields, output, go = good(3)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go, review=BrokenInvoke())

    def test_invoice_focus_missing(self):
        fields, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go, invoice_window=Missing())

    def test_policy_entry_focus_missing(self):
        fields, output, go = good(3)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go, policy_rules=(Missing(), Button()))

    def test_policy_browse_invoker_missing(self):
        fields, output, go = good(3)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go, policy_rules=(Entry(), BrokenInvoke()))

    def test_ledger_header_focus_missing(self):
        fields, output, go = good(2)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go,
                                      ledger_headers=(Entry(), Entry(), Missing(), Entry()))

    def test_no_controls(self):
        _, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets([], output, go)

    def test_four_controls(self):
        _, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(good(3)[0] + good(1)[0], output, go)

    def test_malformed_pair(self):
        _, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets([(Entry(),)], output, go)

    def test_reject_forged_list_subclass(self):
        class Tricky(list):
            def __len__(self):
                raise AssertionError("should not run custom length")
        _, output, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(Tricky([(Entry(), Button())]), output, go)

    def test_malformed_ledger_headers(self):
        fields, output, go = good(2)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, output, go, ledger_headers=(Entry(),))

    def test_no_execution_of_entitlement_or_financial_commands(self):
        fields, output, go = good(3)
        review = Button(command=lambda: self.fail("premium review executed"))
        go.command = lambda: self.fail("financial operation executed")
        validate_shortcut_targets(fields, output, go, review=review)
        self.assertEqual(review.calls, 0)
        self.assertEqual(go.calls, 0)

    def test_disabled_actions_remain_supported_for_native_tk(self):
        fields, output, go = good(3)
        go.enabled = False
        review = Button(enabled=False)
        validate_shortcut_targets(fields, output, go, review=review)
        self.assertEqual((go.calls, review.calls), (0, 0))

    def test_bad_output_sequence_rejected(self):
        fields, _, go = good(1)
        with self.assertRaises(ValueError):
            validate_shortcut_targets(fields, "not-a-widget-pair", go)


if __name__ == "__main__":
    unittest.main()
