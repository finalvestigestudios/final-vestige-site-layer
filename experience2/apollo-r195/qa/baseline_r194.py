#!/usr/bin/env python3
"""Negative control: reproduce R194 keyboard focus and zoom reflow defects."""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
PARENT=HERE.parent/'apollo-r194'
sys.path.insert(0,str(PARENT))
from build_r194 import build

def check():
    build();dist=PARENT/'dist'
    page_data=json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r194.php'),str(dist/'fv-ex2-apollo-r194.php'),'normal'],text=True))
    assert not page_data['fallback']
    css=(dist/'assets/atlas-scoped.css').read_text()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':320,'height':900})
        page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+page_data['html']+'</body></html>')
        page.keyboard.press('Tab');page.keyboard.press('Enter')
        active=page.evaluate('document.activeElement.tagName')
        assert active=='BODY',f'R194 focus negative control changed: {active}'
        page.evaluate("document.documentElement.style.zoom='2'")
        width=page.evaluate('document.documentElement.scrollWidth')
        assert width>320,f'R194 zoom overflow negative control changed: {width}'
        browser.close()
    print(json.dumps({'R194_reproduction':'PASS','skip_link_focus':'BODY','zoom_200_scroll_width':width,'viewport_width':320}))
if __name__=='__main__':check()
