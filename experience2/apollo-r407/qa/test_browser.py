#!/usr/bin/env python3
"""Playwright on real Chromium, actual R407 JS/CSS and PHP namespacer; synthetic text fixture.
No installed WordPress, no trusted LCP/CLS, no axe-core. This never connects to any site.
"""
import json
import subprocess
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT/'QA'
HTML = subprocess.check_output(['php', str(ROOT/'qa/render_fixture.php')], text=True)
JS = (ROOT/'assets/research-desk-r407.js').read_text()
CSS = (ROOT/'assets/chronology.css').read_text()
BASE = '''*{box-sizing:border-box}body{background:#080a0b;color:#f1eee7;margin:0;font:16px/1.55 system-ui}
.fv-ex2-ledger{max-width:1360px;margin:auto;padding:clamp(20px,4vw,45px);background:#11130f;color:#f1eee7}
.fv-ex2-ledger__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.fv-ex2-ledger article{min-width:0;border:1px solid #7f745c;padding:18px;overflow-wrap:anywhere}
.fv-ex2-ledger a{color:#ffdb98}.fv-ex2-ledger [hidden]{display:none!important}
input,button{font:inherit;min-height:44px;max-width:100%}
@media(max-width:760px){.fv-ex2-ledger__grid{grid-template-columns:minmax(0,1fr)}}'''

def page_of(browser, width=390, js=True, touch=False, reduced=False, forced=False):
    ctx = browser.new_context(viewport={'width':width,'height':850},java_script_enabled=js,
        has_touch=touch, reduced_motion='reduce' if reduced else 'no-preference',
        forced_colors='active' if forced else 'none')
    pg = ctx.new_page()
    pg.set_content(HTML.replace('</head>','<style>'+BASE+CSS+'</style></head>'),wait_until='load')
    if js: pg.add_script_tag(content=JS)
    return ctx,pg

class BrowserQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        QA.mkdir(parents=True, exist_ok=True)
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        cls.report={'scope':'R407_SOURCE_JS_PHP_NAMESPACER_SYNTHETIC_TEXT_ONLY',
            'localhost_http':'NOT_USED_SET_CONTENT','actual_nasa_template':'NOT_AVAILABLE_LOCAL',
            'staging_wordpress':'NOT_INSTALLED','axe_core':'NOT_INSTALLED',
            'lcp_ms':None,'cls':None,'native_zoom_400':'NOT_TESTED', 'cases':{},'contexts':[]}
    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()
        (QA/'browser-results.json').write_text(json.dumps(cls.report,indent=2,sort_keys=True)+'\n')
    def log(self,k): self.report['cases'][k]='PASS'

    def test_bad_first_instance_does_not_disable_other_desks(self):
        ctx,p=page_of(self.browser)
        roots=p.locator('[data-fvx-ledger]')
        self.assertEqual(roots.nth(0).get_attribute('data-fvx-r407'),'failed-open')
        self.assertEqual(roots.nth(1).get_attribute('data-fvx-r407'),'ready')
        self.assertEqual(roots.nth(2).get_attribute('data-fvx-r407'),'ready')
        self.assertEqual(roots.nth(0).locator('[data-fvx-record]:visible').count(),6)
        self.assertEqual(roots.nth(0).locator('[data-fvx-tools]:visible').count(),0)
        self.log('bad_selector_isolation');ctx.close()

    def test_search_clear_and_deep_link(self):
        ctx,p=page_of(self.browser)
        root=p.locator('[data-fvx-ledger]').nth(1)
        input_=root.locator('input[data-fvx-search]'); input_.fill('hatch')
        self.assertEqual(root.locator('[data-fvx-record]:visible').count(),1)
        first=root.locator('[data-fvx-record]').first
        before=first.get_attribute('id')
        p.evaluate('(id)=>{location.hash=id}',before)
        p.wait_for_timeout(80)
        self.assertEqual(input_.input_value(),'')
        self.assertEqual(first.get_attribute('id'),before)
        self.assertTrue(first.is_visible())
        input_.fill('nothere')
        input_.press('Escape')
        self.assertEqual(root.locator('[data-fvx-record]:visible').count(),6)
        input_.fill('nothere')
        root.get_by_role('button',name='Clear evidence search').click()
        self.assertEqual(input_.input_value(),'')
        self.log('filter_fragment_keyboard_clear');ctx.close()

    def test_chronology_targets_and_no_fake_pin(self):
        ctx,p=page_of(self.browser)
        for nav in p.locator('nav.fv-r407__rail').all():
            hrefs=nav.locator('ol a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))')
            self.assertEqual(len(hrefs),4)
            for href in hrefs: self.assertEqual(p.locator('[id="'+href[1:]+'"]').count(),1)
        self.assertEqual(p.locator('div[data-lat],div[data-lng],iframe,canvas').count(),0)
        self.assertEqual(p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count(),3)
        self.log('source_linked_chronology_no_geo');ctx.close()

    def test_nojs_semantics_and_disclosure(self):
        ctx,p=page_of(self.browser,js=False)
        self.assertEqual(p.locator('[data-fvx-tools]:visible').count(),0)
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),18)
        self.assertEqual(p.locator('nav.fv-r407__rail ol li').count(),12)
        ids=p.locator('[id]').evaluate_all('(els)=>els.map(el=>el.id)')
        self.assertEqual(len(ids),len(set(ids)))
        p.locator('[data-fvx-record] details').first.locator('summary').click()
        self.assertTrue(p.locator('[data-fvx-record] details').first.evaluate('(el)=>el.open'))
        self.log('nojs_complete_meaning');ctx.close()

    def test_accessible_names_and_focus(self):
        ctx,p=page_of(self.browser)
        self.assertEqual(p.locator('nav[aria-labelledby]').count(),3)
        ready=p.locator('[data-fvx-ledger]').nth(1)
        self.assertEqual(ready.locator('label[for]').count(),1)
        ready.locator('input').focus(); self.assertEqual(ready.locator('input').evaluate('(el)=>el===document.activeElement'),True)
        self.assertEqual(ready.locator('[role="status"][aria-live="polite"]').count(),1)
        self.log('focus_and_status');ctx.close()

    def test_responsive_contexts(self):
        tests=[('320',320,True,False,False,False),('390-touch',390,True,True,False,False),
               ('768',768,True,False,False,False),('1440',1440,True,False,False,False),
               ('1920',1920,True,False,False,False),('320-nojs',320,False,False,False,False),
               ('390-reduced',390,True,True,True,False),('390-forced',390,True,False,False,True),
               ('320-root4x',320,True,False,False,False)]
        for name,width,js,touch,reduced,forced in tests:
            with self.subTest(context=name):
                ctx,p=page_of(self.browser,width,js,touch,reduced,forced)
                if 'root4x' in name: p.evaluate('document.documentElement.style.fontSize="64px"')
                overflow=p.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
                self.assertEqual(overflow,0,f'{name}: horizontal overflow {overflow}px')
                self.assertEqual(p.locator('nav.fv-r407__rail li').count(),12)
                self.assertTrue(p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').first.is_visible())
                p.screenshot(path=str(QA/(name+'.png')),full_page=True)
                self.report['contexts'].append({'name':name,'width':width,'js':js,'touch':touch,
                    'reduced_motion':reduced,'forced_colors':forced,'horizontal_overflow_px':overflow,
                    'lcp_ms':None,'cls':None,'metric_explanation':'set_content is not real navigation'})
                ctx.close()
        self.log('nine_responsive_contexts')

if __name__=='__main__': unittest.main(verbosity=2)
