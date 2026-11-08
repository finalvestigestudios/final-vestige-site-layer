#!/usr/bin/env python3
"""Apollo R210 isolated artifact/interaction QA; never certifies installed WP or live CWV.

Supports an optional *real axe-core* run when FV_AXE_JS points to a local,
authentic distributable. Missing axe produces NOT_EXECUTED, never PASS.
"""
from __future__ import annotations
import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
NASA_BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
NASA_PHOTO='https://www.nasa.gov/image-detail/amf-s67-21294/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def sha(b):return hashlib.sha256(b).hexdigest()
def guard(ok,msg):
 if not ok:raise AssertionError(msg)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.labels=[];self.hrefs=[];self.bad=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if len([k for k,v in attrs if k=='id'])>1:self.bad.append('duplicate-id-attribute')
  if d.get('id'):self.ids.append(d['id'])
  for k in ('aria-labelledby','aria-describedby'):
   if d.get(k):self.labels.extend(d[k].split())
  if tag=='a' and d.get('href'):self.hrefs.append(d['href'])
def check(html):
 a=Links();a.feed(html)
 guard(not a.bad and len(set(a.ids))==len(a.ids),'duplicate IDs')
 guard(all(x in a.ids for x in a.labels),'missing labelled/described target')
 guard(all(h[1:] in a.ids for h in a.hrefs if h.startswith('#')),'broken in-page href')
 guard(html.count('id="fv-apollo-source-test"')==1 and 'fv-apollo-reading-lab' not in html,'duplicate educational activity')
 guard(html.count('href="#fv-apollo-source-test"')==1,'source test not in nav')
 guard(html.count('class="cta"')==1 and html.count('<details')==12,'control contract')
 guard(NASA_BOARD in html and NASA_PHOTO in html,'NASA primary evidence lost')
 guard('datetime="1967-04"' in html and 'datetime="1967-01-27"' in html,'accident/report conflation')
 guard('NASA does not endorse Final Vestige' in html,'rights boundary')
 guard(not re.search(r'\b(buy now|subscribe now|add to cart|limited time offer)\b',html,re.I),'unauthorized commerce')
 guard(not re.search(r'<(?:img|iframe|script)\b',html,re.I),'unreviewed media or scripts')
 guard(not any(x in html for x in ('data-lat','data-lng','data-geo-edge')),'unapproved geo')
 guard(all(h.startswith(('https://www.nasa.gov/','https://finalvestige.com/','#')) for h in a.hrefs),'nonapproved link domain')
 guard(a.hrefs.count(FREE)==1,'free primary destination must be unique')
 return a

def php(mode):
 p=DIST/'fv-ex2-apollo-r210.php';shim=DIST/'wp-render-shim-r210.php'
 return json.loads(subprocess.check_output(['php',str(shim),str(p),mode],text=True))

