"""Offline screenshot/assertion QA. Never opens FV live site or submits forms."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
HTML=(ROOT/'R164-FOCUS-REVIEWER.html').read_text(encoding='utf-8')
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440):
        page=browser.new_page(viewport={'width':width,'height':800},device_scale_factor=1)
        page.set_content(HTML,wait_until='load')
        o=page.evaluate('''()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,heading:document.querySelector('h1')?.textContent,cta:document.querySelector('.button')?.getAttribute('href'),regions:document.querySelectorAll('[role="region"]').length,robots:document.querySelector('meta[name="robots"]')?.getAttribute('content')})''')
        assert o['scroll']<=o['client'],f'horizontal overflow {width}: {o}'
        assert o['cta']=='#review-only-download' and o['regions']==1
        assert 'noindex' in o['robots']
        page.screenshot(path=str(ROOT/f'offline_preview_{width}.png'),full_page=True)
        results.append({'viewport':width,'horizontal_overflow':False,'aria_region_count':1,'local_hash_only_cta':True,'noindex':True})
        page.close()
    browser.close()
(ROOT/'offline_browser_qa_evidence.json').write_text(json.dumps({'status':'PASS','type':'OFFLINE_REVIEWER_ONLY_NOT_WORDPRESS_NOT_EMAIL','results':results},indent=2)+'\n')
print('OFFLINE BROWSER QA',len(results),'viewports PASS')
