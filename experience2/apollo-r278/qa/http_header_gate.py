#!/usr/bin/env python3
"""Local HTTP status/MIME/CSP header contract; Chromium navigation blocked by administrator.
This does not establish that CSP was enforced in a real browser or WordPress.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
import subprocess, threading, json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CSS=(ROOT/'apollo-r273/assets/review-custody.css').read_bytes()
HTML=subprocess.check_output(['php',str(HERE/'render_http.php')])
NASA=b'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FREE=b'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
assert HTML.count(NASA)==4 and HTML.count(FREE)==2
assert b'evil.invalid' not in HTML and b'<script' not in HTML
CSP="default-src 'none'; style-src 'self'; script-src 'none'; img-src 'none'; connect-src 'none'; font-src 'self'; base-uri 'none'; object-src 'none'; form-action 'none'"
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path=='/':
            body,typ,code=HTML,'text/html; charset=utf-8',200
        elif self.path=='/assets/review-custody.css':
            body,typ,code=CSS,'text/css; charset=utf-8',200
        else:
            body,typ,code=b'','text/plain',404
        self.send_response(code)
        self.send_header('Content-Type',typ)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Content-Security-Policy',CSP)
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
url=f'http://127.0.0.1:{server.server_port}/'
try:
    with urlopen(url,timeout=5) as response:
        assert response.status==200
        assert response.headers['Content-Security-Policy']==CSP
        assert response.headers['X-Content-Type-Options']=='nosniff'
        assert response.headers['Content-Type'].startswith('text/html')
        assert b'<link rel="stylesheet" href="/assets/review-custody.css">' in response.read()
    with urlopen(url+'assets/review-custody.css',timeout=5) as response:
        assert response.status==200 and response.headers['Content-Type'].startswith('text/css')
        assert response.read()==CSS
finally:
    server.shutdown();server.server_close();thread.join(timeout=2)
out=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/fv-r278-qa');out.mkdir(parents=True,exist_ok=True)
receipt={'python_local_http':'PASS','served_csp_header':'PASS','actual_browser_http_csp':'BLOCKED_BY_ADMINISTRATOR','installed_wordpress':'NOT_TESTED'}
(out/'http_header_receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print('R278 local Python HTTP content/MIME/CSP-header PASS; Chromium HTTP blocked by administrator')
