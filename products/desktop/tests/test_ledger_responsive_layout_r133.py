"""R133: source-owned deterministic LedgerDiff vertical reflow regressions.

Pure contracts run headlessly on Linux/Windows, normal and -OO. Native R107
must still prove actual Windows Tk mapping/scroll/focus at 200% and 400%.
No private financial values, paths, dialogs, file mutations or premium access.
"""
from __future__ import annotations

import inspect
import unittest

from fvs_suite import app


class LedgerResponsiveLayoutR133(unittest.TestCase):
    def setUp(self):
        self.plan = app._ledger_stacked_rows(2)

    def test_exact_two_input_row_plan(self):
        self.assertEqual(self.plan["inputs"], ((3, 4, 5), (6, 7, 8)))
        self.assertEqual(self.plan["keys"], ((9, 10), (11, 12)))
        self.assertEqual(self.plan["amounts"], ((13, 14), (15, 16)))
        self.assertEqual(self.plan["output"], (17, 18, 19))

    def test_each_rendered_control_gets_its_own_row(self):
        rows = tuple(v for group in
                     (self.plan["inputs"] + self.plan["keys"] + self.plan["amounts"] +
                      (self.plan["output"],))
                     for v in group)
        self.assertEqual(rows, tuple(range(3, 20)))
        self.assertEqual(len(rows), len(set(rows)))

    def test_first_controls_preserve_native_tab_creation_order(self):
        fields = self.plan["inputs"]
        self.assertLess(fields[0][1], fields[0][2])
        self.assertLess(fields[0][2], fields[1][1])
        self.assertLess(fields[1][2], self.plan["keys"][0][1])
        self.assertLess(self.plan["keys"][0][1], self.plan["keys"][1][1])
        self.assertLess(self.plan["keys"][1][1], self.plan["amounts"][0][1])
        self.assertLess(self.plan["amounts"][0][1], self.plan["amounts"][1][1])
        self.assertLess(self.plan["amounts"][1][1], self.plan["output"][1])
        self.assertLess(self.plan["output"][1], self.plan["output"][2])

    def test_actions_and_hint_follow_every_editable_control(self):
        self.assertEqual(self.plan["status"], 20)
        self.assertEqual(self.plan["generate"], 21)
        self.assertEqual(self.plan["disclaimer"], 22)
        self.assertEqual(self.plan["hint"], 23)
        self.assertGreater(self.plan["generate"], self.plan["output"][2])

    def test_title_and_disclaimer_rows_are_not_overwritten(self):
        rows = list(range(3, self.plan["hint"] + 1))
        self.assertFalse({0, 1, 2}.intersection(rows))

    def test_bool_float_and_changed_file_inventory_fail_closed(self):
        for count in (None, False, True, 0, 1, 3, -1, 2.0, "2"):
            with self.subTest(type=type(count).__name__, value=repr(count)):
                with self.assertRaises(ValueError):
                    app._ledger_stacked_rows(count)

    def test_repeat_has_identical_rows(self):
        self.assertEqual(self.plan, app._ledger_stacked_rows(2))

    def test_mutating_returned_map_does_not_modify_future_layout(self):
        self.plan["status"] = -123
        self.assertEqual(app._ledger_stacked_rows(2)["status"], 20)

    def test_production_ui_selects_stacked_ledger_only(self):
        source = inspect.getsource(app.run)
        self.assertIn('_ledger_stacked_rows(len(labels)) if app_id == "ledger" else None',
                      source)
        self.assertIn('frame.columnconfigure(0, weight=1)', source)
        self.assertIn('frame.columnconfigure(1, weight=0)', source)
        self.assertIn('if ledger_layout:', source)
        self.assertIn('columnspan=3, sticky="ew"', source)
        self.assertIn('width=1', source)

    def test_other_apps_stay_in_original_tiers(self):
        self.assertEqual(
            {name: len(config[1]) for name, config in app.APPS.items()},
            {"ledger": 2, "invoices": 1, "spend": 1, "policy": 2,
             "grants": 3, "procurement": 3})
        self.assertEqual(
            {name for name, config in app.APPS.items() if config[3]},
            {"grants", "procurement"})


if __name__ == "__main__":
    unittest.main()
