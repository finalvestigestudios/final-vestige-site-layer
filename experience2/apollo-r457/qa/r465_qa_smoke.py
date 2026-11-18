"""R465 isolated source custody + actual local Chromium acceptance. Never substitutes for hosted staging or axe/CWV."""
from pathlib import Path
import json, os, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_rights_gallery.php'

def php(cmd):
    return subprocess.run(['php','-r',f'require {json.dumps(str(PHP))}; {cmd}'],check=True,capture_output=True,text=True).stdout
records=json.loads(php('echo json_encode(fv457_records());'))
assert len(records)==6
assert [r['source_status'] for r in records].count('accepted')==4
assert [r['source_status'] for r in records].count('id_hold')==1
assert [r['source_status'] for r in records].count('catalogue_hold')==1
candidate=next(r for r in records if r['id'].endswith('_0129'))
assert candidate['date']==candidate['precision']=='unverified'
assert 'Kim Shiflett' in next(r for r in records if r['id'].endswith('_0090'))['credit']
assert php('echo fv457_valid(fv457_records())?"OK":"BAD";')=='OK'
assert php('$x=fv457_records();$x[4]["precision"]="day";echo fv457_valid($x)?"BAD":"OK";')=='OK'
assert php('$x=fv457_records();$x[0]["source_status"]="licensed";echo fv457_valid($x)?"BAD":"OK";')=='OK'
html=php('echo fv457_render();')
assert html.count('data-fv457-card=')==6
assert html.count('data-fv457-choice=')==5
assert html.count('data-fv457-accepted="yes"')==4
assert html.count('Read the complete free Apollo 1 investigation')==1
assert '<img ' not in html and '<form' not in html
count=13
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_BIN','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for js_on in (True,False):
            context=browser.new_context(viewport={'width':width,'height':820},java_script_enabled=js_on,reduced_motion='reduce')
            page=context.new_page();page.set_content('<!doctype html><html lang="en"><body>'+html+'</body></html>',wait_until='load')
            assert page.locator('[data-fv457-card]').count()==6
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            assert page.locator('.fv457__rail li').count()==3
            if js_on:
                page.get_by_role('button',name='NASA ID confirmed (4)').click()
                assert page.locator('[data-fv457-card]:visible').count()==4
                assert page.get_by_role('button',name='NASA ID confirmed (4)').get_attribute('aria-pressed')=='true'
                page.emulate_media(media='print')
                assert page.locator('[data-fv457-card]:visible').count()==6
                assert page.locator('.fv457__print-custody a').count()==6
                assert page.locator('.fv457__chronology-print a').count()==3
            else:
                assert not page.locator('[data-fv457-controls]').is_visible()
                assert page.locator('[data-fv457-card]:visible').count()==6
            count+=7 if js_on else 5
            context.close()
    browser.close()
print(json.dumps({'result':'PASS','checks':count,'environment':'local Chromium set_content','hosted_staging':'NOT RUN','axe':'NOT RUN','navigated_LCP_CLS':'NOT RUN'}))
