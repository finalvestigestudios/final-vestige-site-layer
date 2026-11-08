#!/usr/bin/env python3
"""Fail-closed external WordPress Playground/Assembler admission for FV homepage.
Run only against disposable loopback or the documented WordPress Playground sandbox.
Never changes a CMS, submits an email, purchases, or visits production as a site.
Requires Python Playwright + Chromium. axe-core must be supplied separately.
"""
import argparse, asyncio, hashlib, json, shutil, sys, urllib.parse, urllib.request
from pathlib import Path

SIZES = [(320,568),(360,640),(390,667),(768,1024),(1440,900),(1920,1080)]
CHAPTERS = ['fv-hf-evidence','fv-hf-title','fv-hf-chronicle','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']
FOCUS_PATH = '/fv-ex2-focus-review/'

def allowed_origin(raw):
    url=urllib.parse.urlsplit(raw)
    host=(url.hostname or '').lower()
    if url.scheme not in ('http','https') or url.username or url.password or url.query or url.fragment or url.path not in ('','/'):
        raise ValueError('NON_ISOLATED_ORIGIN: provide only a bare staging origin')
    if not (host in ('127.0.0.1','localhost','::1','wpsandbox.wordpress.net') or host.endswith('.localhost')):
        raise ValueError('NON_ISOLATED_ORIGIN: production and external sites prohibited')
    if host=='wpsandbox.wordpress.net' and url.scheme!='https':
        raise ValueError('PLAYGROUND_REQUIRES_HTTPS')
    return raw.rstrip('/')

def fetch(url, limit=3_000_000):
    request=urllib.request.Request(url,headers={'User-Agent':'FV-EX2-ReadOnly-StagingQA/1.0'})
    with urllib.request.urlopen(request,timeout=12) as r:
        body=r.read(limit+1)
        if len(body)>limit: raise ValueError('RESPONSE_EXCEEDS_QA_LIMIT')
        return r.status,dict(r.headers),body

def preflight(origin):
    result={'origin':origin,'tests':{},'blockers':[]}
    for path, key in [('/wp-json/','core_rest'),('/wp-json/wp/v2/pages?slug=fv-ex2-review&_fields=id,slug,status','review_page'),('/wp-content/themes/assembler/style.css','assembler_css')]:
        try:
            code, headers, body = fetch(origin+path)
            if key=='core_rest':
                data=json.loads(body); ok=code==200 and isinstance(data.get('namespaces'),list) and 'wp/v2' in data['namespaces']
            elif key=='review_page':
                data=json.loads(body);ok=code==200 and isinstance(data,list) and len(data)==1 and data[0].get('slug')=='fv-ex2-review'
            else:
                ok=code==200 and len(body)>100 and (b'Theme Name:' in body or b'Assembler' in body or b'assembler' in body)
            result['tests'][key]={'pass':bool(ok),'status':code,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
            if not ok:result['blockers'].append('NOT_NATIVE_WORDPRESS_'+key.upper())
        except Exception as e:
            result['tests'][key]={'pass':False,'error':type(e).__name__+': '+str(e)[:150]}
            result['blockers'].append('NOT_NATIVE_WORDPRESS_'+key.upper())
    return result

async def browser_gate(origin, axe, output, report):
    from playwright.async_api import async_playwright
    if not axe or not Path(axe).is_file():
        report['blockers'].append('AXE_CORE_NOT_PROVIDED_FAIL_CLOSED')
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium') or '/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width,height in SIZES:
                for js in (True,False):
                    label=f'{width}x{height}_{"js" if js else "nojs"}'
                    entry={'viewport':[width,height],'javascript':js,'checks':{},'errors':[]}
                    report.setdefault('browser',{})[label]=entry
                    ctx=await browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,reduced_motion='reduce')
                    page=await ctx.new_page()
                    page.on('pageerror',lambda e,rec=entry:rec['errors'].append(str(e)[:300]))
                    try:
                        response=await page.goto(origin+'/',wait_until='domcontentloaded',timeout=18000)
                        await page.wait_for_timeout(600)
                        entry['status']=response.status if response else None
                        markup=await page.content()
                        entry['checks']['wp_document']=response is not None and response.status==200 and 'wp-site-blocks' in markup and 'fv-home' in markup
                        entry['checks']['chapters']=(await page.locator('.fv-hf__chapter-nav a').count()==7 and all([await page.locator('#'+i).count()==1 for i in CHAPTERS]))
                        entry['checks']['margins']=await page.locator('.fv-margin-strip__item').count()==72
                        entry['checks']['focus_links']=await page.locator('a[data-fv-ex2-isolated-focus="1"]').count()==5
                        entry['checks']['no_production_focus_leak']=await page.locator('a[href^="https://finalvestige.com/focus/"]').count()==0
                        entry['checks']['no_overflow']=await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        if width==320 and height==568:
                            a=page.locator('a[href="#fv-hf-evidence"]').first
                            box=await a.bounding_box()
                            entry['checks']['primary_cta_visible']=bool(box and box['y']>=0 and box['y']+box['height']<=height)
                        if axe and Path(axe).is_file():
                            await page.add_script_tag(path=str(axe))
                            issues=await page.evaluate('async () => {const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}});return r.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length}));}')
                            entry['checks']['axe_zero_detected_violations']=len(issues)==0
                            entry['axe_violations']=issues
                        else:entry['checks']['axe_zero_detected_violations']=False
                        file=output/f'{label}.png';await page.screenshot(path=str(file),full_page=True)
                        entry['screenshot']=file.name
                        entry['content_sha256']=hashlib.sha256(markup.encode()).hexdigest()
                        if js:
                            try:
                                link=page.locator('a[data-fv-ex2-isolated-focus="1"]').first
                                await link.click(timeout=3500)
                                await page.wait_for_load_state('domcontentloaded',timeout=5000)
                                entry['checks']['same_origin_focus_navigation']=(page.url.startswith(origin+FOCUS_PATH) and 'NO SUBSCRIPTION CAPTURE' in (await page.locator('body').inner_text()).upper() and await page.locator('input[type=email]').count()==0)
                            except Exception as e:entry['checks']['same_origin_focus_navigation']=False;entry['errors'].append('NAVIGATION: '+str(e)[:160])
                    except Exception as e:
                        entry['errors'].append('BROWSER: '+type(e).__name__+': '+str(e)[:200])
                    if not all(entry['checks'].values()) or entry['errors']:
                        report['blockers'].append('BROWSER_'+label)
                    await ctx.close()
        finally:await browser.close()

