"""Real Chromium negative controls for hidden-but-hash-preserved Page 6.

Uses only synthetic public content. The authenticated WordPress site is not
queried or mutated. Chromium must be installed; never silently skip browser QA.
"""
import unittest
from test_homepage_preservation import PreservationGateTests as Base
from verify_homepage_preservation import inventory, evaluate
from verify_homepage_computed_custody import verify

class ComputedStyleCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.setUpClass()
        html=Base.source.replace(Base.jetpack,
          '<div class="wp-block-jetpack-subscriptions"><a href="/dispatch/">Subscribe</a></div>')
        html=html.replace(Base.records,
          '<div class="fv-margin-strip">'+Base.records+'</div>')
        html='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+html+'</body></html>'
        found=inventory(html)
        cls.html=html
        cls.baseline={'record_count':72,'record_spans_sha256':found['record_spans_sha256'],
          'jetpack_block_sha256':found['jetpack_block_sha256'],
          'focus_href_min_count':2,'required_chapter_ids':Base.chapters,
          'page_content_sha256':found['content_sha256']}
    def assert_gate(self, css, wanted):
        changed=self.html.replace('</head>','<style>'+css+'</style></head>')
        # Establish precise bypass: original byte and DOM gates still pass.
        self.assertEqual(evaluate(changed,self.baseline)['gate'],'PASS')
        r=verify(changed,self.baseline,widths=(320,390,768,1440,1920))
        self.assertEqual(len(r['checks']),10)
        self.assertEqual(r['gate'],wanted, r['errors'])
        self.assertFalse(r['release_approved'])
        return r
    def test_unmodified_visible_public_dom(self):
        self.assert_gate('', 'PASS')
    def test_stylesheet_hides_original_margins(self):
        r=self.assert_gate('.fv-margin-strip{display:none!important}', 'HOLD')
        self.assertTrue(any('margin_strip_computed_hidden' in e for e in r['errors']))
    def test_stylesheet_hides_all_margin_records(self):
        self.assert_gate('.fv-margin-strip__item{opacity:0!important}', 'HOLD')
    def test_stylesheet_hides_native_jetpack(self):
        self.assert_gate('.wp-block-jetpack-subscriptions{visibility:hidden!important}', 'HOLD')
    def test_stylesheet_clips_seven_chapter_root(self):
        self.assert_gate('[data-fv-home-flagship]{clip-path:inset(100%)!important}', 'HOLD')
    def test_stylesheet_disables_focus_clicks(self):
        self.assert_gate('a[href="https://finalvestige.com/focus/"]{pointer-events:none!important}', 'HOLD')
    def test_stylesheet_removes_records_from_layout(self):
        self.assert_gate('.fv-margin-strip__item{display:none!important}', 'HOLD')
    def test_horizontal_overflow(self):
        self.assert_gate('body::after{content:"";position:absolute;left:2000px;width:200px;height:10px}', 'HOLD')

    def test_unloaded_external_stylesheet_fails_closed(self):
        html=self.html.replace('</head>','<link rel="stylesheet" href="/wp-content/theme.css"></head>')
        self.assertEqual(evaluate(html,self.baseline)['gate'],'PASS')
        r=verify(html,self.baseline,widths=(390,))
        self.assertEqual(r['gate'],'HOLD')
        self.assertEqual(r['checks'],[])
        self.assertIn('external_stylesheet_not_loaded',str(r['errors']))

    def test_unloaded_external_script_fails_closed(self):
        html=self.html.replace('</head>','<script src="/wp-content/theme.js"></script></head>')
        self.assertEqual(evaluate(html,self.baseline)['gate'],'PASS')
        r=verify(html,self.baseline,widths=(390,))
        self.assertEqual(r['gate'],'HOLD')
        self.assertIn('external_script_not_loaded',str(r['errors']))

    def test_css_import_fails_closed(self):
        html=self.html.replace('</head>','<style>@import url("/wp-content/theme.css");</style></head>')
        self.assertEqual(evaluate(html,self.baseline)['gate'],'PASS')
        r=verify(html,self.baseline,widths=(390,))
        self.assertEqual(r['gate'],'HOLD')
        self.assertIn('stylesheet_import_not_loaded',str(r['errors']))

if __name__=='__main__':unittest.main(verbosity=2)
