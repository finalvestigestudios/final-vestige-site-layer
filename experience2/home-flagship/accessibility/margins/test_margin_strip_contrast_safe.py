"""Source-level regression checks; browser acceptance runs in the companion workflow."""
import unittest
from probe_margin_strip_contrast import BASE_CSS, CSS, WIDTHS, PHASES, fixture, contrast

class MarginStripRemedyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=CSS.read_text()

    def test_exact_original_360_second_schedule_is_represented(self):
        self.assertIn("animation:fvMarginReveal 360s linear infinite",BASE_CSS)
        self.assertIn("animation-delay:calc(var(--i) * 5s)",BASE_CSS)

    def test_baseline_original_opacity_and_blur_problem(self):
        self.assertIn("opacity:.46",BASE_CSS)
        self.assertIn("opacity:.42",BASE_CSS)
        self.assertIn("filter:blur(5px)",BASE_CSS)

    def test_new_animation_name_is_explicit(self):
        self.assertIn("animation-name: fvMarginContrastSafe;",self.css)
        self.assertNotIn("animation-name: fvMarginReveal;",self.css)

    def test_visible_text_is_never_partially_transparent(self):
        self.assertIn("opacity: 1;",self.css)
        self.assertNotIn("opacity: .",self.css)
        self.assertIn("steps(1, end)",self.css)

    def test_visible_text_is_never_blurred(self):
        self.assertIn("filter: none;",self.css)
        self.assertNotIn("filter: blur(",self.css)

    def test_original_timing_preserved_and_hidden_between_slots(self):
        self.assertIn("0%, 1.38%",self.css)
        self.assertIn("1.39%, 100%",self.css)
        self.assertIn("visibility: hidden;",self.css)

    def test_reduced_motion_uses_first_fragment_without_animation(self):
        self.assertIn("prefers-reduced-motion: reduce",self.css)
        self.assertIn(":first-child",self.css)
        self.assertIn("animation: none;",self.css)

    def test_synthetic_fixture_preserves_seventy_two_positions(self):
        self.assertEqual(fixture(True).count('class="fv-margin-strip__item"'),72)
        self.assertIn('style="--i:71"',fixture(True))

    def test_fixture_does_not_include_external_assets_or_live_history(self):
        sample=fixture(True)
        self.assertNotIn("https://",sample)
        self.assertNotIn("<img",sample)
        self.assertNotIn("<script",sample)
        self.assertNotIn("NYPL",sample)

    def test_contrast_math_is_sensitive_to_alpha(self):
        self.assertLess(contrast("rgb(216, 210, 199)","rgb(15, 16, 15)",.42),4.5)
        self.assertGreater(contrast("rgb(216, 210, 199)","rgb(15, 16, 15)",1.0),7.0)

    def test_matrix_has_mobile_desktop_and_wraparound(self):
        self.assertEqual(WIDTHS,(320,390,768,1440,1920))
        self.assertTrue(any(355<t<360 for t in PHASES))
        self.assertTrue(any(t>360 for t in PHASES))

if __name__=="__main__":
    unittest.main()
