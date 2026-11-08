#!/usr/bin/env python3
"""Deterministic, isolated Apollo R211 Playwright/PHP QA. Fixture ≠ installed WordPress."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parent.parent
D=BASE/'dist'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
PHOTO='https://www.nasa.gov/image-detail/amf-s67-15717/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def sha(b):return hashlib.sha256(b).hexdigest()
def g(v,msg):
 if not v: raise AssertionError(msg)
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if d.get('id'):self.ids.append(d['id'])
  for k in ('aria-describedby','aria-labelledby'):
   if d.get(k):self.refs+=d[k].split()
  if tag=='a' and d.get('href'):self.hrefs.append(d['href'])

def check(h):
 sc=Scan();sc.feed(h)
 g(len(sc.ids)==len(set(sc.ids)),'Duplicate IDs')
 g(all(v in sc.ids for v in sc.refs),'ARIA IDREF broken')
 g(all(v[1:] in sc.ids for v in sc.hrefs if v.startswith('#')),'Broken fragment link')
 g(BOARD in sc.hrefs and PHOTO in sc.hrefs,'Required NASA custody links missing')
 g(sc.hrefs.count(FREE)==1 and h.count('class="cta"')==1,'Primary CTA contract')
 g('Open NASA 3 January 1967 spacecraft processing photograph' not in h,'False photo date')
 g('catalog year 1967' in h and 'exact exposure day is not established' in h,'Date precision note missing')
 g(h.count('datetime="1967-01-03"')>=2 and 'datetime="1967"' in h,'Event/year semantics missing')
 g(h.count('class="fv-apollo-date-precision"')==1,'Source precision callout missing')
 g(h.count('<details')==12 and h.count('id="fv-apollo-source-test"')==1,'Evidence features altered')
 g('NASA does not endorse Final Vestige' in h and 'NASA endorses Final Vestige' not in h,'Rights boundary missing or misleading')
 g(not re.search(r'<(?:img|iframe|script)\b|data-lat|data-lng|data-geo-edge',h,re.I),'Unreviewed media/geo/script')
 g(not re.search(r'\b(buy now|checkout|limited time offer)\b',h,re.I),'Unauthorized paid offer')
 return sc

def run(out):
 out.mkdir(parents=True,exist_ok=True)
 m=json.loads((D/'manifest.json').read_text())
 g(m['release']=='r211' and m['upstream_R198_reconciled'] is False,'Ancestry gate')
 g(not m['approved_purchase_offer'] and not m['media_commercial_rights_cleared'],'Commerce gate')
 for n,d in m['files'].items():g(sha((D/n).read_bytes())==d,'Tampered generated file '+n)
 sr=json.loads((D/'source-records.json').read_text())
 r=next(x for x in sr if x['source_id']=='S67-15717')
 g(r['date']=='1967' and r['date_precision']=='year' and r['event_date']=='1967-01-03','Structured dates')
 ledger=json.loads((D/'custody-ledger.json').read_text())
 r=next(x for x in ledger['records'] if x['id']=='S67-15717')
 g(r['date']=='1967' and r['date_precision']=='year' and r['event_source_url']==BOARD,'Ledger custody')
 g(subprocess.run(['php','-l',str(D/'fv-ex2-apollo-r211.php')],capture_output=True).returncode==0,'PHP lint')
 def php(mode):return json.loads(subprocess.check_output(['php',str(D/'wp-render-shim-r211.php'),str(D/'fv-ex2-apollo-r211.php'),mode],text=True))
 norm,late,printed=(php(k) for k in ['normal','late','printed'])
 g(norm['css']=='enqueued' and not norm['fallback'],'Shim normal')
 g(late['fallback'] and FREE in late['html'],'Shim late fail-open')
 g(not printed['fallback'],'Shim printed')
 html=norm['html'];check(html)
 negatives={
   'photo_claim':html.replace('exact exposure day is not established','date is proven January 3',1),
   'lost_precision_note':html.replace('class="fv-apollo-date-precision"','class="removed"',1),
   'dead_fragment':html.replace('href="#fv-apollo-source-test"','href="#missing"',1),
   'duplicate_cta':html.replace('</footer>','<a class="cta" href="'+FREE+'">extra</a></footer>',1),
   'fake_geo':html.replace('</footer>','<div data-lat="1"></div></footer>',1),
   'false_approval':html.replace('NASA does not endorse Final Vestige','NASA endorses Final Vestige',1),
 }
 # Date precision negative is validated by explicit invariant, not dangerous regex over all prose.
 def check_precision(h):
  check(h);g('exact exposure day is not established' in h,'Exact-day disclaimer removed')
 rejected=[]
 for k,h in negatives.items():
  try:check_precision(h)
  except AssertionError:rejected.append(k)
 g(len(rejected)==len(negatives),'Mutation escaped '+str(set(negatives)-set(rejected)))
 css=(D/'assets/atlas-scoped.css').read_text()
 page_html='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
 cases=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),('390-nojs',390,{'java_script_enabled':False}),('390-touch',390,{'has_touch':True,'is_mobile':True}),('390-reduced',390,{'reduced_motion':'reduce'}),('390-forced',390,{'forced_colors':'active'}),('768-zoom',768,{})]
 evidence=[]
 with sync_playwright() as pw:
  br=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,width,opts in cases:
   c=br.new_context(viewport={'width':width,'height':900},**opts)
   p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   p.set_content(page_html,wait_until='domcontentloaded')
   if name=='768-zoom':p.evaluate('document.body.style.zoom="200%"')
   p.screenshot(path=str(out/(name+'.png')),full_page=True,animations='disabled')  # Capture pristine state; touch-hover is timing-dependent
   g(p.locator('.fv-apollo-date-precision').count()==1,'Browser precision note')
   g(p.locator('.fv-apollo-atlas .cta').count()==1,'Browser CTA')
   g(p.locator('.fv-apollo-lesson').count()==1,'Browser lesson')
   g(p.locator('.fv-apollo-rail-source[href="'+BOARD+'"]').count()>=1,'Browser primary report link')
   a=p.locator('.mast nav a[href="#fv-apollo-source-test"]');a.focus();p.keyboard.press('Enter')
   g(p.evaluate('location.hash')=='#fv-apollo-source-test','Keyboard nav')
   key=p.locator('.fv-apollo-lesson-key');key.locator('summary').focus();p.keyboard.press('Enter');g(key.evaluate('(e)=>e.open'),'Keyboard disclosure')
   p.keyboard.press('Enter');g(not key.evaluate('(e)=>e.open'),'Keyboard close')
   if opts.get('has_touch'):
    key.locator('summary').tap();g(key.evaluate('(e)=>e.open'),'Touch disclosure')
    key.locator('summary').tap();g(not key.evaluate('(e)=>e.open'),'Touch close')
   g(p.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'),'Horizontal overflow '+name)
   g(not errors,'Page error '+str(errors))
   metrics=p.evaluate('''async () => {
     let lcp=null,cls=0;
     try {new PerformanceObserver(list=>{const e=list.getEntries();if(e.length)lcp=e[e.length-1].startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
     try {new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}
     await new Promise(r=>setTimeout(r,140));
     return {lcp_ms:lcp,cls,fixture_only:true};
   }''') if opts.get('java_script_enabled',True) else {'fixture_only':True,'reason':'no-JS'}
   evidence.append({'name':name,'width':width,'screenshot_sha256':sha((out/(name+'.png')).read_bytes()),'metrics':metrics})
   c.close()
  c=br.new_context(viewport={'width':390,'height':900});p=c.new_page();p.set_content(page_html);p.emulate_media(media='print')
  g(p.locator('.fv-apollo-lesson-key>div p').first.is_visible(),'Printed lesson answer hidden')
  g(p.locator('.fv-apollo-date-precision').is_visible(),'Printed photo-year note hidden')
  c.close();br.close()
 receipt={'browser_version':br.version if hasattr(br,'version') else 'Chromium','contexts':evidence,'negative_mutations_rejected':rejected,
  'installed_WordPress':'NOT_TESTED','genuine_axe_core':'NOT_EXECUTED','external_browser_navigation':'NOT_TESTED',
  'observed_LCP_CLS':'NOT_PRODUCTION_CWV','assertions':['source custody','keyboard','touch','no-JS','print','reduced-motion','forced-colors','simulated CSS zoom','no-overflow','rights','no-paid-CTA']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'pass':True,'browser_contexts':len(evidence),'mutations_rejected':len(rejected),'screenshots':{x['name']:x['screenshot_sha256'] for x in evidence}},indent=2))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r211-qa'))
