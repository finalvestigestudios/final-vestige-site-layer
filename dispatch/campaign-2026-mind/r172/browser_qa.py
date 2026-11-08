from pathlib import Path
from playwright.sync_api import sync_playwright
html=Path(__file__).with_name('consent_readiness_board.html').read_text()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,390,768,1440]:
  page=browser.new_page(viewport={'width':width,'height':900})
  page.set_content(html)
  assert page.title() == 'The Dispatch · Consent-to-Customer Gate | Offline Review'
  assert page.locator('a').count()==4
  assert page.locator('h1').count()==1
  assert page.locator('.path li').count()==6
  assert page.locator('.hold').first.is_visible()
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
  print(f'PASS Chromium {width}px: 4 sources, 6 steps, visible HOLD, zero horizontal scroll')
  if width==390:page.screenshot(path='preview_390.png',full_page=True)
  page.close()
 browser.close()
