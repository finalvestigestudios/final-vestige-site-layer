#!/usr/bin/env python3
"""R350 executable PHP + real Chromium provenance drift QA. Requires php, Playwright and Chromium.
Runs offline against the checked-out branch; never reaches or changes production.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, shutil, subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'apollo-r350'/'QA'
OUT.mkdir(parents=True,exist_ok=True)

def render(root):
    cmd='define("ABSPATH",true);require '+json.dumps(str(root/'apollo-r348/source-custody.php'))+';echo fv_apollo_r348_experience_shortcode();'
    return subprocess.check_output(['php','-r',cmd],text=True)

def quarantined(html):
    assert 'data-fv-source-review-required="true"' in html
    assert 'data-fv-custody-source' not in html
    assert 'href="https://www.nasa.gov/' not in html
    assert html.count('source link withheld pending editorial verification') >= 10
    assert html.count('data-fv-r339-cta="editorial"') == 1

original=render(ROOT)
assert original.count('data-fv-custody-source')==8
assert original.count('data-fv-source-review-required')==0
assert original.count('data-fv-r339-cta="editorial"')==1
mutations=[
 ('chronology','apollo-r339/chronology-rail.php','First reported emergency','Unverified new assertion'),
 ('finding','apollo-r345/evidence-plate.php','No single ignition source was conclusively identified.','A single exact ignition source was proven.'),
 ('photograph','apollo-r340/apollo-accession-gallery.php','A pre-incident image cannot establish where the fire began.','This image proves where the fire began.'),
 ('approved URL re-pairing','apollo-r339/chronology-rail.php',"'source' => $board_sequence","'source' => $board_voice"),
]
receipt=[]
with TemporaryDirectory(prefix='fv-r350-') as temp:
    copy=Path(temp)/'experience2'
    shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('QA','__pycache__'))
    for name,rel,old,new in mutations:
        path=copy/rel
        before=path.read_text()
        assert old in before,name
        path.write_text(before.replace(old,new,1))
        quarantined(render(copy))
        receipt.append({'scenario':name,'result':'PASS','source_links':0})
        path.write_text(before)
    integrity=copy/'apollo-r350/integrity.php'
    before=integrity.read_text()
    integrity.unlink()
    quarantined(render(copy))
    receipt.append({'scenario':'integrity file absent','result':'PASS','source_links':0})
    integrity.write_text(before)

css='\n'.join((ROOT/file).read_text() for file in [
 'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
 'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
 'apollo-r348/assets/source-custody.css'])
js=(ROOT/'apollo-r347/assets/source-index.js').read_text()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width,enabled in [(320,False),(390,True),(1440,True),(1920,False)]:
        context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
                                    reduced_motion='reduce')
        page=context.new_page()
        page.set_content('<html lang="en"><meta charset="UTF-8"><style>body{margin:0}'+css+'</style><body>'+original+'</body>')
        if enabled:page.add_script_tag(content=js)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        summary=page.locator('.fv-apollo-r348__detail summary').first
        summary.focus()
        page.keyboard.press('Enter')
        assert page.locator('.fv-apollo-r348__detail').first.get_attribute('open') is not None
        assert page.locator('[data-fv-custody-source]').count()==8
        nodes=context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        links=[node for node in nodes if node.get('role',{}).get('value')=='link' and not node.get('ignored')]
        assert links and all(node.get('name',{}).get('value','').strip() for node in links)
        if enabled:
            assert page.locator('.fv-apollo-r347__filters button').count()==5
            page.locator('.fv-apollo-r347__filters button').last.click()
            assert page.locator('.fv-apollo-r347__group:visible').count()==1
        else:assert page.locator('.fv-apollo-r347__group:visible').count()==4
        if width in (320,1440):page.screenshot(path=str(OUT/f'r350-{width}-browser.png'),full_page=True)
        receipt.append({'scenario':f'Chromium {width}px JS={enabled} keyboard/CDP/overflow','result':'PASS'})
        context.close()
    browser.close()
(OUT/'r350-qa.json').write_text(json.dumps({'production_verified':False,'axe_executed':False,'results':receipt},indent=2)+'\n')
print('PASS',len(receipt),'R350 adversarial and real-browser checks (not production or axe certification)')
