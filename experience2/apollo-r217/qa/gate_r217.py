#!/usr/bin/env python3
"""R217 reproducible HTTP-served Chromium, PHP, and adversarial content QA.
No remote navigation, merchant operations, WordPress writes, or claim of installed-site acceptance.
"""
import hashlib, json, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_r217 import verify, FREE

# Protect the exact generated source/ledger records, not merely a hostname.
def protect_markup(html,css):
    entries={n:(DIST/n).read_bytes() for n in ('source-records.json','custody-ledger.json','link-custody-receipt.json')}
    return verify(html,css,entries)


ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
def digest(b):return hashlib.sha256(b).hexdigest()
def check(a,msg):
    if not a:raise AssertionError(msg)
def php(path,mode):
    return json.loads(subprocess.check_output(['php',str(path/'wp-render-shim-r217.php'),str(path/'fv-ex2-apollo-r217.php'),mode],text=True))

def main(folder):
    folder.mkdir(parents=True,exist_ok=True)
    check(subprocess.run(['php','-l',str(DIST/'fv-ex2-apollo-r217.php')],capture_output=True).returncode==0,'PHP parse')
    m=json.loads((DIST/'manifest.json').read_text())
    check(m['release']=='r217' and m['axe_core_accepted'] is False and m['commercial_release_allowed'] is False,'Release state')
    for name,h in m['files'].items():check(digest((DIST/name).read_bytes())==h,'Staging artifact drift: '+name)
    html=php(DIST,'normal')['html']
    check('fv-apollo-atlas' in html and html.count('class="cta"')==1,'PHP normal missing atlas')
    check(php(DIST,'printed')['css']=='done','Print rendering')
    check(php(DIST,'late')['fallback'] is True,'No stylesheet late fall-open')
    check(php(DIST,'normal')['js'] is False,'Unexpected creator/third-party JS')
    helper=php(DIST,'tamper-helper')
    check(helper.get('valid_original') and helper.get('tamper_rejected'),'Verified read-byte helper failed')
    orig=(DIST/'templates/atlas-fragment.html').read_bytes()
    cssbytes=(DIST/'assets/atlas-scoped.css').read_bytes()
    for changed in [
        orig.replace(b'https://www.nasa.gov/image-detail/amf-s67-15717/',b'https://www.nasa.gov/mission/apollo-1/'),
        orig.replace(b'data-source-id="S67-15717"',b'data-source-id="S66-58038"'),
        orig.replace(b'<time datetime="1967-01-27"',b'<time datetime="1967-01-26"'),
        orig.replace(b'</article>',b'<a href="https://www.nasa.gov/unreviewed/">New NASA link</a></article>',1)
    ]:
        try:protect_markup(changed,cssbytes)
        except ValueError:pass
        else:raise AssertionError('Source/chronology URL mutation admitted')
    for key,value in [('date','1967-01-04'),('commercial_advertising_clearance','APPROVED')]:
        records=json.loads((DIST/'source-records.json').read_text())
        records[1][key]=value
        files={n:(DIST/n).read_bytes() for n in ('source-records.json','custody-ledger.json','link-custody-receipt.json')}
        files['source-records.json']=json.dumps(records).encode()
        try:verify(orig,cssbytes,files)
        except ValueError:pass
        else:raise AssertionError('Unverified source record state accepted: '+key)
    files={n:(DIST/n).read_bytes() for n in ('source-records.json','custody-ledger.json','link-custody-receipt.json')}
    ledger=json.loads(files['custody-ledger.json'])
    ledger['geo_pins']=[{'lat':0,'lng':0}]
    files['custody-ledger.json']=json.dumps(ledger).encode()
    try:verify(orig,cssbytes,files)
    except ValueError:pass
    else:raise AssertionError('Speculative geo admitted')

    # Change each independent runtime provenance input while leaving the Atlas HTML/CSS untouched.
    with tempfile.TemporaryDirectory() as tmp:
        tampered=Path(tmp)/'dist';shutil.copytree(DIST,tampered)
        for name in m['source_and_commerce_gate_runtime_hash_checked']:
            f=tampered/name;raw=f.read_bytes();f.write_bytes(raw+b'\n')
            out=php(tampered,'normal')
            check(out['fallback'] is True and FREE in out['html'],'Tampered source/commerce release accepted: '+name)
            f.write_bytes(raw)
    unsafe=[('<iframe src="https://evil.invalid"></iframe>',True),
        ('<svg onload="alert(1)"></svg>',True),('<meta http-equiv="refresh" content="0;url=https://evil.invalid">',True),
        ('<input type="text" autofocus>',True),('<form action="https://evil.invalid"><button>Submit</button></form>',True),
        ('<a href="javascript:alert(1)">Click</a>',True),
        ('<a href="https://www.nasa.gov.evil.invalid/">Forged NASA</a>',True),
        ('<span onclick="alert(1)">Click</span>',True),('<span style="background:url(https://evil.invalid)">X</span>',True),
        ('<object data="https://evil.invalid"></object>',True),('<audio autoplay src="https://evil.invalid/a.mp3"></audio>',True),
        ('<a href="https://evil.invalid" target="_blank">Sales</a>',True),
        ('<link rel="stylesheet" href="https://evil.invalid/x.css">',True),
        ('<span data-lat="1" data-lng="2">Map</span>',True),('<script src="https://evil.invalid/a.js"></script>',True)]
    src=(DIST/'templates/atlas-fragment.html').read_bytes();css=(DIST/'assets/atlas-scoped.css').read_bytes()
    for injected,_ in unsafe:
        try:protect_markup(src.replace(b'</article>',injected.encode()+b'</article>',1),css)
        except ValueError:pass
        else:raise AssertionError('Unsafe active-content mutation admitted: '+injected)
    css_bad=[b'@import "https://evil.invalid/css";',b'.fv-apollo-atlas{background:url(https://evil.invalid/i)}',
             b'@font-face{font-family:a;src:url(https://evil.invalid/a)}',b'.fv-apollo-atlas{behavior: url(#x)}']
    for injected in css_bad:
        try:protect_markup(src,css+injected)
        except ValueError:pass
        else:raise AssertionError('Unsafe CSS mutation admitted')
    # Attempt real browser HTTP navigation; when administratively blocked, use the rendered fixture.
    with tempfile.TemporaryDirectory() as tmp:
        site=Path(tmp);(site/'assets').mkdir()
        (site/'assets'/'atlas-scoped.css').write_bytes(css)
        (site/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Apollo Evidence Atlas — staging fixture</title><link rel="stylesheet" href="/assets/atlas-scoped.css"></head>'
            '<body>'+html+'</body></html>',encoding='utf-8')
        class Quiet(SimpleHTTPRequestHandler):
            def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(site),**kwargs)
            def log_message(self,format,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}/'
        cases=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),
               ('1440',1440,{}),('1920',1920,{}),('no-js',390,{'java_script_enabled':False}),
               ('touch',390,{'is_mobile':True,'has_touch':True}),('reduced',390,{'reduced_motion':'reduce'}),
               ('forced',390,{'forced_colors':'active'})]
        check(urlopen(url,timeout=3).status==200,'Python HTTP fixture unreachable')
        check(urlopen(url+'assets/atlas-scoped.css',timeout=3).status==200,'HTTP CSS fixture unreachable')
        entries=[];labels=[];ax_cases=0;blocked_browser_navigation=False;fallback_count=0
        fixture='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo Evidence Atlas — staging fixture</title><style>'+css.decode()+'</style></head><body>'+html+'</body></html>'
        try:
            with sync_playwright() as pw:
                b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
                for name,width,config in cases:
                    c=b.new_context(viewport={'width':width,'height':850},**config)
                    p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
                    if config.get('java_script_enabled',True):
                        p.add_init_script("""(function() {window.__cls=0;window.__lcp=0;
                           new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});
                           new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});})(); """)
                    response=None
                    if not blocked_browser_navigation:
                        try:response=p.goto(url,wait_until='networkidle')
                        except PlaywrightError as exc:
                            if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc):raise
                            blocked_browser_navigation=True
                            p.close();p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
                    if blocked_browser_navigation:
                        p.set_content(fixture);fallback_count+=1
                    check((response is None or response.status==200) and p.title().startswith('Apollo Evidence Atlas'),'Fixture browser loading failed')
                    check(p.locator('style,link[rel="stylesheet"]').count()==1,'Local stylesheet not present')
                    check(p.locator('.fv-apollo-reading-bridge .cta').get_attribute('href')==FREE,'Original investigation path changed')
                    check(p.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'),'Overflow '+name)
                    nav=p.locator('nav a[href="#fv-apollo-reading-bridge"]').first
                    nav.focus();p.keyboard.press('Enter')
                    check(p.evaluate('location.hash')=='#fv-apollo-reading-bridge','Keyboard focus route '+name)
                    if config.get('has_touch'):nav.tap()
                    if name=='no-js':
                        summary=p.locator('.fv-apollo-atlas details summary').first
                        summary.click();check(summary.evaluate('(el)=>el.parentElement.open'),'NoJS native disclosure')
                    if name=='forced':check(p.locator('.fv-apollo-reading-bridge').is_visible(),'Forced colors hidden')
                    if name=='reduced':check(p.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'),'Reduced motion not effective')
                    # This observer runs on the actual Chromium fixture DOM. It is NOT field CWV or installed WordPress.
                    if config.get('java_script_enabled',True):
                        p.evaluate("""() => { window.__cls = 0; window.__lcp = null;
                          new PerformanceObserver(list => { for (const e of list.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});
                          new PerformanceObserver(list => { for (const e of list.getEntries()) window.__lcp = e.startTime; }).observe({type:'largest-contentful-paint', buffered:true});
                        }""")
                        p.wait_for_timeout(150)
                    session=c.new_cdp_session(p)
                    tree=session.send('Accessibility.getFullAXTree')
                    check(any(node.get('role',{}).get('value')=='link' and node.get('name',{}).get('value') for node in tree['nodes']), 'AX tree lacks named links')
                    ax_cases+=1
                    p.evaluate('document.documentElement.style.scrollBehavior="auto"; document.querySelector(".fv-apollo-atlas").style.scrollBehavior="auto"')
                    p.wait_for_timeout(500)
                    p.screenshot(path=str(folder/(name+'.png')),full_page=True,animations='disabled')
                    check(not errors,'Browser exceptions '+name)
                    metrics=p.evaluate('({lcp:window.__lcp??null,cls:window.__cls??null})') if config.get('java_script_enabled',True) else None
                    entries.append({'case':name,'width':width,'browser_http_response':response.status if response else None,'screenshot_sha256':digest((folder/(name+'.png')).read_bytes()),
                                    'performance_observer_browser_fixture_only':metrics,'ax_tree_nodes':len(tree['nodes'])})
                    c.close()
                c=b.new_context();p=c.new_page();p.set_content(fixture) if blocked_browser_navigation else p.goto(url)
                p.emulate_media(media='print')
                check(p.locator('.fv-apollo-lesson-key>div p').first.is_visible(),'Printed source answers hidden')
                c.close();b.close()
        finally:
            server.shutdown();server.server_close();thread.join(3)
    report={'result':'PASS_LOCAL_HTTP_RESPONSES_CHROMIUM_FIXTURE_AND_PHP','http_fixture_only':True,'chromium_contexts':len(entries),
        'python_real_http_css_and_html_200':True,'chromium_http_navigation_blocked_by_administrator':blocked_browser_navigation,
        'chromium_set_content_fallback_contexts':fallback_count,
        'cases':entries,'accessible_chromium_tree_checks':ax_cases,'active_markup_mutations_rejected':len(unsafe),
        'active_css_mutations_rejected':len(css_bad),'source_crosswalk_mutations_rejected':7,'independent_runtime_custody_mutations_rejected':len(m['source_and_commerce_gate_runtime_hash_checked']),
        'genuine_axe':'NOT_RUN: no verified local axe-core dependency','wordPress_staging':'NOT_TESTED','NVDA_VoiceOver':'NOT_TESTED',
        'revenue_paid_orders':None,'campaign_qualified_sessions':None,'realized_net_revenue':None,'release':'HOLD'}
    (folder/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('R217 PASS: Python local HTTP+CSS; Chromium fixture fallback='+str(blocked_browser_navigation)+'; 10 contexts; 19 active-content/CSS mutations; 7 source mutations; 6 runtime custody mutations')

if __name__=='__main__':main(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r217-qa'))
