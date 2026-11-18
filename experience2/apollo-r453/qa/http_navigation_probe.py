#!/usr/bin/env python3
"""Local HTTP navigation acceptance PROBE against real R448 PHP renderer.
Never substitutes for installed WordPress staging or reviewed axe-core.
"""
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
WIDTHS=(320,360,390,768,1024,1440,1920)
PERF="""(()=>{window.fvLab={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.fvLab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.fvLab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}})();"""

def main():
    OUT.mkdir(exist_ok=True)
    fixture=ROOT.parent/'apollo-r448/qa/fixture.php'
    try:html=subprocess.run(['php',str(fixture)],check=True,capture_output=True,text=True).stdout.encode()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status':'HOLD_NOT_RUN','reason':f'PHP R448 fixture unavailable: {str(exc)[:200]}'}))
        return 2
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path!='/':self.send_error(404);return
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('X-Robots-Tag','noindex,nofollow')
            self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(html)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    origin=f'http://127.0.0.1:{server.server_port}'
    report={'scope':'actual local HTTP navigation of PHP-rendered R448; NOT WordPress staging',
        'wordPress_staging':'NOT_RUN','axe_core':'NOT_RUN','field_CWV':'NOT_RUN',
        'realized_net_revenue_per_1000_sessions':None,'release':'HARD_HOLD',
        'cases':[],'status':'HOLD_NOT_RUN'}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            try:
                page=browser.new_page()
                try:page.goto(origin,wait_until='load',timeout=6000)
                except Exception as exc:
                    report['navigation_blocker']='ERR_BLOCKED_BY_ADMINISTRATOR: local browser navigation refused' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc) else str(exc).splitlines()[0][:160]
                    report['note']='Browser navigation is blocked by the executor; local LCP/CLS and real staging acceptance NOT measured.'
                    return 0
                finally:page.close()
                report['status']='PASS_LOCAL_HTTP_ONLY'
                for w in WIDTHS:
                    for js in (True,False):
                        ctx=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion='reduce')
                        p=ctx.new_page();p.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).netloc==urlsplit(origin).netloc else route.abort())
                        if js:p.add_init_script(PERF)
                        try:
                            r=p.goto(origin,wait_until='load',timeout=15000)
                            p.wait_for_timeout(400)
                            assert r and r.status==200
                            assert p.locator('[data-fv-r448-card]').count()==4
                            assert p.locator('a[href*="the-hatch-opened-inward"]').count()==1
                            assert p.locator('img,iframe,form,[data-lat],[data-lon],a[href*="payhip"]').count()==0
                            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                            if js:
                                p.get_by_role('button',name='1967 inquiry').click()
                                assert p.locator('[data-fv-r448-card]:visible').count()==1
                                p.get_by_role('button',name='All evidence').click()
                            else:assert p.locator('[data-fv-r448-card]:visible').count()==4
                            lab=p.evaluate('window.fvLab') if js else None
                            (OUT/'screenshots').mkdir(exist_ok=True)
                            p.screenshot(path=str(OUT/'screenshots'/f'{w}-{int(js)}.png'),full_page=True)
                            report['cases'].append({'width':w,'javascript':js,'lab':lab,'status':'PASS'})
                        except Exception as exc:
                            report['status']='FAIL_LOCAL_HTTP'
                            report['cases'].append({'width':w,'javascript':js,'status':'FAIL','error':str(exc)[:250]})
                        finally:ctx.close()
            finally:browser.close()
    finally:
        server.shutdown();server.server_close()
        (OUT/'HTTP_NAVIGATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'status':report['status'],'cases':len(report['cases']),'blocker':report.get('navigation_blocker')}))
    return 0 if report['status']!='FAIL_LOCAL_HTTP' else 1
if __name__=='__main__':raise SystemExit(main())
