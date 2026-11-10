"""Offline mutation controls; synthetic WordPress markup, no live site writes."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from verify_homepage_preservation import inventory, evaluate


class PreservationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = ''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">Public record {i}</span>\n' for i in range(72))
        cls.jetpack = '<div class="wp-block-jetpack-subscriptions__supports-newline is-style-split wp-block-jetpack-subscriptions"><div><div><a>Subscribe</a></div></div></div>'
        cls.chapters = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']
        cls.source = (cls.records + cls.jetpack + '<div data-fv-home-flagship>' +
                      ''.join(f'<section id="{x}"></section>' for x in cls.chapters) + '</div>' +
                      '<a href="https://finalvestige.com/focus/">Focus</a>'*2)
        d = inventory(cls.source)
        cls.baseline = dict(record_count=72, record_spans_sha256=d['record_spans_sha256'],
                            jetpack_block_sha256=d['jetpack_block_sha256'],
                            focus_href_min_count=2, required_chapter_ids=cls.chapters,
                            page_content_sha256=d['content_sha256'])

    def fails_for(self, html):
        r = evaluate(html, self.baseline)
        self.assertEqual(r['gate'], 'HOLD')
        self.assertTrue(r['errors'])
        self.assertFalse(r['release_approved'])
        return r

    def test_unchanged_public_content_passes_inventory_only(self):
        r = evaluate(self.source, self.baseline, True)
        self.assertEqual(r['gate'], 'PASS')
        self.assertFalse(r['release_approved'])

    def test_additive_integrated_feature_can_pass(self):
        self.assertEqual(evaluate(self.source+'<aside>New evidence renderer</aside>', self.baseline)['gate'],'PASS')

    def test_standalone_page_replacement_is_blocked(self):
        self.fails_for('<div data-fv-home-flagship><h1 id="fv-hf-title">Unintegrated candidate</h1></div>')

    def test_single_margin_record_deleted_is_blocked(self):
        self.fails_for(self.source.replace('<span class="fv-margin-strip__item" style="--i:71">Public record 71</span>', ''))

    def test_single_record_text_tampering_is_blocked(self):
        self.fails_for(self.source.replace('Public record 18','Altered record 18'))

    def test_record_reordering_is_blocked(self):
        self.fails_for(self.source.replace('--i:1','--i:XXXX').replace('--i:0','--i:1').replace('--i:XXXX','--i:0'))

    def test_jetpack_removal_is_blocked(self):
        r = self.fails_for(self.source.replace(self.jetpack, ''))
        self.assertIn('Native Jetpack subscriptions block missing',r['errors'])

    def test_jetpack_mutation_is_blocked(self):
        self.fails_for(self.source.replace('Subscribe','Broken form'))

    def test_focus_link_loss_is_blocked(self):
        self.fails_for(self.source.replace('https://finalvestige.com/focus/','https://example.invalid/focus/'))

    def test_chapter_missing_is_blocked(self):
        self.fails_for(self.source.replace('id="fv-hf-observer"','id="missing-observer"'))

    def test_full_snapshot_digest_change_requires_reapproval(self):
        self.assertEqual(evaluate(self.source+'safe',self.baseline,True)['gate'],'HOLD')
        self.assertEqual(evaluate(self.source+'safe',self.baseline,False)['gate'],'PASS')


if __name__=='__main__': unittest.main(verbosity=2)
