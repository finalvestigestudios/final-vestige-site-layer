"""Deterministic local HTTP contract for source-controlled R365 chronology.
The server is genuine PHP HTTP; browser navigation is not asserted.
"""
import hashlib, json, socket, subprocess, time, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'apollo-r366'
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
server=subprocess.Popen(['php','-S',f'127.0.0.1:{port}',str(HERE/'qa/http_fixture.php')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    def request(path):
        try:
            with urllib.request.urlopen(base+path,timeout=2) as resp:return resp.status,dict(resp.headers),resp.read()
        except urllib.error.HTTPError as error:return error.code,dict(error.headers),error.read()
    for i in range(40):
        try:
            if request('/probe')[0]==200:break
        except Exception: time.sleep(.08)
    else:raise AssertionError('Local PHP server did not start')
    code,headers,html=request('/')
    assert code==200 and headers['Content-Type'].startswith('text/html')
    policy=headers['Content-Security-Policy']
    for directive in ["default-src 'none'", "script-src 'none'", "style-src 'self'", "img-src 'none'", "connect-src 'none'", "frame-src 'none'", "form-action 'none'"]:
        assert directive in policy,directive
    assert headers['X-Content-Type-Options']=='nosniff'
    assert headers['Referrer-Policy']=='no-referrer'
    assert headers['X-Frame-Options']=='DENY'
    assert html.count(b'data-fv-source-drawer')==4
    assert html.count(b'data-fv-nasa-source')==4
    assert html.count(b'data-fv-free-cta')==1
    assert b'NASA does not endorse' in html
    assert b'commercial reuse' in html
    assert b'102 deliberate Command Module ignitions' in html
    csscode,cssheaders,css=request('/assets/chrono-rail.css')
    assert csscode==200 and cssheaders['Content-Type'].startswith('text/css')
    assert css==(ROOT/'apollo-r365/assets/chrono-rail.css').read_bytes()
    assert request('/missing')[0]==404
    assert b'CSP FAILED' in request('/probe')[2] # negative test exists; execution needs browser
    result={'test':'R366_PHP_HTTP_CONTRACT','passed':True,'server':'actual PHP built-in server on 127.0.0.1','html_http_status':code,'css_http_status':csscode,'missing_http_status':404,'source_count':4,'free_cta_count':1,'headers_checked':['Content-Security-Policy','X-Content-Type-Options','Referrer-Policy','X-Frame-Options'],'css_sha256':hashlib.sha256(css).hexdigest(),'html_sha256':hashlib.sha256(html).hexdigest(),'browser_direct_http':'BLOCKED_BY_ADMINISTRATOR','browser_enforced_http_csp':'NOT_VERIFIED','installed_wordpress':'NOT_VERIFIED','axe_core':'NOT_EXECUTED','hosted_ci':'NOT_EXECUTED'}
    (HERE/'QA').mkdir(exist_ok=True)
    (HERE/'QA/http-contract.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
finally:
    server.terminate()
    try:server.wait(timeout=3)
    except subprocess.TimeoutExpired:server.kill()
