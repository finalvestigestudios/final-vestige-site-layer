#!/usr/bin/env python3
"""Actual inherited R440 PHP browser fixture in offline Chromium (NOT staging)."""
import json, os, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
WIDTHS=(320,360,390,768,1024,1440,1920)

def main():
    source=ROOT/'experience2/apollo-r440'
    fixture=source/'qa/fixture.php'
    if not fixture.is_file():
        raise SystemExit('Missing source-exact R440 fixture: materialize inherited Git sources into workspace first')
    rendered=subprocess.run(['php',str(fixture)],capture_output=True,text=True,check=True).stdout
    output=HERE.parent/'QA/screenshots';output.mkdir(parents=True,exist_ok=True)
    rows=[]
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path=os.getenv('FV_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for js in (False,True):
                    c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=width<=390)
                    page=c.new_page();page.set_content(rendered,wait_until='load')
                    roots=page.locator('[data-r440-root]');assert roots.count()==2
                    assert page.locator('details summary').count()==2
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1')
                    assert page.get_by_text('most probable initiator').count()>=1
                    assert page.locator('a[href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"]').count()==2
                    if js:
                        assert page.get_by_role('button',name='Download original classroom exercise (.txt)').count()==2
                        page.get_by_role('button',name='Download original classroom exercise (.txt)').first.click()
                        assert page.locator('[data-r440-status]').first.inner_text().startswith('Classroom text file')
                    else:
                        assert page.get_by_role('button',name='Download original classroom exercise (.txt)').count()==0
                        assert page.get_by_text('Instructor rubric and source limitations').count()==2
                    page.screenshot(path=str(output / (str(width)+'-'+('js.png' if js else 'nojs.png'))),full_page=True)
                    rows.append({'width':width,'js':js,'assertions':'PASS','mode':'offline_set_content','staging':False})
                    c.close()
        finally:b.close()
    (HERE.parent/'QA/browser_results.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
    print('offline Chromium fixture: '+str(len(rows))+'/14 cases PASS; navigated staging, axe/LCP/CLS NOT RUN')

if __name__=='__main__':main()
