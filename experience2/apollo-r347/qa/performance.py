#!/usr/bin/env python3
"""Actual Chromium PerformanceObserver timings for a *local page.set_content fixture*, never production CWV."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
qa=root/'apollo-r347/QA';qa.mkdir(exist_ok=True)
php=root/'apollo-r347/source-index.php'
markup=subprocess.check_output(['php','-r',"define('ABSPATH',true);require '"+str(php)+"';echo fv_apollo_r347_experience_shortcode();"],text=True)
css='\n'.join((root/p).read_text() for p in ('apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css'))
js=(root/'apollo-r347/assets/source-index.js').read_text()
probe='''<script>window.__r347perf={lcp:null,cls:0,observed_lcp:0,observed_shifts:0};
new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__r347perf.lcp=e.startTime;window.__r347perf.observed_lcp++}}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput){window.__r347perf.cls+=e.value;window.__r347perf.observed_shifts++}}}).observe({type:'layout-shift',buffered:true});</script>'''
rows=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
  c=b.new_context(viewport={'width':width,'height':900});page=c.new_page()
  page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8">'+probe+'<style>body{margin:0}'+css+'</style></head><body>'+markup+'</body></html>',wait_until='load')
  page.add_script_tag(content=js);page.wait_for_timeout(700)
  data=page.evaluate('window.__r347perf');assert data['lcp'] is not None,f'LCP not observed at {width}'
  assert data['cls']<=0.1,f'CLS > 0.1 at {width}'
  rows.append(dict(viewport=width,lcp_ms=round(data['lcp'],1),observed_cls=round(data['cls'],5),lcp_events=data['observed_lcp'],layout_shift_events=data['observed_shifts']))
  c.close()
 b.close()
receipt={'type':'LOCAL_CHROMIUM_FIXTURE_ONLY','method':'PerformanceObserver buffered LCP and layout-shift after page.set_content; 700 ms observation window; no actual HTTP or WordPress','results':rows,'not_established':['production p75 LCP','production CLS','INP','slow-connection performance','WordPress/Assembler/CSP/third-party effects']}
(qa/'r347-local-performance.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS 5 Chromium local fixture PerformanceObserver contexts: '+', '.join(f"{r['viewport']}px={r['lcp_ms']}ms LCP/CLS {r['observed_cls']}" for r in rows))
