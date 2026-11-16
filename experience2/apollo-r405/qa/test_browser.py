#!/usr/bin/env python3
"""True Chromium QA of PHP-generated *structural* fixture; no network/no WordPress install."""
from pathlib import Path
import hashlib
import json
import subprocess
import unittest
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
R404 = ROOT.parent / 'apollo-r404' / 'assets'
OUT = ROOT / 'QA'

class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUT.mkdir(parents=True, exist_ok=True)
        cls.base_html = subprocess.check_output(['php', str(ROOT / 'qa/render_fixture.php')], text=True)
        cls.css = (R404/'research-desk-resilient.css').read_text()
        cls.js = (R404/'research-desk-resilient.js').read_text()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        cls.results = {'scope':'PHP_RENDERED_SYNTHETIC_FIXTURE_R404_SCRIPTS', 'actual_pr158_html':'NOT_TESTED',
                       'axe_core':'NOT_AVAILABLE', 'wordpress':'NOT_INSTALLED', 'screens':[]}
    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()
        (OUT/'browser-results.json').write_text(json.dumps(cls.results,indent=2,sort_keys=True)+'\n')
    def load(self,width=390,js=True,touch=False,motion='no-preference'):
        p = self.browser.new_page(viewport={'width':width,'height':840},has_touch=touch,device_scale_factor=1, reduced_motion=motion)
        style = '<style>html{font:16px/1.5 system-ui}body{margin:0;background:#0e1116;color:#f7eee0}.fv-ex2-ledger{margin:auto;max-width:1180px;padding:24px;box-sizing:border-box}.fv-ex2-ledger *{box-sizing:border-box}.fv-ex2-ledger__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.fv-ex2-ledger article{min-width:0;border:1px solid #756241;padding:14px;background:#1c211f}.fv-ex2-ledger a{color:#f4be74}.fv-ex2-ledger input{min-height:44px;max-width:100%}.fv-ex2-ledger [hidden]{display:none!important}@media(max-width:760px){.fv-ex2-ledger__grid{grid-template-columns:1fr}}</style>'
        html=self.base_html.replace('</head>',style+'</head>')
        p.set_content(html,wait_until='domcontentloaded')
        p.add_style_tag(content=self.css)
        if js: p.add_script_tag(content=self.js)
        return p
    def test_nojs_server_namespaces(self):
        p=self.load(js=False)
        ids=p.locator('[id]').evaluate_all('(xs) => xs.map(x=>x.id)')
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(p.locator('[data-fvx-record]').count(),12)
        self.assertEqual(p.locator('[data-fvx-tools]:visible').count(),0)
        labels=p.locator('label').evaluate_all('(xs)=>xs.map(x=>({ref:x.htmlFor,found:!!document.getElementById(x.htmlFor)}))')
        self.assertTrue(all(x['found'] for x in labels), labels)
        refs=p.locator('input[data-fvx-search]').evaluate_all('(xs)=>xs.map(x=>({id:x.id,controls:!!document.getElementById(x.getAttribute("aria-controls"))}))')
        self.assertTrue(all(x['controls'] for x in refs), refs)
        p.close()
    def test_js_multi_instance_and_reset(self):
        p=self.load()
        self.assertEqual(p.locator('[data-fvx-tools]:visible').count(),2)
        ids=p.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
        self.assertEqual(len(ids),len(set(ids)))
        inp=p.locator('input[data-fvx-search]').nth(1)
        inp.fill('hatch')
        self.assertEqual(p.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]:visible').count(),1)
        self.assertEqual(p.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]:visible').count(),6)
        inp.press('Escape')
        self.assertEqual(p.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]:visible').count(),6)
        p.close()
    def test_hash_recovery_second_instance(self):
        p=self.load()
        inp=p.locator('input[data-fvx-search]').nth(1)
        inp.fill('hatch')
        # R404 JS remaps second desk IDs again; use its actual target ID.
        target=p.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]').first
        identity=target.get_attribute('id')
        p.evaluate('v=>{location.hash="";location.hash=""+v;window.dispatchEvent(new Event("hashchange"))}',identity)
        self.assertEqual(inp.input_value(),'')
        self.assertTrue(target.is_visible())
        p.close()
    def test_responsive_screens(self):
        cases=[(320,False,True,'no-preference'),(390,True,True,'no-preference'),(768,False,True,'no-preference'),(1440,False,True,'no-preference'),(1920,False,True,'no-preference'),(320,False,False,'no-preference'),(390,True,True,'reduce')]
        for width,touch,js,motion in cases:
            with self.subTest(width=width,touch=touch,js=js,motion=motion):
                p=self.load(width=width,touch=touch,js=js,motion=motion)
                overflow=p.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
                self.assertEqual(overflow,0)
                name=f'{width}-{("touch" if touch else "desktop")}-{("js" if js else "nojs")}-{motion}.png'
                p.screenshot(path=str(OUT/name),full_page=True)
                self.results['screens'].append({'name':name,'width':width,'touch':touch,'js':js,'reduced_motion':motion,'overflow_px':overflow})
                p.close()
    def test_js_error_fail_open(self):
        p=self.load()
        inp=p.locator('input[data-fvx-search]').first
        p.evaluate('() => document.querySelector("[data-fvx-record]").removeAttribute("data-fvx-search")')
        inp.fill('hatch')
        self.assertEqual(p.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]:visible').count(),6)
        self.assertEqual(p.locator('[data-fvx-ledger]').first.locator('[data-fvx-tools]:visible').count(),0)
        p.close()

if __name__=='__main__': unittest.main(verbosity=2)
