"""Apollo Experience 2.0 R181: read-only, release-blocked *installed* Research Desk QA.

Fixture evidence is lab-only. Real staging is constrained to an explicitly authorized
nonproduction origin and cannot follow a cross-origin redirect. This tool never writes WP.
"""
from __future__ import annotations
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

WIDTHS = (320, 360, 390, 768, 1440, 1920)
ORIGINAL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
EXPECTED_NASA = 'https://www.nasa.gov/'
PERF = """(()=>{window.__apolloR181Perf={lcp:null,cls:0};
try{new PerformanceObserver(l=>{for(const e of l.getEntries())
window.__apolloR181Perf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(_){}
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)
window.__apolloR181Perf.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(_){}
})();"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _host(host: str | None) -> str:
    if not host or host.strip() != host or host.endswith('.') or '*' in host:
        raise ValueError('Host must be an exact DNS name without wildcard or trailing dot')
    host = host.lower()
    if host in {'finalvestige.com', 'www.finalvestige.com', 'localhost', 'localhost.localdomain'}:
        raise ValueError('Production and loopback hostnames are not staging')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if '.' not in host or any(not label or label.startswith('-') or label.endswith('-') for label in host.split('.')):
            raise ValueError('Host must be an explicit valid DNS hostname')
    else:
        raise ValueError('IP literals are not accepted as authorized staging hosts')
    return host


def approved_url(url: str, hostname: str) -> bool:
    """Only exact authorized HTTPS origin plus normal HTTPS port is permitted."""
    try:
        p = urlsplit(url)
        return (p.scheme == 'https' and p.hostname == _host(hostname)
                and p.port in (None, 443) and not p.username and not p.password
                and not p.fragment)
    except (ValueError, TypeError):
        return False


def preflight(args) -> str:
    if bool(args.fixture) == bool(args.url):
        raise ValueError('Exactly one of --fixture and --url is required')
    if args.fixture:
        if not args.fixture.is_file():
            raise ValueError('Fixture file does not exist')
        return 'LAB_FIXTURE_ONLY'
    _host(args.approved_host)
    if not approved_url(args.url, args.approved_host):
        raise ValueError('Explicit exact-origin nonproduction HTTPS host is required')
    if not args.axe_js or not args.axe_js.is_file() or args.axe_js.stat().st_size < 100_000:
        raise ValueError('Installed-site QA requires genuine local axe-core (>=100 KB)')
    if not args.axe_sha256 or len(args.axe_sha256) != 64 or sha256(args.axe_js) != args.axe_sha256.lower():
        raise ValueError('axe-core file requires an operator-verified SHA-256 pin')
    if args.image_policy not in {'links-only', 'gallery'}:
        raise ValueError('Unknown image policy')
    if args.image_policy == 'gallery' and args.minimum_images < 1:
        raise ValueError('Gallery must declare a positive minimum image count')
    return 'WORDPRESS_STAGING_CANDIDATE'


async def one_context(browser, args, width: int, *, javascript: bool, forced_colors: bool = False):
    context = await browser.new_context(
        viewport={'width': width, 'height': 880}, java_script_enabled=javascript,
        reduced_motion='reduce', has_touch=width == 390,
        forced_colors='active' if forced_colors else 'none',
    )
    page = await context.new_page()
    errors = []
    failed_responses = []
    blocked_redirects = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('response', lambda res: failed_responses.append({'url': res.url, 'status': res.status})
            if res.status >= 400 and (res.request.resource_type in {'document', 'script', 'stylesheet', 'image'}) else None)
    if javascript:
        await context.add_init_script(PERF)
    if not args.fixture:
        # Reject all document cross-origin transitions, including redirects and JS navigation.
        async def route_document(route):
            if route.request.resource_type == 'document' and not approved_url(route.request.url, args.approved_host):
                blocked_redirects.append(route.request.url)
                await route.abort('blockedbyclient')
            else:
                await route.continue_()
        await context.route('**/*', route_document)
    try:
        if args.fixture:
            await page.set_content(args.fixture.read_text(encoding='utf-8'), wait_until='domcontentloaded', timeout=12000)
            # set_content() does not create a navigation in which init scripts run.
            # Initialize only the optional laboratory observer after fixture DOM exists.
            if javascript:
                await page.evaluate(PERF)
        else:
            await page.goto(args.url, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(150)
        root = page.locator('[data-fvx-ledger]')
        checks = {
            'one_ledger': await root.count() == 1,
            'six_records': await page.locator('[data-fvx-record]').count() == 6,
            'all_records_visible': await page.locator('[data-fvx-record]:visible').count() == 6,
            'no_horizontal_overflow': await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
            'original_investigation_link': await page.locator('a[href="'+ORIGINAL+'"]').count() == 1,
            'nasa_links_six_or_more': await page.locator('[data-fvx-record] a[href^="https://www.nasa.gov/"]').count() >= 6,
            'catalog_uncertainty_visible': await page.get_by_text('Catalog identification not verified.', exact=False).count() >= 1,
            'no_unrelated_merchant_links': await root.locator('a[href*="awin1.com"], a[href*="payhip.com"]').count() == 0,
        }
        if javascript:
            search = root.locator('input[data-fvx-search]')
            checks['search_visible'] = await search.count() == 1 and await search.is_visible()
            if checks['search_visible']:
                await search.fill('Catalog identification not verified.')
                checks['search_provenance'] = await page.locator('[data-fvx-record]:visible').count() == 1
                await search.fill('')
                checks['search_reset'] = await page.locator('[data-fvx-record]:visible').count() == 6
                if width == 390:
                    # A touch-emulated context must preserve original evidence after input.
                    await search.tap()
                    checks['touch_search_preserves_records'] = await page.locator('[data-fvx-record]:visible').count() == 6
            await page.keyboard.press('Tab')
            checks['keyboard_focus_present'] = await page.evaluate("document.activeElement !== document.body")
        else:
            checks['no_js_tools_hidden'] = await root.locator('[data-fvx-tools]').is_hidden()
            checks['no_js_evidence_all_visible'] = await page.locator('[data-fvx-record]:visible').count() == 6
        axe_violations = None
        media = {'status': 'NOT_APPLICABLE_LINKS_ONLY' if args.image_policy == 'links-only' else 'NOT_TESTED'}
        if not args.fixture:
            checks['approved_final_origin'] = approved_url(page.url, args.approved_host)
            checks['no_cross_origin_document_redirect'] = not blocked_redirects
            checks['no_asset_http_failures'] = not failed_responses
            checks['wp_site_wrapper_present'] = await page.locator('.wp-site-blocks').count() >= 1
            if args.image_policy == 'gallery':
                images = await root.locator('img').evaluate_all(
                    '(xs)=>xs.map(x=>({src:x.currentSrc||x.src,decoded:x.complete && x.naturalWidth>0,alt:x.hasAttribute("alt")}))')
                media = {'status': 'DECODED' if len(images)>=args.minimum_images and all(x['decoded'] and x['alt'] for x in images) else 'FAILED',
                         'count': len(images), 'minimum': args.minimum_images, 'images': images}
                checks['gallery_media_decoded_with_alt'] = media['status'] == 'DECODED'
            if javascript:
                await page.add_script_tag(path=str(args.axe_js))
                axe_data = await page.evaluate('''async()=>{
                    if(!window.axe || typeof axe.run !== 'function' || !axe.version) return null;
                    const r=await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                    return {version:axe.version, violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})), passes:r.passes.length,incomplete:r.incomplete.length};
                }''')
                checks['axe_runtime_present'] = bool(axe_data and axe_data['version'] and axe_data['passes'] > 0)
                checks['axe_no_violations'] = bool(axe_data and not axe_data['violations'])
                axe_violations = axe_data
        # Screenshot stabilization is lab-only; screenshots do not constitute production perf evidence.
        # Playwright add_style_tag may hang in Chromium with JavaScript disabled.
        # Static no-JS capture already has no caret/active editing to stabilize.
        if javascript:
            await page.add_style_tag(content='input{caret-color:transparent!important} html{scroll-behavior:auto!important}')
            await page.evaluate('document.activeElement && document.activeElement.blur()')
        await page.screenshot(path=str(args.output / f"{width}-{'nojs' if not javascript else 'forced' if forced_colors else 'js'}.png"),
                              full_page=True, animations='disabled', timeout=10000)
        shotpath = args.output / f"{width}-{'nojs' if not javascript else 'forced' if forced_colors else 'js'}.png"
        metrics = await page.evaluate('window.__apolloR181Perf || null') if javascript else None
        return {'width':width, 'javascript':javascript,'forced_colors':forced_colors,
                'checks': checks,'errors':errors,'asset_errors':failed_responses,'blocked_document_urls':blocked_redirects,
                'axe':axe_violations,'media':media,'lab_metrics_not_field_CWV':metrics,
                'screenshot_sha256':sha256(shotpath)}
    finally:
        await context.close()


async def main(args) -> dict:
    mode = preflight(args)
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
        try:
            contexts = [(w, True, False) for w in WIDTHS] + [(320,False,False), (390,True,True)]
            for w, js, forced in contexts:
                try:
                    result = await asyncio.wait_for(one_context(browser,args,w,javascript=js,forced_colors=forced), timeout=args.context_timeout)
                    results.append(result)
                except Exception as exc:
                    errors.append({'width':w,'javascript':js,'forced_colors':forced,'error':type(exc).__name__+': '+str(exc)[:250]})
                # Always write a partial receipt, even if remaining browser contexts fail.
                save_receipt(args.output,mode,results,errors, complete=False)
        finally:
            await browser.close()
    return save_receipt(args.output,mode,results,errors, complete=True)


def save_receipt(folder: Path, mode: str, results: list, errors: list, *, complete: bool) -> dict:
    failure_details = [f"{r['width']}:{k}" for r in results for k,v in r['checks'].items() if not v]
    failure_details.extend(f"{r['width']}:pageerror:{e}" for r in results for e in r['errors'])
    failure_details.extend(f"{r['width']}:asset_http_error" for r in results if r['asset_errors'])
    failure_details.extend(f"{r['width']}:document_redirect" for r in results if r['blocked_document_urls'])
    if errors: failure_details.append('browser_context_error')
    if len(results)!=8: failure_details.append('missing_expected_contexts')
    verdict = ('HOLD' if mode == 'LAB_FIXTURE_ONLY' or failure_details or not complete
               else 'TECHNICAL_CANDIDATE_PENDING_MANUAL_QA_AND_FOUNDER_APPROVAL')
    report = {'mode':mode,'verdict':verdict,'complete':complete,
              'blockers':failure_details,'browser_errors':errors,'runs':results,
              'images_policy': 'per-run',
              'axe_provenance': 'unverified in fixture; pinned local library required in staging',
              'manual_screen_reader':'NOT_TESTED',
              'exact_head_CI':'NOT_ESTABLISHED',
              'realized_revenue':'UNKNOWN_NOT_OBSERVED',
              'report_is_not_production_release_approval':True}
    (folder/'receipt.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n', encoding='utf-8')
    return report


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture',type=Path)
    p.add_argument('--url')
    p.add_argument('--approved-host')
    p.add_argument('--axe-js',type=Path)
    p.add_argument('--axe-sha256')
    p.add_argument('--image-policy',choices=['links-only','gallery'],default='links-only')
    p.add_argument('--minimum-images',type=int,default=0)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--chromium',default='/usr/bin/chromium')
    p.add_argument('--context-timeout',type=float,default=35)
    return p

if __name__=='__main__':
    args=parser().parse_args()
    r=asyncio.run(main(args))
    print(json.dumps({'mode':r['mode'],'verdict':r['verdict'],'contexts':len(r['runs']),
                      'blockers':r['blockers'],'browser_errors':r['browser_errors']}))
