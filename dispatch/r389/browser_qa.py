from pathlib import Path
from playwright.sync_api import sync_playwright
import json
html=Path(__file__).with_name('ISSUE02_CLEVER_HANS_REVIEW.html').read_text()
out=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,360,390,768,1200]:
        page=browser.new_page(viewport={'width':width,'height':850},device_scale_factor=1)
        page.set_content(html)
        page.wait_for_load_state('load')
        result=page.evaluate('''() => ({width:innerWidth, scrollWidth:document.documentElement.scrollWidth, bodyScroll:document.body.scrollWidth,h1:document.querySelectorAll('h1').length,links:document.querySelectorAll('a').length,primaryCta: [...document.querySelectorAll('a')].filter(a=>a.href.includes('/2026/11/02/mesmerism/')).length,lang:document.documentElement.lang,footerHold:document.body.textContent.includes('VALID_POSTAL_ADDRESS_REQUIRED') && document.body.textContent.includes('JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED')})''')
        result['mode']='normal'; result['pass']= result['scrollWidth']<=width and result['bodyScroll']<=width and result['h1']==1 and result['primaryCta']==1 and result['lang']=='en' and result['footerHold']
        if width in [320,390,768]:page.screenshot(path=str(Path(__file__).with_name(f'clever-hans-{width}.png')),full_page=True)
        out.append(result)
        page.close()
    for width in [320,390,768,1200]:
        page=browser.new_page(viewport={'width':width,'height':850},device_scale_factor=1)
        page.set_content(html)
        page.evaluate("document.body.style.zoom='2'")
        result=page.evaluate('''() => ({width:innerWidth, scrollWidth:document.documentElement.scrollWidth, bodyScroll:document.body.scrollWidth})''')
        result['mode']='200%-zoom';result['pass']=result['scrollWidth']<=width and result['bodyScroll']<=width
        out.append(result)
        page.close()
    browser.close()
print(json.dumps(out,indent=2))
Path(__file__).with_name('browser_qa.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(x['pass'] for x in out), 'offline browser QA failed'
