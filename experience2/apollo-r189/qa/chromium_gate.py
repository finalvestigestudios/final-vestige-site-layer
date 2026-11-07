#!/usr/bin/env python3
"""Real Chromium DOM checks with synthetic URL; offline fixture, NOT installed WP/CSP/axe."""
import asyncio, hashlib, json, sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/'dist/templates/atlas-fragment.html').read_text()
CSS = (ROOT/'dist/assets/atlas-scoped.css').read_text()
JS = (ROOT/'dist/assets/campaign-handoff.js').read_text()
DOC = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style></head><body>'+HTML+'</body></html>'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BASE='https://finalvestige.com/apollo-atlas/?utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content='
CASES=[('320',320,'youtube',True),('360',360,'tiktok',True),('390',390,'youtube',True),
       ('768',768,'facebook',True),('1440',1440,'youtube',True),('1920',1920,'youtube',True),
       ('390-nojs',390,'youtube',False),('390-duplicate',390,'youtube&x=1&utm_source=tiktok',True),
       ('390-invalid',390,'unknown',True),('390-reduced',390,'youtube',True)]
async def run(out):
    out.mkdir(parents=True,exist_ok=True)
    results=[]; failures=[]; checks=0
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,width,source,enabled in CASES:
            ctx=await browser.new_context(viewport={'width':width,'height':800},device_scale_factor=1,
                  java_script_enabled=enabled,reduced_motion='reduce' if name.endswith('reduced') else 'no-preference')
            page=await ctx.new_page()
            errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
            await page.goto('about:blank');await page.set_content(DOC)
            url=BASE+'apollo_lf_001&utm_source='+source
            if enabled:
                await page.evaluate('([js, url]) => (new Function("window","document",js))({location:{href:url}},document)',[JS,url])
            href=await page.locator('.fv-apollo-atlas a.cta').get_attribute('href')
            valid=enabled and source in ('youtube','tiktok','facebook')
            facts={'cta':href.startswith(DEST) and (('utm_content=' in href)==valid),
              'chronology':await page.locator('.rail li').count()==4,
              'evidence':await page.locator('.plate').count()==4,
              'sources':await page.locator('.source-card').count()==4,
              'disclosures':await page.locator('details').count()==8,
              'nasa_links':await page.locator('a[href^="https://www.nasa.gov/"]').count()>=8,
              'no_overflow':await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),
              'no_errors':not errs}
            for k,v in facts.items():
                checks+=1
                if not v:failures.append(name+': '+k)
            await page.locator('details summary').first.click()
            checks+=1
            if not await page.locator('details').first.evaluate('(e)=>e.open'):failures.append(name+': details interaction')
            screenshot=out/(name+'.png')
            await page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
            results.append({'name':name,'width':width,'sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                            'href':href,'checks':facts})
            await ctx.close()
        await browser.close()
    receipt={'environment':'actual Chromium/Playwright DOM; synthetic URL; not installed WP or true-navigation cache',
             'contexts':len(CASES),'assertions':checks,'failures':failures,
             'fixture_sha256':hashlib.sha256(DOC.encode()).hexdigest(),'screenshots':results}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt
async def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence'
    receipt=await run(path)
    print(json.dumps({'contexts':receipt['contexts'],'checks':receipt['assertions'],'failures':receipt['failures']},indent=2))
    return 1 if receipt['failures'] else 0
if __name__=='__main__':sys.exit(asyncio.run(main()))
