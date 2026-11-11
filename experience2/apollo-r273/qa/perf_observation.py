#!/usr/bin/env python3
"""Real offline Chromium PerformanceObserver; NOT field HTTP/CSP or p75 Core Web Vitals."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess,json,sys
root=Path(__file__).resolve().parents[1]
h=subprocess.check_output(['php',str(root/'qa/render.php'),'pending']).decode()
rows=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,390,768,1440,1920]:
  context=b.new_context(viewport={'width':w,'height':800},device_scale_factor=1)
  page=context.new_page();page.set_content(h,wait_until='load')
  entries=page.evaluate('''async () => {
    const lcp=[], shifts=[];
    const a=new PerformanceObserver(list=>{for(const e of list.getEntries())lcp.push({startTime:e.startTime,size:e.size})});
    const b=new PerformanceObserver(list=>{for(const e of list.getEntries())shifts.push({value:e.value,hadRecentInput:e.hadRecentInput})});
    a.observe({type:'largest-contentful-paint',buffered:true});
    b.observe({type:'layout-shift',buffered:true});
    await new Promise(resolve=>setTimeout(resolve,300));a.disconnect();b.disconnect();
    return {lcp,shifts,first_contentful_paint:performance.getEntriesByType('paint').filter(e=>e.name==='first-contentful-paint').map(e=>e.startTime)};
  }''')
  rows.append({'viewport_width':w,'lcp_ms':entries['lcp'][-1]['startTime'] if entries['lcp'] else None,
     'lcp_candidate_count':len(entries['lcp']),
     'observed_cls':round(sum(x['value'] for x in entries['shifts'] if not x['hadRecentInput']),6),
     'shift_events':len(entries['shifts']),
     'fcp_ms':entries['first_contentful_paint'][-1] if entries['first_contentful_paint'] else None})
  context.close()
 b.close()
report={'context':'SOURCE-PREVIEW LOCAL-CHROMIUM ONLY; not live WordPress, network or field p75',
    'browser':'Chromium','scenario':'staging R273 PHP-generated HTML via set_content',
    'measurements':rows,'field_p75_lcp':'UNAVAILABLE','field_p75_cls':'UNAVAILABLE'}
output=Path(sys.argv[1]);output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
