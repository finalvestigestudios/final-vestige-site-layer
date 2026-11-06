"""Apollo Atlas READ-ONLY installed-page acceptance witness.

Usage: python live_acceptance.py --url https://STAGING.example/apollo-1-evidence-atlas/ --out ./evidence --axe ./axe.min.js
No WordPress writes, no tracking, no external install. Any missing axe/live-image/JS result BLOCKS release.
"""
import argparse, hashlib, json, os, re, sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Error as PlaywrightError

WIDTHS = (320, 360, 390, 768, 1440, 1920)
OBSERVER = """(() => {
  window.__fvCWV = {lcp: null, cls: 0, errors: []};
  addEventListener('error', () => window.__fvCWV.errors.push('runtime_error'));
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__fvCWV.lcp = Math.round(e.startTime); }).observe({type:'largest-contentful-paint',buffered:true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__fvCWV.cls += e.value; }).observe({type:'layout-shift',buffered:true}); } catch (e) {}
})();"""

def witness(url: str, output: Path, axe: Path | None = None, timeout: int = 30000, fixture_html: Path | None = None):
    parsed = urlparse(url)
    if parsed.scheme not in ('http','https') or not parsed.netloc:
        raise ValueError('Only an explicit HTTP(S) installed-page URL is accepted')
    fixture = fixture_html.read_text(encoding="utf-8") if fixture_html else None
    output.mkdir(parents=True,exist_ok=True)
    report={'url':url, 'model':'SOURCE_PINNED_OFFLINE_FIXTURE_ONLY' if fixture else 'REAL_URL_BROWSER_NOT_FIELD_DATA', 'result':'HOLD',
            'widths':{}, 'no_js':{}, 'touch':{}, 'axe':{'status':'BLOCKED_MISSING_AXE'},
            'limitations':['LCP and CLS are controlled-browser lab observations, not CrUX p75 or production-user CWV.','No paid-order or campaign-attribution assertions.']}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
            context.add_init_script(OBSERVER)
            page=context.new_page()
            network_fail=[]
            page.on('requestfailed',lambda request:network_fail.append(urlparse(request.url).path[:130]))
            row={'checks':{},'errors':[],'network_failures':[]}
            try:
                response=page.goto(url,wait_until='domcontentloaded',timeout=timeout) if fixture is None else None
                if fixture is not None: page.set_content(fixture,wait_until='domcontentloaded')
                page.wait_for_timeout(800)
                row['http_status']=response.status if response else ('FIXTURE_NOT_HTTP' if fixture else None)
                row['checks']['http_ok']=bool((response and 200<=response.status<400) or fixture is not None)
                gallery=page.locator('[data-fvx-chrono-gallery]')
                row['checks']['gallery_present']=gallery.count()==1
                row['checks']['three_archival_sources']=gallery.locator('figcaption a[href*="nasa.gov/"]').count()==3
                row['checks']['no_horizontal_overflow']=page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                row['checks']['reduced_motion']=page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
                row['checks']['independent_controls']=gallery.locator('.fvx-archive-choice button').count()==3
                row['checks']['original_investigation_link']=page.locator('a[href*="the-hatch-opened-inward-apollo-1/"]').count()>=1
                figures=gallery.locator('[data-fvx-chrono-photo]')
                row['checks']['three_figures']=figures.count()==3
                # See all three real images; scroll to trigger lazy loading. Not substituted or mocked.
                images=gallery.locator('img')
                for i in range(images.count()):
                    if row['checks']['independent_controls']:
                        gallery.locator('.fvx-archive-choice button').nth(i).click()
                    if images.nth(i).is_visible():
                        images.nth(i).scroll_into_view_if_needed(timeout=4000)
                if row['checks']['independent_controls']:
                    gallery.locator('.fvx-archive-choice button').nth(0).click()
                page.wait_for_timeout(700)
                row['checks']['real_image_delivery']=images.count()==3 and images.evaluate_all('(els)=>els.every(i=>i.complete && i.naturalWidth>0)')
                if row['checks']['independent_controls'] and row['checks']['three_figures']:
                    b=gallery.locator('.fvx-archive-choice button')
                    b.nth(1).click();row['checks']['selector_selects_second']=gallery.locator('[data-fvx-chrono-photo="1"]').is_visible()
                    sliders=page.locator('[data-fvx-chronology] input[type="range"]')
                    if sliders.count(): sliders.first.fill('14')
                    row['checks']['photo_independent_of_timeline']=gallery.locator('[data-fvx-chrono-photo="1"]').is_visible()
                    b.nth(1).focus();page.keyboard.press('ArrowRight')
                    row['checks']['keyboard_arrows']=b.nth(2).get_attribute('aria-pressed')=='true' and b.nth(2).evaluate('(x)=>document.activeElement===x')
                    page.keyboard.press('Home')
                    row['checks']['keyboard_home']=b.nth(0).get_attribute('aria-pressed')=='true'
                    row['checks']['tap_targets_44px']=all(z>=44 for z in b.evaluate_all('(els)=>els.map(e=>e.getBoundingClientRect().height)'))
                else:
                    for check in ('selector_selects_second','photo_independent_of_timeline','keyboard_arrows','keyboard_home','tap_targets_44px'):row['checks'][check]=False
                row['lab_vitals']=page.evaluate('window.__fvCWV || null')
                filename=f'installed-page-{width}.png'
                page.screenshot(path=str(output/filename),full_page=True,animations='disabled')
                row['screenshot_sha256']=hashlib.sha256((output/filename).read_bytes()).hexdigest()
                if width==390:
                    if axe and axe.is_file():
                        try:
                            page.add_script_tag(path=str(axe))
                            audit=page.evaluate('async () => {const a=await axe.run(document, {runOnly:{type:"tag", values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}});return {violations:a.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),incomplete:a.incomplete.length,passes:a.passes.length}}')
                            report['axe']={'status':'PASS' if not audit['violations'] and not audit['incomplete'] else 'REVIEW','result':audit}
                        except Exception as e:report['axe']={'status':'BLOCKED_AXE_ERROR','error_type':type(e).__name__}
                    else: report['axe']={'status':'BLOCKED_MISSING_AXE','note':'Provide licensed local free axe-core distribution with --axe; do not count as pass.'}
            except PlaywrightError as e:
                row['errors'].append(type(e).__name__)
                row['checks']['navigation_and_execution']=False
            row['network_failures']=sorted(set(network_fail))[:12]
            report['widths'][str(width)]=row
            context.close()
        context=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
        p=context.new_page()
        try:
            response=p.goto(url,wait_until='domcontentloaded',timeout=timeout) if fixture is None else None
            if fixture is not None: p.set_content(fixture,wait_until='domcontentloaded')
            figures=p.locator('[data-fvx-chrono-gallery] figure')
            report['no_js']={'http_ok':bool((response and response.ok) or fixture is not None),'three_figures_visible':figures.count()==3 and all(figures.nth(i).is_visible() for i in range(3)),
                             'three_nasa_links_visible':p.locator('[data-fvx-chrono-gallery] figcaption a[href*="nasa.gov/"]:visible').count()==3}
        except PlaywrightError as e:report['no_js']={'blocked':type(e).__name__}
        context.close()
        context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        p=context.new_page()
        try:
            p.goto(url,wait_until='domcontentloaded',timeout=timeout) if fixture is None else p.set_content(fixture,wait_until='domcontentloaded')
            b=p.locator('[data-fvx-chrono-gallery] .fvx-archive-choice button')
            if b.count()==3:
                b.nth(1).tap()
                report['touch']={'touch_selects_second':p.locator('[data-fvx-chrono-gallery] [data-fvx-chrono-photo="1"]').is_visible()}
            else: report['touch']={'touch_selects_second':False}
        except PlaywrightError as e: report['touch']={'blocked':type(e).__name__}
        context.close();browser.close()
    allchecks=[v for row in report['widths'].values() for v in row['checks'].values()]
    allchecks+= [v for v in report['no_js'].values() if isinstance(v,bool)] + [v for v in report['touch'].values() if isinstance(v,bool)]
    report['checks_total']=len(allchecks)
    report['checks_passed']=sum(allchecks)
    report['result']='PASS_LAB_ONLY' if fixture is None and allchecks and all(allchecks) and report['axe']['status']=='PASS' else 'HOLD'
    if fixture: report['fixture_sha256']=hashlib.sha256(fixture.encode()).hexdigest()
    path=output/'acceptance.json'
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'result':report['result'],'checks_passed':report['checks_passed'],'checks_total':report['checks_total'],'axe':report['axe']['status'],'report':str(path)},indent=2))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--url',required=True)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--axe',type=Path)
    ap.add_argument('--fixture-html',type=Path,help='OFFLINE ONLY: run fixture semantics, never count as WordPress acceptance')
    ap.add_argument('--timeout',type=int,default=30000)
    args=ap.parse_args()
    try: report=witness(args.url,args.out,args.axe,args.timeout,args.fixture_html)
    except Exception as e: print(type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(3)
    sys.exit(0 if report['result']=='PASS_LAB_ONLY' else 2)
