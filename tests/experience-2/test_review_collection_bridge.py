"""Source continuity and commercial safety for isolated homepage exit bridge."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('bridge', ROOT / 'tools/experience-2/review_collection_bridge.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def homepage():
    return ('<div class="fv-hf">' + ''.join(f'<section id="{x}"></section>' for x in mod.CHAPTER_IDS)
            + '<!-- wp:jetpack/subscriptions -->' + '<div class="fv-margin-strip">'
            + '<p class="fv-margin-strip__item">Published position</p>' * 72 + '</div>'
            + '<a href="/focus/">Focus</a>' + '<a href="https://finalvestige.com/focus/">Focus</a>'
            + mod.EXIT + '</div>')


def guide():
    return ('Mini Museum <p>Affiliate disclosure: Commission may be earned.</p>'
            '<a rel="sponsored noopener noreferrer" href="https://www.awin1.com/cread.php?'
            's=4236132&amp;v=89949&amp;q=552988&amp;r=3055117">Specimens</a>')


class ReviewBridgeTests(unittest.TestCase):
    def test_success_and_full_restore(self):
        original = homepage()
        changed, manifest = mod.patch(original, guide())
        self.assertTrue(manifest['byte_perfect_restore'])
        self.assertEqual(changed.count(mod.GUIDE_LINK), 1)
        self.assertEqual(changed.count('class="fv-margin-strip__item"'), 72)
        self.assertEqual(changed.count('<!-- wp:jetpack/subscriptions'), 1)
        self.assertEqual(manifest['new_affiliate_links'], 0)
        self.assertEqual(manifest['new_scripts'], 0)
        self.assertIn(':focus-visible', changed)
        self.assertIn('min-height:44px', changed)
        self.assertEqual(changed.count('href="https://finalvestige.com/focus/"'), 2)
        self.assertEqual(changed.count('href="https://finalvestige.com/blog/"'), 1)

    def test_blocks_duplicate(self):
        bad, _ = mod.patch(homepage(), guide())
        with self.assertRaises(ValueError): mod.patch(bad, guide())

    def test_blocks_missing_margin(self):
        bad = homepage().replace('class="fv-margin-strip__item"', 'class="lost"', 1)
        with self.assertRaises(ValueError): mod.patch(bad, guide())

    def test_blocks_jetpack_removal(self):
        with self.assertRaises(ValueError): mod.patch(homepage().replace('<!-- wp:jetpack/subscriptions -->', ''), guide())

    def test_blocks_changed_exit(self):
        with self.assertRaises(ValueError): mod.patch(homepage().replace('The Public Record', 'Public Records'), guide())

    def test_blocks_missing_chapter(self):
        with self.assertRaises(ValueError): mod.patch(homepage().replace('id="fv-hf-observer"', 'id="none"'), guide())

    def test_blocks_incomplete_guide(self):
        with self.assertRaises(ValueError): mod.patch(homepage(), 'Mini Museum')

    def test_blocks_unapproved_sponsored_rel(self):
        with self.assertRaises(ValueError): mod.patch(homepage(), guide().replace('sponsored noopener noreferrer','noopener noreferrer'))

    def test_no_remote_urls_or_tracking_added(self):
        changed, _ = mod.patch(homepage(), guide())
        fragment = changed.split(mod.EXIT.split('      </section>')[0])[-1].split('</style>')[0]
        self.assertNotIn('https://www.awin1.com', fragment)
        self.assertNotIn('<script', fragment)
        self.assertNotIn('utm_', fragment)


if __name__ == '__main__': unittest.main()
