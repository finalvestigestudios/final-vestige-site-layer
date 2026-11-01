from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.parse import quote

root=Path(__file__).resolve().parent
html=(root/'concept-board.html').read_text(encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(1440,900),(390,844),(768,1024),(1920,1080)]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        page.set_content(html,wait_until="domcontentloaded")
        page.wait_for_load_state('domcontentloaded')
        assert page.locator('h1').count()==1
        assert page.locator('[data-choice]').count()==3
        for choice in ['dossier','museum','observatory']:
            page.get_by_role('button',name={'dossier':'01 Black Dossier','museum':'02 Museum After Hours','observatory':'03 Observatory'}[choice]).click()
            assert page.locator('body').get_attribute('data-direction')==choice
            assert page.locator(f'[data-choice="{choice}"]').get_attribute('aria-pressed')=='true'
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),f'overflow {width} {choice}'
        page.locator('[data-choice="dossier"]').click()
        shot=root/f'concept-{width}.png'
        page.screenshot(path=str(shot),full_page=True)
        print(f'PASS {width}x{height}: no overflow, three switchable directions, screenshot={shot.name}')
        page.close()
    browser.close()
