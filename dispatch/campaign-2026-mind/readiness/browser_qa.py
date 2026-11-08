"""Optional Playwright QA for the static, UNSENT internal review board.

Does not visit a website or send email; uses in-memory HTML from a local file.
Dependencies: installed playwright and Chromium; standard Python tests need neither.
"""
from __future__ import annotations
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
TARGET=(ROOT/'review_board.html').resolve()
assert TARGET.exists()

def main():
    readings=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=False,device_scale_factor=1)
            faults=[]
            page.on('pageerror',lambda error:faults.append(str(error)))
            page.set_content(TARGET.read_text(encoding="utf-8"),wait_until="domcontentloaded")
            assert page.locator('article.card').count()==6,(width,'card count')
            assert page.locator('h1').inner_text().startswith('Six dispatches.'),(width,'h1')
            assert page.locator('strong.status').count()==6,(width,'held statuses')
            page.locator('summary').first.focus()
            page.keyboard.press('Enter')
            assert page.locator('details').first.get_attribute('open') is not None,(width,'keyboard details')
            assert not faults,(width,faults)
            size=page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
            assert size['scroll']<=size['client']+1,(width,'overflow',size)
            if width in (390,1440):
                page.screenshot(path=str(ROOT/f'qa-board-{width}.png'),full_page=True)
            readings.append({'width':width,'cards':6,'keyboard_details':'PASS','js':'OFF','horizontal_overflow':0,'page_errors':0})
            page.close()
        # CSS zoom to 200% at a narrow viewport, representative reflow.
        page=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=True)
        page.set_content(TARGET.read_text(encoding="utf-8"),wait_until="domcontentloaded")
        page.evaluate('document.documentElement.style.zoom="200%"')
        size=page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
        assert size['scroll']<=size['client']+1,('zoom-overflow',size)
        page.close()
        browser.close()
    result={'status':'PASS','artifact':'local_static_review_board_not_jetpack_email','views':readings,'zoom_390_200pct_reflow':'PASS','real_jetpack_render':'NOT_TESTED','mailing_list':'NOT_TOUCHED','tests_are_not_accessibility_certification':True}
    (ROOT/'browser_qa_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
