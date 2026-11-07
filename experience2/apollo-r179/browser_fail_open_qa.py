"""R179 Chromium QA: deliberately fail optional search after record hiding.
Run with original R177 fixture, original and new JS, local fixture CSS; offline only.
Requires Python Playwright and installed Chromium. No WordPress/axe/merchant claim.
"""
import argparse, asyncio, hashlib, json
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
WIDTHS=[320,360,390,768,1440,1920]
PERF="""(() => { window.__lab = { lcp:null, cls:0 };try { new PerformanceObserver(x=>{for(const e of x.getEntries())window.__lab.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true}); } catch(e) {}try { new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__lab.cls+=e.value;}).observe({type:'layout-shift',buffered:true}); } catch(e) {} })();"""
FAULT="""() => { const s=document.querySelector('[data-fvx-status]'); Object.defineProperty(s,'textContent',{configurable:true,set(){throw new Error('R179_SYNTHETIC_STATUS_WRITE_FAULT');}}); }"""
def sha(b):return hashlib.sha256(b).hexdigest()
def fixture(src,js,css):
 s=BeautifulSoup(src,'html.parser');s.select_one('script').string=js
 style=s.new_tag('style');style.string=css;s.head.append(style)
 return str(s)
async def main(a):
 a.out.mkdir(parents=True,exist_ok=True)
 baseline=fixture(a.fixture.read_text(),a.baseline.read_text(),a.css.read_text())
 improved=fixture(a.fixture.read_text(),a.replacement.read_text(),a.css.read_text())
 assert 'Catalog identification not verified.' in improved
 counts={'assertions':0,'comparative_failures_recovered':0,'widths':WIDTHS,'lab_performance':{},'screenshots':{},'network_requests':[],'unexpected_page_errors':[],'context_count':0}
 def chk(x,msg):
  assert x,msg
  counts['assertions']+=1
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  # Baseline control: original R177 listener throws outside its initial try/catch.
  ctx=await browser.new_context(viewport={'width':390,'height':850});counts['context_count']+=1
  pg=await ctx.new_page();baseline_errors=[]
  pg.on('pageerror',lambda e:baseline_errors.append(str(e)))
  await pg.set_content(baseline,wait_until='load');await pg.evaluate(FAULT)
  await pg.locator('input[data-fvx-search]').fill('Catalog identification not verified.')
  chk(await pg.locator('[data-fvx-record]:visible').count()==1,'baseline expected hidden historical sources')
  chk(any('R179_SYNTHETIC_STATUS_WRITE_FAULT' in x for x in baseline_errors),'baseline expected uncaught event failure')
  await pg.screenshot(path=str(a.out/'baseline-390-failure.png'),full_page=True,animations='disabled');await ctx.close()
  for rep in [1,2]:
   for w in WIDTHS:
    ctx=await browser.new_context(viewport={'width':w,'height':850},device_scale_factor=1,has_touch=w in (390,768),reduced_motion='reduce' if w in (320,390) else 'no-preference')
    counts['context_count']+=1
    await ctx.add_init_script(PERF)
    pg=await ctx.new_page();errs=[];requests=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('request',lambda r:requests.append(r.url))
    await pg.set_content(improved,wait_until='load')
    chk(await pg.locator('[data-fvx-record]:visible').count()==6,'initial evidence not visible')
    chk(await pg.locator('a').count()==14,'source link inventory changed')
    chk(await pg.locator('[data-fvx-tools]').is_visible(),'search should enhance')
    chk(not await pg.evaluate('document.documentElement.scrollWidth > innerWidth + 1'),'overflow')
    inp=pg.locator('input[data-fvx-search]')
    chk(await inp.get_attribute('aria-label')=='Search records','search accessible name missing')
    await inp.fill('Catalog identification not verified.')
    chk(await pg.locator('[data-fvx-record]:visible').count()==1,'normal source search broken')
    await inp.fill('')
    chk(await pg.locator('[data-fvx-record]:visible').count()==6,'reset broken')
    await pg.evaluate(FAULT)
    await inp.fill('Catalog identification not verified.')
    chk(await pg.locator('[data-fvx-record]:visible').count()==6,'post-input exception failed to restore all six source records')
    chk(await pg.locator('[data-fvx-tools]').is_hidden(),'failed search UI remained visible')
    chk(await pg.locator('[data-fvx-empty]').is_hidden(),'failed search empty state remained')
    chk(await pg.locator('[data-fvx-r174-media-custody]').count()==6,'NASA provenance missing')
    chk(await pg.locator('[data-fvx-r175-catalog-review]').is_visible(),'unverified catalog notice lost')
    chk(await pg.locator('[data-fvx-ledger]').get_attribute('data-fvx-initialized')=='failed-open','failure state not reported')
    # Running asset twice after failed-open cannot rehide records or re-enable broken search.
    await pg.evaluate(a.replacement.read_text())
    chk(await pg.locator('[data-fvx-record]:visible').count()==6,'duplicate init hid records')
    chk(await pg.locator('[data-fvx-tools]').is_hidden(),'duplicate init re-enabled broken UI')
    chk(len(errs)==0,'unexpected page exception')
    chk(len(requests)==0,'unexpected network request')
    counts['comparative_failures_recovered']+=1
    await pg.wait_for_timeout(60)
    counts['lab_performance'][f'{w}-{rep}']=await pg.evaluate('window.__lab')
    path=a.out/f'r179-{w}-{rep}.png'
    await pg.screenshot(path=str(path),full_page=True,animations='disabled')
    counts['screenshots'][f'{w}-{rep}']=sha(path.read_bytes())
    await ctx.close()
  ctx=await browser.new_context(java_script_enabled=False,viewport={'width':320,'height':850});counts['context_count']+=1
  pg=await ctx.new_page();await pg.set_content(improved)
  chk(await pg.locator('[data-fvx-record]:visible').count()==6,'no-JS lost source records')
  chk(await pg.locator('[data-fvx-tools]').is_hidden(),'no-JS rendered search')
  await pg.screenshot(path=str(a.out/'no-js-320.png'),full_page=True);await ctx.close()
  ctx=await browser.new_context(forced_colors='active',viewport={'width':390,'height':850});counts['context_count']+=1
  pg=await ctx.new_page();await pg.set_content(improved);await pg.evaluate(FAULT)
  await pg.locator('input[data-fvx-search]').fill('Catalog identification not verified.')
  chk(await pg.locator('[data-fvx-record]:visible').count()==6,'forced color fail-open lost records')
  await pg.screenshot(path=str(a.out/'forced-colors-390.png'),full_page=True);await ctx.close()
  await browser.close()
 counts['reproducible_screenshots']=sum(counts['screenshots'][f'{w}-1']==counts['screenshots'][f'{w}-2'] for w in WIDTHS)
 chk(counts['reproducible_screenshots']==6,'nondeterministic screenshots')
 counts.update({'verdict':'CONTROLLED_SOURCE_DERIVED_CHROMIUM_PASS_NOT_WORDPRESS', 'genuine_axe_core':'NOT_RUN','installed_wordpress':'NOT_TESTED','media_delivery':'NOT_TESTED','commercial_conversion':'NOT_COMPUTABLE','laboratory_metrics_not_cwv':True})
 (a.out/'browser_receipt.json').write_text(json.dumps(counts,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in counts.items() if k not in ('lab_performance','screenshots')},sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for x in ('fixture','baseline','replacement','css','out'):p.add_argument('--'+x,type=Path,required=True)
 asyncio.run(main(p.parse_args()))
