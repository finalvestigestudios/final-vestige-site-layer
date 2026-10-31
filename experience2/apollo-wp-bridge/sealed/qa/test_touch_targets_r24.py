"""Staging touch-target CSS source pin / adversarial test contract."""
import hashlib
from pathlib import Path
import unittest
from touch_targets_r24 import build_touch_targets, CSS, SELECTORS

HERE = Path(__file__).resolve().parent
GENERATED = HERE.parent.parent / 'generated'

class TouchTargetsR24(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment = (GENERATED/'fragment.html').read_text(encoding='utf-8')

    def test_eight_scoped_target_regions(self):
        css, receipt = build_touch_targets(self.fragment)
        self.assertEqual(receipt['selectors'], 8)
        self.assertEqual(len(SELECTORS),8)
        self.assertEqual(css.count('min-height:44px'),1)
        self.assertTrue(all(s.startswith('.fv-ex2-apollo ') for s in SELECTORS))

    def test_digest_determinism_and_source_integrity(self):
        css, receipt = build_touch_targets(self.fragment)
        self.assertEqual(css,CSS)
        self.assertEqual(receipt['css_sha256'],hashlib.sha256(css.encode()).hexdigest())
        self.assertFalse(receipt['source_modified'])

    def test_missing_region_refuses_to_build(self):
        for marker in ('ex2-source__links','ex2-gallery__links','id="claim-ledger"',
                       'ex2-footer','ex2-atlas__item'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                build_touch_targets(self.fragment.replace(marker,'R24_DELETED'))

    def test_no_remote_assets_script_geo_or_media_promotion(self):
        css, receipt=build_touch_targets(self.fragment)
        self.assertFalse(any(x in css.lower() for x in ('@import','url(', '<script','<img')))
        self.assertFalse(receipt['external_media_embedded'])
        self.assertFalse(receipt['geography_added'])

    def test_keyboard_focus_and_reduced_motion(self):
        self.assertIn(':focus-visible',CSS)
        self.assertIn('prefers-reduced-motion:reduce',CSS)
        self.assertIn('overflow-wrap:anywhere',CSS)

if __name__=='__main__':unittest.main()
