#!/usr/bin/env python3
"""R442 read-only, HTTPS, same-origin real staging acceptance. Fails HOLD on uncertainty."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
PROBE = """(() => {
window.__apolloVitals = {lcp:null,cls:0,entries:0};
try {new PerformanceObserver(l=>{for(const e of l.getEntries())window.__apolloVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})} catch(e){}
try {new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){window.__apolloVitals.cls+=e.value;window.__apolloVitals.entries++}}).observe({type:'layout-shift',buffered:true})} catch(e){}
})();"""

def canonical_origin(raw):
    try:
        u = urlsplit(raw)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment:
            return None
        if u.port not in (None, 443) or u.hostname.lower() in ('finalvestige.com', 'www.finalvestige.com'):
            return None
        if not u.netloc or u.netloc.endswith('.') or u.hostname in ('localhost', '127.0.0.1'):
            return None
        return 'https://' + u.hostname.lower()
    except (ValueError, TypeError):
        return None

def validate_args(url, origin, axe_path, expected_sha):
    errors = []
    site = canonical_origin(url)
    approved = canonical_origin(origin)
    if not site or not approved or site != approved or urlsplit(origin).path not in ('', '/'):
        errors.append('approved URL and origin must be identical HTTPS nonproduction origins, no query, redirects or credentials')
    if len(expected_sha) != 64 or any(c not in '0123456789abcdef' for c in expected_sha):
        errors.append('independent reviewed axe-core SHA-256 required')
    p = Path(axe_path) if axe_path else None
    if not p or p.is_symlink() or not p.is_file() or p.stat().st_size < 25000:
        errors.append('genuine local axe-core file missing/invalid')
    elif hashlib.sha256(p.read_bytes()).hexdigest() != expected_sha:
        errors.append('axe-core file does not match approved SHA-256')
    return errors

def inspect_document(page):
    """No writes, click events or checkout network requests. All checks DOM-only."""
    return page.evaluate('''() => {
const one = s => document.querySelectorAll(s).length;
const hrefs = [...document.querySelectorAll('[data-r438-card] a[href]')].map(a => a.href);
const cta = [...document.querySelectorAll('.fv-r429__cta a[href]')].map(a=>a.href);
const paid = [...document.querySelectorAll('a[href],form[action]')].filter(a => /payhip\\.com|checkout|stripe\\.com|paypal\\.com|payment|buy-now/i.test(a.href || a.action || '')).length;
return {records:one('[data-r438-card]'), educator:one('[data-r440-root]'),
source_links:hrefs.length, unsafe_source_links:hrefs.filter(u=>!u.startsWith('https://www.nasa.gov/')).length,
free_ctas:cta, paid_ctas:paid, overflow:document.documentElement.scrollWidth>innerWidth+1,
source_drawers:one('details'), text_length:document.body.innerText.length};
}''')

def inspect_row(row):
    problems = []
    def require(condition, problem):
        if not condition: problems.append(problem)
    require(row['http'] == 200, 'HTTP must be exactly 200')
    require(row['redirects'] == 0, 'redirects are prohibited')
    require(row['final_origin'] == row['approved_origin'], 'origin changed')
    d = row['document']
    require(d['records'] >= 5, 'five source records required')
    require(d['educator'] == 1, 'exactly one educator preview required')
    require(d['unsafe_source_links'] == 0 and d['source_links'] >= 2, 'NASA provenance links invalid')
    require(len(d['free_ctas']) == 1, 'one editorial free CTA required')
    require(d['free_ctas'] == ['https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'], 'free CTA does not match reviewed article')
    require(d['paid_ctas'] == 0, 'unapproved paid checkout or payment form')
    require(not d['overflow'], 'horizontal overflow')
    require(d['text_length'] >= 300, 'missing accessible content')
    if row['js']:
        require(not row['axe_violations'], 'axe WCAG violations')
        vital = row['lab_vitals']
        require(isinstance(vital.get('lcp'), (int,float)) and 0 < vital['lcp'] <= 2500, 'LCP unmeasured or over 2500 ms')
        require(isinstance(vital.get('cls'), (int,float)) and 0 <= vital['cls'] <= 0.1, 'CLS unmeasured or over 0.1')
    return problems

def run(url, origin, axe, out):
    output = Path(out)
    output.mkdir(parents=True, exist_ok=True)
    errors, rows = [], []
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=True, executable_path=os.environ.get('FV_CHROMIUM_PATH','/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for js in (True, False):
                    context = browser.new_context(viewport={'width':width,'height':900}, is_mobile=width<=390,
                        has_touch=width<=390, reduced_motion='reduce', java_script_enabled=js, service_workers='block')
                    page = context.new_page()
                    blocked = []
                    def route_guard(route):
                        parsed = urlsplit(route.request.url)
                        if parsed.scheme != 'https' or canonical_origin(parsed.scheme+'://'+parsed.netloc) != origin:
                            blocked.append('out-of-origin request blocked')
                            route.abort()
                        else:
                            route.continue_()
                    page.route('**/*', route_guard)
                    if js: page.add_init_script(PROBE)
                    try:
                        response = page.goto(url, wait_until='load', timeout=30000)
                        page.wait_for_timeout(1200)
                        redirect_count = 0
                        req = response.request if response else None
                        while req and req.redirected_from:
                            redirect_count += 1
                            req = req.redirected_from
                        final_origin = canonical_origin(page.url)
                        row={'width':width,'js':js,'http':response.status if response else None,
                            'redirects':redirect_count, 'final_origin':final_origin, 'approved_origin':origin,
                            'blocked_external_requests':len(blocked), 'document':inspect_document(page),
                            'axe_violations':[], 'lab_vitals':{}}
                        if js:
                            page.add_script_tag(path=str(axe))
                            result=page.evaluate('''async()=>{
if(!window.axe || !window.axe.version || typeof window.axe.run!=='function')throw new Error('not genuine axe-core');
const r=await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
return {version:window.axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))};
}''')
                            row['axe_version']=result['version']
                            row['axe_violations']=result['violations']
                            row['lab_vitals']=page.evaluate('window.__apolloVitals')
                        row['failures']=inspect_row(row)
                        if blocked: row['failures'].append('out-of-origin resources attempted; review sources and rights')
                        page.screenshot(path=str(output / f'{width}-{"js" if js else "nojs"}.png'), full_page=True)
                        rows.append(row)
                        errors.extend(f'{width}/{js}: {item}' for item in row['failures'])
                    except Exception as exc:
                        errors.append(f'{width}/{js}: navigation/axe/metrics not verified: {str(exc)[:280]}')
                    finally:
                        context.close()
        finally:
            browser.close()
    result={'status':'HOLD' if errors else 'PASS_STAGING_LAB_ONLY', 'kind':'origin-locked read-only navigated Chromium; NOT field CWV or merchant validation',
            'tested_url':url,'approved_origin':origin,'rows':rows,'failures':errors, 'release_authorized':False,
            'paid_product_verified':False,'merchant_orders_verified':False}
    (output/'report.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',default=os.environ.get('FV_APOLLO_STAGING_URL',''))
    parser.add_argument('--origin',default=os.environ.get('FV_APOLLO_APPROVED_ORIGIN',''))
    parser.add_argument('--axe-js',default=os.environ.get('FV_AXE_CORE_JS',''))
    parser.add_argument('--axe-sha256',default=os.environ.get('FV_AXE_SHA256',''))
    parser.add_argument('--out',default='QA/staging')
    a=parser.parse_args()
    failures=validate_args(a.url,a.origin,a.axe_js,a.axe_sha256)
    if failures:
        print(json.dumps({'status':'HOLD_NOT_RUN','failures':failures},indent=2));raise SystemExit(2)
    result=run(a.url,canonical_origin(a.origin),a.axe_js,a.out)
    print(json.dumps({'status':result['status'],'rows':len(result['rows']),'failures':result['failures']},indent=2))
    raise SystemExit(0 if result['status']=='PASS_STAGING_LAB_ONLY' else 2)

if __name__=='__main__':main()
