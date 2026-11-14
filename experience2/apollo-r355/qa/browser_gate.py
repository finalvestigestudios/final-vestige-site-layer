#!/usr/bin/env python3
"""R355 actual Chromium Playwright against PHP-rendered local HTML; not installed WordPress/axe-core."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
BASE=Path(__file__).resolve().parents[3];EX=BASE/'experience2'; OUT=EX/'apollo-r355/QA';OUT.mkdir(parents=True,exist_ok=True)
php='define("ABSPATH",true);require '+json.dumps(str(EX/'apollo-r355/postfire-ledger.php'))+';echo fv_apollo_r355_experience_shortcode();'
html=subprocess.check_output(['php','-r',php],text=True)
styles='\n'.join((EX/x).read_text() for x in ['apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css','apollo-r348/assets/source-custody.css','apollo-r355/postfire-ledger.css'])
js=(EX/'apollo-r347/assets/source-index.js').read_text()
assert html.count('data-fv-apollo-entry=')==13 and html.count('data-fv-r339-cta="editorial"')==1
assert html.count('data-fv-r355-reviewed-source')==1
page_html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{margin:0}'+styles+'</style></head><body>'+html+'</body></html>'
cases=[('320-zoom400',320,True,False,64,'reduce','none'),('390-nojs',390,False,True,16,'reduce','none'),('768-touch',768,True,True,16,'reduce','none'),('1440-keyboard',1440,True,False,16,'no-preference','none'),('1920-forced',1920,True,False,16,'reduce','active')]
reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,width,enable,touch,root_size,motion,forced in cases:
  ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enable,has_touch=touch,reduced_motion=motion,forced_colors=forced)
  page=ctx.new_page()
  page.set_content(page_html,wait_until='load')
  if enable:
   page.evaluate('''window.__testPerf={lcp:[],cls:0};try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__testPerf.lcp.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__testPerf.cls+=e.value})).observe({type:'layout-shift',buffered:true})}catch(e){}''')
   page.add_script_tag(content=js)
  if root_size!=16: page.evaluate('(px)=>document.documentElement.style.fontSize=px+"px"',root_size)
  assert page.locator('[data-fv-apollo-entry]:visible').count()==13,name
  assert page.locator('[data-fv-r339-cta="editorial"]').count()==1,name
  assert page.locator('[data-fv-r355-reviewed-source]').count()==1,name
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),name
  dupe=page.evaluate('''() => {let ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return ids.filter((x,i)=>ids.indexOf(x)!==i)}'''); assert not dupe,(name,dupe)
  original=page.locator('.fv-apollo-r355__source summary');original.focus();page.keyboard.press('Enter')
  assert original.evaluate('(e)=>e.parentNode.open'),name
  if enable:
   buttons=page.locator('[data-fv-apollo-filters] button');assert buttons.count()==5,name
   if touch:buttons.nth(1).tap()
   else:buttons.nth(1).click()
   assert page.locator('[data-fv-apollo-entry]:visible').count()==3,name
   buttons.first.click();assert page.locator('[data-fv-apollo-entry]:visible').count()==13,name
  else:assert page.locator('[data-fv-apollo-filters]:visible').count()==0,name
  src=page.locator('[data-fv-r355-reviewed-source]');assert src.get_attribute('href')=='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',name
  assert src.inner_text().strip(),name
  assert page.locator('[data-fv-apollo-postfire] img').count()==0,name
  shot=OUT/f'r355-{name}.png';page.screenshot(path=str(shot),full_page=False)
  page.wait_for_timeout(120)
  perf=page.evaluate('window.__testPerf||null') if enable else None
  reports.append({'case':name,'width':width,'javascript_enabled':enable,'root_font_px':root_size,'touch':touch,'reduced_motion':motion,'forced_colors':forced,'unique_dom_ids':True,'no_horizontal_overflow':True,'source_link_approved':True,'native_details_keyboard':True,'local_fixture_lcp_ms':round(max(perf['lcp']),1) if perf and perf['lcp'] else None,'local_fixture_cls':perf['cls'] if perf else None,'pass':True})
  ctx.close()
 ctx=browser.new_context(viewport={'width':390,'height':900})
 page=ctx.new_page();page.set_content(page_html,wait_until='load');page.add_script_tag(content=js)
 page.locator('[data-fv-apollo-filters] button').last.click()
 pdf=OUT/'r355-custody-print.pdf';pdf.write_bytes(page.pdf(print_background=True,format='A4'))
 ctx.close();browser.close()
pdoc=fitz.open(pdf);text='\n'.join(pg.get_text() for pg in pdoc)
for token in ('102 deliberate ignitions','February 14, 2018','December 1967','Evidence boundary','Later NASA'):
 assert token in text,token
links=[entry.get('uri','') for pg in pdoc for item in pg.get_links() if (entry:=item).get('uri')]
assert any('50-years-ago-apollo-flammability-tests' in link for link in links),links
report={'scope':'Local PHP-rendered fixture in real Chromium; no installed WordPress, axe-core, independent screen reader, browser HTTP CSP or production CWV.','cases':reports,'print':{'pages':len(pdoc),'later_source_in_pdf':True,'annotation_present':True,'pdf':str(pdf.relative_to(BASE))},'pass':True}
(OUT/'r355-browser-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'browser_cases_passed':len(reports),'pdf_pages':len(pdoc),'lcp_ms':[x['local_fixture_lcp_ms'] for x in reports],'cls':[x['local_fixture_cls'] for x in reports]},indent=2))
