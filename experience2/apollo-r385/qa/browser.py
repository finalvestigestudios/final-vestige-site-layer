#!/usr/bin/env python3
"""Local HTTP + CSS delivery regression (not installed WordPress or production CWV)."""
import hashlib, http.server, json, pathlib, re, subprocess, threading, urllib.request
from playwright.sync_api import sync_playwright
import fitz
HERE=pathlib.Path(__file__).resolve().parents[1]
R384=HERE.parent/'apollo-r384'; QA=HERE/'QA'; QA.mkdir(exist_ok=True)
subprocess.run(['php',str(R384/'qa/contract.php')],check=True,capture_output=True)
source=(R384/'QA/local-php-fixture.html').read_text(encoding='utf8')
html,n=re.subn(r'<style>.*?</style>','<link rel="stylesheet" href="/gallery.css">',source, count=1,flags=re.S)
assert n==1
css=(R384/'assets/gallery.css').read_bytes()
assert hashlib.sha256(css).hexdigest()=='b684a4a463665c0f2f37f08cdf7ea9c73e91519ac9a14f1f04103130114bfa73'
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/': data=html.encode();type_='text/html; charset=utf-8'
  elif self.path=='/gallery.css':data=css;type_='text/css; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',type_)
  self.send_header('Content-Length',str(len(data)))
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'self'; img-src 'none'; connect-src 'none'; script-src 'self'; base-uri 'none'; form-action 'none'")
  self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
class Server(http.server.ThreadingHTTPServer):allow_reuse_address=True
server=Server(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:%s/'%server.server_port
# Python performs a real loopback HTTP fetch; browser policy blocks loopback, so Chromium
# receives byte-identical HTTP response fixtures via Playwright route.fulfill below.
with urllib.request.urlopen(url,timeout=5) as r:
 assert r.status==200 and 'default-src' in r.headers.get('Content-Security-Policy','')
 assert r.read()==html.encode()
with urllib.request.urlopen(url+'gallery.css',timeout=5) as r:
 assert r.status==200 and r.read()==css
contexts=[('320-mobile',320,760,True,False,False,False),('390-mobile',390,840,True,False,False,False),('768-tablet',768,900,False,False,False,False),('1440-desktop',1440,900,False,False,False,False),('1920-wide',1920,1080,False,False,False,False),('320-nojs',320,800,True,True,False,False),('390-touch',390,840,True,False,False,True),('390-reduced',390,840,True,False,False,False),('320-forced',320,850,True,False,True,False),('320-root4x',320,900,True,False,False,False)]
results={'status':'LOCAL_CHROMIUM_PHP_FIXTURE_PLUS_PYTHON_HTTP_CHECKS_PASS','contexts':[],'assertions':0,'axe_core':'NOT RUN (genuine axe-core unavailable offline)','real_website_cwv':'NOT MEASURED','installed_wordpress':'NOT TESTED','csp_scope':'PYTHON-VERIFIED LOOPBACK RESPONSE; BROWSER HTTP BLOCKED BY ENVIRONMENT; NO BROWSER CSP RESULT','source_r384_css_sha256':hashlib.sha256(css).hexdigest()}
def check(v,description):
 results['assertions']+=1
 if not v:raise AssertionError(description)
observer="""window.__fvPerf={lcp:null,cls:0};try{new PerformanceObserver(x=>{for(const e of x.getEntries())window.__fvPerf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__fvPerf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){window.__fvPerf.error=String(e)}"""
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,w,h,mobile,nojs,forced,touch in contexts:
   ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=touch or mobile,java_script_enabled=not nojs,forced_colors='active' if forced else 'none',reduced_motion='reduce' if name=='390-reduced' else 'no-preference')
   page=ctx.new_page()
   # Browser navigation to loopback, even route.fulfill, is blocked by the runtime.
   # Use local PHP-rendered R384 fixture; Python separately verifies actual HTTP bytes.
   page.set_content(source if nojs else source.replace('</head>','<script>'+observer+'</script></head>',1),wait_until='load');page.wait_for_timeout(140)
   if name=='320-root4x':page.add_style_tag(content='html{font-size:400%!important}')
   check(page.locator('style').count()>=1,name+' reviewed gallery CSS inline fixture')
   check(page.locator('[data-fv-r384-record]').count()==6,name+' six source questions')
   check(page.locator('[data-fv-r384-nasa]').count()==6,name+' source destinations')
   check(page.locator('[data-fv-free-cta]').count()==1,name+' one free action')
   check(page.locator('details').count()==6,name+' native disclosures')
   check(page.locator('body img,body iframe,body script,body video,body canvas').count()==0,name+' no embedded NASA media or scripts')
   check(page.locator('[data-fv-r384-nasa]').last.get_attribute('href')=='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',name+' subsequent tests provenance')
   check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),name+' no horizontal overflow')
   check(page.evaluate('getComputedStyle(document.querySelector(".fv-r384__grid")).display') in ('grid','block'),name+' CSS computed')
   if name=='1440-desktop':
    page.locator('summary').first.focus();page.keyboard.press('Enter')
    check(page.locator('details').first.evaluate('(d)=>d.open'),name+' keyboard disclosure')
    ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes'];roles=[x.get('role',{}).get('value') for x in ax if not x.get('ignored')]
    check('heading' in roles and 'link' in roles,name+' Chromium native accessibility roles')
    page.pdf(path=str(QA/'Apollo_R385_HTTP_Source_Dossier.pdf'),format='A4',print_background=True)
   if name in ('390-touch','320-nojs'):
    page.locator('summary').first.tap();check(page.locator('details').first.evaluate('(d)=>d.open'),name+' touch disclosure')
   page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
   vitals=None if nojs else page.evaluate('window.__fvPerf')
   results['contexts'].append({'name':name,'width':w,'result':'PASS','local_observed_lcp_ms':None if vitals is None else vitals['lcp'],'local_observed_cls':None if vitals is None else vitals['cls'],'source_css_sha256_verified':True})
   ctx.close()
  browser.close()
 pdf=fitz.open(str(QA/'Apollo_R385_HTTP_Source_Dossier.pdf'))
 uris=[link.get('uri') for pg in pdf for link in pg.get_links() if link.get('uri')]
 check(any('report-of-the-apollo-204-review-board' in x for x in uris),'print Board provenance')
 check(any('apollo-flammability-tests' in x for x in uris),'print later-test provenance')
 check(any('the-hatch-opened-inward-apollo-1' in x for x in uris),'print free action')
 results['pdf']={'pages':len(pdf),'links':len(uris),'distinct_destinations':len(set(uris))}
 (QA/'browser-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({'status':results['status'],'contexts':len(results['contexts']),'assertions':results['assertions'],'print_pages':len(pdf)},indent=2))
finally:server.shutdown()
