#!/usr/bin/env python3
"""Real Chromium against exact, hash-checked PR215 source inside generated PHP output.

This simulates PHP Ajax output in an in-memory document with equivalent META CSP.
Not an HTTP/Cookie/WordPress certification. Does not fabricate LCP or axe results.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SEALED = HERE.parent
BRIDGE = SEALED.parent
OUT = HERE / 'screenshots'
OUT.mkdir(exist_ok=True, parents=True)
REPORT = HERE / 'BROWSER_EXACT_RESULTS.json'
sys.path.insert(0, str(SEALED))
from build_sealed import build, ROOT, PIN


def get_fixture():
    import zipfile
    zip_path = HERE / 'tmp-checked-source.zip'
    build(zip_path)
    with zipfile.ZipFile(zip_path) as z:
        data = z.read(ROOT + '/fv-ex2-apollo-sealed.php')
    plugin = HERE / 'tmp-private.php'
    plugin.write_bytes(data)
    p = subprocess.run(['php', str(HERE / 'mock_wordpress.php'), str(plugin), 'staging', 'page'],
                       capture_output=True, timeout=30)
    assert p.returncode == 0 and not p.stderr, p.stderr
    html = p.stdout.decode('utf-8')
    nonce = re.search(r'<style nonce="([^"]+)"', html).group(1)
    # A META CSP covers script/style execution here, but NOT HTTP cookies,
    # iframe frame-ancestors or download response headers.
    csp = ("default-src 'none'; script-src 'nonce-" + nonce + "'; "
           "style-src 'nonce-" + nonce + "'; img-src 'none'; font-src 'none'; "
           "connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'")
    meta = '<meta http-equiv="Content-Security-Policy" content="' + csp + '">'
    html = html.replace('<head>', '<head>' + meta, 1)
    return html, hashlib.sha256(data).hexdigest()


INIT = r"""(() => {
    window.__fv_cwv = {lcp: null, cls: 0, shifts: 0, fcp: null};
    try { new PerformanceObserver(l=>{for(let e of l.getEntries())window.__fv_cwv.lcp=e.startTime})
      .observe({type:'largest-contentful-paint',buffered:true}); } catch(e) { }
    try { new PerformanceObserver(l=>{for(let e of l.getEntries())if(!e.hadRecentInput){window.__fv_cwv.cls+=e.value;window.__fv_cwv.shifts++}})
      .observe({type:'layout-shift',buffered:true}); } catch(e) { }
    try { new PerformanceObserver(l=>{for(let e of l.getEntries())if(e.name==='first-contentful-paint')window.__fv_cwv.fcp=e.startTime})
      .observe({type:'paint',buffered:true}); } catch(e) { }
})();"""


def run(*, require_axe=False):
    fixture, artifact_sha = get_fixture()
    axe_file = os.environ.get('FV_VERIFIED_AXE_BUNDLE', '')
    axe_hash = os.environ.get('FV_VERIFIED_AXE_SHA256', '')
    actual_axe = None
    if axe_file and axe_hash:
        p = Path(axe_file)
        if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == axe_hash:
            actual_axe = p.read_text(encoding='utf-8')
    if require_axe and actual_axe is None:
        raise RuntimeError('RELEASE HOLD: supply FV_VERIFIED_AXE_BUNDLE and exact FV_VERIFIED_AXE_SHA256; axe did not run')
    report = {
        'exact_source_head': PIN,
        'source_blob_pins': 12,
        'generated_php_sha256': artifact_sha,
        'test_environment': 'system Chromium Playwright; PHP CLI WordPress authorization stub; in-memory page.set_content',
        'scope_warning': 'NOT actual HTTP WordPress, cookie behavior, Safari, screen-reader, or field Core Web Vitals',
        'meta_csp_approximation': True,
        'axe_status': 'VERIFIED_BUNDLE_AVAILABLE' if actual_axe else 'NOT_RUN_NO_PINNED_AXE_BUNDLE',
        'axe_violations': None,
        'measurements': [],
        'screenshots': [],
        'no_js': False,
        'touch': False,
        'zoom_200_percent': None,
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in (320, 360, 390, 768, 1024, 1440, 1920):
            ctx = browser.new_context(viewport={'width':width,'height':930},reduced_motion='reduce' if width==320 else 'no-preference', device_scale_factor=1)
            page = ctx.new_page();page.add_init_script(INIT)
            errors, blocked = [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: blocked.append(r.url))
            page.set_content(fixture, wait_until='load')
            page.evaluate(INIT)  # register buffered paint/layout-shift observers in this same in-memory document
            assert page.locator('.fv-ex2-apollo').count() == 1
            assert page.locator('h1').count() == 1
            assert page.locator('main#fv-ex2-apollo-document').count() == 1
            page.keyboard.press('Tab')
            assert page.evaluate('document.activeElement.getAttribute("href")') == '#fv-ex2-apollo-document', (width, 'skip not first tabstop')
            skip = page.locator('.fv-ex2-apollo__skip').evaluate(
                '(n)=>({transform:getComputedStyle(n).transform,y:n.getBoundingClientRect().top})')
            assert skip['transform'] == 'none' and skip['y'] >= 0, (width, 'skip link not actually visible', skip)
            if width in (390, 1440):
                dest = OUT / f'exact-skip-focused-{width}.png'
                page.screenshot(path=str(dest), animations='disabled', timeout=15000)
                report['screenshots'].append({'name':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
            page.keyboard.press('Enter')
            assert page.evaluate('document.activeElement.id') == 'fv-ex2-apollo-document', (width, 'skip did not focus main')
            assert page.locator('section#atlas').count() == 1
            assert page.locator('#source-concordance [data-concordance-record]').count() == 6
            assert page.locator('#source-concordance .fv-ex2-concordance__card details > summary').count() == 6
            assert page.locator('#source-concordance .fv-ex2-concordance__witness').count() == 12
            assert page.locator('#source-concordance .fv-ex2-concordance__card a[href^="#source-"]').count() == 6
            assert page.locator('#source-concordance a[href^="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"]').count() == 6
            assert page.locator('#source-concordance .fv-ex2-concordance__witness--photo').count() == 6
            page.locator('#source-concordance .fv-ex2-concordance__card details > summary').first.click()
            assert page.locator('#source-concordance .fv-ex2-concordance__card details').first.evaluate('(n)=>n.open')
            # Interactive source routes meet a 44px touch-height budget everywhere.
            sizes = page.locator('#source-concordance .fv-ex2-concordance__card a, #source-concordance .fv-ex2-concordance__card summary').evaluate_all(
                '(nodes)=>nodes.map(n=>({height:n.getBoundingClientRect().height,width:n.getBoundingClientRect().width}))')
            assert len(sizes) == 30 and all(x['height'] >= 43.9 and x['width'] >= 24 for x in sizes), (width,sizes)
            page.locator('#source-concordance .fv-ex2-concordance__card summary').first.focus()
            page.keyboard.press('Enter')
            assert not page.locator('#source-concordance .fv-ex2-concordance__card details').first.evaluate('(n)=>n.open')
            page.locator('#source-concordance .fv-ex2-concordance__card summary').first.click()
            assert page.locator('[data-ex2-trail-card]').count() == 6
            assert page.locator('[data-ex2-response-item]').count() == 6
            assert page.locator('[data-ex2-atlas-item]').count() == 6
            # CSS-only temporal lens is a real, meaningful no-JavaScript interaction.
            # Each filter narrows to NASA-dated source context, not inferred event time.
            lens = page.locator('#source-concordance')
            assert lens.locator('input[type="radio"]').count() == 4
            assert lens.locator('[data-concordance-record]:visible').count() == 6
            for era, expected in [('1966',1),('1967',3),('2017',2)]:
                lens.locator(f'#fv-ex2-lens-{era}').check()
                assert lens.locator('[data-concordance-record]:visible').count() == expected, (width,era)
                assert lens.locator(f'#fv-ex2-lens-{era}').is_checked()
            lens.locator('#fv-ex2-lens-all').check()
            assert lens.locator('[data-concordance-record]:visible').count() == 6
            assert lens.locator('a[download="apollo-source-context.json"]').count() == 1
            # True native keyboard radio-group behavior, not merely Playwright .check().
            lens.locator('#fv-ex2-lens-all').focus()
            page.keyboard.press('ArrowRight')
            assert lens.locator('#fv-ex2-lens-1966').is_checked(),(width,'native keyboard filter failed')
            assert lens.locator('[data-concordance-record]:visible').count()==1
            page.keyboard.press('ArrowRight')
            assert lens.locator('#fv-ex2-lens-1967').is_checked()
            assert lens.locator('[data-concordance-record]:visible').count()==3
            lens.locator('#fv-ex2-lens-all').check()
            if width in (390, 1440):
                lens.locator('#fv-ex2-lens-1967').check()
                dest = OUT / f'exact-era-lens-1967-{width}.png'
                lens.screenshot(path=str(dest), animations='disabled', timeout=15000)
                report['screenshots'].append({'name':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
                lens.locator('#fv-ex2-lens-all').check()
            assert page.locator('[data-ex2-stage]').count() == 6
            # A source drawer route must remain discoverable when JS is absent;
            # the URL fragment targets the native details wrapper, not hidden copy.
            assert page.locator('#source-concordance .fv-ex2-concordance__card a[href="#source-03"]').count() == 1
            assert page.locator('a[href*="fv_ex2_apollo_sealed_download"]').count() == 6
            assert page.locator('[data-ex2-trail-controls]').is_visible(), (width,'JS blocked by CSP')
            assert page.locator('[data-ex2-response-tools]').is_visible(), (width,'response JS blocked')
            assert page.locator('a[href^="https://www.nasa.gov"]').count() >= 12
            dims = page.evaluate('''() => ({viewport:innerWidth, doc:document.documentElement.scrollWidth,
                body:document.body.scrollWidth, height:document.documentElement.scrollHeight,
                title:document.title})''')
            assert dims['doc'] <= width+1,(width,dims,'root overflow')
            # Meaningful source selection and route recovery on tested exact render.
            sel=page.locator('[data-ex2-trail-select]');sel.select_option('05')
            assert page.locator('[data-ex2-trail-card]:visible').count() == 1
            page.locator('#trail-05 summary').click()
            assert page.locator('#trail-05 details').evaluate('(n)=>n.open')
            page.locator('[data-ex2-trail-reset]').click()
            assert page.locator('[data-ex2-trail-card]:visible').count() == 6
            response=page.locator('[data-ex2-response-filter]')
            response.select_option('hardware')
            assert page.locator('[data-ex2-response-item]:visible').count() == 3
            page.locator('[data-ex2-response-reset]').click()
            assert page.locator('[data-ex2-response-item]:visible').count() == 6
            sel.select_option('06');page.evaluate("location.hash='#trail-04'")
            page.wait_for_timeout(50)
            assert page.locator('#trail-04').is_visible()
            assert page.evaluate('document.activeElement.id')=='trail-04'
            page.evaluate("location.hash='#source-03'")
            page.wait_for_timeout(50)
            assert page.locator('#source-03').evaluate('(n)=>n.open')
            if width in (390,1440):
                for title,selector in [('hero','.fv-ex2-apollo .ex2-hero'),
                                       ('trails','.fv-ex2-apollo #documentary-trails'),
                                       ('research','.fv-ex2-apollo #research-desk'),
                                       ('atlas','.fv-ex2-apollo #atlas'),
                                       ('concordance','.fv-ex2-apollo #source-concordance')]:
                    dest=OUT / f'exact-{title}-{width}.png'
                    page.locator(selector).screenshot(path=str(dest),animations='disabled', timeout=15000)
                    report['screenshots'].append({'name':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
            if actual_axe and width in (390,1440):
                page.add_script_tag(content=actual_axe)
                a=page.evaluate("""async()=>{let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact, nodes:v.nodes.length})),passes:r.passes.length,incomplete:r.incomplete.length}}""")
                report.setdefault('axe_by_width',{})[str(width)] = a
                report['axe_violations'] = (report['axe_violations'] or 0)+sum(x['nodes'] for x in a['violations'])
                if require_axe and a['violations']:
                    raise AssertionError(('axe-core WCAG A/AA violations',width,a['violations']))
            cdp=ctx.new_cdp_session(page);cdp.send('Performance.enable')
            perf=cdp.send('Performance.getMetrics')['metrics']
            simple={x['name']:x['value'] for x in perf}
            page.wait_for_timeout(160)
            cwv = page.evaluate('window.__fv_cwv') or {'lcp':None,'fcp':None,'cls':None}
            report['measurements'].append({'width':width,'document_width':dims['doc'],'page_height':dims['height'],
                 'source_stage_count':6,'evidence_atlas_count':6,
                 'trail_filter_and_anchor':True,'response_filter':True,'keyboard_focus_after_hash':True,
                 'axe_checked':actual_axe is not None and width in (390,1440),
                 'page_errors':errors,'network_requests':blocked,'lab_lcp_ms':cwv['lcp'],
                 'lab_fcp_ms':cwv['fcp'],'lab_cls':cwv['cls'],
                 'chromium_js_heap_bytes':round(simple.get('JSHeapUsedSize',0)),
                 'csp_meta_no_external_resources': True})
            assert not errors and not blocked,(width,errors,blocked)
            ctx.close()
        # No-JS preservation on narrow screen.
        ctx=browser.new_context(viewport={'width':390,'height':850},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        assert page.locator('[data-ex2-trail-card]:visible').count() == 6
        assert page.locator('[data-ex2-response-item]:visible').count() == 6
        assert page.locator('[data-ex2-atlas-item]:visible').count() == 6
        assert page.locator('#source-concordance [data-concordance-record]').count() == 6
        assert page.locator('#source-concordance .fv-ex2-concordance__witness').count() == 12
        page.keyboard.press('Tab')
        assert page.evaluate('document.activeElement.textContent.trim()') == 'Skip to Apollo evidence'
        page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.id') == 'fv-ex2-apollo-document'
        # Source-year filter must operate under a genuinely disabled JS context.
        nojs_lens=page.locator('#source-concordance')
        nojs_lens.locator('#fv-ex2-lens-2017').check()
        assert nojs_lens.locator('[data-concordance-record]:visible').count()==2
        nojs_lens.locator('#fv-ex2-lens-all').check()
        assert nojs_lens.locator('[data-concordance-record]:visible').count()==6
        page.locator('#source-concordance .fv-ex2-concordance__card summary').first.click()
        assert page.locator('#source-concordance .fv-ex2-concordance__card details').first.evaluate('(n)=>n.open')
        assert not page.locator('[data-ex2-trail-controls]').is_visible()
        page.locator('#trail-02 summary').click()
        assert page.locator('#trail-02 details').evaluate('(n)=>n.open')
        report['no_js']=True
        ctx.close()
        # Smartphone touch parity.
        ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        page.locator('[data-ex2-trail-select]').select_option('04')
        assert page.locator('[data-ex2-trail-card]:visible').count() == 1
        page.locator('#trail-04 summary').tap()
        assert page.locator('#trail-04 details').evaluate('(n)=>n.open')
        page.locator('#fv-ex2-lens-1966').tap()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==1
        page.locator('#fv-ex2-lens-all').tap()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
        page.locator('#source-concordance .fv-ex2-concordance__card summary').first.tap()
        assert page.locator('#source-concordance .fv-ex2-concordance__card details').first.evaluate('(n)=>n.open')
        report['touch']=True
        ctx.close()
        # Zoom reflow is a synthetic viewport approximation, not an actual browser UI zoom.
        ctx=browser.new_context(viewport={'width':640,'height':850})
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        page.evaluate("document.documentElement.style.zoom='200%'")
        page.wait_for_timeout(90)
        doc=page.evaluate('document.documentElement.scrollWidth')
        report['zoom_200_percent']={'physical_css_viewport':640,'document_width':doc,'no_root_overflow':doc<=641}
        assert doc<=641,report['zoom_200_percent']
        ctx.close()
        browser.close()
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('BROWSER_EXACT_PASS',len(report['measurements']),'widths; source pins=12; no JS; touch; zoom; AXE=',report['axe_status'])
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Apollo exact-source browser + optional strict axe-core gate')
    parser.add_argument('--require-axe', action='store_true', help='FAIL CLOSED when verified axe bundle missing or WCAG violations observed')
    run(require_axe=parser.parse_args().require_axe)
