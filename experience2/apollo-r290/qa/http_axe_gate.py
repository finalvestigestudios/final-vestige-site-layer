#!/usr/bin/env python3
"""R290 optional STRICT HTTP+axe gate. Never reports PASS for an unavailable browser/dependency.

Usage: python experience2/apollo-r290/qa/http_axe_gate.py /tmp/r290-http [path/to/axe.min.js]
This is staging fixture instrumentation, NEVER visitor-facing or public WP code.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib, json, subprocess, sys, threading
from playwright.sync_api import sync_playwright, Error as PlaywrightError

BASE = Path(__file__).resolve().parents[2] / 'apollo-r281'
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/apollo-r290-http')
OUT.mkdir(parents=True, exist_ok=True)
axe = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('node_modules/axe-core/axe.min.js')
css = (BASE / 'assets/apollo-source-experience.css').read_bytes()
php = '''define('ABSPATH','/local-qa/');
function add_action($a,$b,$c=10){} function add_shortcode($a,$b){}
function plugins_url($p,$f){return '/assets/apollo-source-experience.css';}
function wp_style_is($n,$status){return true;}
require 'apollo-source-experience.php'; echo fv_r281_render();'''
run = subprocess.run(['php', '-r', php], cwd=BASE, text=True, capture_output=True, timeout=20)
if run.returncode: raise RuntimeError(run.stderr)
markup = run.stdout
assert 'editorial-review-pending' in markup and 'https://www.nasa.gov/' in markup
# A real stylesheet resource, not an injected style element, on the same local origin.
html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Apollo 1 source QA fixture — NOT PUBLISHED</title>'
        '<link rel="stylesheet" href="/assets/apollo-source-experience.css"></head>'
        '<body style="margin:0;background:#121518;color:white">'+markup+'</body></html>').encode()
# Browser navigation is not permitted in all automation environments.
# The receipt deliberately labels that a blocker, never a failed site or a pass.
csp = "default-src 'none'; base-uri 'none'; object-src 'none'; img-src 'none'; style-src 'self'; script-src 'self'; connect-src 'none'; font-src 'none'; frame-src 'none'; form-action 'none'"
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        resources={'/':(html,'text/html; charset=utf-8'),
                   '/assets/apollo-source-experience.css':(css,'text/css; charset=utf-8')}
        if axe.is_file(): resources['/qa/axe.min.js']=(axe.read_bytes(),'text/javascript; charset=utf-8')
        if self.path not in resources:
            self.send_error(404); return
        data,typ=resources[self.path]
        self.send_response(200)
        self.send_header('Content-Type',typ)
        self.send_header('Content-Security-Policy',csp)
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0), Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'suite':'Apollo R290 real HTTP/CSP/axe local acceptance',
        'source_php_sha256':hashlib.sha256((BASE/'apollo-source-experience.php').read_bytes()).hexdigest(),
        'css_sha256':hashlib.sha256(css).hexdigest(),
        'origin':'local-only; not production', 'axe_core':'NOT_INSTALLED' if not axe.is_file() else 'AVAILABLE',
        'navigation':'NOT_TESTED','csp':'NOT_TESTED','lcp_ms':None,'cls':None,
        'field_cwv':'UNVERIFIED','installed_wp':'UNVERIFIED','verdict':'BLOCKED'}
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        ctx=browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
        # This observer measures the navigated QA fixture, not live visitors.
        ctx.add_init_script('''window.__apolloVitals={lcp:null,cls:0};
          new PerformanceObserver(list=>{for(const x of list.getEntries())window.__apolloVitals.lcp=x.startTime;}).observe({type:'largest-contentful-paint',buffered:true});
          new PerformanceObserver(list=>{for(const x of list.getEntries())if(!x.hadRecentInput)window.__apolloVitals.cls+=x.value;}).observe({type:'layout-shift',buffered:true});''')
        page=ctx.new_page(); outside=[]; console_errors=[]
        page.on('request',lambda r:outside.append(r.url) if not r.url.startswith('http://127.0.0.1:') else None)
        page.on('pageerror',lambda e:console_errors.append(str(e)))
        try:
            response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='load',timeout=12000)
            report['navigation']='PASS' if response and response.status==200 else 'FAIL'
            report['http_status']=response.status if response else None
            report['csp']='PASS' if page.locator('link[href="/assets/apollo-source-experience.css"]').count()==1 and not outside else 'FAIL'
            report['styles_applied']=page.locator('.fv-r281').evaluate('el=>getComputedStyle(el).backgroundColor')
            report['source_links']=page.locator('a[href^="https://www.nasa.gov/"]').count()
            report['no_overflow']=page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
            if axe.is_file():
                page.add_script_tag(url=f'http://127.0.0.1:{server.server_port}/qa/axe.min.js')
                axe_result=page.evaluate('''async () => {
                  const result=await axe.run(document.querySelector('.fv-r281'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                  return {version:axe.version,violations:result.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,targets:v.nodes.map(n=>n.target)})),incomplete:result.incomplete.map(x=>x.id),passes:result.passes.length}; }''')
                report['axe']=axe_result
                report['axe_core']='PASS' if not axe_result['violations'] else 'FAIL'
            vitals=page.evaluate('window.__apolloVitals')
            report['lcp_ms']=round(vitals['lcp'],2) if vitals and vitals['lcp'] is not None else None
            report['cls']=round(vitals['cls'],5) if vitals else None
            report['console_errors']=console_errors
            report['verdict']='PASS_LOCAL_FIXTURE_ONLY' if report['navigation']=='PASS' and report['csp']=='PASS' and report['axe_core']=='PASS' and report['no_overflow'] and not console_errors else 'BLOCKED'
        except PlaywrightError as e:
            msg=str(e)
            report['navigation']='BLOCKED_BY_ADMINISTRATOR' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in msg else 'FAILED_TO_NAVIGATE'
            report['navigation_error']=('net::ERR_BLOCKED_BY_ADMINISTRATOR' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in msg else msg[:180])
        browser.close()
finally:
    server.shutdown();server.server_close()
(OUT/'http-axe-receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('R290 HTTP/axe '+report['verdict']+'; browser='+report['navigation']+'; axe='+report['axe_core'])
# Strict release gate: BLOCKED and FAIL are nonzero.
sys.exit(0 if report['verdict']=='PASS_LOCAL_FIXTURE_ONLY' else 2)