def run(out:Path,require_axe:bool=False):
 out.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((DIST/'manifest.json').read_text())
 guard(manifest['release']=='r210' and not manifest['upstream_R198_reconciled'],'history gate')
 for name,digest in manifest['files'].items():guard(sha((DIST/name).read_bytes())==digest,'tampered artifact '+name)
 guard(sha((DIST/'source-audit.json').read_bytes())==manifest['source_audit_sha256'],'bad source audit')
 source=json.loads((DIST/'source-audit.json').read_text())
 guard(source['claim_source']==NASA_BOARD and source['aftermath_source']==NASA_PHOTO,'source mismatch')
 guard(source['media_rights_for_commercial_promotion']=='NOT_CLEARED','commercial rights unexpectedly opened')
 guard(source['geographic_pins']==[] and source['speculative_relationship_edges']==[],'fabricated geo')
 guard(source['visitor_action']['url']==FREE and source['visitor_action']['type']=='free_editorial','CTA custody')
 l=subprocess.run(['php','-l',str(DIST/'fv-ex2-apollo-r210.php')],capture_output=True,text=True)
 guard(l.returncode==0,'PHP lint failed '+l.stderr)
 normal,late,printed=[php(x) for x in ('normal','late','printed')]
 guard(normal['css']=='enqueued' and not normal['fallback'],'normal render failure')
 guard(late['fallback'] and FREE in late['html'],'late render must fail open')
 guard(not printed['fallback'],'print render failure')
 html=normal['html'];check(html)
 # Explicit mutation tests prove the gate is active; preserve the originals.
 mut={
  'dead_nav_fragment':html.replace('href="#fv-apollo-source-test"','href="#not-real"',1),
  'duplicate_activity':html.replace('<footer class="end">','<section class="fv-apollo-reading-lab"></section><footer class="end">',1),
  'unauthorized_paid_cta':html.replace('Read original investigation →','Buy now →',1),
  'misleading_rights':html.replace('NASA does not endorse Final Vestige','NASA endorses Final Vestige'),
  'false_report_date':html.replace('datetime="1967-04"','datetime="1967-01-27"'),
  'unreviewed_photo':html.replace('<footer class="end">','<img src="third-party.jpg"><footer class="end">',1),
  'unreviewed_geo':html.replace('<footer class="end">','<div data-lat="32"></div><footer class="end">',1),
  'duplicate_primary_cta':html.replace('</footer>','<a class="cta" href="'+FREE+'">click</a></footer>',1),
  'missing_primary_link':html.replace('class="cta" href="'+FREE+'"','class="cta" href="https://example.org/buy"',1),
 }
 negatives=[]
 for name,test in mut.items():
  try:check(test)
  except AssertionError:negatives.append(name)
 guard(len(negatives)==len(mut),'mutation escaped audit: '+str(set(mut)-set(negatives)))
 css=(DIST/'assets/atlas-scoped.css').read_text(encoding='utf8')
 axe_path=Path(os.environ['FV_AXE_JS']) if os.environ.get('FV_AXE_JS') else None
 if require_axe:guard(axe_path is not None and axe_path.is_file(),'REAL axe-core required but missing')
 # Fixture is explicitly not an installed WordPress or remotely navigated page.
 document='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">\n<style>'+css+'</style></head><body>'+html+'</body></html>'
 cases=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),('390-nojs',390,{'java_script_enabled':False}),('390-touch',390,{'has_touch':True,'is_mobile':True}),('390-reduced',390,{'reduced_motion':'reduce'}),('390-forced',390,{'forced_colors':'active'})]
 runs=[];axe_cases=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  browser_ver=browser.version
  print_ctx=browser.new_context(viewport={'width':390,'height':900})
  print_page=print_ctx.new_page();print_page.set_content(document,wait_until='domcontentloaded')
  print_page.emulate_media(media='print')
  guard(print_page.locator('.fv-apollo-lesson-key>div p').first.is_visible(),'Closed lesson answers hidden when printed')
  guard(print_page.locator('.fv-apollo-print-custody').is_visible(),'Printed source index hidden')
  print_ctx.close()
  for label,width,opts in cases:
   ctx=browser.new_context(viewport={'width':width,'height':900},**opts)
   page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.set_content(document,wait_until='domcontentloaded')
   guard(page.locator('.fv-apollo-atlas a.cta').count()==1,'CTA missing in browser')
   guard(page.locator('.fv-apollo-atlas .fv-apollo-lesson').count()==1,'source lesson missing browser')
   guard(page.locator('.fv-apollo-atlas .fv-apollo-reading-lab').count()==0,'old duplicate visible')
   nav=page.locator('.mast nav a[href="#fv-apollo-source-test"]')
   nav.focus();guard(nav.evaluate('(e)=>e===document.activeElement'),'nav not focusable')
   page.keyboard.press('Enter')
   guard(page.evaluate('location.hash')=='#fv-apollo-source-test','keyboard nav did not reach source test')
   key=page.locator('.fv-apollo-lesson-key')
   key.locator('summary').focus();page.keyboard.press('Enter')
   guard(key.evaluate('(e)=>e.open'),'keyboard disclosure failed open')
   page.keyboard.press('Enter');guard(not key.evaluate('(e)=>e.open'),'keyboard disclosure failed close')
   if opts.get('has_touch'):
    key.locator('summary').tap();guard(key.evaluate('(e)=>e.open'),'touch disclosure failed')
    key.locator('summary').tap();guard(not key.evaluate('(e)=>e.open'),'touch disclosure failed close')
    page.touchscreen.tap(1,1) # clear emulated sticky touch-hover before screenshot
   guard(page.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'),'horizontal overflow')
   guard(not errors,'page errors '+str(errors))
   # PerformanceObserver with buffered entries: fixture-only, no field metrics.
   if opts.get('java_script_enabled',True) is False:
    perf={'lcp_ms':None,'cls':None,'reason':'JS disabled; not observed'}
   else:
    perf=page.evaluate('''async () => {
      let lcp=null, cls=0;
      try {new PerformanceObserver(list=>{let a=list.getEntries();if(a.length)lcp=a[a.length-1].startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
      try {new PerformanceObserver(list=>{for(let e of list.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}
      await new Promise(r=>setTimeout(r,140));return {lcp_ms:lcp,cls:cls,reason:lcp===null?'No LCP entry; not measured':null};
    }''')
   if axe_path and axe_path.is_file() and opts.get('java_script_enabled',True) is False:
    # no JS context cannot run axe; only test enabled cases below
    pass
   elif axe_path and axe_path.is_file():
    page.add_script_tag(path=str(axe_path))
    axe=page.evaluate('''async()=>{let a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:a.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:a.passes.length}}''')
    axe_cases.append({'case':label,**axe});guard(not axe['violations'],'genuine axe-core violations '+str(axe['violations']))
   page.evaluate('if(document.activeElement) document.activeElement.blur()')
   shot=page.screenshot(path=str(out/(label+'.png')),full_page=True,animations='disabled')
   runs.append({'case':label,'width':width,'screenshot_sha256':sha(shot),'perf_fixture':perf,'page_errors':errors})
   ctx.close()
  browser.close()
 receipt={'release':'r210','chromium':browser_ver,'contexts':len(cases),'screenshots':runs,
  'negative_mutations_rejected':negatives,
  'genuine_axe_core':{'status':'PASS' if axe_cases else 'NOT_EXECUTED','cases':axe_cases,'reason':None if axe_cases else 'No authenticated local axe-core script available; manual AT tests also pending'},
  'installed_wordpress':'NOT_TESTED','full_canonical_ancestry':'NOT_RECONCILED',
  'production_lcp_cls':'NOT_MEASURED','browser_navigation_to_staging':'NOT_TESTED (environment blocks localhost/external navigation)',
  'print_closed_disclosure_reveals_answer':True,'wp_simulation':'PHP function shim only','paid_conversion':'NOT_VERIFIED'}
 (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
 return receipt

if __name__=='__main__':
 args=sys.argv[1:];strict='--require-axe' in args;args=[x for x in args if x!='--require-axe']
 print(json.dumps(run(Path(args[0] if args else '/tmp/apollo-r210-qa'),strict),sort_keys=True,indent=2))
