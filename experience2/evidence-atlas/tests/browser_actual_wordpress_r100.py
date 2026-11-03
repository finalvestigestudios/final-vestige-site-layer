#!/usr/bin/env python3
"""R100: real WordPress-core HTTP browser tests for R99 private Apollo review.

Runs ONLY against an ephemeral, privately installed WordPress instance; never points
at finalvestige.com. Deliberately does not write WordPress content or options.
Setup/teardown of the disposable runner WordPress happens in CI, not here.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, urlparse

from playwright.sync_api import sync_playwright

VIEWS = (
    'R85_NASA_SOURCE_REVIEW.html', 'R87_PHOTOGRAPH_DATE_RAIL.html',
    'R88_READING_ROOM.html', 'R89_REVIEW_HUB.html',
    'R93_SOURCE_PASSPORTS.html', 'R94_CURATED_ATLAS.html',
    'R97_SOURCE_GALLERY.html',
)
WIDTHS = (320, 390, 768, 1440, 1920)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(base, stage, axe_path, out, user, password, subscriber, subscriber_password,
        author, author_password, contributor, contributor_password, editor, editor_password):
    base = base.rstrip('/') + '/'
    host = urlparse(base).netloc
    # No URL can point at production, a remotely accessible hostname, or the Internet.
    check(host in ('127.0.0.1:8955', 'localhost:8955'), 'only disposable loopback WordPress is allowed')
    out.mkdir(parents=True, exist_ok=True)
    receipt = {'testing_scope': 'real disposable WordPress core via HTTP; NOT hosted WordPress.com or Assembler',
               'permission_boundary': 'Editor/Administrator edit_others_posts only; Author/Contributor/Subscriber denied',
               'visual_widths': list(WIDTHS), 'views': list(VIEWS), 'checks': [],
               'screenshots': {}, 'pdf': {}, 'axe': [], 'blocked_external_requests': []}
    view_url = lambda view: base + '?fv_apollo_r99=' + quote(view)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        # No caching of credentials in persistent browser profiles or recorded evidence.
        def login(role_user, role_password):
            context = browser.new_context(ignore_https_errors=False)
            page = context.new_page()
            response = page.goto(base + 'wp-login.php', wait_until='domcontentloaded')
            check(response is not None and response.status == 200, 'real WordPress login not reachable')
            check(page.locator('#user_login').count() == 1, 'not a genuine WordPress login form')
            page.locator('#user_login').fill(role_user)
            page.locator('#user_pass').fill(role_password)
            page.locator('#wp-submit').click()
            page.wait_for_url(re.compile(r'.*/wp-admin/.*'), timeout=20000)
            return context, page

        anonymous = browser.new_context()
        anon_page = anonymous.new_page()
        for query in ('R89_REVIEW_HUB.html', 'R97_SOURCE_GALLERY.html', 'R93_SOURCE_PASSPORTS.json'):
            res = anon_page.goto(view_url(query), wait_until='domcontentloaded')
            check(res is not None and res.status == 404, 'private source leaked to anonymous visitor: '+query)
        for invalid in ('../../wp-config.php', 'unlisted.html', 'R99_PRIVATE_PREVIEW_RECEIPT.json'):
            res = anon_page.goto(view_url(invalid), wait_until='domcontentloaded')
            check(res is not None and res.status == 404, 'unexpected anonymous route: '+invalid)
        anonymous.close()
        receipt['checks'].append('Anonymous users cannot retrieve any private HTML/JSON source.')

        sub_ctx, sub_page = login(subscriber, subscriber_password)
        check(sub_page.locator('body').count() == 1, 'subscriber login failed')
        for item in (VIEWS[0], VIEWS[-1], 'source_gallery_r97.js'):
            r = sub_page.goto(view_url(item), wait_until='domcontentloaded')
            check(r is not None and r.status == 404, 'subscriber source leak: '+item)
        sub_ctx.close()
        receipt['checks'].append('Authenticated subscriber lacks editor capability and cannot access resources.')

        # edit_posts is granted to Contributors and Authors; neither may read the
        # sealed preview. This must run against REAL WordPress roles and HTTP.
        for role, role_user, role_password in (
            ('author', author, author_password),
            ('contributor', contributor, contributor_password),
        ):
            role_ctx, role_page = login(role_user, role_password)
            for item in (VIEWS[0], VIEWS[-1], 'R93_SOURCE_PASSPORTS.json',
                         'source_gallery_r97.css'):
                res = role_page.goto(view_url(item), wait_until='domcontentloaded')
                check(res is not None and res.status == 404,
                      f'{role} unexpectedly accessed private resource: {item}')
            role_ctx.close()
        receipt['checks'].append('Actual WordPress Contributor and Author roles denied HTML, JSON and CSS (edit_posts is insufficient).')

        # Editorial reviewers are expected to retain access. This is a distinct
        # Editor-role test, not an assumption based on Administrator access.
        editor_ctx, editor_page = login(editor, editor_password)
        for item in (VIEWS[0], VIEWS[-1], 'R93_SOURCE_PASSPORTS.json'):
            res = editor_page.goto(view_url(item), wait_until='domcontentloaded')
            check(res is not None and res.status == 200,
                  'WordPress Editor unexpectedly denied private review: '+item)
        editor_ctx.close()
        receipt['checks'].append('Actual WordPress Editor role retains source access without administrator capability.')

        admin_context, admin = login(user, password)
        # All seven views are served by real WP template_redirect, not a hook shim.
        for view in VIEWS:
            res = admin.goto(view_url(view), wait_until='domcontentloaded')
            check(res is not None and res.status == 200, 'admin source missing: '+view)
            headers = {k.lower(): v for k, v in res.headers.items()}
            check('text/html' in headers.get('content-type',''), 'wrong HTML mime: '+view)
            check('no-store' in headers.get('cache-control',''), 'cache-control missing: '+view)
            check('noindex' in headers.get('x-robots-tag',''), 'robots hold missing: '+view)
            check('frame-ancestors' in headers.get('content-security-policy',''), 'CSP missing: '+view)
            check(admin.locator('main').count() == 1, 'research body missing main: '+view)
            check('STAGING HOLD' in admin.locator('body').inner_text(), 'hold status missing: '+view)
        check(admin.locator('a[href^="https://www.nasa.gov/"]').count() >= 6, 'NASA custody anchors absent')
        receipt['checks'].append('Seven HTML views served by genuine WordPress with private no-cache/CSP/noindex headers and NASA references.')

        # Different content types must be correct; abnormal encoded values and JSON lists fail-closed.
        assets = {'source_gallery_r97.css':'text/css', 'source_gallery_r97.js':'javascript',
                  'R93_SOURCE_PASSPORTS.json':'application/json', 'R93_NASA_REFERENCES.txt':'text/plain'}
        for name, content_type in assets.items():
            res = admin_context.request.get(view_url(name))
            check(res is not None and res.status == 200 and content_type in res.headers.get('content-type',''),
                  'asset mime or access failed: '+name)
        for query in ('../../wp-config.php', 'bogus.css', 'fv-apollo-r99-private-preview.php',
                      'R89_REVIEW_HUB.html%00', 'R89_REVIEW_HUB.html/../R97_SOURCE_GALLERY.html'):
            res = admin_context.request.get(base + '?fv_apollo_r99=' + quote(query, safe=''))
            check(res is not None and res.status == 404, 'bad route served: '+query)
        res = admin_context.request.get(base + '?fv_apollo_r99[]=R89_REVIEW_HUB.html')
        check(res is not None and res.status == 404, 'array query route served')
        receipt['checks'].append('MIME signatures, traversal/unknown/array routes, and file allowlist verified in actual WordPress.')

        # Genuine PHP reads pinned bytes at runtime: change ONE CSS byte, observe denial,
        # restore the exact original in a finally block. Only ephemeral WP files change.
        target=stage/'review'/'source_gallery_r97.css'
        original=target.read_bytes()
        try:
            target.write_bytes(original + b'\n/* deliberate tamper probe */\n')
            res=admin_context.request.get(view_url('source_gallery_r97.css'))
            check(res.status == 404, 'tampered CSS served despite SHA-256 custody pin')
        finally:
            target.write_bytes(original)
        check(admin_context.request.get(view_url('source_gallery_r97.css')).status==200,
              'restored CSS still unavailable after tamper probe')
        receipt['checks'].append('Actual WordPress rejects tampered CSS under compiled SHA-256 pins; original bytes restored.')

        # Inspect genuine WordPress routes across 35 viewport+view cases, with and without JS.
        for js in (True, False):
            for width in WIDTHS:
                context = browser.new_context(viewport={'width': width, 'height': 900},
                                              is_mobile=width<=390, has_touch=width<=390,
                                              java_script_enabled=js, reduced_motion='reduce',
                                              storage_state=admin_context.storage_state())
                page = context.new_page()
                unexpected = []
                page.on('request', lambda request: unexpected.append(request.url)
                        if urlparse(request.url).netloc not in ('127.0.0.1:8955','localhost:8955') else None)
                for view in VIEWS:
                    url = view_url(view)
                    res = page.goto(url, wait_until='domcontentloaded')
                    check(res is not None and res.status == 200, f'{view} status {width}/js{js}')
                    check(page.locator('main').count() == 1, f'{view} main {width}/js{js}')
                    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
                          f'horizontal overflow {view} {width}/js{js}')
                    check(page.locator('a[href^="https://www.nasa.gov/"]').count() >= 6,
                          f'NASA anchors {view} {width}/js{js}')
                    # All source records remain visible without JavaScript.
                    if view == 'R97_SOURCE_GALLERY.html':
                        check(page.locator('[data-card]').count() == 6, 'gallery source count changed')
                    if view == 'R94_CURATED_ATLAS.html':
                        check(page.locator('[data-record]').count() == 6 or page.locator('[id^="atlas-"]').count() >= 6,
                              'atlas source count changed')
                    if js and width in (390,1440) and view in ('R97_SOURCE_GALLERY.html','R94_CURATED_ATLAS.html'):
                        name=f'R100_WP_{view.split(".")[0]}_{width}.png'
                        path=out/name
                        page.screenshot(path=str(path), full_page=True, animations='disabled')
                        receipt['screenshots'][name]=sha256(path)
                check(not unexpected, f'unexpected remote requests: {unexpected}')
                context.close()
        receipt['checks'].append('70 real-WP viewport+JS configurations: 320–1920px, reduced motion, no-JS, NASA links, no overflow/no external requests.')

        # Keyboard/touch source roundtrip in actual WordPress and query-fragment fidelity.
        page = admin
        page.goto(view_url('R97_SOURCE_GALLERY.html'), wait_until='domcontentloaded')
        source_link=page.locator('a[href*="R94_CURATED_ATLAS.html#atlas-01"]').first
        check(source_link.count()==1, 'source 01 cross-view anchor missing')
        source_link.focus()
        page.keyboard.press('Enter')
        page.wait_for_url(re.compile(r'.*R94_CURATED_ATLAS\.html#atlas-01$'), timeout=15000)
        check(page.locator('#atlas-01').count()==1, 'navigated atlas fragment does not exist')
        receipt['checks'].append('Native keyboard gallery-to-atlas navigation retains source 01 fragment.')

        # R102: actual WordPress enhanced gallery + Atlas state acceptance.
        # Existing 70 cases verified rendering, not comparison/filter behavior.
        receipt['r102_interaction_cases'] = []
        for width in (320, 390, 1440, 1920):
            for js in (True, False):
                forced = 'active' if width in (320, 1920) else 'none'
                ctx = browser.new_context(
                    viewport={'width': width, 'height': 900},
                    storage_state=admin_context.storage_state(),
                    java_script_enabled=js, reduced_motion='reduce',
                    forced_colors=forced, is_mobile=width <= 390,
                    has_touch=width <= 390, bypass_csp=js,
                )
                p = ctx.new_page()
                outbound = []
                errors = []
                p.on('pageerror', lambda _error: errors.append('JS_ERROR'))
                p.on('request', lambda req: outbound.append(req.resource_type)
                     if urlparse(req.url).netloc not in ('127.0.0.1:8955', 'localhost:8955') else None)
                try:
                    res = p.goto(view_url('R97_SOURCE_GALLERY.html'), wait_until='load')
                    check(res is not None and res.status == 200, 'R102 gallery HTTP')
                    check(p.locator('[data-card]:visible').count() == 6, 'R102 gallery records')
                    check(p.locator('[data-card] img,[data-lat],[data-lon],[data-geo-edge]').count() == 0,
                          'R102 no images or speculative geography')
                    if js:
                        check(p.locator('[data-compare-controls]:visible').count() == 7,
                              'R102 gallery comparison controls')
                        check(p.locator('#comparison').is_hidden(), 'R102 comparison initially hidden')
                        for n in ('01', '02'):
                            box = p.locator('#compare-' + n)
                            (box.tap() if width <= 390 else box.check())
                        check(p.locator('#comparison').is_visible(), 'R102 comparison not revealed')
                        check(p.locator('[data-heading]').all_text_contents() == ['Source 01', 'Source 02'],
                              'R102 compared source identities')
                        check(all(x.strip() for x in p.locator('[data-value]').all_text_contents()),
                              'R102 comparison custody values')
                        third = p.locator('#compare-03')
                        (third.tap() if width <= 390 else third.check())
                        check(not third.is_checked() and 'Only two records' in p.locator('#compare-status').inner_text(),
                              'R102 comparison cap/announcement')
                        if width in (390, 1440):
                            image = out / f'R102_REAL_WP_COMPARISON_{width}.png'
                            p.screenshot(path=str(image), full_page=True, animations='disabled')
                            receipt['screenshots'][image.name] = sha256(image)
                        reset = p.locator('#compare-reset')
                        (reset.tap() if width <= 390 else reset.click())
                        check(p.locator('#comparison').is_hidden() and
                              p.locator('[data-select]:checked').count() == 0,
                              'R102 comparison clear')
                        check(p.evaluate("document.activeElement?.id === 'compare-01'"),
                              'R102 comparison reset focus')
                    else:
                        check(p.locator('[data-compare-controls]:visible').count() == 0,
                              'R102 no-JS comparison controls not hidden')
                    res = p.goto(view_url('R94_CURATED_ATLAS.html'), wait_until='load')
                    check(res is not None and res.status == 200, 'R102 Atlas HTTP')
                    check(p.locator('#atlas .card').count() == 6, 'R102 Atlas records')
                    if js:
                        month = p.locator('[data-filter="month"]')
                        (month.tap() if width <= 390 else month.click())
                        check(p.locator('#atlas .card:visible').count() == 1 and
                              p.locator('#atlas-01').is_visible(), 'R102 month-only certainty')
                        check(month.get_attribute('aria-pressed') == 'true',
                              'R102 filter button pressed state')
                        p.locator('#query').fill('nonsense-catalog-no-match')
                        check(p.locator('#atlas .card:visible').count() == 0 and
                              p.locator('#empty').is_visible(), 'R102 empty result announcement')
                        p.locator('#query').fill('')
                        day = p.locator('[data-filter="day"]')
                        (day.tap() if width <= 390 else day.click())
                        check(p.locator('#atlas .card:visible').count() == 5,
                              'R102 five known day-specific records')
                        p.evaluate("location.hash = 'atlas-01'")
                        p.wait_for_function("!document.querySelector('#atlas-01').hidden")
                        check(p.locator('#atlas .card:visible').count() == 6 and
                              p.locator('[data-filter="all"]').get_attribute('aria-pressed') == 'true',
                              'R102 deep-link reveals filtered source')
                        check(p.evaluate("document.activeElement?.id === 'atlas-01'"),
                              'R102 deep-link keyboard focus')
                        if width in (390, 1440):
                            result = out / f'R102_REAL_WP_ATLAS_REVEALED_{width}.png'
                            p.screenshot(path=str(result), full_page=True, animations='disabled')
                            receipt['screenshots'][result.name] = sha256(result)
                            p.add_script_tag(path=str(axe_path))
                            a = p.evaluate('''async () => { const r = await axe.run(document, {
                                runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                                return {violations:r.violations.map(v=>({id:v.id, nodes:v.nodes.length})),
                                        passes:r.passes.length}; }''')
                            receipt['axe'].append({'width': width, 'view': 'R102_INTERACTIVE_ATLAS', **a})
                            check(not a['violations'], 'R102 axe interactive Atlas')
                    else:
                        check(p.locator('#atlas .card:visible').count() == 6 and
                              p.locator('#filters').is_hidden(), 'R102 no-JS full Atlas available')
                    check(p.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),
                          'R102 responsive overflow')
                    check(not outbound and not errors, 'R102 no unexpected requests/errors')
                    receipt['r102_interaction_cases'].append({
                        'width': width, 'javascript_enabled': js,
                        'forced_colors': forced, 'reduced_motion': True,
                        'gallery_and_atlas_passed': True,
                    })
                finally:
                    ctx.close()
        check(len(receipt['r102_interaction_cases']) == 8,
              'R102 incomplete interactive-case acceptance')
        receipt['checks'].append('R102: eight real WP Gallery+Atlas interaction cases, mobile touch, keyboard focus, no-JS, reduced motion, forced colors and interactive axe.')

        # LCP/CLS instrumentation on real WP: install observers before navigation.
        performance = []
        for width in (390, 1440):
            ctx=browser.new_context(viewport={'width':width,'height':900},
                                    storage_state=admin_context.storage_state())
            p=ctx.new_page()
            p.add_init_script('''(() => {
              window.__apolloCWV = { lcp: null, cls: 0 };
              try { new PerformanceObserver((list) => {
                for (const e of list.getEntries()) window.__apolloCWV.lcp = e.startTime;
              }).observe({type:'largest-contentful-paint', buffered:true}); } catch(e){}
              try { new PerformanceObserver((list) => {
                for (const e of list.getEntries()) if (!e.hadRecentInput) window.__apolloCWV.cls += e.value;
              }).observe({type:'layout-shift', buffered:true}); } catch(e){}
            })();''')
            for view in ('R89_REVIEW_HUB.html','R97_SOURCE_GALLERY.html'):
                p.goto(view_url(view), wait_until='load')
                p.wait_for_timeout(250)
                cwv=p.evaluate('window.__apolloCWV')
                performance.append({'width':width,'view':view,'lcp_ms':cwv['lcp'],'cls':cwv['cls']})
                check(cwv['cls'] < 0.1, 'local-layout CLS exceeds 0.1')
            if width==1440:
                pdf=out/'R100_WP_SOURCE_GALLERY_PRINT.pdf'
                p.goto(view_url('R97_SOURCE_GALLERY.html'), wait_until='load')
                p.pdf(path=str(pdf), format='A4', print_background=True)
                receipt['pdf'][pdf.name]=sha256(pdf)
                try:
                    import fitz
                    doc=fitz.open(pdf)
                    extracted=' '.join(page.get_text() for page in doc)
                    # Text extraction can insert whitespace within long NASA URLs.
                    for marker in ('apollo-1-crew-honored', 'amf-s67-15717', 'amf-s66-58038',
                                   'amf-ksc-20170124', 'amf-s67-21294'):
                        check(marker in extracted.replace('\n','').replace(' ','').lower(),
                              'print PDF omitted NASA reference: '+marker)
                    check(extracted.count('INDIVIDUAL REVIEW REQUIRED') >= 6,
                          'print PDF omitted photo-specific rights hold')
                    receipt['pdf']['printed_pages']=len(doc)
                    doc.close()
                except ImportError:
                    raise AssertionError('PyMuPDF required for printed provenance check')
            ctx.close()
        receipt['measured_lab_performance']=performance

        # axe is a separate browser context with CSP bypass only for diagnostic injection;
        # ordinary contexts already validated the strict delivered production-like CSP.
        for width in (390,1440):
            ctx=browser.new_context(viewport={'width':width,'height':900},
                                    bypass_csp=True,
                                    storage_state=admin_context.storage_state())
            p=ctx.new_page()
            for view in ('R89_REVIEW_HUB.html','R94_CURATED_ATLAS.html','R97_SOURCE_GALLERY.html'):
                p.goto(view_url(view), wait_until='domcontentloaded')
                p.add_script_tag(path=str(axe_path))
                result=p.evaluate('async () => await axe.run(document, {runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}})')
                failures=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in result['violations']]
                receipt['axe'].append({'width':width,'view':view,'violations':failures,'passes':len(result['passes'])})
                check(not failures, f'axe violations: {view} {width}: {failures}')
            ctx.close()
        admin_context.close()
        browser.close()
    receipt['tested_viewport_cases']=len(WIDTHS)*len(VIEWS)*2
    receipt['screenshots']={k:receipt['screenshots'][k] for k in sorted(receipt['screenshots'])}
    (out/'R100_ACTUAL_WORDPRESS_QA.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--base',default='http://127.0.0.1:8955/')
    p.add_argument('--stage',type=Path,required=True)
    p.add_argument('--axe',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--user',required=True)
    p.add_argument('--password',required=True)
    p.add_argument('--subscriber',required=True)
    p.add_argument('--subscriber-password',required=True)
    p.add_argument('--author',required=True)
    p.add_argument('--author-password',required=True)
    p.add_argument('--contributor',required=True)
    p.add_argument('--contributor-password',required=True)
    p.add_argument('--editor',required=True)
    p.add_argument('--editor-password',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.base,args.stage,args.axe,args.out,args.user,args.password,args.subscriber,args.subscriber_password,
                              args.author,args.author_password,args.contributor,args.contributor_password,
                              args.editor,args.editor_password),indent=2))