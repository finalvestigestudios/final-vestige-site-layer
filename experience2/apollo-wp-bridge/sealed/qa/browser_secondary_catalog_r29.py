#!/usr/bin/env python3
"""Chromium-only R29 editorial component checks; no hosted WP, CSP, axe or CWV claims."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
from qa.browser_exact import get_fixture, INIT

HERE=Path(__file__).resolve().parent
WIDTHS=(320,360,390,768,1024,1440,1920)
SHOTS=HERE/'r29-screenshots'
REPORT=HERE/'R29_CATALOG_BROWSER_RESULTS.json'


def run():
    SHOTS.mkdir(parents=True, exist_ok=True)
    html,plugin_hash=get_fixture()
    receipt={
        'scope':'Real Chromium on exact generated staging PHP HTML via Playwright page.set_content; NOT installed WordPress or HTTP CSP',
        'axe_core':'NOT_RUN_NO_VERIFIED_OFFLINE_BUNDLE',
        'core_web_vitals':'NOT_A_HOSTED_MEASUREMENT',
        'source_plugin_sha256':plugin_hash,
        'widths':list(WIDTHS),'results':[],'screenshots':[],
    }
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce' if width==320 else 'no-preference')
            page=context.new_page()
            page.add_init_script(INIT)
            errors=[];requests=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url))
            page.set_content(html,wait_until='load')
            page.evaluate(INIT)
            cross=page.locator('#fv-ex2-research-desk-crosswalk')
            assert cross.count()==1,(width,'missing crosswalk')
            assert cross.locator('[data-secondary-catalog-review="hold"]').count()==1
            cross.locator('summary').first.focus()
            page.keyboard.press('Enter')
            assert cross.evaluate('(e)=>e.open'),(width,'keyboard disclosure closed')
            identity=page.locator('#fv-ex2-catalog-identity')
            identity.locator('summary').focus()
            page.keyboard.press('Enter')
            assert identity.locator('details').evaluate('(e)=>e.open'),(width,'keyboard nested disclosure closed')
            hint=identity.locator('[data-secondary-source-status="not-first-party"]')
            assert hint.is_visible(),(width,'source qualification hidden')
            note=hint.inner_text()
            assert 'first-party NASA identifier' in note and 'release hold' in note
            assert cross.locator('[data-crosswalk-id]').count()==6
            assert cross.locator('[data-crosswalk-review="hold"]').count()==1
            assert page.locator('#atlas [data-lat],#atlas [data-lon]').count()==0
            link=identity.locator('[data-secondary-catalog-review="hold"] a')
            assert link.count()==1
            assert link.get_attribute('href')=='https://timelessmoon.getarchive.net/amp/media/astro-grissom-chaffee-white-in-va-in-mission-simulator-and-on-complex-34-a5cc67'
            assert link.get_attribute('rel')=='noopener noreferrer'
            assert link.get_attribute('referrerpolicy')=='no-referrer'
            assert link.get_attribute('target')=='_blank'
            heights=page.evaluate('''()=>{
              const e=document.documentElement;
              const r=document.querySelector('#fv-ex2-catalog-identity').getBoundingClientRect();
              return {scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,identityWidth:r.width};
            }''')
            assert heights['scrollWidth']<=heights['clientWidth']+1,(width,heights,'horizontal overflow')
            assert not errors,(width,errors)
            if width in (390,1440):
                path=SHOTS/f'r29-nasa-catalog-{width}.png'
                identity.screenshot(path=str(path),animations='disabled',timeout=20000)
                receipt['screenshots'].append({'name':path.name,'sha256':sha256(path.read_bytes()).hexdigest()})
            receipt['results'].append({'width':width,'keyboard_details':True,'editorial_hold_visible':True,
                'same_image_not_asserted':True,'geopins':0,'external_asset_requests':requests,
                'horizontal_overflow':False,'page_errors':errors})
            context.close()
        # Native details disclosure, both open without client JavaScript.
        context=browser.new_context(viewport={'width':390,'height':850},java_script_enabled=False)
        page=context.new_page();page.set_content(html,wait_until='load')
        page.locator('#fv-ex2-research-desk-crosswalk>summary').click()
        page.locator('#fv-ex2-catalog-identity summary').click()
        assert page.locator('[data-secondary-source-status="not-first-party"]').is_visible()
        assert page.locator('#source-concordance [data-concordance-record]').count()==6
        receipt['no_javascript_native_details']='PASS';context.close();browser.close()
    REPORT.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R29 real Chromium: 7 widths PASS; keyboard/nested details PASS; no-JS PASS')
    return receipt

if __name__=='__main__':run()
