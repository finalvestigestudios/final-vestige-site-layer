#!/usr/bin/env python3
"""Real Chromium negative controls for first-screen sign-up acceptance."""
import asyncio
import json
from pathlib import Path
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools' / 'experience-2'))
from verify_optin_viewport_geometry import inspect_optin_viewport

BASE = '''<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;background:#101512;color:#ecd9ae;font-family:Arial"><main><h1>Fieldbook</h1><section class="wp-block-jetpack-subscriptions" style="padding:16px"><form><label for="signup">Email address</label><input id="signup" type="email" style="display:block;width:240px;height:48px;margin-top:12px;background:#fff"></form></section></main></body></html>'''

async def run():
    out = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        try:
            for w in (320,390,768,1440,1920):
                page=await browser.new_page(viewport={'width':w,'height':900},reduced_motion='reduce')
                await page.set_content(BASE)
                result=await inspect_optin_viewport(page)
                assert result['labeled_unobstructed_first_viewport']==1, (w,result)
                out.append({'scenario':'healthy '+str(w),'result':'PASS','geometry':result})
                await page.close()
            variants = {
              'offscreen': ('<main>', '<main><div style="height:1400px"></div>'),
              'covered_by_fixed_overlay': ('</body>','<div style="position:fixed;inset:0;z-index:999;background:#222;opacity:.95"></div></body>'),
              'opacity_zero': ('display:block;width:240px','opacity:0;display:block;width:240px'),
              'disabled': ('id="signup" type="email"','id="signup" disabled type="email"'),
              'placeholder_not_a_label': ('<label for="signup">Email address</label>',''),
              'visibility_hidden': ('display:block;width:240px','visibility:hidden;display:block;width:240px'),
              'off_to_right': ('display:block;width:240px','position:absolute;left:1500px;display:block;width:240px'),
              'no_form': ('<input id="signup" type="email" style="display:block;width:240px;height:48px;margin-top:12px;background:#fff">',''),
            }
            for name,(a,b) in variants.items():
                page=await browser.new_page(viewport={'width':390,'height':900})
                await page.set_content(BASE.replace(a,b))
                result=await inspect_optin_viewport(page)
                assert result['labeled_unobstructed_first_viewport']==0, (name,result)
                out.append({'scenario':name,'result':'PASS','geometry':result})
                await page.close()
        finally:
            await browser.close()
    receipt={'scope':'SYNTHETIC CHROMIUM NEGATIVE CONTROLS, NOT LIVE WORDPRESS','checks':len(out),'passed':sum(x['result']=='PASS' for x in out),'scenarios':out}
    file=Path(__file__).resolve().parents[2]/'docs'/'experience-2'/'local_optin_geometry_receipt.json'
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'checks':receipt['checks'],'passed':receipt['passed'],'live_verified':False},indent=2))

if __name__ == '__main__':
    asyncio.run(run())
