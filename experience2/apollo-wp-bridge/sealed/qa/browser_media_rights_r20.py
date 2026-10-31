#!/usr/bin/env python3
"""Chromium R20: exact PHP fixture, NASA media-review accessibility and no-JS.

Synthetic in-memory browser checks; does NOT claim axe, WordPress hosting,
HTTP CSP, Safari, real-user CWV or legal rights clearance.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture, INIT

HERE=Path(__file__).resolve().parent
OUT=HERE/'r20-screenshots'
RESULT=HERE/'R20_MEDIA_BROWSER_RESULTS.json'
WIDTHS=(320,360,390,768,1024,1440,1920)


def run():
    fixture, plugin_sha = get_fixture()
    OUT.mkdir(exist_ok=True,parents=True)
    report={'test_kind':'REAL_CHROMIUM_IN_MEMORY_PHP_FIXTURE','plugin_sha256':plugin_sha,
            'widths':[],'screenshots':[],'no_js':False,'touch':False,'zoom_200_equivalent':False,
            'real_wordpress':False,'verified_axe':False,'http_csp_enforcement':False,
            'field_core_web_vitals':False}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':930},
                                    reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page(); page.add_init_script(INIT)
            errors=[];requests=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.on('request',lambda req:requests.append(req.url))
            page.set_content(fixture,wait_until='load')
            page.evaluate(INIT)
            rights=page.locator('#fv-ex2-media-rights')
            assert rights.count()==1
            assert rights.locator('h2').count()==1
            assert rights.locator('[data-media-review]').count()==6
            assert rights.locator('[data-media-hold="true"]').count()==6
            assert rights.locator('details').count()==6
            assert rights.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6
            assert rights.locator('a[href="https://www.nasa.gov/nasa-brand-center/images-and-media/"]').count()==1
            assert rights.locator('a[download="apollo-media-rights-hold.json"]').count()==1
            assert rights.locator('img,picture,svg,canvas,iframe').count()==0
            assert page.locator('img,picture,svg,canvas,iframe').count()==0
            assert not errors,(width,errors)
            assert not requests,(width,'No external resources may load',requests)
            controls=rights.locator('summary').evaluate_all(
                '(nodes)=>nodes.map(n=>({height:n.getBoundingClientRect().height,width:n.getBoundingClientRect().width}))')
            assert len(controls)==6 and all(c['height']>=44 and c['width']>=40 for c in controls),(width,controls)
            first=rights.locator('details').first
            first.locator('summary').focus();page.keyboard.press('Enter')
            assert first.evaluate('(n)=>n.open'),(width,'keyboard disclosure unavailable')
            assert first.locator('a[href="#source-01"]').count()==1
            assert first.locator('a[href="#stage-01"]').count()==1
            assert 'S67-19766' in first.inner_text()
            for a in first.locator('a').all():
                assert a.evaluate('(n)=>n.getBoundingClientRect().height')>=43.9,(width,'short link hit target',a.inner_text())
            ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            active=[n for n in ax if not n.get('ignored')]
            names=[n.get('name',{}).get('value','') for n in active]
            assert any('Inspect NASA catalog record' in n for n in names),(width,'catalog link not exposed')
            assert any('Review chronology 01' in n for n in names),(width,'chronology link missing from AX')
            scroll=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})')
            assert scroll['document']<=width+1,(width,'horizontal page overflow',scroll)
            if width in (390,1440):
                shot=OUT/f'r20-media-rights-{width}.png'
                rights.screenshot(path=str(shot),animations='disabled',timeout=15000)
                report['screenshots'].append({'filename':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            first.locator('summary').focus();page.keyboard.press('Enter')
            assert not first.evaluate('(n)=>n.open')
            page.wait_for_timeout(70)
            metrics=page.evaluate('window.__fv_cwv')
            report['widths'].append({'px':width,'disclosures':6,'native_keyboard':'PASS',
                'touch_target_height_min_px':round(min(x['height'] for x in controls),2),
                'ax_catalog_link_exposed':'PASS','root_scroll_px':scroll['document'],
                'synthetic_lcp_ms':metrics.get('lcp'),'synthetic_cls':metrics.get('cls'),
                'reduced_motion':width==320})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        rights=page.locator('#fv-ex2-media-rights');rights.locator('summary').last.click()
        assert rights.locator('details').last.evaluate('(n)=>n.open')
        assert rights.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6
        report['no_js']=True
        ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        d=page.locator('#fv-ex2-media-rights details').nth(2)
        d.locator('summary').tap()
        assert d.evaluate('(n)=>n.open')
        report['touch']=True
        ctx.close()
        ctx=browser.new_context(viewport={'width':780,'height':900},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        rights=page.locator('#fv-ex2-media-rights')
        rights.evaluate('(n)=>{n.style.width="390px";n.style.maxWidth="390px"}')
        columns=rights.locator('.fv-ex2-rights__cards').evaluate('(n)=>getComputedStyle(n).gridTemplateColumns.split(" ").length')
        assert columns==1,('narrow WordPress container failed',columns)
        report['zoom_200_equivalent']=True
        ctx.close();browser.close()
    RESULT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R20_MEDIA_BROWSER_PASS',len(report['widths']),'viewports','no JS / touch / narrow WP container; screenshots',len(report['screenshots']))
    return report

if __name__=='__main__':run()
