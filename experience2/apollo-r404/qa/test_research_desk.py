#!/usr/bin/env python3
"""Real Chromium set_content fixture QA for isolated R404 Research Desk replacement.
No navigation or external calls; no WordPress, merchants, or analytics.
"""
import hashlib
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT/'assets/research-desk-resilient.js'
CSS = ROOT/'assets/research-desk-resilient.css'
OUT = ROOT/'QA'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'


def block(i):
    records = ''.join(f'''<article class="fv-ex2-ledger__card" id="fv-ex2-ledger-apollo1-record-0{n}" data-fvx-record data-fvx-search="NASA record {n} {'ignition' if n==5 else 'hatch' if n==4 else 'chronology'}">
      <h2>Research record {n}</h2><p>Fixture only; no historical claims supplied.</p><details><summary>Source limitations</summary><p>Open original source before drawing conclusions.</p></details><a href="{NASA}">NASA Review Board</a></article>''' for n in range(1,7))
    return f'''<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title">
      <h1 id="fv-ex2-ledger-apollo1-title">Research Desk · structural QA fixture</h1>
      <div data-fvx-tools hidden><label for="fv-ex2-ledger-apollo1-search">Search source records</label>
      <input id="fv-ex2-ledger-apollo1-search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid" placeholder="Search"></div>
      <p role="status" aria-live="polite" data-fvx-status></p>
      <div id="fv-ex2-ledger-apollo1-grid" class="fv-ex2-ledger__grid">{records}</div>
      <p data-fvx-empty hidden>No matching evidence records.</p>
      <a data-fv-free-cta href="{FREE}">Read the free investigation</a>
    </section>'''


