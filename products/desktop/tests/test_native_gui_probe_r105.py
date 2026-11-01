"""Synthetic Windows GUI gate regressions: no GUI or customer files required."""
import unittest
from pathlib import Path
from scripts import windows_gui_probe_r105 as gate

class NativeGuiAdmissibilityR105(unittest.TestCase):
    def setUp(self):
        self.parents = {200: 100, 300: 200, 900: 800, 800: 0}
        self.new = [(51, 300, "Final Vestige Labs — LedgerDiff Lite")]
        self.exact = "Final Vestige Labs — LedgerDiff Lite"

    def test_child_window_admitted(self):
        self.assertTrue(gate._admit(self.new, set(), self.parents, 100, self.exact, "main"))

    def test_launcher_own_window_admitted(self):
        self.assertTrue(gate._admit([(51, 100, self.exact)], set(), self.parents,
                                    100, self.exact, "main"))

    def test_different_process_rejected(self):
        self.assertFalse(gate._admit([(51, 900, self.exact)], set(), self.parents,
                                     100, self.exact, "main"))

    def test_preexisting_window_rejected(self):
        self.assertFalse(gate._admit(self.new, {51}, self.parents, 100, self.exact, "main"))

    def test_wrong_window_title_rejected(self):
        self.assertFalse(gate._admit([(51, 300, "LedgerDiff Lite — impostor")],
                                     set(), self.parents, 100, self.exact, "main"))

    def test_child_of_unrelated_parent_rejected(self):
        self.assertFalse(gate._descends(900, 100, self.parents))

    def test_parent_process_itself_valid(self):
        self.assertTrue(gate._descends(100, 100, self.parents))

    def test_loop_in_parent_links_does_not_hang(self):
        self.assertFalse(gate._descends(901, 100, {901: 902, 902: 901}))

    def test_unknown_parent_refused(self):
        self.assertFalse(gate._descends(300, 400, self.parents))

    def test_premium_lock_dialog_admitted(self):
        windows = [(8, 200, "Premium preview locked")]
        self.assertTrue(gate._admit(windows, set(), self.parents, 100,
                                    "Premium preview locked", "locked"))

    def test_premium_main_editor_exposure_refused_even_if_locked(self):
        windows = [(8, 200, "Premium preview locked"),
                   (9, 300, gate.FORBIDDEN_PREMIUM[0])]
        with self.assertRaises(gate.GUIBlocked):
            gate._admit(windows, set(), self.parents, 100,
                        "Premium preview locked", "locked")

    def test_other_process_premium_editor_not_attributed(self):
        windows = [(8, 200, "Premium preview locked"),
                   (9, 900, gate.FORBIDDEN_PREMIUM[0])]
        self.assertTrue(gate._admit(windows, set(), self.parents, 100,
                                    "Premium preview locked", "locked"))

    def test_all_six_products_have_explicit_distinct_names(self):
        self.assertEqual(len(gate.WINDOWS), 6)
        self.assertEqual(len({entry[0] for entry in gate.WINDOWS}), 6)
        self.assertEqual([entry[2] for entry in gate.WINDOWS],
                         ["main"] * 4 + ["locked"] * 2)

    def test_no_product_claims_premium_activation(self):
        self.assertEqual(gate.WINDOWS[-2][1], "Premium preview locked")
        self.assertEqual(gate.WINDOWS[-1][1], "Premium preview locked")

if __name__ == "__main__":
    unittest.main()
