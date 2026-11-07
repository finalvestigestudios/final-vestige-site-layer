#!/usr/bin/env python3
"""Real Chromium/CDP role-name acceptance for PHP-rendered Atlas in a MOCK WP shell.
NOT installed WordPress, genuine axe-core, real NASA delivery or production CWV.
"""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=subprocess.run(['php',str(ROOT/'qa/wp_function_harness.php'),'--html'],capture_output=True,text=True,check=True).stdout
assert hashlib.sha256(HTML.encode()).hexdigest()=='f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315', 'PHP-rendered Atlas was not the pinned evidence template'
CSS=(ROOT/'dist/assets/atlas-scoped.css').read_bytes()
LINK='<link rel="stylesheet" href="data:text/css;base64,'+base64.b64encode(CSS).decode()+'">'
CONTEXTS=[('320',320,True,{}),('360',360,True,{}),('390',390,True,{}),('768',768,True,{}),('1440',1440,True,{}),('1920',1920,True,{}),('320-nojs',320,False,{}),('390-nojs-nocss',390,False,{'nocss':True}),('390-forced',390,True,{'forced':True}),('390-reduced',390,True,{'reduced':True}),('390-touch',390,True,{'touch':True}),('640-200zoom',640,True,{'zoom':True})]
NAMES=['A fire. A record. Unanswered questions.','Four dates. Distinct kinds of evidence.','What the records support','Photographs document a different layer.']
PERF='''<script>window.__fv_lab={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fv_lab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fv_lab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}</script>'''
BASE='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:18px Arial;background:#edf1f4}#host-header{padding:12px}</style>__STYLE____PERF__</head><body><header id="host-header">Simulated host</header><main>__HTML__</main></body></html>'
def get_named_regions(page):
 client=page.context.new_cdp_session(page)
 result=client.send('Accessibility.getFullAXTree')
 return [n.get('name',{}).get('value','') for n in result['nodes'] if n.get('role',{}).get('value')=='region' and not n.get('ignored',False)]
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 failures=[];tests=[];shots={};metrics=[];ax={}
 def check(case,label,passed):
  tests.append({'case':case,'check':label,'pass':bool(passed)})
  if not passed:failures.append(case+': '+label)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
  for label,width,js,opt in CONTEXTS:
   ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,device_scale_factor=1,
     has_touch=bool(opt.get('touch')),is_mobile=bool(opt.get('touch')),
     forced_colors='active' if opt.get('forced') else 'none',reduced_motion='reduce' if opt.get('reduced') else 'no-preference')
   page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   shell=BASE.replace('__STYLE__','' if opt.get('nocss') else LINK).replace('__PERF__',PERF if js else '').replace('__HTML__',HTML)
   page.set_content(shell,wait_until='load')
   if opt.get('zoom'):page.evaluate('document.querySelector("main").style.zoom=2')
   regs=get_named_regions(page);ax[label]=regs
   for name in NAMES:check(label,'CDP accessible region: '+name,name in regs)
   check(label,'all aria-labelledby IDREFs resolve',page.evaluate(r'''() => [...document.querySelectorAll('[aria-labelledby]')].every(e => e.getAttribute('aria-labelledby').split(/\s+/).every(id => document.getElementById(id)))'''))
   check(label,'one contextual free investigation action',page.locator('.fv-apollo-atlas a.cta').count()==1)
   check(label,'four chronology entries',page.locator('.fv-apollo-atlas .rail li').count()==4)
   check(label,'four NASA source records',page.locator('.fv-apollo-atlas .source-card').count()==4)
   check(label,'eight native evidence disclosures',page.locator('.fv-apollo-atlas details').count()==8)
   check(label,'no embedded image or JS',page.locator('.fv-apollo-atlas img,.fv-apollo-atlas script').count()==0)
   check(label,'no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+2'))
   check(label,'no runtime errors',not errors)
   if label=='390':
    s=page.locator('#fv-apollo-finding-fire summary');s.focus();page.keyboard.press('Enter')
    check(label,'keyboard opens source disclosure',page.locator('#fv-apollo-finding-fire details').evaluate('(e)=>e.open'))
    page.set_content(shell,wait_until='load')
   if label=='390-touch':
    page.locator('#fv-apollo-photo-aftermath summary').tap()
    check(label,'touch opens archival source',page.locator('#fv-apollo-photo-aftermath details').evaluate('(e)=>e.open'))
    page.set_content(shell,wait_until='load')
   if label=='390-reduced':check(label,'reduced-motion media',page.evaluate("matchMedia('(prefers-reduced-motion:reduce)').matches"))
   if label=='390-forced':check(label,'forced-colors media',page.evaluate("matchMedia('(forced-colors:active)').matches"))
   page.screenshot(path=str(out/(label+'.png')),animations='disabled',full_page=True)
   shots[label]=hashlib.sha256((out/(label+'.png')).read_bytes()).hexdigest()
   if js:
    page.wait_for_timeout(160)
    metrics.append({'case':label,**page.evaluate('window.__fv_lab || {lcp:null,cls:0}')})
   ctx.close()
  browser.close()
 receipt={'build':'UNPUBLISHED_PHP_FUNCTION_MOCK_CHROMIUM_NOT_WORDPRESS','contexts':len(CONTEXTS),'passed':sum(x['pass'] for x in tests),'failed':sum(not x['pass'] for x in tests),'tests':tests,'errors':failures,'screenshot_sha256':shots,'CDP_named_regions':ax,'lab_metrics':metrics,'axe_executed':False,'installed_WordPress':False,'merchant_orders_verified':False}
 (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
 if failures:raise AssertionError('; '.join(failures[:8]))
 return receipt
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
 x=run(args.out);print(json.dumps({'contexts':x['contexts'],'passed':x['passed'],'failed':x['failed'],'lab_metrics':x['lab_metrics']},indent=2))
