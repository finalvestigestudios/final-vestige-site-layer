#!/usr/bin/env python3
"""R156 independent, read-only offline Chromium QA; NOT WordPress site acceptance."""
import argparse, hashlib, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1440,1920)
EXPECTED_TEMPLATE_SHA256='7aea496f2a88a7d1eec8bb12e0161d6b34fdfe1797822f6fda333463a7f85ee4'
EXPECTED_PR158_HTML_BLOB='403d128c57b9bc82dac7c619651689070edef86c'
INVESTIGATION='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def sha(b): return hashlib.sha256(b).hexdigest()
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\\0'+b).hexdigest()

def run(a):
    source=Path(a.source).read_bytes()
    original=Path(a.original).read_bytes()
    assert sha(source)==EXPECTED_TEMPLATE_SHA256, 'R156 reviewed template was modified'
    assert gitblob(original)==EXPECTED_PR158_HTML_BLOB, 'PR158 original changed'
    css=Path(a.css).read_text()+'\\n'+Path(a.orig_css).read_text()+'\\n'+Path(a.compat_css).read_text()
    js=Path(a.compat_js).read_text()
    out=Path(a.out)
    if out.exists(): raise RuntimeError('Refusing to overwrite prior evidence')
    out.mkdir(parents=True)
    receipt={'scope':'EXACT_R156_REVIEW_BLOB_OFFLINE_NOT_WORDPRESS','release':'STAGING_HOLD',
             'source_sha256':sha(source),'screenshots':[],'checks':[],'page_errors':[],
             'axe':'NOT_EXECUTED' if not a.axe else 'ATTEMPTED'}
    def ck(w,key,condition):receipt['checks'].append({'width':w,'check':key,'pass':bool(condition)})
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
        receipt['chromium_version']=browser.version
        for w in WIDTHS:
            ctx=browser.new_context(viewport={'width':w,'height':820},has_touch=(w==390),
                                    reduced_motion='reduce',service_workers='block')
            ctx.route('**/*',lambda route:route.abort())
            page=ctx.new_page()
            page.on('pageerror', lambda error,width=w:receipt['page_errors'].append({'width':width,'error':str(error)}))
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>'+source.decode()+'</main></body></html>')
            page.add_style_tag(content=css)
            cards=page.locator('[data-fvx-record]')
            ck(w,'six_records',cards.count()==6)
            ck(w,'six_source_custody_notes',page.locator('[data-fvx-source-custody]').count()==6)
            ck(w,'six_nasa_images_and_documents',page.locator('[data-fvx-record] a[href^="https://www.nasa.gov/"]').count()==12)
            ck(w,'no_js_records_visible',all(cards.nth(i).is_visible() for i in range(6)))
            ck(w,'no_js_search_inactive',not page.locator('[data-fvx-tools]').is_visible())
            cards.nth(0).locator('summary').click()
            ck(w,'no_js_native_details',cards.nth(0).locator('details').get_attribute('open') is not None)
            ck(w,'single_read_cta',page.locator(f'a[href="{INVESTIGATION}"]').count()==1)
            ck(w,'no_commerce_or_fake_pins',page.locator('a[href*="payhip"],a[href*="checkout"],[data-lat],[data-lng]').count()==0)
            page.add_script_tag(content=js)
            search=page.locator('input[data-fvx-search]')
            clear=page.locator('[data-fvx-clear]')
            ck(w,'real_template_compat_enabled',page.locator('[data-fvx-ledger][data-fvx-initialized="yes"]').count()==1)
            search.fill('S67-21294')
            ck(w,'source_id_search',cards.nth(4).is_visible() and sum(cards.nth(i).is_visible() for i in range(6))==1)
            ck(w,'clear_minimum_touch_target',clear.evaluate('(n)=>n.getBoundingClientRect().height>=44'))
            if w==390: clear.tap()
            else: clear.click()
            ck(w,'touch_or_click_clear',search.input_value()=='' and all(cards.nth(i).is_visible() for i in range(6)))
            search.fill('no_matching_record_ZZZ999')
            ck(w,'empty_state',page.locator('[data-fvx-empty]').is_visible())
            search.press('Escape')
            ck(w,'keyboard_escape',search.input_value()=='' and all(cards.nth(i).is_visible() for i in range(6)))
            ck(w,'zero_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            ck(w,'reduced_motion',page.evaluate('matchMedia("(prefers-reduced-motion:reduce)").matches'))
            ck(w,'no_js_errors',not any(x['width']==w for x in receipt['page_errors']))
            if a.axe:
                page.add_script_tag(path=a.axe)
                result=page.evaluate('async()=>axe.run(document.querySelector("[data-fvx-ledger]"),{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}})')
                receipt.setdefault('axe_results',[]).append({'width':w,'violations':[v['id'] for v in result['violations']],'incomplete':[x['id'] for x in result['incomplete']]})
                ck(w,'axe_zero_violations_and_incomplete',not result['violations'] and not result['incomplete'])
            page.evaluate('()=>{document.querySelectorAll("details").forEach(d=>d.open=false);scrollTo(0,0)}')
            dest=f'apollo-r156-{w}.png'
            data=page.screenshot(path=str(out/dest),full_page=True,animations='disabled')
            receipt['screenshots'].append({'width':w,'file':dest,'sha256':sha(data)})
            ctx.close()
        browser.close()
    receipt['summary']={'passed':sum(c['pass'] for c in receipt['checks']),
        'failed':sum(not c['pass'] for c in receipt['checks']), 'axe_executed':bool(a.axe),
        'production_acceptance':False}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\\n')
    (out/'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['file']}\\n" for e in receipt['screenshots']))
    print(json.dumps(receipt['summary'],sort_keys=True))
    return 1 if receipt['summary']['failed'] else 0

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ('source','original','css','orig-css','compat-css','compat-js','out'):
        ap.add_argument('--'+name,required=True)
    ap.add_argument('--axe',help='Reviewed local axe-core JS; no network fetch')
    ap.add_argument('--chromium',default=os.getenv('FV_CHROMIUM','/usr/bin/chromium'))
    raise SystemExit(run(ap.parse_args()))
