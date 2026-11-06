"""Native Chromium adversarial test of audit sequencing, NOT axe/WCAG qualification.
The intentionally synthetic axe object is solely a test double; it must never
be used as the --axe resource for a release or staging acceptance test.
"""
import unittest
from playwright.sync_api import sync_playwright
from fv_ex2_guest_browser_admission_20261105 import inspect, run_axe_all_widths, WIDTHS

FAKE_AXE = """window.axe = {run: async () => ({violations:
  window.innerWidth===390 ? [{id:'synthetic-mobile-only',impact:'critical',nodes:[{},{}]}] : []
})};"""
GOOD_FAKE_AXE = "window.axe={run:async()=>({violations:[]})};"

class MultiviewAxeGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver=sync_playwright().start()
        cls.browser=cls.driver.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.driver.stop()
    def browser_page(self, html='<html><body><h1>Deliberately synthetic fixture</h1></body></html>'):
        p=self.browser.new_page(viewport={'width':1920,'height':844})
        p.set_content(html)
        return p
    def test_desktop_only_historical_false_negative_reproduced(self):
        p=self.browser_page()
        try:
            p.add_script_tag(content=FAKE_AXE)
            p.set_viewport_size({'width':1920,'height':844})
            self.assertEqual(p.evaluate('async()=> (await axe.run()).violations.length'),0)
            p.set_viewport_size({'width':390,'height':844})
            self.assertEqual(p.evaluate('async()=> (await axe.run()).violations.length'),1)
        finally:p.close()
    def test_all_six_viewports_audited_and_mobile_failure_rejected(self):
        p=self.browser_page()
        try:
            p.add_script_tag(content=FAKE_AXE)
            r=run_axe_all_widths(p)
            self.assertEqual(list(r['widths']),list(map(str,WIDTHS)))
            self.assertEqual(r['status'],'VIOLATIONS')
            self.assertFalse(r['all_widths_pass'])
            self.assertEqual(r['widths']['390']['violations'][0]['id'],'synthetic-mobile-only')
            self.assertEqual(r['widths']['1920']['status'],'NO_AUTOMATED_VIOLATIONS')
        finally:p.close()
    def test_all_six_clean_test_double_does_not_claim_wcag(self):
        p=self.browser_page()
        try:
            p.add_script_tag(content=GOOD_FAKE_AXE)
            r=run_axe_all_widths(p)
            self.assertTrue(r['all_widths_pass'])
            self.assertEqual(len(r['widths']),6)
            self.assertIn('not full WCAG',r['note'])
        finally:p.close()
    def test_missing_axe_fail_closed_on_every_width(self):
        p=self.browser_page()
        try:
            r=run_axe_all_widths(p)
            self.assertFalse(r['all_widths_pass'])
            self.assertEqual(r['status'],'BLOCKED_AXE_RUNTIME')
            self.assertTrue(all('BLOCKED' in x['status'] for x in r['widths'].values()))
        finally:p.close()
    def test_reduced_motion_hidden_margins_are_detected(self):
        p=self.browser_page('<style>@media(prefers-reduced-motion:reduce){.fv-margin-strip__item:not(:first-child){display:none}}</style><div class="fv-margin-strip">'+''.join('<span class="fv-margin-strip__item">archive</span>' for _ in range(72))+'</div>')
        try:
            p.emulate_media(reduced_motion='reduce')
            before=inspect(p)
            self.assertEqual(before['margins'],72)
            self.assertEqual(before['marginsInLayout'],1)
            p.add_style_tag(content='@media(prefers-reduced-motion:reduce){.fv-margin-strip__item:not(:first-child){display:inline !important}}')
            after=inspect(p)
            self.assertEqual(after['marginsInLayout'],72)
        finally:p.close()

if __name__=='__main__':unittest.main(verbosity=2)
