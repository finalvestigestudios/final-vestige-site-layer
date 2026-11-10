#!/usr/bin/env python3
"""Chromium CDP accessible-name and offline performance sampling, NOT axe or field CWV."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

NAMES=('Check the atmosphere finding','Check the ignition finding','Examine the aftermath record')
def digest(data):return hashlib.sha256(data).hexdigest()

def main():
 p=argparse.ArgumentParser()
 for n in ('atlas','r253','r254','r255','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
 m=(a.atlas/'manifest.json').read_bytes()
 assert digest(m)=='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
 for name,expected in json.loads(m)['files'].items():assert digest((a.atlas/name).read_bytes())==expected
 php=subprocess.run(['php',str(a.atlas/'wp-render-shim-r224.php'),str((a.atlas/'fv-ex2-apollo-r224.php').resolve()),'normal'],capture_output=True,text=True,check=True)
 html=json.loads(php.stdout)['html'];assert html==(a.atlas/'templates/atlas-fragment.html').read_text()
 css='\n'.join(p.read_text() for p in (a.atlas/'assets/atlas-scoped.css',a.r253,a.r254,a.r255))
 monitor='''<script>window.apolloMetrics={lcp:[],cls:[]};
 try{new PerformanceObserver(xs=>{for(const e of xs.getEntries())window.apolloMetrics.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
 try{new PerformanceObserver(xs=>{for(const e of xs.getEntries())if(!e.hadRecentInput)window.apolloMetrics.cls.push(e.value)}).observe({type:'layout-shift',buffered:true});}catch(e){}
 </script>'''
 out=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in (320,390,768,1440,1920):
   c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=True,reduced_motion='reduce')
   pg=c.new_page();pg.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style>'+monitor+'</head><body>'+html+'</body></html>')
   pg.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
   pg.evaluate('document.fonts.ready')
   pg.wait_for_timeout(120)
   ses=c.new_cdp_session(pg);nodes=ses.send('Accessibility.getFullAXTree')['nodes']
   names={n.get('name',{}).get('value') for n in nodes if n.get('role',{}).get('value')=='link'}
   assert all(v in names for v in NAMES),f'missing Chromium AX accessible names at {width}: {names}'
   mt=pg.evaluate('window.apolloMetrics')
   out.append({'width':width,'cda_link_names_verified':len(NAMES),'observed_lcp_ms':round(max(mt['lcp']),1) if mt['lcp'] else None,'observed_cls':round(sum(mt['cls']),5),'layout_shift_entries':len(mt['cls'])})
   c.close()
  b.close()
 receipt={'status':'PASS','scope':'original-PHP offline Chromium CDP AX tree and PerformanceObserver','contexts':len(out),'rows':out,'genuine_axe':'NOT_RUN','field_cwv':'NOT_MEASURED','installed_wordpress':'NOT_RUN'}
 (a.out/'ax-performance.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
