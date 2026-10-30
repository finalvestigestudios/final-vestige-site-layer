#!/usr/bin/env python3
"""Real Playwright/Chromium source-link and AX smoke; offline fixture, NOT hosted CWV or axe."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf8')
results={'mode':'in-memory Chromium set_content (browser navigation blocked by admin policy)','viewport_results':{},'axe':'NOT_RUN','field_cwv':'NOT_MEASURED'}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in [320,360,390,768,1024,1440,1920]:
        page=browser.new_page(viewport={'width':width,'height':900},has_touch=width==390,
                              reduced_motion='reduce' if width==390 else 'no-preference')
        errors=[];requests=[]
        page.on('pageerror',lambda x:errors.append(str(x)))
        page.on('request',lambda x:requests.append(x.url))
        page.set_content(HTML,wait_until='load')
        info=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,
          sourceCount:document.querySelectorAll('details.ex2-source').length,
          ledgerCount:document.querySelectorAll('[data-ex2-claim-item]').length,
          exportLinks:document.querySelectorAll('.ex2-custody__downloads a').length})''')
        assert not errors and not requests and not info['overflow'],(width,errors,requests,info)
        assert (info['sourceCount'],info['ledgerCount'],info['exportLinks'])==(6,6,2),info
        if width in (390,1440):
            src=page.locator('.ex2-gallery__links a[href="#source-05"]')
            src.focus();page.keyboard.press('Enter');page.wait_for_timeout(70)
            assert page.locator('#source-05').evaluate('(x)=>x.open')
            assert page.evaluate('document.activeElement.closest("details")?.id')=='source-05'
            page.locator('#claim-filter').select_option('timing')
            assert page.locator('#custody-05').is_hidden()
            page.evaluate('location.hash="#custody-05"');page.wait_for_timeout(70)
            assert page.locator('#custody-05').is_visible()
            assert page.locator('#claim-filter').input_value()=='all'
            assert page.evaluate('document.activeElement.id')=='custody-05'
            if width==390:
                page.locator('.ex2-gallery__links a[href="#source-03"]').tap()
                page.wait_for_timeout(70)
                assert page.locator('#source-03').evaluate('(x)=>x.open')
        results['viewport_results'][str(width)]=info
        if width==390:
            page.locator('.ex2-gallery__links a[href="#source-05"]').focus()
            page.keyboard.press('Enter');page.wait_for_timeout(70)
            cdp=page.context.new_cdp_session(page);cdp.send('Accessibility.enable')
            nodes=cdp.send('Accessibility.getFullAXTree')['nodes']
            src=[x for x in nodes if x.get('role',{}).get('value')=='DisclosureTriangle' and x.get('name',{}).get('value')=='Open source drawer: record 05']
            assert len(src)==1
            assert any(v['name']=='expanded' and v.get('value',{}).get('value') for v in src[0].get('properties',[]))
            cdp.detach()
        page.close()
    nojs=browser.new_page(java_script_enabled=False,viewport={'width':320,'height':900})
    nojs.set_content(HTML)
    assert nojs.locator('[data-ex2-claim-item]:visible').count()==6
    assert nojs.locator('[data-ex2-claim-tools]').is_hidden()
    nojs.locator('#source-05 summary').click()
    assert nojs.locator('#source-05').evaluate('(x)=>x.open')
    nojs.close();browser.close()
(ROOT/'qa'/'SOURCE_TRAIL_GATED_BROWSER.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n',encoding='utf8')
print('SOURCE_TRAIL_PLAYWRIGHT_PASS: 7 widths, deep links, filter restore, touch, native no-JS, Chrome AX expanded state')
