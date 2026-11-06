#!/usr/bin/env python3
"""Local-document LCP/CLS instrumentation. NOT real-site Core Web Vitals."""
import argparse,hashlib,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
WIDTHS=(320,360,390,768,1440,1920)
REVIEW='67b612be3dfb385fd03e952a59e9ec5088c25a89821a3420a5f199326da57c83'
def main(a):
    html=Path(a.review).read_bytes()
    assert hashlib.sha256(html).hexdigest()==REVIEW, 'Changed source: STOP'
    css='\n'.join(Path(f).read_text() for f in a.css)
    report={'scope':'LOCAL_DOCUMENT_OFFLINE_LAB_ONLY','production_CWV':False,'release':'STAGING_HOLD','source_sha256':REVIEW,'results':[]}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
      report['browser']=browser.version
      for w in WIDTHS:
        context=browser.new_context(viewport={'width':w,'height':850},device_scale_factor=1,service_workers='block')
        context.route('**/*',lambda r:r.abort())
        page=context.new_page()
        page.set_content('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><body style="margin:0"><main>'+html.decode()+'</main></body>')
        page.evaluate("""() => {
          window.__localLCP=[]; window.__localCLS=[];
          new PerformanceObserver(list => { for(const entry of list.getEntries()) window.__localLCP.push({ms:entry.startTime,size:entry.size,element:entry.element?.tagName || null}) }).observe({type:'largest-contentful-paint',buffered:true});
          new PerformanceObserver(list => { for(const entry of list.getEntries()) if(!entry.hadRecentInput) window.__localCLS.push(entry.value) }).observe({type:'layout-shift',buffered:true});
        }""")
        page.add_style_tag(content=css)
        page.wait_for_timeout(400)
        perf=page.evaluate("""() => ({lcp:window.__localLCP,cls:window.__localCLS.reduce((x,y)=>x+y,0),layoutOverflow:document.documentElement.scrollWidth>innerWidth+1})""")
        report['results'].append({'width':w,'lcp_entries':perf['lcp'],'cls_without_recent_input':perf['cls'], 'horizontal_overflow':perf['layoutOverflow']})
        context.close()
      browser.close()
    Path(a.out).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('LAB ONLY:',[(r['width'],r['lcp_entries'][-1]['ms'] if r['lcp_entries'] else None,r['cls_without_recent_input']) for r in report['results']])
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--review',required=True);ap.add_argument('--css',required=True,action='append');ap.add_argument('--out',required=True)
    ap.add_argument('--chromium',default=os.getenv('FV_CHROMIUM','/usr/bin/chromium'))
    main(ap.parse_args())
