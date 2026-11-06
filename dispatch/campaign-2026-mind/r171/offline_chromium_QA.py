import json
from pathlib import Path
from playwright.sync_api import sync_playwright
source=(Path(__file__).parent/'optional_issue01_mcGurk_preview.html').read_text()
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in (320,390,768,1440):
        page=browser.new_page(viewport={'width':width,'height':800},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content(source,wait_until='load')
        dims=page.evaluate('({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})')
        link=page.locator('a[href="https://finalvestige.com/2026/11/02/change-blindness/"]')
        count=link.count();visible=link.first.is_visible() if count else False
        page.keyboard.press('Tab')
        focused=page.evaluate('document.activeElement && document.activeElement.tagName')
        row={'viewport':width,'overflow':dims['scroll']>dims['client'],'first_party_cta_count':count,'cta_visible':visible,'keyboard_tab_target':focused,'errors':errors,'result':'PASS' if dims['scroll']<=dims['client'] and count==1 and visible and not errors else 'FAIL'}
        if width in (320,390):page.screenshot(path=str(Path(__file__).parent/f'offline_preview_{width}.png'),full_page=True)
        results.append(row)
        page.close()
    browser.close()
(Path(__file__).parent/'browser_QA.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
assert all(x['result']=='PASS' for x in results)
