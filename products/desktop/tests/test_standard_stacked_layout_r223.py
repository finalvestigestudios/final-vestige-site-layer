"""R223: deterministic five-app 200%/400% reflow plans, no Tk display required."""
from __future__ import annotations
import unittest
from fvs_suite.form_layout import standard_stacked_rows

COUNTS = {"invoices": 1, "spend": 1, "policy": 2,
          "grants": 3, "procurement": 3}


class StandardStackedLayoutR223(unittest.TestCase):
    def test_all_five_exact_input_layouts(self):
        for app, count in COUNTS.items():
            with self.subTest(app=app):
                self.assertEqual(standard_stacked_rows(app, count)["inputs"],
                                 tuple((3 + 3*i, 4 + 3*i, 5 + 3*i)
                                       for i in range(count)))

    def test_no_row_is_reused_by_another_control(self):
        for app, count in COUNTS.items():
            plan = standard_stacked_rows(app, count)
            positions = []
            for key, value in plan.items():
                if key == "inputs":
                    positions.extend(row for triple in value for row in triple)
                elif type(value) is tuple:
                    positions.extend(value)
                else:
                    positions.append(value)
            with self.subTest(app=app):
                self.assertEqual(positions, list(range(3, plan["hint"] + 1)))
                self.assertEqual(len(positions), len(set(positions)))

    def test_native_tab_order_browse_after_entry(self):
        for app, count in COUNTS.items():
            plan = standard_stacked_rows(app, count)
            for label, entry, browse in plan["inputs"]:
                self.assertLess(label, entry)
                self.assertLess(entry, browse)
            self.assertLess(plan["inputs"][-1][-1], plan["output"][1])
            self.assertLess(plan["output"][1], plan["output"][2])
            self.assertLess(plan["output"][2], plan["generate"])

    def test_invoice_window_not_overlaid_by_output(self):
        plan = standard_stacked_rows("invoices", 1)
        self.assertEqual(plan["window"], (6, 7))
        self.assertEqual(plan["output"], (8, 9, 10))
        self.assertEqual(plan["generate"], 12)

    def test_spend_free_rows(self):
        plan = standard_stacked_rows("spend", 1)
        self.assertEqual(plan["output"], (6, 7, 8))
        self.assertEqual(plan["status"], 9)
        self.assertEqual(plan["hint"], 12)

    def test_policy_two_inputs(self):
        plan = standard_stacked_rows("policy", 2)
        self.assertEqual(plan["output"], (9, 10, 11))
        self.assertEqual(plan["hint"], 15)

    def test_grant_premium_review_is_after_generate(self):
        plan = standard_stacked_rows("grants", 3)
        self.assertEqual(plan["output"], (12, 13, 14))
        self.assertEqual(plan["review"], 17)
        self.assertEqual(plan["hint"], 19)

    def test_procurement_rules_browse_separate_row(self):
        plan = standard_stacked_rows("procurement", 3)
        self.assertEqual(plan["rules"], (15, 16, 17))
        self.assertEqual(plan["review"], 20)
        self.assertEqual(plan["hint"], 22)

    def test_free_apps_never_gain_premium_review(self):
        for app in ("invoices", "spend", "policy"):
            self.assertNotIn("review", standard_stacked_rows(app, COUNTS[app]))

    def test_premium_review_is_preserved(self):
        for app in ("grants", "procurement"):
            self.assertIn("review", standard_stacked_rows(app, COUNTS[app]))

    def test_invoice_window_only_for_invoices(self):
        for app in COUNTS:
            self.assertEqual("window" in standard_stacked_rows(app, COUNTS[app]),
                             app == "invoices")

    def test_optional_policy_picker_only_in_procurement(self):
        for app in COUNTS:
            self.assertEqual("rules" in standard_stacked_rows(app, COUNTS[app]),
                             app == "procurement")

    def test_reject_unknown_app_id(self):
        for app in ("ledger", "wrong", "", None, b"invoices", True):
            with self.subTest(app=repr(app)), self.assertRaises(ValueError):
                standard_stacked_rows(app, 1)

    def test_reject_wrong_count_and_non_native_int(self):
        for app, correct in COUNTS.items():
            for count in (correct-1, correct+1, True, False, float(correct),
                          str(correct), None, -1):
                with self.subTest(app=app, count=repr(count)):
                    with self.assertRaises(ValueError):
                        standard_stacked_rows(app, count)

    def test_repeat_deterministic_and_not_shared_mutable_state(self):
        for app, count in COUNTS.items():
            expected = standard_stacked_rows(app, count)
            again = standard_stacked_rows(app, count)
            self.assertEqual(expected, again)
            expected["status"] = -1
            self.assertNotEqual(expected, standard_stacked_rows(app, count))

    def test_layout_contains_only_public_geometry(self):
        for app, count in COUNTS.items():
            plan = standard_stacked_rows(app, count)
            self.assertTrue(all(type(key) is str for key in plan))
            self.assertNotIn("file", str(plan).lower())
            self.assertNotIn("amount", str(plan).lower())


if __name__ == "__main__":
    unittest.main()
