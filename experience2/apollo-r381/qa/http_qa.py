#!/usr/bin/env python3
"""R381 genuine loopback HTTP acceptance gate. A failed navigation is NOT a fixture pass."""
import hashlib,json,re,subprocess
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experience2/apollo-r381';OUT=BASE/'QA/http_gate.json'
CSS=BASE/'assets/evidence-to-investigation.css'
STUB=BASE/'qa/wp_stub.php'
CSP="default-src 'none'; style-src 'self'; script-src 'none'; img-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'"
class Server(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/':
   html=subprocess.run(['php',str(STUB),'--html'],check=True,capture_output=True,text=True).stdout
   data=html.replace('</head>','<link rel="stylesheet" href="/r381.css"></head>').encode();kind='text/html'
  elif self.path=='/r381.css':data=CSS.read_bytes();kind='text/css'
  elif self.path=='/csp':data=b'<script>window.__unsafe=true</script>';kind='text/html'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Security-Policy',CSP)
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(data)))
  self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass

def main():
 OUT.parent.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),Server)
 thread=Thread(target=server.serve_forever,daemon=True);thread.start()
 base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   try:
    page=browser.new_page();responses=[];page.on('response',lambda r:responses.append((r.url,r.status,r.headers)))
    main=page.goto(base+'/',wait_until='load',timeout=10000)
    assert main.status==200 and main.headers.get('content-security-policy')==CSP
    assert page.locator('[data-fv-r381-item]').count()==3
    assert any(u==base+'/r381.css' and s==200 and 'text/css' in h.get('content-type','') for u,s,h in responses)
    assert page.locator('[data-fv-r381]').evaluate("e=>getComputedStyle(e).getPropertyValue('--fv381-bg').trim()")=='#121617'
    assert hashlib.sha256(page.request.get(base+'/r381.css').body()).digest()==hashlib.sha256(CSS.read_bytes()).digest()
    page.goto(base+'/csp',wait_until='load')
    assert page.evaluate('typeof window.__unsafe === "undefined"'), 'inline script escaped CSP'
    result={'status':'LOCAL_REAL_HTTP_CSP_PASS_NOT_WORDPRESS_STAGING','checked':['HTTP navigation','response CSP','CSS network response','exact CSS bytes','browser-enforced inline-script block']}
   finally:browser.close()
 except Exception as exc:
  reason=re.sub(r'127\.0\.0\.1:[0-9]+','127.0.0.1:<ephemeral-port>',str(exc).splitlines()[0])[:350]
  result={'status':'BLOCKED_REAL_HTTP_ACCEPTANCE_NOT_STAGING','failure':type(exc).__name__,'reason':reason,'browser_fixture_is_not_a_substitute':True}
 finally:
  server.shutdown();server.server_close();thread.join(timeout=2)
 OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(result['status'],result.get('reason',''))
 return 0 if result['status'].startswith('LOCAL_REAL_HTTP_') else 2
if __name__=='__main__':raise SystemExit(main())
