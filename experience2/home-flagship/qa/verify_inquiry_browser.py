"""Reproducible real Chromium QA for the isolated inquiry section; NOT full WordPress."""
from pathlib import Path
import asyncio,json,os
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
HTML=(ROOT/'inquiry.html').read_text(encoding='utf-8');CSS=(ROOT/'inquiry.css').read_text(encoding='utf-8')
STYLES=":root{--hf-ink:#f4efe6;--hf-sans:system-ui,sans-serif;--hf-serif:Georgia,serif;--hf-mono:'Courier New',monospace}*{box-sizing:border-box}html,body{margin:0;background:#0c0f0e;color:#f4efe6;font:16px/1.6 system-ui,sans-serif}.fv-hf{width:100%;overflow:clip}.fv-hf__eyebrow{font:700 10px/1.5 'Courier New',monospace;letter-spacing:.17em;color:#e1bd82}.fv-hf a:focus-visible,.fv-hf summary:focus-visible{outline:3px solid #ffe1a8;outline-offset:4px}"
PAGE='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+STYLES+CSS+'</style></head><body><div class="fv-hf"><main>'+HTML+'</main></div></body></html>'
async def run():
 records=[]
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  for width in (360,390,600,768,1024,1440,1920,320):
   page=await b.new_page(viewport={'width':width,'height':900},java_script_enabled=False,reduced_motion='reduce')
   err=[];page.on('pageerror',lambda e:err.append(str(e)))
   await page.set_content(PAGE,wait_until='load')
   q=await page.evaluate("() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,cards:document.querySelectorAll('.fv-hf__inquiry-record').length,sources:document.querySelectorAll('.fv-hf__inquiry-sources a').length})")
   target=page.locator('.fv-hf__inquiry-record').nth(1)
   await target.locator('summary').click(timeout=5000)
   q['mouseWorks']=await target.evaluate('(e)=>e.open')
   await target.locator('summary').focus();await page.keyboard.press('Enter')
   q['keyboardWorks']=not await target.evaluate('(e)=>e.open')
   q['overflowPx']=max(0,q['scrollWidth']-q['clientWidth'])
   q['pageErrors']=err
   records.append(q)
   if width in (390,1440):
    await target.locator('summary').evaluate('(e)=>e.blur()')
    await page.screenshot(path=str(OUT/f'inquiry-{width}.png'),full_page=True,animations='disabled',timeout=15000)
   await page.close()
  await b.close()
 result={'scope':'Exact inquiry module in isolated offline set_content fixture, not complete WP page','viewports':records,'pass':all(x['overflowPx']==0 and x['cards']==3 and x['sources']==6 and x['mouseWorks'] and x['keyboardWorks'] and not x['pageErrors'] for x in records)}
 (OUT/'INQUIRY_BROWSER_RESULTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
 if not result['pass']:raise SystemExit(1)
if __name__=='__main__':asyncio.run(run())
