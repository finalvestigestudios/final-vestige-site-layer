import unittest
from pathlib import Path

CSS = (Path(__file__).resolve().parent / 'focus_autofill.css').read_text()


class AutofillCSSContractTests(unittest.TestCase):
    def test_patches_autofill(self):
        self.assertIn(':-webkit-autofill:focus', CSS)
        self.assertIn(':autofill', CSS)

    def test_dark_background_and_visible_text(self):
        self.assertIn('0 1000px #101111 inset !important', CSS)
        self.assertIn('-webkit-text-fill-color: #F4EFE6 !important', CSS)

    def test_no_jetpack_behavior_override(self):
        for unsafe in ('pointer-events', 'disabled', 'readonly', 'display:none', 'visibility:hidden'):
            self.assertNotIn(unsafe, CSS)

    def test_scoped_to_focus_page(self):
        import re
        selectors = re.findall(r'([^{}]+)\{[^{}]*\}', re.sub(r'/\*.*?\*/', '', CSS, flags=re.S))
        for group in selectors:
            for selector in group.split(','):
                self.assertTrue(selector.strip().startswith('.fv-focus .wp-block-jetpack-subscriptions input[type="email"]'), selector)


if __name__ == '__main__': unittest.main()
