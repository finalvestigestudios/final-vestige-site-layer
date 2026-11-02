#!/usr/bin/env python3
"""Offline hostile/positive contract tests for the private WP usability gate."""
import importlib.util
from pathlib import Path
from unittest import TestCase, main

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fv_usability_gate", HERE / "verify_private_usability.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

REQUIRED = {
    "reflow_320:real_wordpress", "reflow_320:no_root_overflow",
    "reflow_320:seven_chapters", "reflow_320:reduced_motion",
    "reflow_320:primary_nav_fully_visible",
    "reflow_640:real_wordpress", "reflow_640:no_root_overflow",
    "reflow_640:seven_chapters", "reflow_640:primary_nav_fully_visible",
    "reflow_640:reduced_motion",
    "keyboard_390:real_wordpress", "keyboard_390:focus_visible",
    "keyboard_390:case_enter", "keyboard_390:case_space",
    "keyboard_390:chronicle_enter", "keyboard_390:native_details_keyboard",
    "keyboard_390:reduced_motion", "touch_390:real_wordpress",
    "touch_390:case_tap", "touch_390:chronicle_tap",
    "touch_390:reduced_motion",
    "pinch_200_390:real_wordpress", "pinch_200_390:reduced_motion",
    "pinch_200_390:visual_viewport_2x",
    "pinch_200_390:seven_chapters", "pinch_200_390:case_tap_at_2x",
    "pinch_200_390:zoomed_layout_no_global_overflow"
}


class UsabilityContract(TestCase):
    def test_all_twenty_seven_checks_produce_clean_result(self):
        self.assertEqual(module.grade({k: True for k in REQUIRED}), [])

    def test_empty_checks_fail_closed(self):
        self.assertIn("MISSING_OR_NONBOOLEAN_CHECK", module.grade({}))

    def test_false_case_keyboard_activation_is_rejected(self):
        checks = {k: True for k in REQUIRED}
        checks["keyboard_390:case_enter"] = False
        self.assertIn("FAIL_keyboard_390_case_enter", module.grade(checks))

    def test_false_touch_case_is_rejected(self):
        checks = {k: True for k in REQUIRED}
        checks["touch_390:case_tap"] = False
        self.assertIn("FAIL_touch_390_case_tap", module.grade(checks))

    def test_missing_reflow_is_rejected(self):
        checks = {k: True for k in REQUIRED if k != "reflow_320:no_root_overflow"}
        self.assertIn("MISSING_reflow_320_no_root_overflow", module.grade(checks))

    def test_nonboolean_result_cannot_pass(self):
        checks = {k: True for k in REQUIRED}
        checks["keyboard_390:focus_visible"] = "true"
        self.assertIn("MISSING_OR_NONBOOLEAN_CHECK", module.grade(checks))

    def test_profile_contract_five_browser_modes(self):
        self.assertEqual(module.PROFILES, (
            ("reflow_320", 320, False), ("reflow_640", 640, False),
            ("keyboard_390", 390, False), ("touch_390", 390, True),
            ("pinch_200_390", 390, True)))

    def test_missing_actual_visual_zoom_fails_closed(self):
        checks = {k: True for k in REQUIRED if k != "pinch_200_390:visual_viewport_2x"}
        self.assertIn("MISSING_pinch_200_390_visual_viewport_2x", module.grade(checks))

    def test_false_pinch_zoom_target_fails_closed(self):
        checks = {k: True for k in REQUIRED}
        checks["pinch_200_390:visual_viewport_2x"] = False
        self.assertIn("FAIL_pinch_200_390_visual_viewport_2x", module.grade(checks))

    def test_2x_pinch_global_overflow_fails_closed(self):
        checks = {k: True for k in REQUIRED}
        checks["pinch_200_390:zoomed_layout_no_global_overflow"] = False
        self.assertIn("FAIL_pinch_200_390_zoomed_layout_no_global_overflow", module.grade(checks))

    def test_reflow_640_nav_clipping_fails_closed(self):
        checks = {k: True for k in REQUIRED}
        checks["reflow_640:primary_nav_fully_visible"] = False
        self.assertIn("FAIL_reflow_640_primary_nav_fully_visible", module.grade(checks))

    def test_production_is_never_a_target(self):
        self.assertEqual(module.PAGE,
                         "http://127.0.0.1:9400/?pagename=fv-ex2-playground-review")
        self.assertNotIn("finalvestige.com", module.PAGE)

    def test_unexpected_extra_false_check_does_not_pass(self):
        checks = {k: True for k in REQUIRED}
        checks["keyboard_390:unexpected_control"] = False
        self.assertIn("FAIL_keyboard_390_unexpected_control", module.grade(checks))


if __name__ == "__main__":
    main()
