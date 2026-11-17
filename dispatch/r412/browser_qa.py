"""Offline local HTML viewport smoke test; never touches WordPress or sends email."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
src=Path(__file__).with_name('ISSUE04_APOLLO_OFFLINE.html')
out=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,360,390,768,1024,1440,1920]:
        page=browser.new_page(viewport={'width':width,'height':820},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(src.read_text(encoding='utf-8'),wait_until='domcontentloaded')
        r=page.evaluate("""() => ({scrollWidth:document.documentElement.scrollWidth, innerWidth:window.innerWidth, anchors:document.querySelectorAll('a').length, h1:document.querySelectorAll('h1').length, bodyText:document.body.innerText.length})""")
        r.update({'viewport':width,'js_errors':errors,'pass':r['scrollWidth']<=r['innerWidth'] and not errors and r['anchors']==5 and r['h1']==1})
        if width in [390,1440]:page.screenshot(path=str(src.parent/f'REVIEW_{width}.png'),full_page=True)
        out.append(r)
        page.close()
    browser.close()
(src.parent/'BROWSER_QA.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
assert all(x['pass'] for x in out)
