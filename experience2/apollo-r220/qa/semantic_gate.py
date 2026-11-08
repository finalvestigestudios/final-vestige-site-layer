#!/usr/bin/env python3
"""R220 isolated native Chromium accessibility and resilient navigation gate.
Reuses exact GitHub R219 gate; no axe-core, real zoom, or WordPress claims.
"""
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

R219_BLOB='99e4ee33e69ddeee011b33b25ab6c54fef8c8e89'
WIDTHS=(320,390,768,1440,1920)
IDS={'S66-58038','S67-15717','Apollo 204 Review Board','S67-21294'}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def check(ok,msg):
    if not ok: raise AssertionError(msg)
def sha(data): return hashlib.sha256(data).hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def run(workspace,out):
    out.mkdir(parents=True,exist_ok=True)
    parent=workspace/'r219/qa/mobile_gate.py'
    check(blob(parent.read_bytes())==R219_BLOB,'R219 exact GitHub blob changed')
    spec=importlib.util.spec_from_file_location('r219_gate',parent)
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    gate.run(workspace,out/'r219-regression')  # Full 320–1920, JS and no-JS, LCP/CLS.
    dist=workspace/'apollo-r217/dist'
    php=json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r217.php'),
       str(dist/'fv-ex2-apollo-r217.php'),'normal'],text=True))
    check(not php['fallback'] and not php['js'],'Unverified PHP fragment')
    css=(dist/'assets/atlas-scoped.css').read_text()
    cross=json.loads((dist/'source-url-crosswalk.json').read_text())
    doc='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+php['html']+'</body></html>'
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':844},is_mobile=width<=390,
                    has_touch=width<=390,java_script_enabled=js,forced_colors='active',reduced_motion='reduce')
                page=ctx.new_page();page.set_content(doc,wait_until='domcontentloaded')
                data=page.evaluate('''() => {
                   const anchors=[...document.querySelectorAll('.fv-apollo-atlas a[href]')];
                   const ids=new Set([...document.querySelectorAll('[id]')].map(e=>e.id));
                   return {broken:anchors.filter(a=>a.getAttribute('href').startsWith('#') &&
                     !ids.has(a.getAttribute('href').slice(1))).length,
                     external:anchors.filter(a=>!a.getAttribute('href').startsWith('#')).map(a=>a.href),
                     sources:[...document.querySelectorAll('[data-source-id]')].map(a=>[a.dataset.sourceId,a.href]),
                     links:anchors.length, overflow:document.documentElement.scrollWidth>innerWidth+2};}''')
                check(not data['broken'] and not data['overflow'] and data['links']>=50,'Links/overflow')
                check({x[0] for x in data['sources']}==IDS,'NASA catalog ID drift')
                check(all({'source_id':sid,'url':url} in cross['source_bindings'] for sid,url in data['sources']),
                      'Research Desk source-url mismatch')
                check(FREE in data['external'] and all(urlsplit(u).scheme=='https' and
                     urlsplit(u).netloc in ('www.nasa.gov','finalvestige.com') for u in data['external']),
                     'Unauthorized commerce/source host')
                ax=ctx.new_cdp_session(page);ax.send('Accessibility.enable')
                tree=ax.send('Accessibility.getFullAXTree')['nodes']
                tree=[n for n in tree if not n.get('ignored')]
                roles=[n.get('role',{}).get('value','') for n in tree]
                names=[n.get('name',{}).get('value','') for n in tree]
                check(all(r in roles for r in ('article','heading','link')) and
                      any('Read original investigation' in n for n in names),'Chromium AX tree')
                page.keyboard.press('Tab')
                check(page.evaluate('document.activeElement.getAttribute("href")')=='#fv-apollo-main',
                      'Skip link not keyboard-first')
                page.keyboard.press('Enter')
                check(page.evaluate('location.hash')=='#fv-apollo-main','Skip link fails without JS')
                page.locator('.fv-apollo-nav-read').focus();page.keyboard.press('Enter')
                check(page.evaluate('location.hash')=='#fv-apollo-reading-bridge','Reading route fails')
                page.locator('.fv-apollo-atlas').evaluate("e=>e.style.zoom='200%'")
                stress=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth+3,
                   target:document.querySelector('a.cta').getBoundingClientRect().height})''')
                check(not stress['overflow'] and stress['target']>=44,'200% CSS zoom overflow/CTA')
                page.locator('.fv-apollo-atlas').evaluate("e=>e.style.zoom=''")
                png=out/f'{width}-{("js" if js else "nojs")}-forced.png'
                page.screenshot(path=str(png),full_page=True,animations='disabled')
                results.append({'width':width,'js':js,'AX':'CHROMIUM NATIVE; NOT SCREEN READER',
                    'forced_colors':True,'css_zoom_200pct':'PASS; NOT BROWSER ZOOM',
                    'sha256':sha(png.read_bytes())})
                ctx.close()
        browser.close()
    receipt={'status':'STAGING_HOLD','r219_blob':R219_BLOB,'results':results,'contexts':len(results),
      'axe_core':'NOT EXECUTED','real_zoom':'NOT TESTED','WordPress':'NOT TESTED',
      'merchant_orders':'UNVERIFIED','net_revenue':'NOT COMPUTABLE','production_writes':False}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('R220 PASS',len(results),'native accessibility/forced-colors/no-JS checks')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);a=parser.parse_args()
    run(a.workspace.resolve(),a.output.resolve())
