from playwright.sync_api import sync_playwright
from pathlib import Path
import json
p=Path(__file__).parent
out=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for w in [320,390,768,1440]:
        page=browser.new_page(viewport={'width':w,'height':900},device_scale_factor=1)
        errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content((p/'ISSUE_06_PREVIEW.html').read_text(),wait_until='load')
        x=page.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,links:Array.from(document.querySelectorAll("a")).map(a=>a.href),isHeld:document.body.innerText.includes("DO NOT SEND")})')
        if w in [320,390,1440]:page.screenshot(path=str(p/f'reviewer_{w}.png'),full_page=True)
        out.append({'width':w,**x,'no_horizontal_overflow':x['sw']<=x['cw'],'page_errors':errs})
        page.close()
    browser.close()
(p/'browser_qa.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
assert all(r['no_horizontal_overflow'] and not r['page_errors'] and r['isHeld'] for r in out)
