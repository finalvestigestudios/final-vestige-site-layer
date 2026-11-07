"""R177 real Chromium QA of source-derived offline fixture, NOT installed WordPress.

Browses with genuine JS, keyboard, touch, forced colors, reduced motion, no-JS;
measures fixture LCP/CLS only. Native axe-core and real-site tests remain gated.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

WIDTHS=[320,360,390,768,1440,1920]
PERF='''(() => {window.__r177={lcp:null,cls:0};
try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r177.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(_){}
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__r177.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(_){}
})();'''

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def render(html:str,js:str,css:str):
    soup=BeautifulSoup(html,'html.parser')
    script=soup.select_one('script')
    assert script is not None
    script.string=js
    style=soup.new_tag('style')
    style.string=css
    soup.head.append(style)
    return str(soup)

async def run(base:str,original:str,improved:str,css:str,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    old_html=render(base,original,css);new_html=render(base,improved,css)
    (out/'baseline-UNPUBLISHED.html').write_text(old_html)
    (out/'enhanced-UNPUBLISHED.html').write_text(new_html)
    asserts=0;errors=[];hashes={};performances={};network_calls=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        # Reproduce real defect against exact historical JS from PR #158, offline source-derived DOM.
        bctx=await browser.new_context(viewport={'width':390,'height':850})
        baseline=await bctx.new_page();await baseline.set_content(old_html,wait_until='load')
        baseline_search=baseline.locator('input[data-fvx-search]')
        await baseline_search.fill('Catalog identification not verified.')
        assert await baseline.locator('[data-fvx-record]:visible').count()==0;asserts+=1
        await baseline.screenshot(path=str(out/'baseline-390-no-provenance-results.png'),animations='disabled',full_page=True)
        await bctx.close()
        for repeat in [1,2]:
            for w in WIDTHS:
                ctx=await browser.new_context(viewport={'width':w,'height':850},device_scale_factor=1,
                   has_touch=w in [390,768],reduced_motion='reduce' if w in [320,390] else 'no-preference')
                await ctx.add_init_script(PERF)
                pg=await ctx.new_page()
                pg.on('pageerror',lambda e:errors.append(str(e)))
                pg.on('request',lambda r:network_calls.append(r.url))
                await pg.set_content(new_html,wait_until='load');await pg.wait_for_timeout(120)
                assert await pg.locator('[data-fvx-record]:visible').count()==6;asserts+=1
                assert await pg.locator('[data-fvx-r174-media-custody]').count()==6;asserts+=1
                assert await pg.locator('a').count()==14;asserts+=1
                assert await pg.locator('[data-fvx-tools]').is_visible();asserts+=1
                assert '6 of 6' in await pg.locator('[data-fvx-status]').inner_text();asserts+=1
                assert not await pg.evaluate('document.documentElement.scrollWidth > innerWidth + 1');asserts+=1
                path=out/f'r177-{w}-{repeat}.png'
                await pg.screenshot(path=str(path),animations='disabled',full_page=True)
                hashes[f'{w}-{repeat}']=sha(path)
                input=pg.locator('input[data-fvx-search]')
                await input.fill('Catalog identification not verified.')
                assert await pg.locator('[data-fvx-record]:visible').count()==1;asserts+=1
                assert '1 of 6' in await pg.locator('[data-fvx-status]').inner_text();asserts+=1
                assert await pg.locator('[data-fvx-r175-catalog-review]').is_visible();asserts+=1
                await input.fill('Photograph provenance')
                assert await pg.locator('[data-fvx-record]:visible').count()==6;asserts+=1
                await input.fill('no-result-string-r177')
                assert await pg.locator('[data-fvx-record]:visible').count()==0;asserts+=1
                assert await pg.locator('[data-fvx-empty]').is_visible();asserts+=1
                assert '0 of 6' in await pg.locator('[data-fvx-status]').inner_text();asserts+=1
                await input.fill('')
                assert await pg.locator('[data-fvx-record]:visible').count()==6;asserts+=1
                assert await pg.locator('[data-fvx-empty]').is_hidden();asserts+=1
                await pg.locator('details summary').first.focus()
                await pg.keyboard.press('Enter')
                assert await pg.locator('details').first.evaluate('(el)=>el.open');asserts+=1
                # Optional search is intentionally not a dependency for the source record.
                performances[f'{w}-{repeat}']=await pg.evaluate('window.__r177')
                await ctx.close()
        nctx=await browser.new_context(java_script_enabled=False,viewport={'width':320,'height':850})
        pg=await nctx.new_page();await pg.set_content(new_html)
        assert await pg.locator('[data-fvx-record]:visible').count()==6;asserts+=1
        assert await pg.locator('[data-fvx-tools]').is_hidden();asserts+=1
        assert 'Catalog identification not verified.' in await pg.locator('[data-fvx-r175-catalog-review]').text_content();asserts+=1
        await pg.screenshot(path=str(out/'no-js-320.png'),full_page=True)
        await nctx.close()
        hctx=await browser.new_context(forced_colors='active',viewport={'width':390,'height':850})
        pg=await hctx.new_page();await pg.set_content(new_html)
        await pg.locator('input[data-fvx-search]').fill('catalog identification not verified')
        assert await pg.locator('[data-fvx-r175-catalog-review]').is_visible();asserts+=1
        await pg.screenshot(path=str(out/'forced-colors-390.png'),full_page=True)
        await hctx.close()
        await browser.close()
    matched=sum(hashes[f'{w}-1']==hashes[f'{w}-2'] for w in WIDTHS)
    assert matched==len(WIDTHS),f'nondeterministic screenshots {matched}/6'
    assert not errors,errors
    assert not network_calls, network_calls
    report={'verdict':'OFFLINE_CHROMIUM_PASS_NOT_WORDPRESS_ACCEPTANCE','assertions':asserts,
      'baseline_confirmed_defect':'Searching catalog caution yields 0 / 6 with original verified JS',
      'replacement_verified_behavior':'Catalog caution 1/6, photograph provenance 6/6, no-result 0/6, reset 6/6',
      'widths':WIDTHS,'browser_contexts':16,'reproducible_screenshots':matched,
      'screenshot_sha256':hashes,'page_errors':errors,'network_requests':network_calls,
      'fixture_LCP_CLS_NOT_REAL_SITE':performances,'genuine_axe_core':'NOT_RUN',
      'assisted_screen_reader':'NOT_RUN','wordpress_staging':'NOT_TESTED','real_media_delivery':'NOT_TESTED',
      'revenue_and_paid_conversion':'NOT_COMPUTABLE'}
    (out/'browser_receipt.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('screenshot_sha256','fixture_LCP_CLS_NOT_REAL_SITE')},sort_keys=True))
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for x in ['fixture','original-js','replacement-js','css','out']:a.add_argument('--'+x,required=True,type=Path)
    v=a.parse_args();asyncio.run(run(v.fixture.read_text(),v.original_js.read_text(),v.replacement_js.read_text(),v.css.read_text(),v.out))
