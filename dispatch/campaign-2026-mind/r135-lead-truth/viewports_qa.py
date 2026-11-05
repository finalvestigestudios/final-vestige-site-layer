"""Offline responsive reviewer smoke test; not a live website or inbox test."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
p=Path(__file__).resolve().parent
html=(p/'reviewer.html').read_text()
rows=[]
with sync_playwright() as play:
    b=play.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in [320,390,768,1440]:
        page=b.new_page(viewport={'width':width,'height':850})
        page.set_content(html)
        stats=page.evaluate('''() => ({width: innerWidth, scrollWidth: document.documentElement.scrollWidth, headings: document.querySelectorAll('h1').length, links: document.querySelectorAll('a[href]').length})''')
        stats['no_horizontal_overflow']=stats['scrollWidth']<=stats['width']
        assert stats['no_horizontal_overflow'] and stats['headings']==1 and stats['links']>=3,stats
        page.screenshot(path=str(p/f'reviewer-{width}.png'),full_page=True)
        rows.append(stats)
        page.close()
    b.close()
(p/'chromium-viewports.json').write_text(json.dumps({'mode':'OFFLINE_BROWSER_ONLY','results':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
