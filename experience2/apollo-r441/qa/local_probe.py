#!/usr/bin/env python3
"""Reproducible OFFLINE Chromium smoke against R440 real PHP; not staging, axe or CWV."""
import argparse
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo-root',required=True);a.add_argument('--out',default='QA/offline');args=a.parse_args()
    fixture=Path(args.repo_root)/'experience2/apollo-r440/qa/fixture.php'
    html=subprocess.check_output(['php',str(fixture)], text=True)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    failures=[];count=0
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for w in WIDTHS:
            for js in (True,False):
                context=browser.new_context(viewport={'width':w,'height':900},has_touch=w<=390,
                                              is_mobile=w<=390,java_script_enabled=js,reduced_motion='reduce',accept_downloads=True)
                page=context.new_page();page.set_content(html,wait_until='load')
                assertions={
                    'two_instances':page.locator('[data-r440-root]').count()==2,
                    'no_paid_cta':page.locator('a[href*="payhip"],form').count()==0,
                    'official_nasa_links':page.locator('a[href^="https://www.nasa.gov/"]').count()==6,
                    'native_disclosure':page.locator('details > summary').count()==2,
                    'no_horizontal_overflow':page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),
                    'no_duplicate_ids':page.evaluate('''() => {let ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size}'''),
                }
                if js:
                    assertions['user_initiated_export']=page.locator('[data-r440-export] button').count()==2
                    try:
                        with page.expect_download(timeout=5000) as download:
                            page.locator('[data-r440-export] button').first.click()
                        text=download.value.path().read_text()
                        assertions['real_text_export']='FINAL VESTIGE' in text and 'APOLLO' in text.upper()
                    except Exception as e: assertions['real_text_export']=False
                else:assertions['no_js_complete_text']=page.locator('ol li').count()>=6 and page.locator('details').count()==2
                count+=len(assertions)
                for desc,success in assertions.items():
                    if not success:failures.append(f'{w}/JS={js} {desc}')
                page.screenshot(path=str(out / f"{w}-{'js' if js else 'nojs'}.png"),full_page=True)
                context.close()
        browser.close()
    report={'kind':'OFFLINE_PHP_CHROMIUM_NOT_NAVIGATED_STAGING','assertions':count,'screenshots':len(WIDTHS)*2,
            'status':'PASS_OFFLINE_ONLY' if not failures else 'FAIL','failures':failures}
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2));raise SystemExit(bool(failures))
if __name__=='__main__':main()
