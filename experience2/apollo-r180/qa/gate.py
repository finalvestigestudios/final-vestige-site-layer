"""R180 read-only Research Desk acceptance. Fixture mode ALWAYS HOLD. No production runs."""
import argparse, asyncio, hashlib, json
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright
WIDTHS=(320,360,390,768,1440,1920)
ORIGINAL='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PERF='''(()=>{window.apollo={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.apollo.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.apollo.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}})();'''
def preflight(a):
 if bool(a.fixture)==bool(a.url): raise ValueError('Provide exactly one of --fixture or --url')
 if a.fixture: return 'FIXTURE_ONLY'
 u=urlparse(a.url)
 if u.scheme!='https' or u.hostname!=a.approved_host or u.hostname in ('finalvestige.com','www.finalvestige.com'):
  raise ValueError('Remote QA requires matching explicit nonproduction HTTPS --approved-host')
 if not a.axe_js or not a.axe_js.is_file(): raise ValueError('Real staging requires local genuine axe-core JS')
 return 'STAGING_UNAPPROVED'
async def inspect(browser,a,width,js=True):
 ctx=await browser.new_context(viewport={'width':width,'height':850},java_script_enabled=js,
  reduced_motion='reduce',has_touch=width==390)
 if js: await ctx.add_init_script(PERF)
 page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 if a.fixture: await page.set_content(a.fixture.read_text(),wait_until='load')
 else: await page.goto(a.url,wait_until='load',timeout=45000)
 await page.wait_for_timeout(100)
 checks={
  'six_records':await page.locator('[data-fvx-record]').count()==6,
  'all_evidence_visible':await page.locator('[data-fvx-record]:visible').count()==6,
  'no_horizontal_overflow':await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
  'original_link':await page.locator('a[href="'+ORIGINAL+'"]').count()>=1,
  'six_NASA_links':await page.locator('[data-fvx-record] a[href^="https://www.nasa.gov/"]').count()>=6,
  'no_intrusive_commerce':await page.locator('[data-fvx-ledger] a[href*="awin1.com"], [data-fvx-ledger] a[href*="payhip.com"]').count()==0,
  'catalog_warning':await page.get_by_text('Catalog identification not verified.',exact=False).count()>0,
  'no_errors':not errors}
 if js:
  search=page.locator('input[data-fvx-search]')
  checks['search_visible']=await search.count()==1 and await search.is_visible()
  if checks['search_visible']:
   await search.fill('Catalog identification not verified.')
   checks['search_provenance']=await page.locator('[data-fvx-record]:visible').count()==1
   await search.fill('')
   checks['search_reset']=await page.locator('[data-fvx-record]:visible').count()==6
 else: checks['no_js_fail_open']=await page.locator('[data-fvx-tools]').is_hidden()
 if not a.fixture:
  checks['installed_wp_dom']=await page.locator('.wp-site-blocks').count()>0
  imgs=await page.locator('[data-fvx-ledger] img').evaluate_all('(xs)=>xs.map(x=>x.complete&&x.naturalWidth>0)')
  checks['actual_media_loaded']=bool(imgs) and all(imgs)
  if js:
   await page.add_script_tag(path=str(a.axe_js))
   violations=await page.evaluate('async()=>{const r=await axe.run(document.querySelector("[data-fvx-ledger]"),{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}});return r.violations.map(x=>x.id)}')
   checks['genuine_axe_zero_violations']=not violations
  else: checks['axe_not_applicable_without_javascript']=True
 path=a.output/('no-js' if not js else str(width));shot=path.with_suffix('.png')
 await page.screenshot(path=str(shot),full_page=True,animations='disabled')
 result={'width':width,'javascript':js,'checks':checks,'errors':errors,
  'screenshot_sha256':hashlib.sha256(shot.read_bytes()).hexdigest(),
  'lab_metrics_not_field_CWV':await page.evaluate('window.apollo||null') if js else None}
 await ctx.close();return result
async def main(a):
 kind=preflight(a);a.output.mkdir(parents=True,exist_ok=True)
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
  results=[await inspect(b,a,w) for w in WIDTHS]+[await inspect(b,a,320,False)];await b.close()
 failures=[str(r['width'])+':'+k for r in results for k,v in r['checks'].items() if not v]
 report={'mode':kind,'verdict':'HOLD' if a.fixture or failures else 'TECHNICAL_PASS_NEEDS_FOUNDER_RELEASE',
  'failures':failures,'results':results,'realized_revenue':'NOT_VERIFIED',
  'commercial_clearance':'NOT_VERIFIED','screen_reader_manual':'NOT_TESTED'}
 (a.output/'receipt.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'mode':kind,'verdict':report['verdict'],'failures':failures,'contexts':len(results)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path);p.add_argument('--url');p.add_argument('--approved-host');p.add_argument('--axe-js',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--chromium',default='/usr/bin/chromium');asyncio.run(main(p.parse_args()))
