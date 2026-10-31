#!/usr/bin/env python3
"""R21 real Chromium checks for the exact PHP-generated private custody shelf.

In-memory PHP fixture: not actual installed WordPress, not native HTTP CSP,
not axe, not a screen reader, and not real-user Core Web Vitals.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture, INIT
from custody_receipts import EXPORT_NAMES

HERE=Path(__file__).resolve().parent
OUT=HERE/'r21-screenshots'
RESULT=HERE/'R21_CUSTODY_BROWSER_RESULTS.json'
WIDTHS=(320,360,390,768,1024,1440,1920)


def run():
    fixture, plugin_sha=get_fixture()
    OUT.mkdir(exist_ok=True,parents=True)
    report={'mode':'REAL_CHROMIUM_IN_MEMORY_DIGEST_VERIFIED_PHP_FIXTURE',
            'exact_plugin_sha256':plugin_sha,'results':[],'screenshots':[],
            'no_js':False,'touch':False,'narrow_container':False,
            'native_http_csp':False,'axe_core':False,'real_wordpress':False,'field_cwv':False}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},
                                    reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page();page.add_init_script(INIT)
            errors=[];requests=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url))
            page.set_content(fixture,wait_until='load')
            page.evaluate(INIT)
            shelf=page.locator('#fv-ex2-custody-receipts')
            assert shelf.count()==1
            assert shelf.get_by_role('heading',name='Download receipts for seven research evidence exports').count()==1
            assert shelf.locator('[data-custody-receipt]').count()==7
            assert shelf.locator('script,img,iframe,picture,svg,canvas').count()==0
            assert not requests,(width,'Unexpected requests',requests)
            assert not errors,(width,'Unexpected JS errors',errors)
            links=shelf.locator('a[download]')
            assert links.count()==7
            for i,name in enumerate(EXPORT_NAMES):
                item=shelf.locator('[data-custody-receipt]').nth(i)
                assert item.get_attribute('data-custody-receipt')==name
                code=item.locator('code[aria-label^="SHA-256 of "]')
                digest=code.text_content().strip()
                assert len(digest)==64 and set(digest)<=set('0123456789abcdef'),name
                assert code.get_attribute('aria-label')=='SHA-256 of '+name
                a=item.locator('a[download]')
                assert a.get_attribute('download')=='apollo-'+name
                assert 'fv_ex2_apollo_sealed_download' in a.get_attribute('href')
                assert a.evaluate('(n)=>n.getBoundingClientRect().height')>=43.9,(width,name)
            link=links.first
            link.focus()
            assert link.evaluate('(n)=>document.activeElement===n'),(width,'Keyboard focus unavailable')
            ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            active=[n for n in ax if not n.get('ignored')]
            accessible=[n.get('name',{}).get('value','') for n in active]
            for name in EXPORT_NAMES:
                assert any('Download and compare '+name in a for a in accessible),(width,name,'unnamed AX download')
            dims=page.evaluate('''()=>({vp:innerWidth,doc:document.documentElement.scrollWidth})''')
            assert dims['doc']<=width+1,(width,'Horizontal overflow',dims)
            if width in (390,1440):
                shot=OUT/f'r21-custody-receipts-{width}.png'
                shelf.screenshot(path=str(shot),animations='disabled',timeout=15000)
                report['screenshots'].append({'name':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            page.wait_for_timeout(130)
            perf=page.evaluate('window.__fv_cwv') or {}
            report['results'].append({'width':width,'status':'PASS',
                 'digest_cards':7,'keyboard_focus':True,'named_ax_downloads':7,
                 'min_link_height_px':round(min(links.evaluate_all('(a)=>a.map(x=>x.getBoundingClientRect().height)')),2),
                 'root_width':dims['doc'],'synthetic_lcp_ms':perf.get('lcp'),
                 'synthetic_cls':perf.get('cls'),'reduced_motion':width==320})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        shelf=page.locator('#fv-ex2-custody-receipts')
        assert shelf.locator('a[download]').count()==7
        for name in EXPORT_NAMES:
            assert shelf.locator('[data-custody-receipt="'+name+'"]').is_visible()
        report['no_js']=True;ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        assert page.locator('#fv-ex2-custody-receipts a').first.is_visible()
        assert page.locator('#fv-ex2-custody-receipts a').first.evaluate('(n)=>n.getBoundingClientRect().height')>=44
        report['touch']=True;ctx.close()
        ctx=browser.new_context(viewport={'width':780,'height':844},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        shelf=page.locator('#fv-ex2-custody-receipts')
        shelf.evaluate('(n)=>{n.style.width="390px";n.style.maxWidth="390px"}')
        columns=shelf.locator('.fv-ex2-receipts__list').evaluate('(n)=>getComputedStyle(n).gridTemplateColumns.split(" ").length')
        assert columns==1,('Content-box narrow WordPress layout',columns)
        report['narrow_container']=True;ctx.close();browser.close()
    RESULT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('R21_CUSTODY_BROWSER_PASS',len(report['results']),'widths; no-JS/touch/keyboard/AX/narrow container; screenshots',len(report['screenshots']))
    return report

if __name__=='__main__':run()
