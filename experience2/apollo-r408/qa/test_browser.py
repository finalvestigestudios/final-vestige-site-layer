#!/usr/bin/env python3
"""Actual system Chromium on a synthetic, PHP-rendered, route-free fixture.
Navigation/LCP/CLS and axe-core are UNTESTED, never synthetic passes.
"""
import json, subprocess, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; QA=R/'QA'; QA.mkdir(exist_ok=True)
HTML=subprocess.check_output(['php',str(R/'qa/fixture.php')],text=True)
CSS=(R/'assets/evidence-atlas.css').read_text(); JS=(R/'assets/evidence-atlas.js').read_text()
BASE='''body{margin:0;background:#080a0b;color:#eee;font:16px/1.5 system-ui} .fv-r407{padding:20px;max-width:1320px;margin:auto} .fv-r407 article{border:1px solid #777;padding:16px;margin:10px 0} .fv-r407 a{color:#ffdb98}'''
REPORT={'test_methods':[],'contexts':[],'environment':'Local Chromium + PHP structural fixture; no installed WordPress, no NASA template, no axe core or trusted LCP/CLS'}

def build(browser,width=390,js=True,touch=False,reduced=False,forced=False):
    context=browser.new_context(viewport={'width':width,'height':840},java_script_enabled=js,has_touch=touch,device_scale_factor=1,
        reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
    page=context.new_page()
    page.set_content(HTML.replace('</head>','<style>'+BASE+CSS+'</style></head>'))
    if js:page.add_script_tag(content=JS)
    return context,page

class BrowserTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):
    cls.browser.close();cls.pw.stop();(QA/'browser-results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True)+'\n')
 def mark(self,x):REPORT['test_methods'].append(x)
 def test_all_questions_and_source_disclosures(self):
    ctx,p=build(self.browser);atlas=p.locator('[data-fv-r408-atlas]').first
    self.assertEqual(atlas.locator('li[data-fv-r408-card]').count(),6)
    self.assertEqual(atlas.locator('a[href^="https://www.nasa.gov/"]').count(),6)
    self.assertEqual(atlas.locator('a.fv-r408__jump').count(),6)
    for link in atlas.locator('a.fv-r408__jump').all():
        self.assertEqual(p.locator('[id="'+link.get_attribute('href')[1:]+'"]').count(),1)
    atlas.locator('summary').first.click()
    self.assertTrue(atlas.locator('details').first.evaluate('(x)=>x.open'))
    self.mark('six_questions_verified_source_links_native_disclosures');ctx.close()
 def test_real_filter_counts_and_aria(self):
    ctx,p=build(self.browser);a=p.locator('[data-fv-r408-atlas]').first
    self.assertFalse(a.locator('[data-fv-r408-filters]').is_hidden())
    a.locator('button[data-fv-r408-filter="conditions"]').click()
    self.assertEqual(a.locator('li[data-fv-r408-card]:visible').count(),3)
    self.assertEqual(a.locator('button[aria-pressed="true"]').get_attribute('data-fv-r408-filter'),'conditions')
    a.locator('button[data-fv-r408-filter="sequence"]').click()
    self.assertEqual(a.locator('li[data-fv-r408-card]:visible').count(),1)
    a.locator('button[data-fv-r408-filter="all"]').click()
    self.assertEqual(a.locator('li[data-fv-r408-card]:visible').count(),6)
    self.mark('filter_counts_pressed_status');ctx.close()
 def test_keyboard_and_instance_isolation(self):
    ctx,p=build(self.browser);a=p.locator('[data-fv-r408-atlas]')
    b=a.first.locator('button[data-fv-r408-filter="aftermath"]');b.focus();p.keyboard.press('Enter')
    self.assertEqual(a.first.locator('li[data-fv-r408-card]:visible').count(),1)
    self.assertEqual(a.nth(1).locator('li[data-fv-r408-card]:visible').count(),6)
    self.assertEqual(a.first.locator('button[aria-pressed="true"]').get_attribute('data-fv-r408-filter'),'aftermath')
    self.mark('keyboard_enter_multi_instance_isolation');ctx.close()
 def test_no_javascript_all_records(self):
    ctx,p=build(self.browser,js=False)
    for a in p.locator('[data-fv-r408-atlas]').all():
        self.assertEqual(a.locator('li[data-fv-r408-card]:visible').count(),6)
        self.assertTrue(a.locator('[data-fv-r408-filters]').is_hidden())
        a.locator('summary').last.click();self.assertTrue(a.locator('details').last.evaluate('(x)=>x.open'))
    self.mark('nojs_native_complete');ctx.close()
 def test_adversarial_filter_fails_open(self):
    ctx=self.browser.new_context(viewport={'width':390,'height':800});p=ctx.new_page()
    corrupted=HTML.replace('data-fv-r408-kind="aftermath"','data-fv-r408-kind="unreviewed"')
    p.set_content(corrupted.replace('</head>','<style>'+CSS+'</style></head>'));p.add_script_tag(content=JS)
    self.assertEqual(p.locator('[data-fv-r408-atlas]').first.get_attribute('data-fv-r408'),'failed-open')
    self.assertEqual(p.locator('[data-fv-r408-atlas]').first.locator('li[data-fv-r408-card]:visible').count(),6)
    self.assertTrue(p.locator('[data-fv-r408-atlas]').first.locator('[data-fv-r408-filters]').is_hidden())
    self.mark('corrupt_classification_fail_open');ctx.close()
 def test_source_boundary_and_no_commerce(self):
    ctx,p=build(self.browser)
    self.assertEqual(p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count(),2)
    self.assertEqual(p.locator('a[href*="payhip"],a[href*="checkout"],a[href*="affiliat"]').count(),0)
    self.assertEqual(p.locator('img,svg,iframe,canvas').count(),0)
    self.assertEqual(p.locator('[data-fv-r408-atlas] [data-lat],[data-fv-r408-atlas] [data-lng]').count(),0)
    self.mark('no_purchased_offer_media_geo_atlas');ctx.close()
 def test_responsive_screenshots(self):
    cases=[('320',320,True,False,False,False),('390-touch',390,True,True,False,False),('768',768,True,False,False,False),('1440',1440,True,False,False,False),('1920',1920,True,False,False,False),('320-nojs',320,False,False,False,False),('390-reduced',390,True,True,True,False),('390-forced',390,True,False,False,True),('320-root4x',320,True,False,False,False)]
    for n,w,js,touch,reduced,forced in cases:
        with self.subTest(n=n):
            ctx,p=build(self.browser,w,js,touch,reduced,forced)
            if n.endswith('root4x'): p.evaluate('document.documentElement.style.fontSize="64px"')
            overflow=p.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
            self.assertEqual(overflow,0,f'{n} overflow={overflow}')
            self.assertEqual(p.locator('[data-fv-r408-atlas] li[data-fv-r408-card]').count(),12)
            p.screenshot(path=str(QA/(n+'.png')),full_page=True)
            REPORT['contexts'].append({'name':n,'width':w,'js':js,'touch':touch,'reduced_motion':reduced,'forced_colors':forced,'overflow_px':overflow,
                'lcp_ms':None,'cls':None,'note':'No actual browser navigation: set_content fixture'})
            ctx.close()
    self.mark('nine_real_chromium_screenshots')
if __name__=='__main__':unittest.main(verbosity=2)
