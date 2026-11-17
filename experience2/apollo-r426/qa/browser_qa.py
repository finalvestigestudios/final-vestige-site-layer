"""Real Chromium exercise of PHP-rendered offline HTML; navigation/staging/LCP/axe remain HOLD."""
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'; SHOTS=OUT/'screenshots'; SHOTS.mkdir(parents=True,exist_ok=True)
html=subprocess.run(['php',str(ROOT/'qa/render_fixture.php'),'2'],check=True,capture_output=True,text=True).stdout
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
    for width in (320,360,390,768,1024,1440,1920):
        page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
        page.set_content(html)
        assert page.locator('.fv-r426').count()==2
        assert page.locator('details').count()==12
        assert len(page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)'))==len(set(page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')))
        overflow=page.evaluate('document.documentElement.scrollWidth - window.innerWidth')
        assert overflow<=1, (width,overflow)
        page.locator('summary').first.focus();page.keyboard.press('Enter')
        assert page.locator('details').first.evaluate('(e)=>e.open')
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
        results.append({'context':str(width),'assertions':['two real PHP instances','12 native disclosures','unique IDs','no horizontal overflow','keyboard disclosure'],'overflow_px':overflow,'PASS':True})
        page.close()
    mobile=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
    mobile.set_content(html); mobile.locator('summary').first.tap();assert mobile.locator('details').first.evaluate('(e)=>e.open')
    mobile.screenshot(path=str(SHOTS/'touch.png'),full_page=True);results.append({'context':'touch 390','PASS':True});mobile.close()
    for key,context in [('nojs',{'java_script_enabled':False}),('reduce',{'reduced_motion':'reduce'}),('contrast',{'forced_colors':'active'})]:
        p=browser.new_page(viewport={'width':390,'height':844},**context);p.set_content(html)
        assert p.locator('.fv-r426__plate').count()==12
        p.locator('summary').first.click();assert p.locator('details').first.evaluate('(e)=>e.open')
        p.screenshot(path=str(SHOTS/(key+'.png')),full_page=True);results.append({'context':key,'PASS':True});p.close()
    zoom=browser.new_page(viewport={'width':320,'height':850});zoom.set_content(html);zoom.add_style_tag(content='html{font-size:40px}');assert zoom.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
    zoom.screenshot(path=str(SHOTS/'enlarged-text.png'),full_page=True);results.append({'context':'enlarged-text','PASS':True});zoom.close()
    browser.close()
(OUT/'browser-results.json').write_text(json.dumps({'mode':'PHP offline set_content; not installed WP','results':results,'axe_core':'NOT RUN: pinned axe-core unavailable','navigated_LCP_CLS':'NOT RUN: local navigation blocked','production':'HARD HOLD'},indent=2)+'\n')
print(json.dumps({'passed_contexts':len(results),'screenshots':len(list(SHOTS.glob('*.png'))),'navigation':'HOLD'}))
