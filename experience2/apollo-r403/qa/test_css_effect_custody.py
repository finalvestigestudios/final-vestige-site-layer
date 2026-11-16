"""R403 actual headless Chromium regression of CSS applied to Apollo markup.
Set FV_APOLLO_OFFLINE_FIXTURE to a locally generated R384 fixture. No network.
"""
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from playwright.sync_api import sync_playwright
from css_effect_custody import probe,guard,inspect_receipt,audit_run,REQUIRED_CONTEXTS

FIXTURE=os.getenv('FV_APOLLO_OFFLINE_FIXTURE')
FIT=os.getenv('FV_APOLLO_MOBILE_CSS')

class CssEffectChromium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not FIXTURE or not Path(FIXTURE).is_file():
            raise unittest.SkipTest('source-generated Apollo fixture absent; no synthetic PASS')
        cls.html=Path(FIXTURE).read_text(encoding='utf-8')
        cls.fit=Path(FIT).read_text(encoding='utf-8') if FIT else ''
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(headless=True,
          executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop()
    def page(self,width=1440,nojs=False,reduced=False):
        ctx=self.browser.new_context(viewport={'width':width,'height':900},
          java_script_enabled=not nojs,reduced_motion='reduce' if reduced else 'no-preference',service_workers='block')
        ctx.route('**/*',lambda route:route.abort('blockedbyclient'))
        page=ctx.new_page();page.set_content(self.html,wait_until='domcontentloaded')
        if self.fit and not nojs:page.add_style_tag(content=self.fit)
        return ctx,page
    def test_real_gallery_css_effect_320_to_1920(self):
        for width in (320,390,768,1440,1920):
            with self.subTest(width=width):
                ctx,page=self.page(width)
                try:self.assertEqual(probe(page)['defects'],[])
                finally:ctx.close()
    def test_mobile_nojs_and_reduced_motion(self):
        for nojs,reduced in ((True,False),(False,True)):
            with self.subTest(nojs=nojs,reduced=reduced):
                ctx,page=self.page(390,nojs,reduced)
                try:
                    self.assertEqual(probe(page)['defects'],[])
                    self.assertEqual(page.locator('.fv-r384__card').count(),6)
                finally:ctx.close()
    def test_fetched_but_not_applied_css_rejected(self):
        ctx,page=self.page(1440)
        try:
            self.assertEqual(probe(page)['status'],'PASS')
            page.evaluate("document.querySelectorAll('style').forEach(e=>e.media='print')")
            self.assertIn('reviewed_background_not_applied',probe(page)['defects'])
            with self.assertRaisesRegex(AssertionError,'rendered_css_custody'):guard(page)
        finally:ctx.close()
    def test_stylesheet_override_rejected(self):
        ctx,page=self.page(1440)
        try:
            page.add_style_tag(content='.fv-r384{background:magenta!important}.fv-r384__grid{display:block!important}')
            result=probe(page)
            self.assertIn('reviewed_background_not_applied',result['defects'])
            self.assertIn('evidence_grid_css_missing',result['defects'])
        finally:ctx.close()
    def test_mobile_breakpoint_override_rejected(self):
        ctx,page=self.page(320)
        try:
            page.add_style_tag(content='@media(max-width:740px){.fv-r384__grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}')
            self.assertIn('mobile_evidence_not_stacked',probe(page)['defects'])
        finally:ctx.close()
    def test_root_text4x_stress(self):
        ctx,page=self.page(320)
        try:
            page.add_style_tag(content='html{font-size:64px!important}')
            result=probe(page)
            self.assertLessEqual(result['metrics']['overflow'],1)
            self.assertEqual(result['defects'],[])
        finally:ctx.close()
    def test_axe_not_implicitly_claimed_from_css(self):
        r={'blockers':[],'status':'PASS_STAGING_BROWSER_GATE_ONLY',
           'screens':[{'context':x,'rendered_css_custody':'PASS','rendered_css_overflow':0} for x in REQUIRED_CONTEXTS],
           'r402_trace_defects':[]}
        self.assertEqual(inspect_receipt(r,True),[])
        for key,val in [('status','PASS_LOCAL_FIXTURE_ONLY'),('r402_trace_defects',['network_denied'])]:
            q=dict(r,**{key:val});self.assertTrue(inspect_receipt(q,True))
        q=dict(r,screens=[{'context':x} for x in REQUIRED_CONTEXTS]);self.assertTrue(inspect_receipt(q,True))
        self.assertEqual(inspect_receipt(r,False),[])
    def test_inprocess_wrapper_restores_parent_even_on_error(self):
        base=SimpleNamespace(inspect=lambda page:{'cards':6})
        class FakeOverlay:pass
        class FakeNetwork:
            def audit_run(self,args,overlay,base):
                self.bound=base.inspect is not original
                raise RuntimeError(' deliberate network failure')
        original=base.inspect;net=FakeNetwork()
        with self.assertRaisesRegex(RuntimeError,'deliberate'):
            audit_run(SimpleNamespace(url=None),FakeOverlay(),net,base)
        self.assertTrue(net.bound);self.assertIs(base.inspect,original)

if __name__=='__main__':unittest.main()
