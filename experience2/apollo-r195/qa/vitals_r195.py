#!/usr/bin/env python3
"""True Chromium PerformanceObserver measurements of the OFFLINE PHP fixture.
Not production Lighthouse, RUM or installed WordPress Core Web Vitals.
"""
import json,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r195 import build
WIDTHS=(320,390,768,1440,1920)

def measure(out:Path):
    build();dist=ROOT/'dist';out.mkdir(parents=True,exist_ok=True)
    res=json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r195.php'),str(dist/'fv-ex2-apollo-r195.php'),'normal'],text=True))
    assert not res['fallback']
    css=(dist/'assets/atlas-scoped.css').read_text()
    receipt={'kind':'actual Chromium PerformanceObserver / offline PHP shim, NOT production CWV','contexts':[]}
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
            page=ctx.new_page()
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+res['html']+'</body></html>',wait_until='load')
            result=page.evaluate('''async () => {
              const L=[], S=[];
              const po=new PerformanceObserver(items => { for (const e of items.getEntries()) L.push(e.startTime); });
              const cls=new PerformanceObserver(items => { for (const e of items.getEntries()) if (!e.hadRecentInput) S.push(e.value); });
              po.observe({type:'largest-contentful-paint',buffered:true});
              cls.observe({type:'layout-shift',buffered:true});
              await new Promise(resolve=>setTimeout(resolve,190));
              po.disconnect();cls.disconnect();
              return {lcp_ms:L.length?Math.max(...L):null,cls:S.reduce((a,b)=>a+b,0),lcp_entries:L.length,cls_entries:S.length};
            }''')
            assert result['lcp_ms'] is not None,('LCP observer unsupported or no entry',width)
            assert result['cls']<=0.1,('offline layout shift budget',width,result)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            receipt['contexts'].append({'width':width,**result})
            ctx.close()
        b.close()
    (out/'fixture-vitals.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':measure(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence')
