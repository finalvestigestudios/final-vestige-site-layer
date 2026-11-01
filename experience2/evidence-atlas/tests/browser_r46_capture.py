#!/usr/bin/env python3
"""Reproducible R46 screenshots from actual PHP markup, never hosted WordPress."""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r46_pair_smoke import fixture

def capture(out):
    out.mkdir(parents=True,exist_ok=True)
    html=fixture()
    receipts=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (390,1440):
            for enabled in (False,True):
                digests=[]
                for attempt in (1,2):
                    ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
                        has_touch=width==390,is_mobile=width==390,reduced_motion='reduce')
                    page=ctx.new_page();page.set_content(html);page.wait_for_timeout(120)
                    if enabled:
                        for idx in (0,3):
                            target=page.locator('[data-fva-select]').nth(idx)
                            target.tap() if width==390 else target.click()
                        assert page.locator('[data-fva-compare-slot] h3').count()==2
                    else:
                        assert not page.locator('[data-fva-compare]').is_visible()
                    page.evaluate('document.activeElement?.blur();window.scrollTo(0,0)')
                    image=page.screenshot(full_page=True,animations='disabled')
                    digests.append(hashlib.sha256(image).hexdigest())
                    if attempt==1:
                        name=f'r46-{width}-'+('pair' if enabled else 'nojs')+'.png'
                        (out/name).write_bytes(image)
                    ctx.close()
                assert digests[0]==digests[1],(width,enabled,digests)
                receipts.append({'width':width,'js':enabled,'sha256':digests[0],'identical_runs':2})
        browser.close()
    summary={'schema':'fv.ex2.r46.screenshots.v1','staging_only':True,
        'transport':'PHP_SHORTCODE_SET_CONTENT_NO_HTTP','axe':'NOT_EXECUTED',
        'hosted_CWV':'NOT_MEASURED','screenshots':receipts}
    (out/'R46_SCREENSHOT_MANIFEST.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    print('PASS four screenshot variants; two byte-identical Chromium captures each')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();capture(args.output)
