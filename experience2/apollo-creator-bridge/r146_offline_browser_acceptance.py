#!/usr/bin/env python3
"""Apollo R146: read-only WordPress HTML-export browser acceptance.

Requires Python Playwright and local Chromium. No network, CMS, purchase, or
analytics writes. page.set_content avoids navigation policy blocking
http/file/data URLs; it does NOT establish live-site acceptance.

python r146_offline_browser_acceptance.py --input exported-repaired.html --out output/
Optional: --axe-js /approved/local/axe.min.js (never fetches a vendor script).
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1440, 1920)
GALLERY = '[data-fvx-chrono-gallery]'
PHOTOS = '[data-fvx-chrono-photo]'
RANGE = '[data-fvx-chrono-tool] input[type=range]'
BAD = "const photos = $(box, '[data-fvx-chrono-photo]');"
FIX = "const photos = $$(box, '[data-fvx-chrono-photo]');"

def sha(b): return hashlib.sha256(b).hexdigest()

def local_page(browser, width, js=True, touch=False, reduce=False):
    ctx = browser.new_context(viewport={'width':width,'height':850}, device_scale_factor=1,
                              java_script_enabled=js, has_touch=touch, reduced_motion='reduce' if reduce else 'no-preference')
    # We deliberately never contact WordPress, analytics, Google or NASA during this QA.
    ctx.route('**/*', lambda route: route.abort('blockedbyclient'))
    page=ctx.new_page()
    return ctx,page

def validate_input(html):
    problems=[]
    if html.count(FIX)!=1 or BAD in html: problems.append('GALLERY_SELECTOR_NOT_REPAIRED_EXACTLY_ONCE')
    if html.count('data-fvx-chrono-photo=')!=3: problems.append('THREE_GALLERY_SOURCE_RECORDS_NOT_CONFIRMED')
    if 'data-fvx-chronology' not in html: problems.append('MISSING_CHRONOLOGY')
    if 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' not in html:
        problems.append('MISSING_PRIMARY_NASA_BOARD_REFERENCE')
    if 'Read the full investigation' not in html: problems.append('MISSING_EXISTING_READER_ACTION')
    return problems

def run(html, out, axe_source=None):
    out.mkdir(parents=True, exist_ok=False)
    receipt={'schema':'fv.apollo.r146.offline-browser-acceptance.v1',
             'input_sha256':sha(html.encode('utf8')),'scope':'LOCAL_EXPORTED_WORDPRESS_HTML_ONLY',
             'network':'BLOCKED','published_page_browser':'NOT_TESTED',
             'production_cwv':'NOT_MEASURED','photographic_commercial_rights':'NOT_APPROVED',
             'merchant':'NOT_VERIFIED','verified_sales':'NOT_OBSERVED','approved_to_publish':False,
             'release':'STAGING_HOLD','checks':[], 'screenshots':[]}
    def check(kind, width, name, passed, detail=''):
        receipt['checks'].append({'kind':kind,'width':width,'name':name,'pass':bool(passed),'detail':str(detail)[:300]})
    issues=validate_input(html)
    for issue in issues: check('source',0,issue,False)
    if issues:
        receipt['status']='SOURCE_FAIL'
        (out/'r146_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8')
        return receipt
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                context,page=local_page(browser,width,js=True,touch=width==390,reduce=width==768)
                errors=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                try:
                    page.set_content(html,wait_until='domcontentloaded',timeout=15000)
                    page.locator(GALLERY).wait_for(timeout=5000)
                    photos=page.locator(PHOTOS)
                    check('js',width,'three_dom_figures',photos.count()==3,str(photos.count()))
                    sliders=page.locator(RANGE)
                    check('js',width,'range_exists',sliders.count()==1,str(sliders.count()))
                    # Test historical context mapping, NOT a claim that images depict particular seconds.
                    if sliders.count()==1:
                        for timevalue,expected in [('0',0),('6',1),('11.3',2),('14.7',2)]:
                            sliders.evaluate('(el, value) => {el.value=value; el.dispatchEvent(new Event("input", {bubbles:true}));}',timevalue)
                            shown=photos.evaluate_all('(els) => els.map((e,i) => !e.hidden ? i : -1).filter(i=>i>=0)')
                            check('js',width,'gallery_at_'+timevalue,shown==[expected],str(shown))
                        check('js',width,'historical_disclaimer_visible',
                              page.locator(GALLERY+' .fvx-chrono-gallery__note').is_visible())
                        sliders.focus(); old=float(sliders.input_value());sliders.press('ArrowLeft')
                        new=float(sliders.input_value())
                        check('keyboard',width,'range_arrow_navigation',new<old,f'{old}->{new}')
                        if width==390:
                            sliders.evaluate('(el) => {el.value="0";el.dispatchEvent(new Event("input",{bubbles:true}));}')
                            sliders.tap(position={'x':sliders.bounding_box()['width']*.9,'y':10})
                            check('touch',width,'range_touch_changes_value',float(sliders.input_value())>0,sliders.input_value())
                    check('js',width,'no_runtime_errors',len(errors)==0,' | '.join(errors))
                    overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                    check('layout',width,'no_horizontal_overflow',not overflow)
                    if axe_source:
                        try:
                            page.add_script_tag(content=axe_source)
                            result=page.evaluate('async () => await axe.run(document, {runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}})')
                            violations=[{'id':v['id'],'impact':v.get('impact'),'nodes':len(v['nodes'])} for v in result['violations']]
                            check('axe',width,'zero_wcag_violations',not violations,json.dumps(violations))
                        except Exception as exc:
                            check('axe',width,'axe_execution',False,str(exc))
                    file=out/f'r146-staging-js-{width}.png'
                    page.screenshot(path=str(file),full_page=True,animations='disabled',timeout=20000)
                    receipt['screenshots'].append({'file':file.name,'sha256':sha(file.read_bytes()),'width':width,'mode':'offline_js'})
                except Exception as exc:check('browser',width,'js_execution',False,str(exc))
                finally:context.close()
            # No JS must retain all archival captions and the ordinary article link.
            ctx,p=local_page(browser,390,js=False)
            try:
                p.set_content(html,wait_until='domcontentloaded',timeout=15000)
                fs=p.locator(PHOTOS)
                check('no_js',390,'all_three_archival_photos_readable',fs.count()==3 and all(fs.nth(i).is_visible() for i in range(3)))
                action=p.get_by_role('link',name='Read the full investigation',exact=True)
                check('no_js',390,'ordinary_reader_action',action.count()==1 and action.is_visible())
                sources=p.locator(GALLERY+' figcaption a')
                check('no_js',390,'three_source_links',sources.count()==3 and all(sources.nth(i).is_visible() for i in range(3)))
                file=out/'r146-staging-nojs-390.png';p.screenshot(path=str(file),full_page=True,animations='disabled')
                receipt['screenshots'].append({'file':file.name,'sha256':sha(file.read_bytes()),'width':390,'mode':'offline_no_js'})
            except Exception as exc:check('no_js',390,'execution',False,str(exc))
            finally:ctx.close()
        finally:browser.close()
    if not axe_source:receipt['axe']='NOT_EXECUTED_LOCAL_AXE_NOT_SUPPLIED'
    else:receipt['axe']='EXECUTED_OFFLINE_DOCUMENT_ONLY'
    receipt['status']='OFFLINE_TEST_PASS' if all(c['pass'] for c in receipt['checks']) else 'OFFLINE_TEST_FAIL'
    (out/'r146_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8')
    return receipt

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True,help='Read-only exported repaired WordPress HTML')
    ap.add_argument('--out',type=Path,required=True,help='Local evidence-only directory')
    ap.add_argument('--axe-js',type=Path,help='Preapproved local copy of axe-core; never fetched')
    args=ap.parse_args()
    original=args.input.resolve();target=args.out.resolve()
    if not original.is_file():ap.error('input must be a regular file')
    if original==target or original.parent==target:ap.error('output must not contain original input')
    if args.axe_js and not args.axe_js.is_file():ap.error('axe source must be local file')
    receipt=run(original.read_text(encoding='utf8'),target,args.axe_js.read_text(encoding='utf8') if args.axe_js else None)
    print(json.dumps({'status':receipt['status'],'pass':sum(c['pass'] for c in receipt['checks']),
                      'fail':sum(not c['pass'] for c in receipt['checks']), 'output':str(target)},sort_keys=True))
    return 0 if receipt['status']=='OFFLINE_TEST_PASS' else 2
if __name__=='__main__':sys.exit(main())
