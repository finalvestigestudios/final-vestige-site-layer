#!/usr/bin/env python3
"""Source-controlled R343 real Chromium replay; genuine axe only if AXE_JS is supplied."""
import json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.getenv('FV_R343_OUT', str(Path(__file__).resolve().parents[1]/'QA')))
OUT.mkdir(parents=True,exist_ok=True)
PHP=ROOT/'apollo-r339/chronology-rail.php'
CSS=(ROOT/'apollo-r339/assets/chronology-rail.css').read_text()
render=lambda n:subprocess.run(['php','-r',"define('ABSPATH',true);require '"+str(PHP)+"';for($i=0;$i<"+str(n)+";$i++)echo fv_apollo_r339_shortcode();"],check=True,capture_output=True,text=True).stdout
html=render(1)
assert html.count('data-fv-r339-source=')==6 and html.count('data-fv-r339-cta="editorial"')==1
assert not any(q in html for q in ['data-geo-pin','data-affiliate','<img'])
wp=json.loads(subprocess.run(['php',str(Path(__file__).with_name('standalone_preflight.php'))],check=True,text=True,capture_output=True).stdout)
assert wp['scenarios']==16
cases=[(320,16,True,False,False,False,1),(390,16,True,True,False,False,1),(768,16,True,False,True,False,1),(1440,16,True,False,False,False,1),(1920,16,True,False,False,False,1),(320,64,True,False,False,False,1),(320,32,False,False,False,False,1),(390,16,False,False,False,False,1),(1440,16,False,False,False,False,1),(768,16,True,False,False,True,1),(1440,16,True,False,False,False,2)]
results=[];axe=[]
script="""<script>window.r343={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.r343.lcp=+e.startTime.toFixed(1)}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.r343.cls+=e.value}).observe({type:'layout-shift',buffered:true});}catch(e){window.r343.error=String(e)}</script>"""
axe_path=Path(os.getenv('AXE_JS','/nonexistent'))
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 for w,font,js,touch,reduced,forced,n in cases:
  cx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js,has_touch=touch,is_mobile=touch,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
  pg=cx.new_page()
  content=html if n==1 else render(2)
  page='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>html{font-size:'+str(font)+'px}body{margin:0;background:#101311;color:#f0ede6}'+CSS+'</style>'+script+'</head><body><main>'+content+'</main></body></html>'
  pg.set_content(page,wait_until='load');pg.wait_for_timeout(150)
  assert pg.locator('.fv-apollo-r339__event').count()==6*n
  assert pg.locator('[data-fv-r339-source]').count()==6*n
  assert pg.locator('[data-fv-r339-cta="editorial"]').count()==n
  ids=pg.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
  assert len(ids)==len(set(ids))
  if not forced:assert pg.locator('.fv-apollo-r339').first.evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(13, 16, 16)'
  summary=pg.locator('.fv-apollo-r339__source summary').first
  summary.focus();pg.keyboard.press('Enter')
  assert pg.locator('[data-fv-r339-source]').first.is_visible()
  bounds=pg.locator('[data-fv-r339-source]').first.bounding_box()
  assert bounds and bounds['width']>=8 and bounds['height']>=24
  pg.keyboard.press('Space');assert not pg.locator('.fv-apollo-r339__source').first.evaluate('e=>e.open')
  link=pg.locator('.fv-apollo-r339__nav a').first
  target=link.get_attribute('href');link.click();assert pg.evaluate('location.hash')==target
  assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  if js and axe_path.is_file() and not forced:
   pg.add_script_tag(path=str(axe_path))
   ax=pg.evaluate("async()=>{const a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return a.violations.map(x=>x.id)}")
   assert not ax,ax;axe.append({'width':w,'violations':ax})
  if (w,font,js,n) in [(320,64,True,1),(320,32,False,1),(390,16,True,1),(1440,16,True,1)]:pg.screenshot(path=str(OUT/f'r343-committed-{w}-font{font}-{int(js)}.png'),full_page=True)
  perf=pg.evaluate('window.r343') if js else None
  results.append({'width':w,'font':font,'js':js,'touch':touch,'reduced':reduced,'forced_colors':forced,'instances':n,'lcp_fixture_ms':perf['lcp'] if perf else None,'cls_fixture':perf['cls'] if perf else None})
  cx.close()
 # Negative control: previously unstyled standalone shortcode.
 cx=b.new_context();pg=cx.new_page();pg.set_content('<style>body{margin:0}</style>'+html)
 unstyled=pg.locator('.fv-apollo-r339').evaluate('e=>getComputedStyle(e).backgroundColor')
 assert unstyled=='rgba(0, 0, 0, 0)',unstyled
 cx.close();b.close()
receipt={'status':'PASS','real_chromium_cases':len(results),'wp_stub_cases':wp['scenarios'],'axe_status':'PASS' if axe else 'NOT_EXECUTED','axe_results':axe,'unstyled_negative_control':unstyled,'cases':results,'limits':'Fixture only; no installed WP, HTTP CSP, independent screen readers or production CWV'}
(OUT/'r343-committed-gate.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','chromium_contexts':len(results),'wp_cases':wp['scenarios'],'axe_status':receipt['axe_status']}))
