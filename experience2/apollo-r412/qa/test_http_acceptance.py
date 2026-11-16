#!/usr/bin/env python3
"""Real HTTP navigated Chromium QA on immutable R411 source.

LCP/CLS here are measured browser-local **fixture samples**, NEVER real-user p75
or proof of live-site Core Web Vitals. axe-core requires a verified JS vendor
file: if unavailable the report honestly records BLOCKED rather than PASS.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import unittest
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from http_server import LocalFixture

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA';SHOTS=QA/'screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
PERF_OBSERVER = r'''(() => {
 window.__fvR412Performance = {lcpEntries:[], cls:0, shifts:[], unsupported:[]};
 try {new PerformanceObserver(list => {
  for(const e of list.getEntries()) window.__fvR412Performance.lcpEntries.push({startTime:e.startTime, size:e.size, element:e.element?.tagName || null});
 }).observe({type:'largest-contentful-paint', buffered:true});}
 catch(e){window.__fvR412Performance.unsupported.push('LCP:'+String(e));}
 try {new PerformanceObserver(list => {
  for(const e of list.getEntries()) if(!e.hadRecentInput) {window.__fvR412Performance.cls += e.value; window.__fvR412Performance.shifts.push({value:e.value,startTime:e.startTime});}
 }).observe({type:'layout-shift', buffered:true});}
 catch(e){window.__fvR412Performance.unsupported.push('CLS:'+String(e));}
})();'''
REPORT={
 'test_kind':'ACTUAL_LOOPBACK_HTTP_NAVIGATION_NOT_WORDPRESS',
 'read_only':True,'no_production_writes':True,'actual_origin':'127.0.0.1 loopback ephemeral port',
 'installed_wordpress':False,'real_production_cwv':False,
 'axe_core':{'status':'BLOCKED_NOT_INSTALLED_OR_VERIFIED'},
 'chromium_http_navigation':{'status':'NOT_YET_PROBED','error':None},
 'metrics':[],'screenshots':[],'css_http':{},'external_requests':[],
 'release_gate':'HOLD_PENDING_INSTALLED_WP_AND_VERIFIED_AXE_AND_FOUNDER_QD',
}

class R412Browser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.fixture=LocalFixture();cls.fixture.__enter__()
    cls.pw=sync_playwright().start()
    cls.browser=cls.pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    # Probe rather than falsely claiming a navigation pass when the runtime
    # administratively blocks Chromium localhost access. Python HTTP itself works.
    probe=cls.browser.new_page()
    try:
        response=probe.goto(cls.fixture.base_url+'/healthz',timeout=3500,wait_until='domcontentloaded')
        cls.navigation_supported=response is not None and response.status==200
        REPORT['chromium_http_navigation']={'status':'AVAILABLE' if cls.navigation_supported else 'BLOCKED','error':None}
    except Exception as e:
        cls.navigation_supported=False
        REPORT['chromium_http_navigation']={'status':'BLOCKED_BY_RUNTIME_POLICY','error':str(e).split('Call log:')[0].strip()}
    finally:probe.close()
 @classmethod
 def tearDownClass(cls):
    cls.browser.close();cls.pw.stop();cls.fixture.__exit__(None,None,None)
    (QA/'http_report.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
 def setUp(self):
    if self._testMethodName != 'test_09_explicit_optional_axe_gate' and not self.navigation_supported:
        self.skipTest('Chromium HTTP navigation BLOCKED_BY_RUNTIME_POLICY: no fake LCP/CLS/CSP pass')
 def page(self,width=390,height=850,perf=False,**kwargs):
    context=self.browser.new_context(viewport={'width':width,'height':height},**kwargs)
    page=context.new_page()
    if perf:page.add_init_script(script=PERF_OBSERVER)
    return context,page
 def navigate(self,page):
    response=page.goto(self.fixture.base_url+'/apollo-r411/',wait_until='networkidle',timeout=15000)
    self.assertIsNotNone(response);self.assertEqual(response.status,200)
    return response
 def test_01_real_http_asset_csp(self):
    c,p=self.page();captured=[]
    p.on('response',lambda x:captured.append((x.url,x.status)))
    response=self.navigate(p)
    self.assertEqual(response.headers['content-type'],'text/html; charset=utf-8')
    self.assertIn("style-src 'self'",response.headers['content-security-policy'])
    self.assertIn("script-src 'none'",response.headers['content-security-policy'])
    self.assertEqual(p.locator('link[rel="stylesheet"]').get_attribute('href'),'/assets/source-drawer.css')
    self.assertEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).backgroundColor'),'rgb(28, 29, 24)')
    self.assertEqual(len(captured),2,captured)
    self.assertTrue(any(url.endswith('/assets/source-drawer.css') and code==200 for url,code in captured))
    REPORT['css_http']={'document_status':200,'stylesheet_status':200,'stylesheet_applied':True,'csp_header':response.headers['content-security-policy']}
    c.close()
 def test_02_source_custody_no_external_embeds(self):
    c,p=self.page();self.navigate(p)
    self.assertEqual(p.locator('[data-fv-r411-sources]').count(),1)
    self.assertEqual(p.locator('details>summary').count(),6)
    self.assertEqual(p.locator('.fv-r411__sources a').count(),12)
    self.assertEqual(p.locator('script,img,iframe,video,audio,form').count(),0)
    urls=p.locator('.fv-r411__sources a').evaluate_all('(a)=>a.map(x=>new URL(x.href).hostname)')
    self.assertEqual(set(urls),{'www.nasa.gov'})
    self.assertEqual(p.get_by_role('link',name='Continue to the free Apollo 1 investigation').count(),1)
    self.assertEqual(p.locator('[id]').evaluate_all('(a)=>new Set(a.map(x=>x.id)).size'),p.locator('[id]').count())
    c.close()
 def test_03_keyboard_and_nojs_native(self):
    c,p=self.page(java_script_enabled=False);self.navigate(p)
    first=p.locator('summary').first;first.focus();p.keyboard.press('Enter')
    self.assertTrue(p.locator('details').first.evaluate('(el)=>el.open'))
    self.assertTrue(p.locator('.fv-r411__sources a').first.is_visible())
    p.keyboard.press('Space');self.assertFalse(p.locator('details').first.evaluate('(el)=>el.open'))
    p.screenshot(path=str(SHOTS/'390-nojs-http.png'),full_page=True);REPORT['screenshots'].append('390-nojs-http.png')
    c.close()
 def test_04_touch_and_reduced_motion(self):
    c,p=self.page(390,844,has_touch=True,is_mobile=True,reduced_motion='reduce');self.navigate(p)
    p.locator('summary').nth(5).tap();self.assertTrue(p.locator('details').nth(5).evaluate('(e)=>e.open'))
    self.assertTrue(p.get_by_text('102 deliberate Command Module tests',exact=False).is_visible())
    self.assertEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).animationName'),'none')
    p.screenshot(path=str(SHOTS/'390-touch-reduced-http.png'),full_page=True);REPORT['screenshots'].append('390-touch-reduced-http.png')
    c.close()
 def test_05_responsive_css_lcp_cls_in_real_http(self):
    for width in (320,360,390,768,1024,1440,1920):
     with self.subTest(width=width):
      c,p=self.page(width,900,perf=True)
      self.navigate(p)
      p.wait_for_timeout(500)
      entry=p.evaluate('''() => {
        const s=window.__fvR412Performance||{};
        const nav=performance.getEntriesByType('navigation')[0];
        return {lcp_ms:s.lcpEntries?.length ? s.lcpEntries.at(-1).startTime : null,
        lcp_count:s.lcpEntries?.length||0,cls:s.cls??null,shifts:s.shifts||[],
        unsupported:s.unsupported||[],ttfb_ms:nav?nav.responseStart-nav.requestStart:null,
        scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,
        grid:getComputedStyle(document.querySelector('.fv-r411__list')).gridTemplateColumns};}''')
      self.assertLessEqual(entry['scrollWidth'],width+1,entry)
      self.assertEqual(len(entry['grid'].split()),1 if width<=760 else 2)
      self.assertIsNotNone(entry['lcp_ms'],entry)
      self.assertIsNotNone(entry['cls'],entry)
      self.assertEqual(entry['unsupported'],[])
      self.assertGreaterEqual(entry['lcp_ms'],0)
      self.assertGreaterEqual(entry['cls'],0)
      entry['width']=width
      REPORT['metrics'].append(entry)
      p.screenshot(path=str(SHOTS/f'{width}-http.png'),full_page=True)
      REPORT['screenshots'].append(f'{width}-http.png')
      c.close()
 def test_06_enlarged_text_and_forced_colors(self):
    c,p=self.page(320,900,forced_colors='active');self.navigate(p)
    p.evaluate('document.documentElement.style.fontSize="64px"')
    self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'),321)
    self.assertEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).borderTopStyle'),'solid')
    p.screenshot(path=str(SHOTS/'320-4x-forced-http.png'),full_page=True)
    REPORT['screenshots'].append('320-4x-forced-http.png')
    c.close()
 def test_07_unknown_paths_404_and_no_internal_source(self):
    c,p=self.page()
    r=p.goto(self.fixture.base_url+'/staging-source-drawer.php');self.assertEqual(r.status,404)
    self.assertNotIn('function fv_r411_catalog',p.content())
    c.close()
 def test_08_guard_against_external_subresource_requests(self):
    c,p=self.page();external=[]
    p.on('request',lambda req: external.append(req.url) if not req.url.startswith(self.fixture.base_url) else None)
    self.navigate(p);p.locator('summary').first.click();p.wait_for_timeout(200)
    self.assertEqual(external,[])
    REPORT['external_requests']=external
    c.close()
 def test_09_explicit_optional_axe_gate(self):
    vendor=os.getenv('FV_AXE_CORE_PATH','')
    if not vendor:
     REPORT['axe_core']={'status':'BLOCKED_NOT_INSTALLED_OR_VERIFIED','violations':None,'incomplete':None}
     return
    if not self.navigation_supported:
     REPORT['axe_core']={'status':'BLOCKED_BROWSER_NAVIGATION','violations':None}
     return
    path=Path(vendor)
    if not path.is_file():
     self.fail('FV_AXE_CORE_PATH points to missing file; cannot assert axe pass')
    c,p=self.page();self.navigate(p)
    p.add_script_tag(content=path.read_text(encoding='utf-8'))
    result=p.evaluate('''async()=>{if(!window.axe)throw new Error('axe-core is unavailable');return await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});}''')
    REPORT['axe_core']={'status':'EXECUTED','version':p.evaluate('axe.version'),'violations':result['violations'],'incomplete_count':len(result['incomplete'])}
    self.assertEqual(result['violations'],[],result['violations'])
    c.close()

if __name__=='__main__': unittest.main(verbosity=2)
