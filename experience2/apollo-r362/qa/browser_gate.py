#!/usr/bin/env python3
"""Actual Chromium for rendered PHP + CSS, with no claim of installed WP or axe-core."""
from pathlib import Path
import json, subprocess
from playwright.sync_api import sync_playwright
import fitz
ROOT=Path(__file__).resolve().parents[3]
EX=ROOT/'experience2'
R=EX/'apollo-r362'
OUT=R/'QA';OUT.mkdir(exist_ok=True)
php=R/'research-crosswalk.php'
script='define("ABSPATH",true); require '+json.dumps(str(php))+'; echo fv_apollo_r362_shortcode();'
content=subprocess.check_output(['php','-r',script],text=True)
assert content.count('data-fv-r362-reviewed-source')==4
style=(R/'assets/research-crosswalk.css').read_text()
fixture='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R362 research custody</title><style>'+style+'</style></head><body><main>'+content+'</main></body></html>'
CASES=[('nojs-320',320,False,16,'reduce','none',False),('zoom-320',320,True,64,'reduce','none',False),('touch-390',390,True,16,'no-preference','none',True),('keyboard-768',768,True,16,'no-preference','none',False),('desktop-1440',1440,True,16,'no-preference','none',False),('forced-1920',1920,True,16,'reduce','active',False)]
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,width,js,font,motion,colors,touch in CASES:
  ctx=browser.new_context(viewport={'width':width,'height':940},java_script_enabled=js,reduced_motion=motion,forced_colors=colors,has_touch=touch)
  if js: ctx.add_init_script("""window.__vitals={cls:0,lcp:null};try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});new PerformanceObserver(list=>{for(const e of list.getEntries())window.__vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}""")
  page=ctx.new_page(); page.set_content(fixture,wait_until='load')
  if font!=16: page.evaluate('(v)=>document.documentElement.style.fontSize=v+"px"',font)
  assert page.locator('[data-fv-r362-crosswalk]').count()==1,name
  assert page.locator('[data-fv-r362-period="board"]').count()==3,name
  assert page.locator('[data-fv-r362-period="postfire"]').count()==1,name
  assert page.locator('[data-fv-r362-editorial-cta]').count()==1,name
  assert page.locator('img,script,iframe,form').count()==0,name
  assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'),name
  details=page.locator('details[data-fv-r362-details]')
  assert details.count()==4,name
  details.first.locator('summary').click()
  assert details.first.get_attribute('open') is not None,name
  links=page.locator('[data-fv-r362-reviewed-source]')
  assert links.count()==4,name
  assert all((l.get_attribute('href') or '').startswith('https://www.nasa.gov/') for l in links.all()),name
  links.first.focus()
  assert links.first.evaluate('(a)=>document.activeElement===a'),name
  if touch:
   details.nth(1).locator('summary').tap()
   assert details.nth(1).get_attribute('open') is not None,name
  tree=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
  names=[n.get('name',{}).get('value','') for n in tree if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
  assert len(names)>=2 and all(names),name
  # The first source and only editorial action have distinct, specific names.
  assert len(names)==len(set(names)),name
  page.screenshot(path=str(OUT/(name+'.png')),full_page=False)
  values=page.evaluate('window.__vitals||null') if js else None
  results.append(dict(case=name,width=width,js=js,root_font_px=font,touch=touch,forced_colors=colors,reduced_motion=motion,source_links=4,unique_ax_link_names=len(names),horizontal_overflow=False,fixture_vitals=values,passed=True))
  ctx.close()
 context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':940})
 page=context.new_page();page.set_content(fixture,wait_until='load');page.emulate_media(media='print')
 pdf=OUT/'source-crosswalk-print.pdf';pdf.write_bytes(page.pdf(format='A4',print_background=True))
 context.close();browser.close()
 doc=fitz.open(pdf)
 text=' '.join(p.get_text() for p in doc)
 nasa=set(link.get('uri','') for p in doc for link in p.get_links() if link.get('uri','').startswith('https://www.nasa.gov/'))
 assert len(nasa)==2, nasa # shared Board report + distinct 2018 post-fire report
 assert '102 deliberate ignitions' in text and 'NOT CLEARED' in text and 'Original 1967 Board' in text
 assert 'what it does not establish' in text.lower()
 results_summary={'pass':True,'browser':'system Chromium via Playwright','case_count':len(results),'cases':results,'print_pages':len(doc),'distinct_print_nasa_url_count':len(nasa),'limitations':['Local browser set_content PHP/CSS fixture; not installed WordPress','No genuine axe-core or independent screen-reader verification','No HTTP/CSP and no production Core Web Vitals','No payable rights-cleared FV offer, no user sessions, no confirmed revenue']}
 (OUT/'browser-result.json').write_text(json.dumps(results_summary,indent=2)+'\n')
 print(json.dumps({'chromium_passed':len(results),'print_pages':len(doc),'print_nasa_urls':len(nasa),'fixture_lcp_ms':[r['fixture_vitals']['lcp'] for r in results if r['fixture_vitals']],'fixture_cls':[r['fixture_vitals']['cls'] for r in results if r['fixture_vitals']]},indent=2))
