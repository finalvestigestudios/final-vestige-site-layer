#!/usr/bin/env python3
"""R264 offline, source-matched text-resize & conversion-link acceptance.
Run with real R224+R262 PHP via the R263 WordPress API mock; never contacts WP.
CSS root font-size testing is NOT browser UI zoom or an axe-core audit.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MANIFEST='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
BLOBS={'fv-apollo-staging-overlay.php':'e6406fea01435d51817edcc20d69b9b3808505ac',
       'assets/source-drawer-focus.js':'2c196dbb733345e6e51a27af2d2894ca4461a2c9',
       'integrity.json':'4dd45c5fc2fb35d93d702c079f83528b85c937c2'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def require(test,message):
    if not test:raise AssertionError(message)
def main(a):
    root=a.fixture.resolve();over=a.overlay.resolve();mock=a.mock.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    require(sha((root/'manifest.json').read_bytes())==MANIFEST,'sealed fixture manifest drift')
    for path,digest in json.loads((root/'manifest.json').read_text())['files'].items():
        require(sha((root/path).read_bytes())==digest,'original historical source drift: '+path)
    for path,digest in BLOBS.items():require(blob((over/path).read_bytes())==digest,'staging integration drift: '+path)
    def render(mode):
        result=subprocess.run(['php',str(mock),str(root/'fv-ex2-apollo-r224.php'),str(over/'fv-apollo-staging-overlay.php'),mode],capture_output=True,text=True,check=True,timeout=12)
        return json.loads(result.stdout)
    for mode in ('direct','synced'):
        check=render(mode)
        require(check['atlas_present'] and not check['fallback'],mode+' did not render exact Apollo')
        require('fv-apollo-r262-overlays' in check['styles'],mode+' overlay not loaded')
    html=render('direct')['html']
    require(sha(html.encode())=='50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6','Apollo HTML changed')
    css=(root/'assets/atlas-scoped.css').read_text()+'\n'+(over/'assets/apollo-overlays.css').read_text()
    script=(over/'assets/source-drawer-focus.js').read_text()
    page_html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
    cases=[];shots={}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for size in (100,200,400):
                for enabled in (False,True):
                    ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                    page=ctx.new_page();requests=[];page.on('request',lambda r:requests.append(r.url));page.set_content(page_html)
                    if enabled:page.add_script_tag(content=script)
                    page.evaluate('(size)=>document.documentElement.style.fontSize=size+"%"',size)
                    metrics=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth > innerWidth+1,
                      nasa:[...document.querySelectorAll('a[href^="https://www.nasa.gov/"]')].length,
                      anchors:[...document.querySelectorAll('a[href^="#"]')].every(a=>!!document.getElementById(a.hash.slice(1))),
                      free:[...document.querySelectorAll('a[href]')].filter(a=>a.href==='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/').length,
                      merchants:[...document.querySelectorAll('a[href]')].filter(a=>/payhip|awin1|mini-museum/i.test(a.href)).length})''')
                    require(not metrics['overflow'] and metrics['nasa']==55 and metrics['anchors'] and metrics['free']==1 and metrics['merchants']==0 and not requests,f'reflow/link breach {width} {size}% JS={enabled} {metrics}')
                    link=page.locator('a[href="#fv-apollo-source-drawer"]').first
                    link.focus();link.press('Enter');page.wait_for_timeout(50)
                    drawer=page.locator('#fv-apollo-source-drawer');summary=drawer.locator('summary')
                    require(page.evaluate('location.hash')=='#fv-apollo-source-drawer','fragment broken')
                    if enabled:
                        require(drawer.evaluate('(x)=>x.open') and summary.evaluate('(x)=>x===document.activeElement'),'keyboard focus broken')
                    else:
                        summary.focus();summary.press('Enter');require(drawer.evaluate('(x)=>x.open'),'no-JS disclosure broken')
                    if width in (390,1440) and size==200:
                        filename=f'{width}-{size}-'+('js' if enabled else 'nojs')+'.png'
                        image=page.screenshot(animations='disabled');(out/filename).write_bytes(image);shots[filename]=sha(image)
                    cases.append({'width':width,'text_size_percent':size,'javascript':enabled,'passed':True})
                    ctx.close()
        # Deliberate mutation: a fixed 900px min-width must be rejected by the reflow assertion.
        ctx=browser.new_context(viewport={'width':320,'height':900});page=ctx.new_page();page.set_content(page_html)
        page.add_style_tag(content='.fv-apollo-atlas {min-width:900px !important}')
        # Assert the target or its ancestor itself overflows; a separate doc-scroll guard
        # alone can be masked by an overflow:hidden wrapper.
        mutation=page.locator('.fv-apollo-atlas').evaluate('(e)=>e.getBoundingClientRect().width>window.innerWidth+1')
        require(mutation,'negative-control overflow mutation escaped detection')
        ctx.close();browser.close()
    receipt={'status':'LOCAL_COMPONENT_QA_PASS_NOT_LIVE','cases':cases,'source_manifest_sha256':MANIFEST,
      'original_html_sha256':sha(html.encode()),'verified_overlay_git_blobs':BLOBS,'screenshots':shots,
      'negative_control':'900px min-width detected at 320px',
      'genuine_axe':'NOT EXECUTED: no verified bundle available',
      'browser_ui_zoom':'NOT EXECUTED: root font-size stress is not browser UI zoom',
      'installed_wordpress':'NOT EXECUTED','http_csp':'NOT EXECUTED: browser navigation blocked',
      'performance':'No production/field LCP or CLS claim','release':'STAGING HOLD'}
    receipt['receipt_sha256']=sha(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode())
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'contexts':len(cases),'screenshot_count':len(shots),'receipt_sha256':receipt['receipt_sha256']}))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--fixture',type=Path,required=True);a.add_argument('--overlay',type=Path,required=True);a.add_argument('--mock',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--chromium',default='/usr/bin/chromium');main(a.parse_args())
