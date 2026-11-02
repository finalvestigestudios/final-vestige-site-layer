"""R107 scaled form and fail-closed preflight regressions; no Tk display needed."""
from __future__ import annotations

import contextlib
import io
import math
from pathlib import Path
import sys
import unittest

from fvs_suite.scroll_access import focus_scroll_fraction

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import native_scale_probe_r107 as probe


def observed(app_id="ledger", scale=2.0):
    browse_fields = probe.FREE_INPUTS[app_id] + 1
    editable_fields = browse_fields + (4 if app_id == "ledger" else 1 if app_id == "invoices" else 0)
    return dict(scale=scale, entries=editable_fields, browse=browse_fields, generate=1,
                scrollable=True, focus_revealed=True, labels_wrapped=True,
                controls_nonfocus=True, system_background=True)


class ScrollMathR107(unittest.TestCase):
    def test_no_scroll_when_all_content_fits(self):
        self.assertIsNone(focus_scroll_fraction(300, 400, 0, 10, 30))

    def test_no_scroll_for_visible_midpoint(self):
        self.assertIsNone(focus_scroll_fraction(1000, 300, 200, 300, 30))

    def test_reveal_lower_control(self):
        self.assertAlmostEqual(focus_scroll_fraction(1000, 200, 0, 700, 30), .542)

    def test_reveal_earlier_control(self):
        self.assertAlmostEqual(focus_scroll_fraction(1000, 200, 500, 20, 30), .008)

    def test_at_bottom_fraction_is_bounded(self):
        self.assertLessEqual(focus_scroll_fraction(1000, 200, 0, 995, 100), 1.0)

    def test_at_top_fraction_is_bounded(self):
        self.assertGreaterEqual(focus_scroll_fraction(1000, 200, 500, -20, 30), 0.0)

    def test_scroll_fraction_is_repeatable(self):
        args = (2500, 390, 0, 1800, 55)
        self.assertEqual(focus_scroll_fraction(*args), focus_scroll_fraction(*args))

    def test_small_viewport_is_supported(self):
        self.assertIsInstance(focus_scroll_fraction(1000, 40, 0, 200, 20), float)

    def test_margin_does_not_oscillate_when_centered(self):
        fraction = focus_scroll_fraction(1000, 200, 0, 700, 30)
        self.assertIsNone(focus_scroll_fraction(1000, 200, fraction * 1000, 700, 30))

    def test_untrusted_nan_rejected(self):
        with self.assertRaises(ValueError):
            focus_scroll_fraction(math.nan, 200, 0, 10, 30)

    def test_untrusted_infinity_rejected(self):
        with self.assertRaises(ValueError):
            focus_scroll_fraction(1000, math.inf, 0, 10, 30)

    def test_untrusted_string_rejected(self):
        with self.assertRaises(ValueError):
            focus_scroll_fraction(1000, 200, "input/path", 10, 30)

    def test_boolean_geometry_rejected(self):
        with self.assertRaises(ValueError):
            focus_scroll_fraction(1000, True, 0, 10, 30)

    def test_nonpositive_geometry_rejected(self):
        for args in ((0, 100, 0, 10, 20),
                     (100, 0, 0, 10, 20),
                     (100, 50, 0, 10, -1)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    focus_scroll_fraction(*args)

    def test_values_do_not_depend_on_financial_input(self):
        self.assertEqual(focus_scroll_fraction(700, 200, 0, 500, 20), .4742857142857143)


class NativeScaleContractR107(unittest.TestCase):
    def check_blocked(self, app_id="ledger", **changes):
        sample = observed(app_id)
        sample.update(changes)
        with self.assertRaises(probe.ScaleBlocked):
            probe.verify_snapshot(app_id, **sample)

    def test_source_free_app_inventory(self):
        self.assertEqual(set(probe.FREE_INPUTS), {"ledger", "invoices", "spend", "policy"})

    def test_eight_native_observation_shapes_pass(self):
        for app_id in probe.FREE_INPUTS:
            for scale in probe.SCALES:
                with self.subTest(app=app_id, zoom=scale):
                    probe.verify_snapshot(app_id, **observed(app_id, scale))

    def test_premium_editor_is_out_of_scope(self):
        with self.assertRaises(probe.ScaleBlocked):
            probe.verify_snapshot("grants", **observed())

    def test_unknown_editor_is_rejected(self):
        with self.assertRaises(probe.ScaleBlocked):
            probe.verify_snapshot("other", **observed())

    def test_wrong_scale_rejected(self):
        self.check_blocked(scale=1.0)

    def test_boolean_scale_rejected(self):
        self.check_blocked(scale=True)

    def test_missing_entry_rejected(self):
        self.check_blocked(entries=2)

    def test_too_many_entry_rejected(self):
        self.check_blocked(entries=4)

    def test_missing_browse_rejected(self):
        self.check_blocked(browse=1)

    def test_missing_generate_rejected(self):
        self.check_blocked(generate=0)

    def test_boolean_count_rejected(self):
        self.check_blocked(generate=True)

    def test_inaccessible_scroll_rejected(self):
        self.check_blocked(scrollable=False)

    def test_missing_keyboard_focus_reveal_rejected(self):
        self.check_blocked(focus_revealed=False)

    def test_unwrapped_hints_rejected(self):
        self.check_blocked(labels_wrapped=False)

    def test_scrollbar_as_extra_focus_stop_rejected(self):
        self.check_blocked(controls_nonfocus=False)

    def test_non_system_background_rejected(self):
        self.check_blocked(system_background=False)

    def test_truthy_nonboolean_observation_rejected(self):
        self.check_blocked(scrollable=1)

    def test_extra_cli_argument_fails_without_details(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            result = probe.main(["--unsafe"])
        self.assertEqual(result, 1)
        self.assertEqual(out.getvalue().strip(), probe.ERROR)


if __name__ == "__main__":
    unittest.main()
