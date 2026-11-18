#!/usr/bin/env python3
"""Actual R440 PHP preview in offline Chromium; not navigated staging or accessibility/CWV certification."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT/'apollo-r440/qa/fixture.php'
WIDTHS = (320,360,390,768,1024,1440,1920)

def main():
    out=HERE.parent/'QA/offline';out.mkdir(parents=True,exist_ok=True)
    markup=subprocess.check_output(['php',str(FIXTURE)],text=True)
    checks=[]; failures=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True,False):
                context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                page=context.new_page();page.set_content(markup,wait_until='load')
                row={'width':width,'javascript':js,
                    'preview_instances':page.locator('[data-r440-root]').count(),
                    'original_questions':page.locator('.fv-r440 ol li').count(),
                    'source_links':page.locator('.fv-r440 a[href^="https://www.nasa.gov/"]').count(),
                    'paid_checkout_links':page.locator('.fv-r440 a[href*="payhip.com"]').count(),
                    'printable':page.locator('.fv-r440 details').count(),
                    'overflow':page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')}
                if row['preview_instances']!=2 or row['original_questions']!=6 or row['source_links']<4 or row['paid_checkout_links'] or row['overflow']:
                    failures.append(f'{width}/{js}: content/overflow contract')
                if js:
                    page.locator('.fv-r440 summary').first.click()
                    row['rubric_revealed']=page.locator('.fv-r440 details').first.get_attribute('open') is not None
                    if not row['rubric_revealed']:failures.append(f'{width}: rubric not operable')
                page.screenshot(path=str(out/f'{width}-{"js" if js else "nojs"}.png'),full_page=True)
                checks.append(row);context.close()
        browser.close()
    report={'status':'PASS_OFFLINE_FIXTURE_ONLY' if not failures else 'HOLD','screenshots':len(checks),
            'checks':checks,'failures':failures,'axe':'NOT_RUN','navigated_staging':'NOT_RUN',
            'lcp_cls':'NOT_RUN','merchant_conversion':'UNVERIFIED'}
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'screenshots':len(checks),'failures':failures}))
    raise SystemExit(bool(failures))

if __name__=='__main__':main()
