#!/usr/bin/env python3
"""R333 executable: local HTTP cache/CSP receipts; offline Chromium META-CSP.
NOT browser HTTP-header acceptance, axe-core, WordPress, or production CWV.
"""
import hashlib, json, re, subprocess, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
JS=ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
HARNESS=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r333/QA'
PINS={PHP:'f59a083de8d0774ed7210bfe4e18726feea73f76',CSS:'577a5d33518baec6e1beff1517779264d342bc50',JS:'f85617e5f12ba747908ac507261f69c377369de7',HARNESS:'f8987327fd6b49afcf8996c695100e3e7471c831'}
GOOD='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_abc123'
BAD=GOOD.replace('apollo1_yt_','apollo1_tt_')
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MODES=('allowed','script-blocked','all-blocked','no-js')
WIDTHS=(320,390,768,1440,1920)

def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def policy(mode):
    s="'none'" if mode in ('script-blocked','all-blocked') else "'unsafe-inline'"
    c="'none'" if mode=='all-blocked' else "'unsafe-inline'"
    return f"default-src 'none'; script-src {s}; style-src {c}; img-src 'none'; connect-src 'none'; base-uri 'none'; object-src 'none'"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for path,sha in PINS.items():assert blob(path)==sha,(path,blob(path))
    subprocess.run(['php','-l',str(PHP)],capture_output=True,check=True)
    subprocess.run(['node','--check',str(JS)],capture_output=True,check=True)
    html=subprocess.check_output(['php',str(HARNESS),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
    html=re.sub(r'<link rel="stylesheet" href="/assets/apollo-source-experience.css[^\"]*">','',html)
    css=CSS.read_text();js=JS.read_text()
    class Server(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            mode=urlsplit(self.path).path.strip('/')
            if mode not in MODES:self.send_error(404);return
            body=html.encode()
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Security-Policy',policy(mode))
            self.send_header('Content-Length',str(len(body)))
            self.end_headers();self.wfile.write(body)
    srv=ThreadingHTTPServer(('127.0.0.1',0),Server)
    thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(srv.server_address[1])
    screenshots=[];cases=[];pdf_info={}
    try:
        bodies=[urlopen(url+'/allowed/?'+q).read() for q in ('',GOOD,BAD)]
        assert bodies[0]==bodies[1]==bodies[2]
        for mode in MODES:
            with urlopen(url+'/'+mode+'/') as r:
                assert r.headers['Content-Security-Policy']==policy(mode)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            try:
                for mode in MODES:
                    for width in WIDTHS:
                        for font in ((16,64) if width==320 else (16,)):
                            page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=mode!='no-js',reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==390 else 'none')
                            page.goto('about:blank?'+GOOD)
                            meta='<meta http-equiv="Content-Security-Policy" content="'+policy(mode)+'">'
                            fixture=html.replace('</head>',meta+'<style>'+css+'</style></head>').replace('</body>','<script>'+js+'</script></body>')
                            req=[];page.on('request',lambda r:req.append(r.url))
                            page.set_content(fixture,wait_until='load')
                            page.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
                            evidence=page.locator('section.fv-r281').evaluate('''root=>{
                              let tags=[...root.querySelectorAll('a,summary')];
                              return {controls:tags.map(x=>{let r=x.getBoundingClientRect();return [x.textContent.trim(),r.left,r.right,r.width,r.height]}),
                              docs:[...root.querySelectorAll('.fv-r281__source-list>li')].map(x=>x.dataset.fvEvidenceRole),
                              media:[...root.querySelectorAll('[data-fv-media-record]')].map(x=>[x.dataset.fvEvidenceRole,x.dataset.fvImageRights,x.dataset.fvClaimProof]),
                              links:[...root.querySelectorAll('a[data-fv-link-purpose]')].map(x=>x.href),
                              geo:root.querySelectorAll('[data-lat],[data-lng],[data-map-pin],[data-geo-edge]').length,
                              overflow:document.documentElement.scrollWidth-innerWidth};}''')
                            assert len(evidence['controls'])==46 and all(t[0] for t in evidence['controls'])
                            assert evidence['docs']==['documented-textual-claim']*3
                            assert evidence['media']==[['contextual-media-only','not-cleared-for-reuse','no']]*4
                            assert len(evidence['links'])==17 and all(x.startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for x in evidence['links'])
                            assert evidence['geo']==0 and not req
                            if mode!='all-blocked':
                                assert evidence['overflow']<=1
                                assert all(t[3]>=12 and t[4]>=24 and t[1]>=-1 and t[2]<=width+1 for t in evidence['controls'])
                            link=page.locator('a[data-fv-cta="apollo-read-free-investigation"]')
                            link.click(button='right')
                            assert link.get_attribute('href')==(FREE+'?'+GOOD if mode=='allowed' else FREE)
                            if mode=='allowed' and width==390:
                                pdf=page.pdf(format='A4',print_background=True)
                                (OUT/'r333-390-source-dossier.pdf').write_bytes(pdf)
                                doc=fitz.open(stream=pdf,filetype='pdf')
                                uris=[x['uri'] for p in doc for x in p.get_links() if x.get('uri')]
                                assert FREE in uris and not any('utm_' in u for u in uris)
                                pdf_info={'pages':len(doc),'links':len(uris),'utmLeaks':0}
                                doc.close();assert link.get_attribute('href')==FREE
                            if (mode,width,font) in (('allowed',390,16),('script-blocked',390,16),('all-blocked',320,16),('allowed',1440,16)):
                                name=f'r333-{mode}-{width}-{font}.png';page.screenshot(path=str(OUT/name),full_page=True);screenshots.append(name)
                            cases.append({'mode':mode,'width':width,'rootFont':font,'controls':46})
                            page.close()
                bad=browser.new_page();bad.goto('about:blank?'+BAD)
                bad.set_content(html.replace('</head>','<style>'+css+'</style></head>').replace('</body>','<script>'+js+'</script></body>'))
                bad.locator('a[data-fv-cta]').click(button='right')
                assert bad.locator('a[data-fv-cta]').get_attribute('href')==FREE;bad.close()
            finally:browser.close()
        result={'sprint':'R333','cases':cases,'httpHeadersReadByPython':4,'byteIdenticalCachedBodies':3,'browserCSP':'META ONLY — HTTP navigation administrator-blocked','pdf':pdf_info,'screenshots':screenshots,'sourceGitBlobs':{str(k.relative_to(ROOT)):v for k,v in PINS.items()},'axe':'NOT RUN','installedWordPress':False,'productionLCP':None,'productionCLS':None,'paidOrders':None,'release':'HARD HOLD'}
        (OUT/'r333-commit-gate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('PASS R333:',len(cases),'Chromium meta-CSP contexts, four actual HTTP headers (Python only), 3 identical cache bodies; PDF',pdf_info)
    finally:
        srv.shutdown();srv.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