def fixture(two=False, broken=False):
    content = block(0) + (block(1) if two else '')
    if broken:
        content = content.replace('data-fvx-search="NASA record 6 chronology"','')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>html{font:16px/1.5 system-ui}body{margin:0;background:#0e1217;color:#f4efe6}.fv-ex2-ledger{box-sizing:border-box;max-width:1150px;margin:auto;padding:24px;}
    .fv-ex2-ledger *{box-sizing:border-box}.fv-ex2-ledger__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
    .fv-ex2-ledger__card{min-width:0;padding:14px;background:#151b20;border:1px solid #5d523f}.fv-ex2-ledger a{color:#e9c986}
    .fv-ex2-ledger input{min-height:44px;max-width:100%}.fv-ex2-ledger [hidden]{display:none!important}
    [data-fvx-tools]{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:16px 0}
    @media(max-width:740px){.fv-ex2-ledger__grid{grid-template-columns:1fr}}
    </style><link rel="stylesheet" href="/addon.css"></head><body>''' + content + '''<script src="/addon.js" defer></script></body></html>'''


class BrowserContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUT.mkdir(exist_ok=True)
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        cls.report={'scope':'LOCAL_SET_CONTENT_FIXTURE','status':'PASS_LOCAL_FIXTURE_ONLY','released':False,'axe':'NOT_RUN',
                    'installed_wordpress':'NOT_TESTED','provenance':{'research_desk_markup_git_blob':'403d128c57b9bc82dac7c619651689070edef86c',
                    'original_js_git_blob':'32e757cc4dc8708397ff65ac21e89dd319781d78',
                    'r404_js_sha256':hashlib.sha256(JS.read_bytes()).hexdigest()},'screens':[]}

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
        (OUT/'browser-results.json').write_text(json.dumps(cls.report,indent=2,sort_keys=True)+'\n')

    def load(self, page, two=False, broken=False, js=True):
        html=fixture(two=two,broken=broken).replace('<link rel="stylesheet" href="/addon.css">','').replace('<script src="/addon.js" defer></script>','')
        html=html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
        page.set_content(html,wait_until='domcontentloaded')
        if js: page.add_script_tag(path=str(JS))

    def context(self,width=390,js=True,touch=False,reduced=False):
        ctx=self.browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=touch,
                                      reduced_motion='reduce' if reduced else 'no-preference',service_workers='block')
        self.addCleanup(ctx.close)
        page=ctx.new_page()
        page.set_default_timeout(4000)
        page.add_init_script('''() => { window.__layoutShift=0;new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__layoutShift+=e.value})).observe({type:'layout-shift',buffered:true}); }''')
        return page

    def test_search_reset_escape_and_cta(self):
        p=self.context();self.load(p)
        q=p.locator('input[data-fvx-search]');self.assertTrue(q.is_visible());q.fill('ignition')
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),1)
        self.assertEqual(p.locator('[data-fvx-status]').inner_text(),'1 of 6 evidence records')
        q.press('Escape');self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)
        q.fill('no-record-matches');self.assertTrue(p.locator('[data-fvx-empty]').is_visible())
        p.get_by_role('button',name='Clear evidence search').click()
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)
        self.assertEqual(p.locator('[data-fv-free-cta]').count(),1)
        self.assertEqual(p.locator('[data-fv-free-cta]').get_attribute('href'),FREE)

    def test_deep_link_reveals_hidden_card(self):
        p=self.context();self.load(p)
        p.locator('input[data-fvx-search]').fill('ignition')
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),1)
        p.evaluate("location.hash = '#fv-ex2-ledger-apollo1-record-04'; window.dispatchEvent(new HashChangeEvent('hashchange'))")
        p.wait_for_function("document.querySelector('input[data-fvx-search]').value === ''")
        self.assertTrue(p.locator('#fv-ex2-ledger-apollo1-record-04').is_visible())
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)

    def test_duplicate_shortcodes_keep_unique_ids_and_labels(self):
        p=self.context(width=768);self.load(p,two=True)
        ids=p.locator('[id]').evaluate_all('(els)=>els.map(el=>el.id)')
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(p.locator('[data-fvx-ledger]').count(),2)
        second=p.locator('[data-fvx-ledger]').nth(1)
        self.assertEqual(second.locator('label').get_attribute('for'),second.locator('input').get_attribute('id'))
        self.assertEqual(second.locator('input').get_attribute('aria-controls'),second.locator('.fv-ex2-ledger__grid').get_attribute('id'))
        second.locator('input').fill('ignition')
        self.assertEqual(second.locator('[data-fvx-record]:visible').count(),1)
        self.assertEqual(p.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]:visible').count(),6)

    def test_missing_search_index_fails_open(self):
        p=self.context();self.load(p,broken=True)
        self.assertEqual(p.locator('[data-fvx-ledger]').get_attribute('data-fvx-r404'),'failed-open')
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)
        self.assertFalse(p.locator('[data-fvx-tools]').is_visible())

    def test_no_js_preserves_six_records_sources_and_cta(self):
        p=self.context(width=320,js=False);self.load(p,js=False)
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)
        self.assertEqual(p.locator('details summary').count(),6)
        self.assertEqual(p.locator(f'a[href="{NASA}"]').count(),6)
        self.assertFalse(p.locator('[data-fvx-tools]').is_visible())
        self.assertEqual(p.locator('[data-fv-free-cta]').count(),1)

    def test_touch_and_keyboard_sources(self):
        p=self.context(width=390,touch=True);self.load(p)
        summary=p.locator('details summary').first;summary.tap()
        self.assertIsNotNone(p.locator('details').first.get_attribute('open'))
        summary.focus();p.keyboard.press('Enter')
        self.assertIsNone(p.locator('details').first.get_attribute('open'))
        p.locator('input[data-fvx-search]').fill('hatch')
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),1)

    def test_responsive_and_real_navigation_performance(self):
        for name,width,js,touch,reduced in [('320',320,True,False,False),('390-touch',390,True,True,False),
                            ('768',768,True,False,False),('1440',1440,True,False,False),('1920',1920,True,False,False),
                            ('320-nojs',320,False,False,False),('390-reduced',390,True,False,True),('320-root4x',320,True,False,False)]:
            p=self.context(width=width,js=js,touch=touch,reduced=reduced)
            if js:
                p.add_init_script("window.__lcp=null; new PerformanceObserver(l=>{const x=l.getEntries();if(x.length)window.__lcp=x[x.length-1].startTime}).observe({type:'largest-contentful-paint',buffered:true});")
            self.load(p,js=js)
            if name=='320-root4x':p.add_style_tag(content='html{font-size:64px!important}')
            p.wait_for_timeout(220)
            overflow=p.evaluate('Math.max(0,document.documentElement.scrollWidth-window.innerWidth)')
            self.assertLessEqual(overflow,1,name)
            self.assertEqual(p.locator('[data-fvx-record]:visible').count(),6)
            p.screenshot(path=str(OUT/(name+'.png')),full_page=True,animations='disabled')
            metrics={'lcp':None,'cls':None}  # set_content cannot supply valid navigation CWV
            self.report['screens'].append(dict(context=name,width=width,nojs=not js,touch=touch,reduced=reduced,
                                               overflow_px=overflow,**metrics))


if __name__=='__main__':unittest.main(verbosity=2)
