#!/usr/bin/env python3
"""Apollo R154: read-only Chromium QA of byte-identical PR #158 Research Desk.

Offline synthetic page shell is NOT a WordPress staging deployment. This harness
loads actual Git-blob-verified PR #158 template/CSS with the proposed R153 JS/CSS.
No URLs navigated to, external requests aborted, no analytics/merchant writes.

Example:
 python r154_exact_template_browser_qa.py --template ledger.html \
   --css source-ledger.css --js r153_source_ledger_compat.js \
   --extra-css r153_source_ledger_compat.css --out ./r154-evidence
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SOURCE_BLOBS = {
    'template': '403d128c57b9bc82dac7c619651689070edef86c',
    'css': 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
    'js': '3610ec8f68fc0332db04bcfa5c368574818e9866',
}
WIDTHS = [320, 360, 390, 768, 1440, 1920]
ORIGINAL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def blob(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def checked_file(path, key):
    b = Path(path).read_bytes()
    actual = blob(b)
    if actual != SOURCE_BLOBS[key]:
        raise RuntimeError(f'Git blob mismatch for {key}: expected {SOURCE_BLOBS[key]} got {actual}')
    return b.decode('utf-8')


def document(template):
    # Preserve source as-is, adding only a minimal HTML document shell.
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Research Desk exact-source offline review</title></head><body>'
            '<main>' + template + '</main></body></html>')


def run(args):
    template = checked_file(args.template, 'template')
    css = checked_file(args.css, 'css')
    js = checked_file(args.js, 'js')
    extra_css = Path(args.extra_css).read_text(encoding='utf-8')
    if Path(args.out).exists():
        raise RuntimeError('Refusing to overwrite evidence; use a fresh output directory.')
    out = Path(args.out); out.mkdir(parents=True)
    report = {
        'scope': 'EXACT_GITHUB_PR158_TEMPLATE_AND_CSS__OFFLINE_BROWSER_SHELL',
        'not_claimed': ['wordpress_staging', 'theme_integration', 'published_page',
                        'live_lcp_cls', 'merchant_acceptance', 'paid_conversion'],
        'release': 'STAGING_HOLD',
        'sha256': {k: sha256(Path(v).read_bytes()) for k,v in {
            'template': args.template, 'css': args.css, 'js': args.js,
            'extra_css': args.extra_css}.items()},
        'source_git_blob_sha1': SOURCE_BLOBS,
        'axe': 'NOT_EXECUTED' if not args.axe else 'RUN',
        'checks': [], 'screenshots': [], 'errors': [], 'offline_performance': [], 'accessibility_tree': [],
    }
    def check(width, name, cond):
        report['checks'].append({'width': width, 'name': name, 'pass': bool(cond)})
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
        report['chromium_version'] = browser.version
        for width in WIDTHS:
            context = browser.new_context(viewport={'width':width,'height':860},
                reduced_motion='reduce', has_touch=(width==390), service_workers='block')
            context.route('**/*', lambda route: route.abort())
            p = context.new_page()
            p.on('pageerror', lambda exc, w=width: report['errors'].append({'width':w,'message':str(exc)}))
            p.evaluate("""() => { window.__fvPerf={lcp:[], shifts:[]};
                new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__fvPerf.lcp.push(e.startTime))).observe({type:'largest-contentful-paint', buffered:true});
                new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__fvPerf.shifts.push({value:e.value, hadRecentInput:e.hadRecentInput}))).observe({type:'layout-shift', buffered:true});
            }""")
            p.set_content(document(template), wait_until='load')
            p.add_style_tag(content=css+'\n'+extra_css)
            cards = p.locator('[data-fvx-record]')
            links = p.locator('[data-fvx-record] .fv-ex2-ledger__recordlinks a[href^="https://www.nasa.gov/"]')
            check(width,'exact_six_records',cards.count()==6)
            check(width,'six_nasa_archive_records',links.count()==12)
            check(width,'source_limitations_six',p.locator('[data-fvx-record] .fv-ex2-ledger__boundary').count()==6)
            check(width,'original_investigation_action',p.locator(f'a[href="{ORIGINAL}"]').count()==1)
            check(width,'no_js_all_six_visible',all(cards.nth(i).is_visible() for i in range(6)))
            check(width,'no_js_controls_hidden',not p.locator('[data-fvx-tools]').is_visible())
            # All details content must remain accessible without JavaScript.
            cards.nth(0).locator('summary').click()
            check(width,'native_details_expands_without_js',cards.nth(0).locator('details').get_attribute('open') is not None)
            check(width,'no_js_zero_horizontal_overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            p.add_script_tag(content=js)
            search=p.locator('input[data-fvx-search]')
            clear=p.locator('button[data-fvx-clear]')
            check(width,'real_template_script_activates',p.locator('[data-fvx-ledger][data-fvx-initialized="yes"]').count()==1 and clear.count()==1 and p.locator('[data-fvx-tools]').is_visible())
            search.fill('S67-21294')
            check(width,'clear_button_44px',clear.evaluate('(b)=>b.getBoundingClientRect().height>=44') )
            check(width,'search_specific_verified_record',cards.nth(4).is_visible() and sum(cards.nth(i).is_visible() for i in range(6))==1)
            check(width,'clear_control_appears',clear.is_visible())
            check(width,'status_1_of_6',p.locator('[data-fvx-status]').inner_text()=='1 of 6 evidence records')
            # Test exact external hash entry while matching record is hidden by the previous search.
            p.evaluate("() => {const a=document.createElement('a');a.href='#fv-ex2-ledger-apollo1-record-04';a.id='external-test-link';a.textContent='Research record 4';document.body.prepend(a)}")
            p.locator('#external-test-link').click()
            p.wait_for_timeout(35)
            check(width,'external_fragment_restores_hidden',cards.nth(3).is_visible() and sum(cards.nth(i).is_visible() for i in range(6))==6)
            check(width,'external_fragment_focus',cards.nth(3).evaluate('(n)=>document.activeElement===n'))
            search.fill('no matching unique term ZZ-929292')
            check(width,'zero_results_message',p.locator('[data-fvx-empty]').is_visible() and sum(cards.nth(i).is_visible() for i in range(6))==0)
            search.press('Escape')
            check(width,'keyboard_escape_resets',search.input_value()=='' and all(cards.nth(i).is_visible() for i in range(6)))
            check(width,'keyboard_escape_focus',search.evaluate('(n)=>document.activeElement===n'))
            search.fill('S67-21294')
            if width==390:
                clear.tap()
            else:
                clear.click()
            check(width,'touch_or_pointer_clear_restores',search.input_value()=='' and all(cards.nth(i).is_visible() for i in range(6)))
            check(width,'post_js_zero_horizontal_overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            check(width,'reduced_motion_respected',p.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
            check(width,'no_runtime_errors',not any(x['width']==width for x in report['errors']))
            check(width,'no_unrelated_commerce',p.locator('a[href*="payhip"],a[href*="awin1"],a[href*="checkout"]').count()==0)
            check(width,'no_geo_pins_without_provenance',p.locator('[data-lat],[data-lng],[data-geopoint]').count()==0)
            check(width,'source_context_count',p.locator('[data-fvx-record] .fv-ex2-ledger__boundary strong').count()==6)
            check(width,'search_input_has_visible_label',p.locator('label[for="fv-ex2-ledger-apollo1-search"]').count()==1)
            # CDP exposes the real Chromium accessibility tree, but is not axe/WCAG certification.
            ax=context.new_cdp_session(p).send('Accessibility.getFullAXTree')
            nodes=[n for n in ax['nodes'] if not n.get('ignored')]
            roles=[n.get('role',{}).get('value','') for n in nodes]
            names=[n.get('name',{}).get('value','') for n in nodes]
            check(width,'ax_tree_has_searchbox', 'searchbox' in roles)
            check(width,'ax_tree_investigation_cta',any('Read original investigation' in n for n in names))
            check(width,'ax_tree_six_expanders',sum('Review the underlying finding' in n for n in names)>=6)
            report['accessibility_tree'].append({'width':width,'nonignored_nodes':len(nodes),'searchboxes':roles.count('searchbox')})
            if args.axe:
                p.add_script_tag(path=args.axe)
                result=p.evaluate('async()=>axe.run(document.querySelector("[data-fvx-ledger]"),{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}})')
                report.setdefault('axe_results', []).append({'width':width,
                    'violations':[{'id':x['id'],'impact':x['impact'],'nodes':len(x['nodes'])} for x in result['violations']],
                    'incomplete':[{'id':x['id'],'nodes':len(x['nodes'])} for x in result['incomplete']]})
                check(width,'axe_zero_violations_and_incomplete',not result['violations'] and not result['incomplete'])
            p.evaluate("() => {document.getElementById('external-test-link')?.remove();document.querySelectorAll('details').forEach(d=>d.open=false);window.scrollTo(0,0)}")
            p.evaluate('document.fonts.ready')
            p.wait_for_timeout(200)
            metrics=p.evaluate("""() => ({
                offline_last_lcp_observer_ms:window.__fvPerf.lcp.at(-1) ?? null,
                offline_cls_without_recent_input:window.__fvPerf.shifts.filter(e=>!e.hadRecentInput).reduce((n,e)=>n+e.value,0),
                layout_shift_entries:window.__fvPerf.shifts.length,
                navigation_scope:'set_content_offline_not_wordpress'})""")
            report['offline_performance'].append({'width':width,**metrics})
            filename=f'full-pr158-{width}-r154.png'
            b=p.screenshot(path=str(out/filename), full_page=True, animations='disabled')
            report['screenshots'].append({'width':width,'file':filename,'sha256':sha256(b)})
            context.close()
        browser.close()
    report['summary'] = {
        'passed':sum(x['pass'] for x in report['checks']),
        'failed':sum(not x['pass'] for x in report['checks']),
        'check_count':len(report['checks']),
        'actual_template':True,
        'axe_complete':bool(args.axe),
        'production_acceptance':False, 'offline_perf_not_real_world_cwv':True,
    }
    (out/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (out/'SHA256SUMS').write_text(''.join(f'{i["sha256"]}  {i["file"]}\n' for i in report['screenshots']))
    print(json.dumps(report['summary'],sort_keys=True))
    return 1 if report['summary']['failed'] else 0


def main():
    ap=argparse.ArgumentParser()
    for key in ('template','css','js','extra-css','out'):
        ap.add_argument('--'+key,required=True)
    ap.add_argument('--axe',help='Local path to reviewed axe-core; no network fetch')
    ap.add_argument('--chromium',default=os.getenv('FV_CHROMIUM','/usr/bin/chromium'))
    sys.exit(run(ap.parse_args()))

if __name__=='__main__': main()
