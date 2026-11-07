#!/usr/bin/env python3
"""Laboratory-only LCP/CLS observations from a PHP-rendered Apollo Atlas.
Real Chromium PerformanceObserver, but set_content, not a network navigation.
Do NOT interpret values as installed WordPress or field Core Web Vitals.
"""
from pathlib import Path
import json,subprocess,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
shim=DIST/'wp-render-shim-r193.php'
if not shim.exists():
    sys.path.insert(0,str(ROOT/'qa'))
    from gate_r193 import get_php_html
    get_php_html()
res=subprocess.run(['php',str(shim),str(DIST/'fv-ex2-apollo-r193.php')],capture_output=True,text=True,check=True)
html=json.loads(res.stdout)['html']
css=(DIST/'assets/atlas-scoped.css').read_text()
instrument="""<script>
window.__vitals={lcp:[],cls:0};
new PerformanceObserver(list=>{for(const e of list.getEntries())window.__vitals.lcp.push(Math.round(e.startTime));}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value;}).observe({type:'layout-shift',buffered:true});
</script>"""
out=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
    page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
    page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1">'+instrument+'<style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
    page.wait_for_timeout(300)
    metrics=page.evaluate('window.__vitals')
    assert metrics['lcp'], f'no LCP observer entry at {width}'
    assert metrics['cls']>=0
    out.append({'width':width,'fixture_lcp_ms':metrics['lcp'][-1],'fixture_cls':metrics['cls'],'mode':'Chromium set_content (NOT real page navigation)'})
    page.close()
 browser.close()
path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence/fixture_vitals.json'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps({'observations':out,'not_field_data':True},sort_keys=True,indent=2)+'\n')
print(json.dumps(out,indent=2))
