"""Local only: screenshot six unsent offline HTML files. No external navigation or requests."""
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

root = Path(sys.argv[1]).resolve()
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for w in (360,390,768,1440):
        page=browser.new_page(viewport={'width':w,'height':860},device_scale_factor=1)
        bad=[]
        page.on('pageerror',lambda e:bad.append(str(e)))
        page.route('http://**/*',lambda route:route.abort())
        page.route('https://**/*',lambda route:route.abort())
        for i in range(1,7):
            file=root/f'issue-{i:02d}.html'
            page.set_content(file.read_text(encoding='utf-8'),wait_until='load')
            widths=page.evaluate('''() => ({vw: innerWidth, doc:document.documentElement.scrollWidth, body: document.body.scrollWidth, titles:document.querySelectorAll('h1').length, links: [...document.querySelectorAll('a[href]')].length, alert:document.body.innerText.includes('DO NOT SEND')})''')
            good=(widths['doc']<=w+1 and widths['titles']==1 and widths['alert'] and not bad)
            checks.append({'width':w,'issue':i,'pass':good,**widths,'js_errors':bad.copy()})
            if not good: print('FAIL',checks[-1])
            page.screenshot(path=str(root/f'qa-{i:02d}-{w}.png'),full_page=True)
        page.close()
    browser.close()
(root/'browser-evidence.json').write_text(json.dumps({'checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks)},indent=2)+'\n')
print('PASSED',sum(x['pass'] for x in checks),'/',len(checks))
if not all(x['pass'] for x in checks):sys.exit(2)
