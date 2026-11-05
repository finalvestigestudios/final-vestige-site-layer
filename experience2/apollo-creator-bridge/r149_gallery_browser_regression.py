#!/usr/bin/env python3
"""Offline browser acceptance of a source excerpt, not a rendered/live WordPress page.

Requires explicit local HTML source extract or controlled fixture, and Chromium.
Network requests are blocked; image loads, CWV and commercial rights are NOT tested.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from r149_gallery_release_candidate import BAD, GOOD, inspect, propose, digest

WIDTHS = (320,360,390,768,1440,1920)
GALLERY = '[data-fvx-chrono-photo]'
RANGE = '[data-fvx-chrono-tool] input[type=range]'
CTA = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def review(html: str, out: Path) -> dict:
    """Run before/after positive and negative controls without navigating to any URL."""
    if out.exists(): raise ValueError('Output destination already exists')
    if inspect(html): raise ValueError('Unpatched fixture/source shape unexpected: '+str(inspect(html)))
    after=propose(html)
    out.mkdir(parents=True)
    result={'schema':'fv.apollo.r149.browser.v1','scope':'OFFLINE_SOURCE_FRAGMENT_NOT_RENDERED_WP',
            'source_sha256':digest(html),'candidate_sha256':digest(after),
            'images':'NETWORK_BLOCKED_NOT_TESTED','axe':'NOT_EXECUTED','lcp_cls':'NOT_MEASURED',
            'commercial_product':'NOT_VERIFIED','approved_to_publish':False,
            'release':'STAGING_HOLD','checks':[],'screenshots':[]}
    def check(stage,width,key,passed,detail=''):
        result['checks'].append({'stage':stage,'width':width,'check':key,'pass':bool(passed),'detail':str(detail)[:160]})
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            result['browser_version']=b.version
            for stage,source in (('before',html),('after',after)):
                for width in WIDTHS:
                    ctx=b.new_context(viewport={'width':width,'height':820},java_script_enabled=True,
                                      reduced_motion='reduce',has_touch=(width==390))
                    ctx.route('**/*',lambda route:route.abort('blockedbyclient'))
                    page=ctx.new_page()
                    try:
                        errs=[];page.on('pageerror',lambda err:errs.append(str(err)))
                        page.set_content(source,wait_until='domcontentloaded',timeout=15000)
                        slider=page.locator(RANGE);figures=page.locator(GALLERY)
                        check(stage,width,'range_exists',slider.count()==1)
                        check(stage,width,'three_source_figures',figures.count()==3)
                        if slider.count()!=1 or figures.count()!=3:continue
                        for instant,expected in (('0',[0]),('6',[1]),('11.3',[2]),('14.7',[2])):
                            slider.evaluate('(el,v) => {el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}));}',instant)
                            visible=figures.evaluate_all('(els)=>els.map((x,i)=>!x.hidden?i:-1).filter(i=>i>=0)')
                            # Negative control expects defective published selector to leave all 3 exposed.
                            goal=[0,1,2] if stage=='before' else expected
                            check(stage,width,'gallery_at_'+instant,visible==goal,str(visible))
                        pos=page.locator('[data-fvx-chrono-position]')
                        if stage=='after':
                            check(stage,width,'status_announced',pos.get_attribute('role')=='status'
                                  and pos.get_attribute('aria-live')=='polite' and pos.is_visible())
                            check(stage,width,'status_historical_disclaimer',
                                  'do not depict' in pos.text_content().lower())
                            link=page.get_by_role('link',name='Read the full investigation',exact=True)
                            check(stage,width,'one_real_reader_link',link.count()==1
                                  and link.get_attribute('href')==CTA and link.is_visible())
                            slider.focus();slider.press('ArrowLeft')
                            check(stage,width,'keyboard_operates_range',float(slider.input_value())<14.7)
                        check(stage,width,'no_runtime_exception',not errs,' | '.join(errs))
                        check(stage,width,'no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'))
                        if stage=='after':
                            f=out/f'r149-{stage}-{width}.png'
                            page.screenshot(path=str(f),full_page=True,animations='disabled')
                            result['screenshots'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
                    except Exception as exc:check(stage,width,'browser_exception',False,exc)
                    finally:ctx.close()
            # No-JS baseline: all three archival figure captions/sources remain present.
            ctx=b.new_context(viewport={'width':390,'height':820},java_script_enabled=False)
            ctx.route('**/*',lambda route:route.abort('blockedbyclient'))
            page=ctx.new_page()
            try:
                page.set_content(after,wait_until='domcontentloaded',timeout=15000)
                figures=page.locator(GALLERY)
                check('nojs',390,'all_three_figures_visible',figures.count()==3 and all(figures.nth(i).is_visible() for i in range(3)))
                check('nojs',390,'all_three_nasa_links',page.locator('[data-fvx-chrono-gallery] figcaption a').count()==3)
                check('nojs',390,'slider_enhancement_hidden',page.locator('[data-fvx-chrono-tool]').is_hidden())
                f=out/'r149-after-nojs-390.png';page.screenshot(path=str(f),full_page=True,animations='disabled')
                result['screenshots'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
            finally:ctx.close()
        finally:b.close()
    result['passed']=sum(x['pass'] for x in result['checks'])
    result['failed']=sum(not x['pass'] for x in result['checks'])
    result['status']='FIXTURE_BROWSER_PASS_STAGING_HOLD' if result['failed']==0 else 'FIXTURE_BROWSER_FAIL_STAGING_HOLD'
    (out/'r149_browser_receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    r=review(a.input.read_text(),a.out)
    print(json.dumps({'status':r['status'],'passed':r['passed'],'failed':r['failed'],'screenshots':len(r['screenshots'])}))
    return 0 if r['failed']==0 else 2

if __name__=='__main__':raise SystemExit(main())
