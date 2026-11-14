#!/usr/bin/env python3
"""R354 independent Playwright Chromium release-candidate QA (PHP-rendered fixture, NOT installed WP/axe)."""
import json, subprocess, hashlib, re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]; EX2=ROOT/'experience2'
OUT=EX2/'apollo-r354'/'QA';OUT.mkdir(parents=True,exist_ok=True)
render='define("ABSPATH",true);require '+json.dumps(str(EX2/'apollo-r348/source-custody.php'))+';echo fv_apollo_r348_experience_shortcode();'
html=subprocess.check_output(['php','-r',render],text=True)
styles='\n'.join((EX2/p).read_text() for p in ['apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css','apollo-r348/assets/source-custody.css'])
js=(EX2/'apollo-r347/assets/source-index.js').read_text()
assert html.count('data-fv-apollo-entry=')==13
assert html.count('data-fv-r339-cta="editorial"')==1
perf='''window.__perf={lcp:[],cls:0};
try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__perf.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}'''
def doc():return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+styles+'</style></head><body>'+html+'</body></html>'
# Collect visible named interactive elements, run document/section/link integrity checks.
probe='''() => {
 const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
 const a=[...document.querySelectorAll('a[href]')];
 const bad=a.filter(x=>{if(x.getAttribute('href').startsWith('#'))return !document.getElementById(x.getAttribute('href').slice(1));let u=new URL(x.href);return u.protocol!=='https:'||(!['www.nasa.gov','finalvestige.com'].includes(u.hostname))});
 const source=a.filter(x=>x.href.startsWith('https://www.nasa.gov/'));
 return {ids:ids.length,duplicate_ids:ids.filter((x,i)=>ids.indexOf(x)!==i),links:a.length,nasa_links:source.length,
 bad_links:bad.map(x=>x.href),unnamed_links:a.filter(x=>!x.textContent.trim()&&!x.getAttribute('aria-label')).map(x=>x.outerHTML.slice(0,100)),
 headings:[...document.querySelectorAll('h2')].map(e=>e.textContent.trim()),source_drawers:document.querySelectorAll('summary').length,
 original_context:document.body.innerText.includes('single ignition source')};
}'''
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 configurations=[('narrow-320-400percent',320,True,False,'no-preference','none',64),('mobile-390-nojs',390,False,True,'reduce','none',16),('tablet-touch-768',768,True,True,'reduce','none',16),('desktop-keyboard-1440',1440,True,False,'no-preference','none',16),('wide-forced-colors-1920',1920,True,False,'reduce','active',16)]
 for name,width,enabled,touch,motion,forced,font in configurations:
  ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,has_touch=touch,is_mobile=False,reduced_motion=motion,forced_colors=forced)
  page=ctx.new_page();page.set_content(doc(),wait_until='load')
  if enabled: page.evaluate(perf);page.add_script_tag(content=js)
  if font!=16: page.evaluate('(f)=>document.documentElement.style.fontSize=f+"px"',font)
  v=page.evaluate(probe)
  assert not v['duplicate_ids'], (name,v['duplicate_ids'][:10])
  assert not v['bad_links'] and not v['unnamed_links'],(name,v['bad_links'],v['unnamed_links'])
  assert v['source_drawers']==21, (name,v['source_drawers'])
  assert v['nasa_links']>0, name
  assert page.locator('[data-fv-apollo-entry]:visible').count()==13
  assert page.locator('[data-fv-r339-cta="editorial"]').count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),name
  summary=page.locator('details > summary').first
  summary.focus()
  page.keyboard.press('Enter')
  assert summary.evaluate('(el)=>el.parentElement.open'),name
  page.keyboard.press('Enter')
  assert not summary.evaluate('(el)=>el.parentElement.open'),name
  if enabled:
   buttons=page.locator('[data-fv-apollo-filters] button')
   assert buttons.count()==5,name
   buttons.nth(1).focus()
   page.keyboard.press('Space')
   assert page.locator('[data-fv-apollo-entry]:visible').count()==3,name
   assert buttons.nth(1).get_attribute('aria-pressed')=='true'
   if touch:buttons.last.tap()
   else:buttons.last.click()
   assert page.locator('[data-fv-apollo-entry]:visible').count()==4,name
   buttons.first.click()
   assert page.locator('[data-fv-apollo-entry]:visible').count()==13,name
  else:assert page.locator('[data-fv-apollo-filters]:visible').count()==0
  picture=OUT/(name+'.png');page.screenshot(path=str(picture),full_page=(width in (320,390)))
  page.wait_for_timeout(200)
  data=page.evaluate('window.__perf') if enabled else None
  results.append({'case':name,'width':width,'js':enabled,'touch':touch,'reduced_motion':motion,'forced_colors':forced,'font_px':font,'nasa_links':v['nasa_links'],'disclosures':21,'all_13_visible_initially':True,'links_named':True,'unique_dom_ids':True,'overflow':False,'pass':True,'local_fixture_lcp_ms':(max(data['lcp']) if data and data['lcp'] else None),'local_fixture_cls_observed':data['cls'] if data else None,'screenshot':str(picture.relative_to(ROOT))})
  ctx.close()
 ctx=b.new_context(viewport={'width':390,'height':900})
 page=ctx.new_page();page.set_content(doc(),wait_until='load');page.add_script_tag(content=js)
 page.locator('[data-fv-apollo-filters] button').last.click()
 pdf=OUT/'apollo-r354-printed-custody.pdf';pdf.write_bytes(page.pdf(print_background=True,format='A4'))
 ctx.close();b.close()
import fitz
pdfdoc=fitz.open(pdf)
text='\n'.join(page.get_text() for page in pdfdoc)
for s in ['Board findings','Recorded chronology','Later NASA history','Contextual photographs','Evidence boundary:','Rights review required:']:
 assert s in text,('missing print evidence',s)
print_info={'pages':len(pdfdoc),'all_four_groups_print':True,'source_limits_print':True,'pdf':str(pdf.relative_to(ROOT))}
result={'scope':'Local PHP-rendered Chromium set_content fixture; no installed WordPress, browser-enforced HTTP/CSP, axe-core or third-party screen reader.','cases':results,'print':print_info,'passed':True}
(OUT/'browser-qa.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pass':True,'contexts':len(results),'print_pages':len(pdfdoc),'local_lcp_ms':[round(x['local_fixture_lcp_ms'],1) if x['local_fixture_lcp_ms'] else None for x in results],'local_cls':[x['local_fixture_cls_observed'] for x in results]},indent=2))
