#!/usr/bin/env python3
"""R233: actual generated Apollo Atlas LCP/CLS/reflow probe; local fixture, NOT field CWV.

No CDN, network analytics, paid service, or WordPress writes. Chrome system binary is
required. Performance results intentionally excluded from deterministic receipt.
"""
import argparse, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright

MANIFEST = '28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413'
WIDTHS = (320, 390, 768, 1440, 1920)

def sha(b): return hashlib.sha256(b).hexdigest()
def put(path, data): path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n', encoding='utf8')

def run(dist, out):
    if sha((dist/'manifest.json').read_bytes()) != MANIFEST:
        raise AssertionError('R228 manifest drift')
    manifest = json.loads((dist/'manifest.json').read_text())
    for path, expected in manifest['files'].items():
        if sha((dist/path).read_bytes()) != expected: raise AssertionError('Modified fixture: '+path)
    html = (dist/'templates/atlas-fragment.html').read_text()
    css = (dist/'assets/atlas-scoped.css').read_text()
    doc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
    out.mkdir(parents=True, exist_ok=True)
    fixed=[]; perf=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (*WIDTHS, 256):
            for js in ((True,False) if width!=256 else (False,)):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    device_scale_factor=1,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                page=ctx.new_page(); network=[]
                page.on('request', lambda r: network.append(r.url))
                page.set_content(doc,wait_until='load')
                page.wait_for_timeout(80)
                metrics=page.evaluate('''() => ({
                  width:document.documentElement.clientWidth,
                  overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
                  source_records:document.querySelectorAll('[data-source-record]').length,
                  native_disclosures:document.querySelectorAll('details>summary').length,
                  cta:document.querySelectorAll('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').length,
                  scripts:document.querySelectorAll('script').length,
                  geo:document.querySelectorAll('[data-lat],[data-lng],[data-latitude],[data-longitude]').length
                })''')
                assert not network, network
                assert metrics['overflow']<=1 and metrics['source_records']==4 and metrics['native_disclosures']>=4
                assert metrics['cta']==1 and metrics['scripts']==0 and metrics['geo']==0
                if js:
                    lcp=page.evaluate('''() => new Promise(resolve=>{
                      const v=[];const ob=new PerformanceObserver(l=>l.getEntries().forEach(e=>v.push(e.startTime)));
                      ob.observe({type:'largest-contentful-paint',buffered:true});
                      setTimeout(()=>{ob.disconnect();resolve(v.length?Math.round(Math.max(...v)):null)},75)
                    })''')
                    cls=page.evaluate('''() => new Promise(resolve=>{
                      let x=0;const ob=new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)x+=e.value}));
                      ob.observe({type:'layout-shift',buffered:true});
                      setTimeout(()=>{ob.disconnect();resolve(Math.round(x*1000000)/1000000)},75)
                    })''')
                    perf.append({'width':width,'fixture_lcp_ms':lcp,'fixture_cls_post_observer':cls})
                # Native keyboard disclosure must remain functional with JS disabled.
                summary=page.locator('details>summary').first
                parent=summary.locator('xpath=..')
                before=parent.evaluate('(e)=>e.open')
                summary.focus();page.keyboard.press('Enter')
                assert parent.evaluate('(e)=>e.open') != before
                summary.press('Enter')
                page.evaluate('scrollTo(0,0)')
                screenshot=out/f'{width}-{"js" if js else "nojs"}.png'
                page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
                fixed.append({'width':width,'js':js,'metrics':metrics,'screenshot_sha256':sha(screenshot.read_bytes())})
                ctx.close()
        version=browser.version
        browser.close()
    receipt={'scope':'exact SHA-pinned generated R228 Atlas offline component only',
       'browser':version,'manifest_sha256':MANIFEST,'results':fixed,
       'unverified':['production or field CWV','true browser UI zoom','axe-core','installed WordPress','screen reader','hosted CI']}
    put(out/'receipt.json',receipt)
    put(out/'fixture-performance-observations.json',perf)
    return {'receipt_sha256':sha((out/'receipt.json').read_bytes()),'contexts':len(fixed),'performance':perf}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--dist',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();print(json.dumps(run(a.dist,a.out),indent=2))
