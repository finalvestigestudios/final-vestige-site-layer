#!/usr/bin/env python3
"""Actual Chromium/Playwright Atlas admission UX and fail-open/no-JS checks.

Uses the exact generated PHP output in an in-memory browser, not an installed
WordPress host. Does not imply verified HTTP CSP, WCAG, axe, or field CWV.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture, INIT

HERE=Path(__file__).resolve().parent
OUT=HERE/'r19-screenshots'
RESULT=HERE/'R19_ATLAS_BROWSER_RESULTS.json'
WIDTHS=(320,360,390,768,1024,1440,1920)

def run():
    fixture,php_sha=get_fixture()
    OUT.mkdir(exist_ok=True,parents=True)
    report={'status':'PASS_CHROMIUM_IN_MEMORY_ONLY', 'php_plugin_sha256':php_sha,
            'axe_status':'NOT_RUN_VERIFIED_BUNDLE_UNAVAILABLE',
            'word_press_staging_installed':False,'http_csp_not_browser_verified':True,
            'widths':[],'screenshots':[],'no_js':False,'nested_420px':False}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':930},
                reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page()
            page.add_init_script(INIT)
            errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
            page.set_content(fixture,wait_until='load')
            page.evaluate(INIT)
            atlas=page.locator('#atlas')
            admission=atlas.locator('#fv-ex2-atlas-admission')
            assert admission.count()==1
            assert not admission.evaluate('(n)=>n.open'),(width,'must be closed by default')
            admission.locator('summary').focus()
            assert admission.locator('summary').evaluate('n=>n.getBoundingClientRect().height')>=44
            page.keyboard.press('Enter')
            assert admission.evaluate('(n)=>n.open'),(width,'native keyboard open')
            assert admission.locator('[data-admission-record]:visible').count()==6
            assert admission.locator('a[href^="https://finalvestige.com/"]').count()==6
            assert admission.locator('a[download="apollo-atlas-admission.json"]').count()==1
            assert atlas.locator('[data-ex2-atlas-item]').count()==6
            assert atlas.locator('[data-ex2-atlas-item]:visible').count()==6
            assert page.locator('img,iframe,canvas,svg').count()==0,(width,'no media embedded')
            assert not atlas.locator('[data-lat],[data-lng],[data-lon],[data-geo],[data-edge]').count()
            assert not page.locator('a[href^="data:"]').count()
            assert not page.locator('a[href^="javascript:"]').count()
            assert not errors,(width,errors)
            widths=page.evaluate('({viewport:innerWidth,scroll:document.documentElement.scrollWidth})')
            assert widths['scroll']<=width+1,(width,'root horizontal overflow',widths)
            locations=admission.locator('.fv-ex2-atlas-admission__records').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
            assert locations in (1,2),(width,locations)
            cdp=ctx.new_cdp_session(page)
            ax=cdp.send('Accessibility.getFullAXTree')['nodes']
            links=[n for n in ax if not n.get('ignored') and n.get('role',{}).get('value')=='link']
            # Ensure new source links are exposed to screen-reader accessibility tree.
            named=[n for n in links if n.get('name',{}).get('value','').strip().startswith('Open original published investigation')]
            assert len(named)==6,(width,'atlas links not named/exposed',len(named))
            if width in (390,1440):
                shot=OUT/f'r19-atlas-admission-{width}.png'
                admission.screenshot(path=str(shot),animations='disabled',timeout=15000)
                report['screenshots'].append({'name':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            # Native closing interaction remains keyboard accessible.
            admission.locator('summary').focus();page.keyboard.press('Enter')
            assert not admission.evaluate('n=>n.open')
            report['widths'].append({'px':width,'root_scroll_px':widths['scroll'],
                'native_keyboard_details':'PASS','visible_review_records_open':6,
                'accessible_named_published_links_open':len(named),'layout_columns':locations})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        d=page.locator('#fv-ex2-atlas-admission')
        d.locator('summary').click()
        assert d.evaluate('(n)=>n.open') and d.locator('[data-admission-record]:visible').count()==6
        assert page.locator('[data-ex2-atlas-item]:visible').count()==6
        assert page.locator('[data-ex2-atlas-tools]').is_hidden()
        report['no_js']=True
        ctx.close()
        ctx=browser.new_context(viewport={'width':1920,'height':930},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        atlas=page.locator('#atlas')
        atlas.evaluate('(n)=>{n.style.width="420px";n.style.maxWidth="420px"}')
        d=atlas.locator('#fv-ex2-atlas-admission');d.locator('summary').click()
        count=d.locator('.fv-ex2-atlas-admission__records').evaluate('(n)=>getComputedStyle(n).gridTemplateColumns.split(" ").length')
        assert count==1,('narrow embedded WordPress column should be single-column',count)
        report['nested_420px']=True
        ctx.close();browser.close()
    RESULT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R19_ATLAS_BROWSER_PASS',len(report['widths']),'viewports; 390px no JS; 420px CMS column; screenshots',len(report['screenshots']))
    return report

if __name__=='__main__':run()
