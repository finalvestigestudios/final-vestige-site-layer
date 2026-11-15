#!/usr/bin/env python3
"""READ-ONLY real installed staging smoke, deliberately refuses production.

Usage:
  python qa/staging_smoke.py --url https://staging.example.test/apollo-review/ \
    --approved-staging-host staging.example.test --axe-script /path/to/axe.min.js \
    --axe-sha256 <reviewed axe-core SHA256> --output-dir /tmp/apollo-r389-stage

The axe script must be a separately sourced, checksum-reviewed genuine axe-core build.
It is not bundled, downloaded, or loaded by visitor-facing WordPress code.
This script cannot run from the unapproved local fixture as staging acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
# R392 exact textual source custody: no visitor-facing code, network or WP writes.
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'apollo-r392'/'qa'))
from semantic_custody import verify_page, verified_records
from urllib.parse import urlparse, urlsplit, urlunsplit
from playwright.sync_api import sync_playwright

VIEWPORTS=(320,390,768,1440,1920)
PRODUCTION={'finalvestige.com','www.finalvestige.com'}

def _approved_host(allowed):
    """An explicit bare hostname, not a production alias, URL, port or userinfo."""
    if not allowed or allowed.strip() != allowed or any(c in allowed for c in '/:@?#\\'):
        raise ValueError('HARD STOP: --approved-staging-host must be a bare staging hostname')
    host = allowed.lower().rstrip('.')
    if not host or host in PRODUCTION or host.startswith('.') or '..' in host:
        raise ValueError('HARD STOP: approved hostname is invalid or production')
    return host

def scrub_url(raw):
    """No query strings, user credentials or fragments in captured QA evidence."""
    try:
        u=urlsplit(raw)
        hostname = (u.hostname or 'invalid-host').lower()
        port = ':' + str(u.port) if u.port is not None else ''
        # Host/path are helpful for debugging; query tokens and fragment are not.
        return urlunsplit((u.scheme, hostname + port, u.path, '', ''))
    except (ValueError, TypeError):
        return '[invalid URL redacted]'

def guard(url, allowed):
    host = _approved_host(allowed)
    dest=urlparse(url)
    try: port = dest.port
    except ValueError: port = -1
    if (dest.scheme != 'https' or not dest.hostname or
        dest.hostname.lower() != host or port not in (None, 443) or
        dest.username is not None or dest.password is not None or dest.fragment):
        raise ValueError('HARD STOP: explicit HTTPS non-production staging origin required')
    return host

def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

# The digest is sealed in the reviewed R389 PHP shortcode adapter. A remotely
# loaded stylesheet must match this *exact* payload, not merely a computed color.
REVIEWED_GALLERY_CSS_SHA256 = '4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9'

def staging_resource_allowed(resource_url, approved_host, method='GET'):
    """Only idempotent methods on exact HTTPS staging origin may reach network.

    Crucially, R390 previously permitted POST/PUT/DELETE even though the tool
    described itself as read-only. Deny all such requests *before* route.fetch.
    """
    if method not in ('GET', 'HEAD'):
        return False
    try:
        host = _approved_host(approved_host)
        parsed = urlparse(resource_url)
        port = parsed.port
        return (parsed.scheme == 'https' and parsed.hostname is not None
                and parsed.hostname.lower() == host
                and port in (None,443)
                and parsed.username is None and parsed.password is None
                and not parsed.fragment)
    except (ValueError,TypeError):
        return False

def install_network_boundary(context, approved_host, denied):
    """Deny mutations, off-origin fetches, redirects and all WebSocket traffic.

    Passing this mocked contract does NOT prove deployed browser interception.
    """
    def check_route(route):
        request = route.request
        method = getattr(request,'method','GET')
        if not staging_resource_allowed(request.url, approved_host, method):
            denied.append({'url': scrub_url(request.url), 'kind': request.resource_type,
                           'method': method, 'navigation': request.is_navigation_request(),
                           'reason': 'METHOD_OR_ORIGIN_DENIED'})
            route.abort(error_code='blockedbyclient')
        else:
            try:
                response = route.fetch(max_redirects=0, timeout=15000)
                if 300 <= response.status < 400:
                    denied.append({'url':scrub_url(request.url),'kind':request.resource_type,
                                   'method':method, 'navigation':request.is_navigation_request(),
                                   'reason':'REDIRECT_DENIED', 'redirect_status':response.status,
                                   'redirect_location':scrub_url(response.headers.get('location',''))})
                    route.abort(error_code='blockedbyclient')
                else:
                    route.fulfill(response=response)
            except Exception as exc:
                # Library exceptions can contain signed URLs or request tokens.
                denied.append({'url':scrub_url(request.url),'kind':request.resource_type,
                               'method':method, 'reason':'FETCH_FAILED',
                               'error_class':type(exc).__name__})
                try: route.abort(error_code='failed')
                except Exception: pass
    context.route('**/*', check_route)
    if not hasattr(context, 'route_web_socket'):
        raise RuntimeError('HARD STOP: Playwright must support preconnection WebSocket routing')
    def block_ws(ws):
        denied.append({'url':scrub_url(ws.url), 'kind':'websocket','reason':'WEBSOCKET_DENIED'})
        ws.close(code=1008, reason='Read-only staging evidence capture')
    context.route_web_socket('**/*',block_ws)


def inspect_stylesheet_responses(responses):
    """Require one successful, same-origin gallery.css response of reviewed bytes."""
    candidates = [r for r in responses if urlparse(r.url).path.endswith('/assets/gallery.css')]
    found = []
    for r in candidates:
        try:
            found.append({'url': scrub_url(r.url), 'status': r.status,
                          'sha256': hashlib.sha256(r.body()).hexdigest()})
        except Exception as exc:
            found.append({'url': scrub_url(r.url), 'error_class': type(exc).__name__})
    ok = (len(found) == 1 and found[0].get('status') == 200
          and found[0].get('sha256') == REVIEWED_GALLERY_CSS_SHA256)
    return ok, found


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--url',required=True)
    a.add_argument('--approved-staging-host',required=True)
    a.add_argument('--axe-script',required=True)
    a.add_argument('--axe-sha256',required=True)
    a.add_argument('--output-dir',required=True)
    a.add_argument('--chromium',default='/usr/bin/chromium')
    args=a.parse_args()
    host=guard(args.url,args.approved_staging_host)
    axe_path=Path(args.axe_script)
    if not axe_path.is_file() or len(args.axe_sha256)!=64 or sha_file(axe_path)!=args.axe_sha256.lower():
        raise ValueError('HARD STOP: genuine axe-core bundle must be present and pinned to a reviewed SHA256')
    # Fail before opening browser if the approved source ledger has drifted.
    verified_records()
    folder=Path(args.output_dir)
    folder.mkdir(parents=True,exist_ok=True)
    output={'kind':'REAL_INSTALLED_STAGING_CANDIDATE','url':scrub_url(args.url),'approved_host':host,'axe_bundle_sha256':args.axe_sha256,
            'contexts':[], 'production_changes':False,'release_allowed':False}
    failures=[]
    vitals_script="""window.__fvVitals={lcp:null,cls:0};try{
    new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
    new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});
    }catch(e){window.__fvVitals.error=String(e)}"""
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=args.chromium,args=['--no-sandbox'])
        try:
            for width in VIEWPORTS:
                ctx=browser.new_context(viewport={'width':width,'height':880},java_script_enabled=True,
                                        service_workers='block')
                denied = []
                install_network_boundary(ctx, host, denied)
                page=ctx.new_page()
                responses=[]
                page.on('response',lambda response: responses.append(response))
                page.add_init_script(vitals_script)
                try:
                    response=page.goto(args.url,wait_until='load',timeout=30000)
                    page.wait_for_timeout(500)
                except Exception as exc:
                    output['contexts'].append({'width':width,'status':'HARD_HOLD_NETWORK',
                                               'error_class':type(exc).__name__,'blocked_requests':denied})
                    failures.append(f'{width}: navigation/redirect rejected or unavailable')
                    ctx.close()
                    continue
                item={'width':width,'http_status':response.status if response else None,
                      'final_url':scrub_url(page.url), 'blocked_requests':denied,
                      'csp_header':response.headers.get('content-security-policy') if response else None}
                if not staging_resource_allowed(page.url, host):
                    failures.append(f'{width}: final browser URL escaped approved staging origin')
                if denied:
                    failures.append(f'{width}: blocked {len(denied)} off-staging resource/redirect requests')
                css_ok, css_responses = inspect_stylesheet_responses(responses)
                item['gallery_css_verified']=css_ok
                item['gallery_css_responses']=css_responses
                if not css_ok:
                    failures.append(f'{width}: reviewed gallery stylesheet bytes not delivered')
                item['gallery_present']=page.locator('[data-fv-r384-gallery]').count()==1
                item['card_count']=page.locator('[data-fv-r384-record]').count()
                item['publication_count']=page.locator('[data-fv-r384-publication]').count()
                item['nasa_card_links']=page.locator('[data-fv-r384-nasa]').count()
                item['free_ctas']=page.locator('[data-fv-free-cta]').count()
                item['overflow']=page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')
                item['computed_background']=page.locator('[data-fv-r384-gallery]').evaluate('(el)=>getComputedStyle(el).backgroundColor') if item['gallery_present'] else None
                item['stylesheets']=page.evaluate("[...document.styleSheets].map(x=>x.href).filter(Boolean)")
                custody_ok, custody_blockers = verify_page(page)
                item['exact_source_custody_pass']=custody_ok
                item['source_custody_blockers']=custody_blockers
                if not custody_ok: failures.append(f'{width}: NASA source content, limitations, chronology or CTA integrity failed')
                item['local_vitals']=page.evaluate('window.__fvVitals')
                page.add_script_tag(path=str(axe_path))
                item['axe_version']=page.evaluate('window.axe&&window.axe.version')
                if not item['axe_version']:
                    failures.append(f'{width}: supplied bundle failed genuine axe.version guard')
                    item['axe_violations']=['axe.js missing or invalid']
                else:
                    axe=page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                      return r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.length}))}""")
                    item['axe_violations']=axe
                if not (response and response.ok and item['gallery_present'] and item['card_count']==6
                      and item['publication_count']==2 and item['nasa_card_links']==6 and item['free_ctas']==1
                      and not item['overflow'] and item['computed_background']=='rgb(21, 27, 32)' and css_ok and not denied and not item['axe_violations']):
                    failures.append(f'{width}: staging structural/stylesheet/axe acceptance incomplete')
                if not item['csp_header']:
                    failures.append(f'{width}: CSP response header not established (manual governance required)')
                page.screenshot(path=str(folder/f'{width}-installed-staging.png'),full_page=True,animations='disabled')
                if width==1440:
                    page.pdf(path=str(folder/'installed-staging-document.pdf'),format='A4',print_background=True)
                ctx.close()
                # No action beyond read-only page navigation and fixture capture.
                ctx2=browser.new_context(viewport={'width':width,'height':880},java_script_enabled=False,
                                         service_workers='block')
                denied_nojs=[]
                install_network_boundary(ctx2,host,denied_nojs)
                nojs=ctx2.new_page()
                nojs_responses=[]
                nojs.on('response',lambda response: nojs_responses.append(response))
                try:
                    nojs.goto(args.url,wait_until='load',timeout=30000)
                except Exception as exc:
                    failures.append(f'{width}: no-JS navigation/redirect failed closed: {exc}')
                    item['nojs_navigation_error']=type(exc).__name__
                    item['nojs_blocked_requests']=denied_nojs
                    ctx2.close()
                    output['contexts'].append(item)
                    continue
                item['nojs_blocked_requests']=denied_nojs
                item['nojs_final_url']=scrub_url(nojs.url)
                if denied_nojs or not staging_resource_allowed(nojs.url,host):
                    failures.append(f'{width}: no-JS off-staging request or redirect')
                item['nojs_cards']=nojs.locator('[data-fv-r384-record]').count()
                item['nojs_disclosures']=nojs.locator('details').count()
                item['nojs_publication_links']=nojs.locator('[data-fv-r384-publication]').count()
                item['nojs_nasa_question_links']=nojs.locator('[data-fv-r384-nasa]').count()
                item['nojs_free_ctas']=nojs.locator('[data-fv-free-cta]').count()
                nojs_custody_ok, nojs_custody_blockers = verify_page(nojs)
                item['nojs_exact_source_custody_pass']=nojs_custody_ok
                item['nojs_source_custody_blockers']=nojs_custody_blockers
                if not nojs_custody_ok: failures.append(f'{width}: no-JS NASA source / rights / CTA custody mismatch')
                css_nojs_ok, css_nojs_responses=inspect_stylesheet_responses(nojs_responses)
                item['nojs_gallery_css_verified']=css_nojs_ok
                item['nojs_gallery_css_responses']=css_nojs_responses
                if not css_nojs_ok:
                    failures.append(f'{width}: no-JavaScript reviewed stylesheet missing/tampered')
                if (item['nojs_cards']!=6 or item['nojs_disclosures']!=6 or
                    item['nojs_publication_links']!=2 or item['nojs_nasa_question_links']!=6 or
                    item['nojs_free_ctas']!=1):
                    failures.append(f'{width}: no-JavaScript source or free CTA incomplete')
                ctx2.close()
                output['contexts'].append(item)
        finally:
            browser.close()
    output['blockers']=failures
    output['status']='LOCAL_STAGING_TESTS_PASSED_BUT_NO_RELEASE_APPROVAL' if not failures else 'HOLD_STAGING_QA_FAILED'
    (folder/'staging-browser-evidence.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'status':output['status'],'widths':VIEWPORTS,'blockers':failures},indent=2))
    if failures:
        raise SystemExit(1)

if __name__=='__main__':main()
