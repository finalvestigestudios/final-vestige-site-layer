"""R176 offline-only real Chromium QA; never claim fixture is installed WordPress."""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

WIDTHS=(320,360,390,768,1440,1920)
PERF="""(() => { window.__fvPerf={lcp:null,cls:0,shifts:0};
try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__fvPerf.lcp=Math.round(e.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput){window.__fvPerf.cls+=e.value;window.__fvPerf.shifts++}})).observe({type:'layout-shift',buffered:true})}catch(e){}
})()"""
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

async def run(source:Path, dest:Path, axe:Path|None):
    dest.mkdir(parents=True,exist_ok=True)
    html=source.read_text(encoding='utf-8')
    assert html.count('data-fvx-r175-catalog-review=')==1
    assert html.count('data-fvx-r174-media-custody=')==6
    assert '<p class="fv-ex2-catalog-warning">' in html
    if html.lstrip().startswith('<section'):
        html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>'+html+'</body></html>'
    no_css=re.sub(r'<style(?:\s[^>]*)?>','<style media="not all">',html,flags=re.I)
    (dest/'R176-UNPUBLISHED.html').write_text(html,encoding='utf-8')
    errors=[]; hashes={}; performance={}; assertions=0
    axe_result={'status':'NOT_RUN','reason':'No independently obtained local axe-core distribution supplied'}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for repeat in (1,2):
            for w in WIDTHS:
                context=await browser.new_context(viewport={'width':w,'height':850},device_scale_factor=1,
                    reduced_motion='reduce' if w==390 else 'no-preference',has_touch=w in (390,768))
                await context.add_init_script(PERF)
                page=await context.new_page()
                page.on('pageerror', lambda e:errors.append(str(e)))
                await page.set_content(html,wait_until='load')
                await page.wait_for_timeout(120)
                assert await page.locator('[data-fvx-record]').count()==6; assertions+=1
                assert await page.locator('[data-fvx-r175-catalog-review]').count()==1; assertions+=1
                assert await page.locator('[data-fvx-r174-media-custody]').count()==6; assertions+=1
                assert await page.locator('a').count()==14; assertions+=1
                notice=page.locator('[data-fvx-r175-catalog-review]')
                assert 'Catalog identification not verified.' in await notice.inner_text(); assertions+=1
                assert 'photograph. ' in await notice.text_content(); assertions+=1
                assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'); assertions+=1
                out=dest/f'r176-{w}-{repeat}.png'
                await page.screenshot(path=str(out),full_page=True,animations='disabled')
                hashes[f'{w}-{repeat}']=sha(out)
                await page.locator('details summary').first.focus()
                await page.keyboard.press('Enter')
                assert await page.locator('details').first.evaluate('(el)=>el.open'); assertions+=1
                search=page.locator('[data-fvx-search]').first
                if await search.count() and await search.is_visible():
                    await search.fill('S67-19766')
                    assert await page.locator('[data-fvx-record]:visible').count()==1; assertions+=1
                    await search.fill('not-a-match')
                    assert await page.locator('[data-fvx-record]:visible').count()==0; assertions+=1
                    await search.fill('')
                performance[f'{w}-{repeat}']=await page.evaluate('window.__fvPerf')
                await context.close()
        nojs=await browser.new_context(java_script_enabled=False,viewport={'width':320,'height':850})
        pg=await nojs.new_page(); await pg.set_content(html)
        assert await pg.locator('[data-fvx-record]:visible').count()==6;assertions+=1
        await nojs.close()
        nocss=await browser.new_context(java_script_enabled=False,viewport={'width':320,'height':850})
        pg=await nocss.new_page(); await pg.set_content(no_css)
        assert 'photograph. ' in await pg.locator('[data-fvx-r175-catalog-review]').text_content();assertions+=1
        assert 'does not confirm' in await pg.locator('[data-fvx-r175-catalog-review]').text_content();assertions+=1
        await pg.screenshot(path=str(dest/'no-css-no-js.png'),full_page=True)
        await nocss.close()
        hc=await browser.new_context(forced_colors='active',viewport={'width':390,'height':850})
        pg=await hc.new_page(); await pg.set_content(html)
        assert await pg.locator('[data-fvx-r175-catalog-review]').is_visible();assertions+=1
        await pg.screenshot(path=str(dest/'forced-colors.png'),full_page=True)
        await hc.close()
        if axe:
            if not axe.is_file() or axe.stat().st_size<150000: raise ValueError('axe-core bundle missing/untrustworthy: HOLD')
            ac=await browser.new_context();ap=await ac.new_page();await ap.set_content(html)
            await ap.add_script_tag(path=str(axe))
            result=await ap.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}})')
            axe_result={'status':'EXECUTED','violations':[{'id':x['id'],'impact':x['impact'],'nodes':len(x['nodes'])} for x in result['violations']],
                'passes':len(result['passes']),'incomplete':len(result['incomplete'])}
            await ac.close()
        await browser.close()
    reproduced=sum(hashes[f'{w}-1']==hashes[f'{w}-2'] for w in WIDTHS)
    assert reproduced==len(WIDTHS), 'screenshot non-determinism: HOLD'
    assert not errors, f'Chromium page errors: {errors}'
    report={'status':'OFFLINE_ONLY','source_sha256':sha(source),'viewports':WIDTHS,
      'real_chromium_contexts':16+(1 if axe else 0),'assertions':assertions,'reproduced_screenshots':reproduced,
      'screenshot_sha256':hashes,'browser_performance_fixture_only':performance,'pageerrors':errors,
      'axe':axe_result,'installed_wordpress':False,'actual_media_delivery_verified':False,
      'commercial_conversion_verified':False}
    (dest/'browser_receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('screenshot_sha256','browser_performance_fixture_only')},sort_keys=True))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--fixture',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--axe',type=Path)
    args=parser.parse_args()
    asyncio.run(run(args.fixture,args.out,args.axe))
