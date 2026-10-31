#!/usr/bin/env python3
"""R25 real Chromium print CSS + no-JS evidence custody acceptance.

Exact generated private PHP through an in-memory Playwright document; NOT a
real WordPress install, browser HTTP/CSP, screen reader, axe or field CWV.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from browser_exact import get_fixture, INIT
WIDTHS=(320,360,390,768,1024,1440,1920)
SHOTS=HERE/'r25-screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
RESULT=HERE/'R25_PRINT_BROWSER_RESULTS.json'

def run():
    html,plugin_hash=get_fixture()
    report={'environment':'real Chromium Playwright page.set_content; PHP WordPress shim; not genuine WP/HTTP/CSP',
            'browser':'system /usr/bin/chromium', 'widths':list(WIDTHS),
            'canonical_apollo_pin':'74375657f2cdaac0710f94c6de6c24534ee06858',
            'private_plugin_sha256':plugin_hash,'axe_core':'NOT_EXECUTED_NO_PINNED_VENDOR_BUNDLE',
            'hosted_core_web_vitals':'NOT_MEASURED','measures':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':960},reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page();page.add_init_script(INIT)
            errors=[]; requests=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.on('request',lambda req:requests.append(req.url))
            page.set_content(html,wait_until='load')
            page.evaluate(INIT)
            transcript=page.locator('#fv-ex2-print-transcript')
            assert transcript.count()==1 and not transcript.is_visible(),(width,'print transcript leaked on screen')
            assert transcript.locator('[data-r25-print-record]').count()==6
            assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
            page.locator('#fv-ex2-lens-1967').check()
            assert page.locator('#source-concordance [data-concordance-record]:visible').count()==3
            page.locator('#fv-ex2-lens-all').check()
            assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
            assert page.locator('h1').count()==1
            page.emulate_media(media='print')
            assert transcript.is_visible(),(width,'print transcript not visible')
            assert transcript.locator('[data-r25-print-record]:visible').count()==6
            assert not page.locator('#source-concordance').is_visible(),(width,'interactive casefile printed alongside source ledger')
            assert not page.locator('#fv-ex2-custody-receipts').is_visible()
            assert not page.locator('#fv-ex2-wayfinder').is_visible()
            text=transcript.inner_text()
            assert text.count('LINK ONLY — IMAGE REUSE NOT CLEARED')==6
            assert 'IDENTITY REVIEW HOLD' in text and 'S67-19766' in text and 'S66-30236' in text
            assert 'zero geographic pins/edges admitted' in text
            sources=transcript.locator('a[href^="https://www.nasa.gov/image-"]')
            assert sources.count()==6
            assert transcript.locator('img,iframe,script').count()==0
            assert not any(x in transcript.inner_html() for x in ('_wpnonce','admin-ajax','data-lat=','data-lon='))
            sample=sources.first.evaluate('(e)=>getComputedStyle(e,"::after").content')
            assert 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/' in sample,(width,sample)
            styles=transcript.evaluate('''e=>{const s=getComputedStyle(e);return {color:s.color,bg:s.backgroundColor,font:s.fontFamily,display:s.display}}''')
            assert styles['color']=='rgb(17, 17, 17)' and styles['bg']=='rgb(255, 255, 255)',(width,styles)
            dims=page.evaluate('''()=>({root:document.documentElement.scrollWidth, viewport:document.documentElement.clientWidth})''')
            assert dims['root']<=dims['viewport']+1,(width,dims,'print horizontal overflow')
            if width in (390,1440):
                dest=SHOTS/f'r25-print-ledger-{width}.png'
                transcript.screenshot(path=str(dest),animations='disabled',timeout=20000)
                report['screenshots'].append({'filename':dest.name,'sha256':sha256(dest.read_bytes()).hexdigest()})
            metrics=page.evaluate('window.__fv_cwv') or {}
            assert not errors and not requests,(width,errors,requests)
            report['measures'].append({'width':width,'status':'PASS','print_records':6,'screen_records':6,
                 'no_download_nonce':True,'nasa_source_urls':6,'print_opaque_image_count':0,
                 'print_root_width':dims['root'],'styles':styles,'page_errors':errors,
                 'lab_lcp_ms':metrics.get('lcp'),'lab_cls':metrics.get('cls')})
            ctx.close()
        # Truly disabled-JS print view; no browser script or CSS :has dependence.
        ctx=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
        page=ctx.new_page();page.set_content(html,wait_until='load')
        assert page.locator('#fv-ex2-print-transcript').count()==1
        page.emulate_media(media='print')
        assert page.locator('#fv-ex2-print-transcript [data-r25-print-record]:visible').count()==6
        assert 'IDENTITY REVIEW HOLD' in page.locator('#fv-ex2-print-transcript').inner_text()
        report['no_javascript_print']='PASS';ctx.close();browser.close()
    RESULT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R25 Chromium print: 7/7 widths; 6/6 NASA records; no-JS PASS')
    return report
if __name__=='__main__':run()
