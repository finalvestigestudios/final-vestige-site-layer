"""Offline Chromium-only preview QA. Does not touch WordPress or email services."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parent
OUT=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        page=browser.new_page(viewport={'width':width,'height':850},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((BASE/'offline_review.html').read_text(encoding='utf-8'), wait_until='domcontentloaded')
        result=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth-innerWidth, issueRows:document.querySelectorAll('tbody tr').length,scriptCount:document.querySelectorAll('script').length,images:document.querySelectorAll('img').length, external:performance.getEntriesByType('resource').filter(x=>/^https?:/.test(x.name)).length, linkCount:document.querySelectorAll('a').length, mainTitle:document.querySelector('h1')?.innerText, caption:document.querySelector('caption')?.innerText})''')
        assert result['overflow']==0,(width,result)
        assert result['issueRows']==6 and result['scriptCount']==0 and result['external']==0 and result['linkCount']==0
        assert result['mainTitle']=='Measure what actually happened.'
        assert result['caption'].startswith('Six draft editions')
        assert not errors,errors
        page.keyboard.press('Tab')
        focused=page.evaluate('document.activeElement.getAttribute("aria-label")')
        assert focused=='Email campaign aggregate metrics',focused
        if width in (390,1440):page.screenshot(path=str(BASE/f'review-{width}.png'),full_page=True)
        OUT.append({'viewport_width':width,'overflow':result['overflow'],'issue_rows':6,'resource_requests':0,'page_errors':0,'keyboard_region':True,'passed':True})
        page.close()
    browser.close()
(BASE/'browser_qa_evidence.json').write_text(json.dumps({'kind':'offline_static_preview_only','not_wordpress_email_or_wcag_certification':True,'results':OUT},indent=2)+'\n')
print('Offline Chromium viewport QA:',len(OUT),'passed')
