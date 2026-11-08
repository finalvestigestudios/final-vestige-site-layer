#!/usr/bin/env python3
"""Offline Chromium LCP/CLS fixture measurement; not installed WP or field CWV."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1]/'dist'
res=json.loads(subprocess.check_output(['php',str(R/'wp-render-shim-r215.php'),str(R/'fv-ex2-apollo-r215.php'),'normal'],text=True))
html=res['html'];css=(R/'assets/atlas-scoped.css').read_text()
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,390,768,1024,1440,1920]:
  c=browser.new_context(viewport={'width':w,'height':850})
  page=c.new_page()
  page.evaluate('''() => {window.__fvCLS=0;window.__fvLCP=null;
    new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)window.__fvCLS+=e.value}}).observe({type:'layout-shift',buffered:true});
    new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__fvLCP=e.startTime}}).observe({type:'largest-contentful-paint',buffered:true});}''')
  page.set_content('<!DOCTYPE html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>')
  page.wait_for_timeout(220)
  x=page.evaluate('''() => ({LCP_ms:window.__fvLCP,CLS:window.__fvCLS,CLS_POsupported:PerformanceObserver.supportedEntryTypes.includes('layout-shift'),LCP_POsupported:PerformanceObserver.supportedEntryTypes.includes('largest-contentful-paint'),body_w:document.body.scrollWidth,viewport_w:document.documentElement.clientWidth})''')
  x['viewport']=w;results.append(x)
  c.close()
 browser.close()
out=R.parent/'fixture-performance.json'
out.write_text(json.dumps({'tool':'Chromium PerformanceObserver in injected offline fixture', 'production_metric':False,'not_a_lighthouse_report':True,'observations':results},indent=2)+'\n')
print(out.read_text())
