#!/usr/bin/env python3
"""Actual Chromium/Playwright verifies PHP-rendered Apollo HTML and PRINT custody.
Not an installed WordPress/axe/real-navigation test; no synthetic performance claims.
"""
import asyncio,hashlib,json,subprocess,sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
CSS=(DIST/'assets/atlas-scoped.css').read_text()
SHIM=ROOT/'qa/wp_render_shim.php'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CASES=[('320',320,True,False,False),('360',360,True,False,False),('390',390,True,False,False),
 ('768',768,True,False,False),('1440',1440,True,False,False),('1920',1920,True,False,False),
 ('390-nojs',390,False,False,False),('390-reduced',390,True,False,False),
 ('390-forced',390,True,False,False),('390-touch',390,True,True,False),
 ('390-print',390,False,False,True),('1440-print',1440,False,False,True)]

def renderer():
    p=subprocess.run(['php',str(SHIM),str(DIST/'fv-ex2-apollo-r191.php')],capture_output=True,text=True,check=True)
    return json.loads(p.stdout)

async def run(out):
 out.mkdir(parents=True,exist_ok=True)
 r=renderer();assert not r['fallback'] and r['chronology']==4 and r['details']==8
 doc='<!DOCTYPE html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style></head><body>'+r['html']+'</body></html>'
 reports=[];failures=[];count=0
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,width,js,touch,print_mode in CASES:
   ctx=await browser.new_context(viewport={'width':width,'height':820},device_scale_factor=1,java_script_enabled=js,
       has_touch=touch,reduced_motion='reduce' if 'reduced' in name else 'no-preference',
       forced_colors='active' if 'forced' in name else 'none')
   page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto('about:blank')
   # Browser observed load/shift only within a controlled document fixture.
   if js:
    await page.evaluate('''() => {
      window.__layoutShifts=[];
      try {new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__layoutShifts.push(e.value)})).observe({type:'layout-shift',buffered:true})}catch(e){}
    }''')
   await page.set_content(doc)
   if print_mode:await page.emulate_media(media='print')
   el=page.locator('.fv-apollo-print-custody')
   visible=await el.is_visible()
   details=page.locator('.plate details').first
   facts={
    'actual_php_render':r['css']=='enqueued' and not r['fallback'],
    'print_index_visibility': visible is print_mode,
    'print_8_custody_entries':await page.locator('.fv-apollo-print-custody li').count()==8,
    'historical_chronology':await page.locator('.rail li').count()==4,
    'evidence_plates':await page.locator('.plate').count()==4,
    'source_drawers':await page.locator('details').count()==8,
    'original_investigation_cta':await page.locator('.fv-apollo-atlas a.cta[href="'+DEST+'"]').count()==1,
    'all_index_external_links_no_referrer':await page.locator('.fv-apollo-print-custody a[rel="noreferrer noopener"]').count()==8,
    'no_horizontal_scroll':await page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),
    'browser_errors_zero':len(errors)==0,
   }
   if print_mode:
    # The original closed <details> links are hidden in print: we verify the new index repairs this.
    facts['print_source_link_visible']=await page.locator('.fv-apollo-print-custody a').first.is_visible()
    facts['print_source_has_full_literal_url']='https://www.nasa.gov/' in await el.inner_text()
   else:
    facts['native_closed_details_preserved']=not await details.evaluate('(e)=>e.open')
    if js:
     await details.locator('summary').focus();await page.keyboard.press('Enter')
     facts['keyboard_disclosure_operates']=await details.evaluate('(e)=>e.open')
     await details.locator('summary').press('Enter')
    if touch:
     await page.locator('.source-card summary').first.tap()
     facts['touch_disclosure_operates']=await page.locator('.source-card details').first.evaluate('(e)=>e.open')
   for key,value in facts.items():
    count+=1
    if not value: failures.append(name+':'+key)
   pic=out/(name+'.png');await page.screenshot(path=str(pic),full_page=True,animations='disabled')
   # Browser entry APIs may have no LCP for about:blank/set_content. Report unavailable, not invented.
   perf=await page.evaluate('''() => ({lcp: performance.getEntriesByType('largest-contentful-paint').slice(-1).map(x=>x.startTime)[0]||null,cls:window.__layoutShifts?window.__layoutShifts.reduce((a,b)=>a+b,0):null})''') if js else {'lcp':None,'cls':None}
   reports.append({'case':name,'width':width,'checks':facts,'screenshot_sha256':hashlib.sha256(pic.read_bytes()).hexdigest(),
                   'lcp_lab_ms':perf['lcp'],'cls_lab':perf['cls']})
   await ctx.close()
  await browser.close()
 receipt={'description':'Real Chromium/Playwright of PHP-function-shim-rendered HTML via set_content; NOT installed WP; NOT real navigation/CDN; NOT axe.',
   'contexts':len(CASES),'assertions':count,'failures':failures,'source_html_sha256':hashlib.sha256(r['html'].encode()).hexdigest(),
   'css_sha256':hashlib.sha256(CSS.encode()).hexdigest(),'cases':reports}
 (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
 return receipt
async def main():
 out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence'
 r=await run(out);print(json.dumps({'contexts':r['contexts'],'checks':r['assertions'],'failures':r['failures']},indent=2));return bool(r['failures'])
if __name__=='__main__':sys.exit(asyncio.run(main()))
