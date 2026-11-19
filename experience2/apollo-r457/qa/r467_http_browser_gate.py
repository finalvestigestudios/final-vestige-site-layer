#!/usr/bin/env python3
"""R467: actual HTTP-navigation attempt with fail-closed LCP/CLS/axe acceptance.
If environment policy blocks navigation, exercise local markup in Chromium but
report navigated LCP/CLS as HOLD, not a fictitious pass. No live CMS changes.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import fitz
from pathlib import Path
import subprocess
import threading
from playwright.sync_api import sync_playwright, Error as PlaywrightError

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'QA' / 'r467'
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
PROBE = r"""
window.__fvCWV={lcp:null,cls:0,shifts:0};
try { new PerformanceObserver(list=>{for(const e of list.getEntries())
  window.__fvCWV.lcp=e.startTime
}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){window.__fvCWV.lcp_error=String(e)}
try { new PerformanceObserver(list=>{for(const e of list.getEntries())
  if(!e.hadRecentInput){window.__fvCWV.cls+=e.value;window.__fvCWV.shifts++}
}).observe({type:'layout-shift',buffered:true});}catch(e){window.__fvCWV.cls_error=String(e)}
"""
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()

@contextmanager
def site():
    server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:QuietHandler(*a,directory=str(ROOT),**kw))
    thr=threading.Thread(target=server.serve_forever,daemon=True)
    thr.start()
    try: yield f'http://127.0.0.1:{server.server_port}/preview.html'
    finally: server.shutdown();server.server_close();thr.join(timeout=5)

def render():
    php='require '+json.dumps(str(ROOT/'apollo_rights_gallery.php'))+'; echo fv457_render();'
    content=subprocess.check_output(['php','-r',php],text=True)
    assert content.count('data-fv457-plate=')==3
    assert content.count('data-fv457-card=')==6
    html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+content+'</body></html>'
    (ROOT/'preview.html').write_text(html,encoding='utf-8')

def run(axe_path:Path|None,axe_sha:str|None):
    render();QA.mkdir(parents=True,exist_ok=True)
    axe_ok=False
    if axe_path:
        assert axe_sha and len(axe_sha)==64, 'Axe supplied without explicit trusted digest'
        assert hashlib.sha256(axe_path.read_bytes()).hexdigest()==axe_sha, 'Axe hash mismatch'
        axe_ok=True
    result={'suite':'R467 locally navigated Chromium','widths':WIDTHS,
            'test_cases':0,'violations':[],'navigation_metrics':[],
            'axe':'HOLD_NOT_RUN: verified axe-core bundle unavailable',
            'hosted_wp':'HOLD_NOT_RUN','field_core_web_vitals':'HOLD_NOT_RUN',
            'local_http_navigation':'PENDING'}
    with site() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',
                                  args=['--no-sandbox','--disable-background-networking'])
        for width in WIDTHS:
            for enabled in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},
                         java_script_enabled=enabled,reduced_motion='reduce',device_scale_factor=1)
                page=ctx.new_page()
                if enabled: page.add_init_script(PROBE)
                bad=[]
                page.on('pageerror',lambda e:bad.append(str(e)))
                try:
                    response=page.goto(url,wait_until='load',timeout=6000)
                    assert response and response.status==200
                    navigated=True
                except PlaywrightError as exc:
                    if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc): raise
                    page.close();page=ctx.new_page()
                    page.on('pageerror',lambda e:bad.append(str(e)))
                    page.set_content((ROOT/'preview.html').read_text(encoding='utf-8'))
                    navigated=False
                    result['local_http_navigation']='HOLD_NOT_RUN: browser navigation blocked; set_content fallback only'
                page.wait_for_timeout(250)
                assert not bad,bad
                assert page.locator('[data-fv457-root]').count()==1
                assert page.locator('[data-fv457-card]').count()==6
                assert page.locator('[data-fv457-plate]').count()==3
                assert page.locator('.fv457__moment').count()==3
                assert page.locator('a.fv457__skip').count()==1
                assert page.locator('[data-fv457-card] a').count()==12
                assert page.locator('.fv457__cta a').count()==1
                assert page.locator('[data-fv457-choice]').count()==5
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                target=page.locator('ol.fv457__grid')
                tid=target.get_attribute('id')
                assert tid and tid==page.locator('a.fv457__skip').get_attribute('href')[1:]
                for b in page.locator('[data-fv457-choice]').all():
                    assert b.get_attribute('aria-controls')==tid
                for drawer in page.locator('.fv457 details').all():
                    assert '—' in drawer.locator('summary').inner_text()
                if enabled:
                    assert page.locator('[data-fv457-controls]').is_visible()
                    page.get_by_role('button',name='NASA ID confirmed (4)').click()
                    assert page.locator('[data-fv457-card]:visible').count()==4
                    assert '4 of 6' in page.locator('[data-fv457-status]').inner_text()
                    page.get_by_role('button',name='All six').focus()
                    page.keyboard.press('Enter')
                    assert page.locator('[data-fv457-card]:visible').count()==6
                    if navigated:
                        metrics=page.evaluate('window.__fvCWV')
                        assert metrics and metrics['cls']>=0
                        result['local_http_navigation']='EXECUTED LOCAL HTTP — not hosted WordPress'
                        result['navigation_metrics'].append({'width':width,'lcp_ms':metrics.get('lcp'),
                           'cls':metrics.get('cls'),'navigation_type':'local_HTTP','sample':'single_offline_run'})
                else:
                    assert not page.locator('[data-fv457-controls]').is_visible()
                    assert page.locator('[data-fv457-card]:visible').count()==6
                page.locator('a.fv457__skip').focus();page.keyboard.press('Enter')
                assert page.evaluate('location.hash')=='#'+tid
                assert page.evaluate('document.activeElement.id')==tid
                if width in (320,390,768,1440,1920) and enabled:
                    page.get_by_role('button',name='All six').click()
                    page.screenshot(path=str(QA/f'{width}-http.png'),full_page=True,animations='disabled')
                if width==390 and enabled:
                    raw=page.pdf(print_background=True,tagged=True)
                    doc=fitz.open(stream=raw,filetype='pdf')
                    metadata=doc.metadata or {}
                    metadata.update({'creationDate':'D:20261118000000Z','modDate':'D:20261118000000Z',
                                     'title':'FV Apollo source custody — staging QA'})
                    doc.set_metadata(metadata)
                    doc.save(str(QA/'390-http-print.pdf'),garbage=4,deflate=True,no_new_id=True)
                    doc.close()
                if axe_ok and width in (320,390,1440) and enabled:
                    page.add_script_tag(path=str(axe_path))
                    axe=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
                    result['violations'].extend([{'width':width,'id':v['id'],
                          'impact':v.get('impact'),'nodes':len(v['nodes'])} for v in axe['violations']])
                result['test_cases']+=1
                ctx.close()
        browser.close()
    if axe_ok:
        result['axe']='EXECUTED '+axe_path.name
        assert not result['violations'],result['violations']
    assert result['test_cases']==14
    (QA/'local_http_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--axe-js',type=Path)
    parser.add_argument('--axe-sha256')
    args=parser.parse_args()
    print(json.dumps(run(args.axe_js,args.axe_sha256),indent=2))