def run_self_test():
    bad=['https://finalvestige.com','https://evil.invalid','http://wpsandbox.wordpress.net','https://wpsandbox.wordpress.net/path','http://localhost/?subscribe=anything','http://user@localhost']
    good=['http://127.0.0.1:8012','http://localhost:8000','https://wpsandbox.wordpress.net','http://site.localhost:9000']
    n=0
    for x in bad:
        try:allowed_origin(x)
        except ValueError:n+=1
        else:raise AssertionError('UNSAFE_ORIGIN_ACCEPTED '+x)
    for x in good:
        assert allowed_origin(x)==x;n+=1
    from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
    from threading import Thread
    class Fake(BaseHTTPRequestHandler):
        def do_GET(self):
            b=b'{"namespaces":["fake/v1"]}'
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Fake);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        x=preflight('http://127.0.0.1:'+str(server.server_port))
        assert len(x['blockers'])==3 and not any(v.get('pass') for v in x['tests'].values())
        n+=3
    finally:server.shutdown();server.server_close()
    return {'pass':n,'fail':0,'scope':'isolation/false-WordPress fail-closed; actual WordPress unavailable'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--origin');ap.add_argument('--axe-js');ap.add_argument('--out',default='native-wp-evidence');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:
        print(json.dumps(run_self_test(),indent=2));sys.exit(0)
    if not args.origin:ap.error('--origin is required')
    try:origin=allowed_origin(args.origin)
    except ValueError as e:print('BLOCKED',str(e),file=sys.stderr);sys.exit(2)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    report=preflight(origin)
    if not report['blockers']:
        try:asyncio.run(browser_gate(origin,args.axe_js,out,report))
        except Exception as e:report['blockers'].append('BROWSER_UNAVAILABLE_'+type(e).__name__);report['browser_error']=str(e)[:500]
    else:report['blockers'].append('BROWSER_SKIPPED_NO_WORDPRESS')
    report['blockers'].append('LIGHTHOUSE_CWV_NOT_MEASURED')
    report['blockers'].append('JETPACK_REAL_SUBSCRIPTION_UNVERIFIED')
    report['blockers'].append('ARCHIVAL_SOURCE_RIGHTS_AND_MEDIA_TRANSFER_UNVERIFIED')
    report['release']='HOLD' if report['blockers'] else 'INDEPENDENT_REVIEW_REQUIRED'
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2));sys.exit(1 if report['blockers'] else 0)
