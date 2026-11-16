#!/usr/bin/env python3
"""Local ONLY document.write Chromium paint/shift observations; never p75 CWV."""
import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT="""<script>window.__apolloLab={lcp:null,cls:0,observer_errors:[]};
try { new PerformanceObserver(list=>{for(const entry of list.getEntries()){
 if(!entry.hadRecentInput)window.__apolloLab.cls+=entry.value;
 }}).observe({type:'layout-shift',buffered:true});
 new PerformanceObserver(list=>{for(const entry of list.getEntries()){
 window.__apolloLab.lcp=entry.startTime;
 }}).observe({type:'largest-contentful-paint',buffered:true});
}catch(e){window.__apolloLab.observer_errors.push(String(e));}</script>"""

def measure(path):
    source=Path(path).read_text(encoding='utf-8')
    if '<head>' not in source:raise ValueError('fixture needs exact <head>')
    html=source.replace('<head>','<head>'+SCRIPT,1)
    rows=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        try:
            for name,width in [('320',320),('390',390),('768',768),('1440',1440),('1920',1920)]:
                ctx=b.new_context(viewport={'width':width,'height':860})
                page=ctx.new_page();page.set_content(html,wait_until='load');page.wait_for_timeout(250)
                d=page.evaluate('window.__apolloLab')
                rows.append({'context':name,'width':width,'lcp_ms':d['lcp'],'cls':d['cls'],
                    'observer_errors':d['observer_errors'],'scope':'LOCAL_HTML_FIXTURE'})
                ctx.close()
        finally:b.close()
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--fixture',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();r=measure(a.fixture)
    Path(a.output).write_text(json.dumps({'scope':'LOCAL_ONLY_NOT_CWV','samples':r},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'samples':len(r),'lcp_ms':[x['lcp_ms'] for x in r],
                      'cls':[x['cls'] for x in r],'scope':'LOCAL_ONLY_NOT_CWV'}))
