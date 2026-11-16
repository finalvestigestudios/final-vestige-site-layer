#!/usr/bin/env python3
"""Local-network Chromium acceptance for R406, synthetic historical TEXT ONLY.
This tests the exact R406 JS/PHP namespacer, not installed WordPress nor NASA rights.
"""
import hashlib
import json
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'QA'
HTML = subprocess.check_output(['php', str(ROOT/'qa/render_fixture.php')], text=True)
JS = (ROOT/'assets/research-desk-r406.js').read_text()
CSS = """*{box-sizing:border-box} html{font:16px/1.5 system-ui} body{margin:0;background:#11151a;color:#f7eee0}
.fv-ex2-ledger{max-width:1180px;margin:auto;padding:24px} .fv-ex2-ledger__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.fv-ex2-ledger article{background:#1b2228;border:1px solid #bc9863;padding:18px;min-width:0;overflow-wrap:anywhere}
.fv-ex2-ledger a{color:#ffcb86}.fv-ex2-ledger input,.fv-ex2-ledger button{min-height:44px;max-width:100%;font:inherit}
.fv-ex2-ledger [hidden]{display:none!important} :focus-visible{outline:3px solid #ffcb86;outline-offset:3px}
@media(max-width:760px){.fv-ex2-ledger__grid{grid-template-columns:minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        data = {
            '/': (HTML, 'text/html; charset=utf-8'),
            '/no-script.html': (HTML.replace('<script defer src="/r406.js"></script>', ''), 'text/html; charset=utf-8'),
            '/r406.js': (JS, 'application/javascript; charset=utf-8'),
            '/fixture.css': (CSS, 'text/css; charset=utf-8'),
            '/access.css': ((ROOT.parent/'apollo-r404'/'assets/research-desk-resilient.css').read_text(), 'text/css; charset=utf-8'),
        }
        if path not in data:
            self.send_response(404); self.end_headers(); return
        payload, typ = data[path]
        self.send_response(200)
        self.send_header('Content-Type', typ)
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'")
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload.encode('utf-8'))
    def log_message(self, *_): pass

class BrowserQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        QA.mkdir(parents=True, exist_ok=True)
        cls.server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        probe = cls.browser.new_page()
        try:
            probe.goto(cls.origin + '/', timeout=2000)
            cls.http_allowed = True
        except Exception:
            cls.http_allowed = False  # Host policy blocks all localhost HTTP from Chromium.
        finally:
            probe.close()
        cls.report = {'scope':'EXACT_R406_SOURCE_PHP_NAMESPACER_SYNTHETIC_EVIDENCE',
                      'http_transport':'LOCAL_HTTP' if cls.http_allowed else 'SET_CONTENT_LOCAL_HTTP_BLOCKED_BY_ADMINISTRATOR',
                      'wordpress':'NOT_INSTALLED','actual_NASA_template':'NOT_TESTED','axe_core':'NOT_AVAILABLE',
                      'native_400_percent_zoom':'NOT_TESTED','contexts':[],'cases':{}}
    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.playwright.stop(); cls.server.shutdown(); cls.server.server_close()
        (QA/'browser-results.json').write_text(json.dumps(cls.report, sort_keys=True, indent=2)+'\n')

    def page(self, width=390, js=True, touch=False, motion='no-preference', path='/'):
        p = self.browser.new_page(viewport={'width':width,'height':820}, java_script_enabled=js,
                                  has_touch=touch, reduced_motion=motion, device_scale_factor=1)
        requests=[]
        p.on('request', lambda req: requests.append(req.url))
        p.add_init_script('''window.__perf={lcp:null,cls:0};
          try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__perf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
          try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value;}).observe({type:'layout-shift',buffered:true})}catch(e){}''')
        if self.http_allowed:
            p.goto(self.origin + path, wait_until='load')
        else:
            # Real browser, exact code, but no actual HTTP delivery/CSP acceptance.
            doc = HTML.replace('<script defer src="/r406.js"></script>', '')
            core = CSS
            access = (ROOT.parent/'apollo-r404'/'assets/research-desk-resilient.css').read_text()
            doc = doc.replace('<link rel="stylesheet" href="/fixture.css">', '<style>'+core+'</style>')
            doc = doc.replace('<link rel="stylesheet" href="/access.css">', '<style>'+access+'</style>')
            p.set_content(doc, wait_until='load')
            if js and path != '/no-script.html': p.add_script_tag(content=JS)
        p.wait_for_timeout(100)
        return p, requests

    def test_nojs_unique_server_ids(self):
        p,_=self.page(js=False)
        ids=p.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(p.locator('[data-fvx-record]:visible').count(),12)
        self.assertEqual(p.locator('[data-fvx-tools]:visible').count(),0)
        self.assertEqual(p.locator('a[href^="https://www.nasa.gov/"]').count(),12)
        self.assertEqual(p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count(),2)
        self.assertTrue(all(p.locator('label').evaluate_all('(xs)=>xs.map(x=>!!document.getElementById(x.htmlFor))')))
        p.close()

    def test_reproduces_r404_double_remap_bug(self):
        # R405 server IDs are stable before JS but R404 changes the second desk again.
        old=(ROOT.parent/'apollo-r404'/'assets/research-desk-resilient.js').read_text()
        p,_=self.page(path='/no-script.html')
        second=p.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]').first
        before=second.get_attribute('id')
        p.add_script_tag(content=old)
        after=second.get_attribute('id')
        self.assertNotEqual(before,after, 'regression must reproduce old identity instability')
        self.assertIn('-r404-2',after)
        p.close()

    def test_r406_id_stability_search_and_escape(self):
        p,_=self.page()
        second=p.locator('[data-fvx-ledger]').nth(1)
        target=second.locator('[data-fvx-record]').first
        id_before=target.get_attribute('id')
        self.assertIn('r406-i2-',id_before)
        self.assertEqual(second.locator('[data-fvx-tools]:visible').count(),1)
        input=second.locator('input[data-fvx-search]')
        input.fill('hatch')
        self.assertEqual(second.locator('[data-fvx-record]:visible').count(),1)
        self.assertEqual(p.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]:visible').count(),6)
        input.press('Escape')
        self.assertEqual(second.locator('[data-fvx-record]:visible').count(),6)
        self.assertEqual(target.get_attribute('id'),id_before)
        input.fill('no-match'); second.get_by_role('button',name='Clear evidence search').click()
        self.assertEqual(input.input_value(),'')
        self.assertEqual(second.locator('[data-fvx-record]:visible').count(),6)
        p.close()

    def test_fragment_target_recovery_and_native_disclosure(self):
        p,_=self.page()
        second=p.locator('[data-fvx-ledger]').nth(1)
        inp=second.locator('input[data-fvx-search]'); inp.fill('hatch')
        target=second.locator('[data-fvx-record]').first
        target_id=target.get_attribute('id')
        p.evaluate('(v)=>{location.hash=v}',target_id)
        p.wait_for_timeout(100)
        self.assertEqual(inp.input_value(),'')
        self.assertTrue(target.is_visible())
        self.assertEqual(target.get_attribute('id'),target_id)
        nested=second.locator('[data-fvx-record]').nth(2).locator('p[id]')
        nested_id=nested.get_attribute('id')
        self.assertFalse(second.locator('details').nth(2).evaluate('(el)=>el.open'))
        p.evaluate('(v)=>{location.hash=v}',nested_id)
        p.wait_for_timeout(100)
        self.assertTrue(second.locator('details').nth(2).evaluate('(el)=>el.open'))
        p.close()

    def test_fails_open_on_missing_card(self):
        p,_=self.page(path='/no-script.html')
        p.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]').first.evaluate('(el)=>el.remove()')
        p.add_script_tag(content=JS)
        first=p.locator('[data-fvx-ledger]').first
        self.assertEqual(first.get_attribute('data-fvx-r406'),'failed-open')
        self.assertEqual(first.locator('[data-fvx-record]:visible').count(),5)
        self.assertEqual(first.locator('[data-fvx-tools]:visible').count(),0)
        self.assertEqual(p.locator('[data-fvx-ledger]').nth(1).get_attribute('data-fvx-r406'),'ready')
        p.close()

    def test_fails_open_on_cross_component_id_collision(self):
        p,_=self.page(path='/no-script.html')
        p.evaluate('''()=>{let e=document.createElement('div');e.id=document.querySelector('[data-fvx-record]').id;document.body.append(e)}''')
        p.add_script_tag(content=JS)
        first=p.locator('[data-fvx-ledger]').first
        self.assertEqual(first.get_attribute('data-fvx-r406'),'failed-open')
        self.assertEqual(first.locator('[data-fvx-record]:visible').count(),6)
        p.close()

    def test_responsive_local_http_and_metrics(self):
        cases=[('320',320,True,False,'no-preference'),('390-touch',390,True,True,'no-preference'),
               ('768',768,True,False,'no-preference'),('1440',1440,True,False,'no-preference'),
               ('1920',1920,True,False,'no-preference'),('320-nojs',320,False,False,'no-preference'),
               ('390-reduced',390,True,True,'reduce'),('320-text4x',320,True,False,'no-preference')]
        for name,width,js,touch,motion in cases:
            with self.subTest(context=name):
                p,requests=self.page(width,js,touch,motion)
                if 'text4x' in name: p.evaluate('document.documentElement.style.fontSize="64px"')
                overflow=p.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
                self.assertEqual(overflow,0, f'{name} horizontal overflow {overflow}px')
                self.assertTrue(p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').first.is_visible())
                if self.http_allowed: self.assertTrue(all(url.startswith(self.origin) for url in requests),requests)
                self.assertEqual(p.locator('[data-fvx-record]').count(),12)
                p.screenshot(path=str(QA/f'{name}.png'), full_page=True)
                perf=p.evaluate('window.__perf') if (js and self.http_allowed) else {'lcp':None,'cls':None}
                self.report['contexts'].append({'name':name,'width':width,'js':js,'touch':touch,
                    'motion':motion,'overflow_px':overflow,'lcp_ms':perf.get('lcp'),
                    'cls_observed':perf.get('cls'),'resource_requests':len(requests)})
                p.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)
