"""Review-only native Chromium test for standalone Gutenberg fallback snippet.
Does NOT execute Jetpack/WordPress, or certify production, subscriptions or sales.
Usage: python test_focus_fallback_browser.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os, sys

here=Path(__file__).resolve().parent
block=(here/'focus_nojs_fallback_block.html').read_text()
url='https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf'
assert block.count('<noscript>')==1 and block.count('</noscript>')==1
assert block.count(url)==1
assert 'join the dispatch' not in block.lower()
body='<div class="fv-focus">'+block+'</div>'
report=[]
with sync_playwright() as p:
    executable=os.environ.get('FV_CHROMIUM_EXECUTABLE','/usr/bin/chromium')
    launch={'headless':True,'args':['--no-sandbox']}
    if Path(executable).exists(): launch['executable_path']=executable
    browser=p.chromium.launch(**launch)
    for width,zoom in [(320,1),(360,1),(390,1),(768,1),(1440,1),(1280,2)]:
        for js in (False,True):
            page=browser.new_page(viewport={'width':width,'height':850},java_script_enabled=js,device_scale_factor=1)
            page.set_content('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Review fixture only</title><body style="background:#090A0A;color:#f4efe6">'+body+'</body></html>',wait_until='domcontentloaded')
            if zoom==2:page.evaluate("document.body.style.zoom='200%'")
            anchor=page.locator('.fvf-nojs-fallback a')
            visible=anchor.is_visible()
            rect=anchor.bounding_box() if visible else None
            overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
            ok=(visible is (not js) and not overflow)
            if visible:
                ok=ok and anchor.get_attribute('href')==url and rect['height']>=44 and rect['width']>=44 and rect['x']+rect['width']<=width+1
                anchor.focus()
                ok=ok and page.evaluate('document.activeElement===document.querySelector(".fvf-nojs-fallback a")')
                if width in (320,390) and zoom==1: page.screenshot(path=str(here/f'focus_fallback_{width}_nojs.png'),full_page=True)
            report.append({'width':width,'zoom':zoom,'javascript':js,'visible':visible,'rect':rect,'overflow':overflow,'pass':ok})
            page.close()
    browser.close()
(here/'browser_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'scenarios':len(report),'passing':sum(x['pass'] for x in report),'failures':[x for x in report if not x['pass']]},indent=2))
sys.exit(0 if all(x['pass'] for x in report) else 2)
