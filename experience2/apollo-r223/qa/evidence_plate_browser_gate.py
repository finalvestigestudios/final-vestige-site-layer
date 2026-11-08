#!/usr/bin/env python3
"""R223 offline exact-builder browser gate; NOT WordPress staging or axe-core."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
WIDTHS=(320,360,390,768,1024,1440,1920)
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MANIFEST='60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(x,msg):
    if not x:raise AssertionError(msg)
def run(parent:Path,builder:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    sp=importlib.util.spec_from_file_location('build_r223',builder)
    mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    dist=out/'dist'; pin=mod.create(parent,dist)
    ck(pin==MANIFEST,'Exact R223 build manifest mismatch')
    m=json.loads((dist/'manifest.json').read_text())
    for name,h in m['files'].items():ck(sha(dist/name)==h,'Artifact integrity '+name)
    adapter=dist/'fv-ex2-apollo-r223.php'
    ck('No syntax errors' in subprocess.check_output(['php','-l',str(adapter)],text=True),'PHP lint')
    sh=['php',str(dist/'wp-render-shim-r223.php'),str(adapter)]
    modes={mode:json.loads(subprocess.check_output(sh+[mode],text=True)) for mode in ('normal','printed','late')}
    ck(not modes['normal']['fallback'] and not modes['printed']['fallback'] and modes['late']['fallback'],'PHP normal/print/late regression')
    ck(FREE in modes['late']['html'] and not modes['normal']['js'],'Free fallback or campaign script regression')
    ledger=dist/'source-context-plates.json';original=ledger.read_bytes()
    try:
        ledger.write_bytes(original+b' ')
        corrupted=json.loads(subprocess.check_output(sh+['normal'],text=True))
        ck(corrupted['fallback'] and FREE in corrupted['html'],'Ledger mutation did not fail open')
    finally:ledger.write_bytes(original)
    custody=json.loads(ledger.read_text())['source_records']
    css=(dist/'assets/atlas-scoped.css').read_text()
    doc='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+modes['normal']['html']+'</body></html>'
    results=[]
    with sync_playwright() as play:
        browser=play.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                mobile=width<=390
                ctx=browser.new_context(viewport={'width':width,'height':844},java_script_enabled=js,is_mobile=mobile,has_touch=mobile,reduced_motion='reduce')
                page=ctx.new_page();page.set_content(doc,wait_until='domcontentloaded')
                audit=page.evaluate('''() => {
                  let root=document.querySelector('.fv-apollo-atlas'), d=document.querySelector('#fv-apollo-source-drawer');
                  let ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
                  let plates=[...d.querySelectorAll('[data-fv-plate-source]')].map(li=>({id:li.dataset.fvPlateSource,
                    link:li.querySelector('a[href^="https://www.nasa.gov/"]')?.href,
                    context:li.querySelector('a[href^="#"]')?.getAttribute('href'),
                    labels:[...li.querySelectorAll('dt')].map(x=>x.textContent.trim()),
                    recorded:li.querySelector('time')?.getAttribute('datetime')}));
                  let broken=[...document.querySelectorAll('[aria-describedby],[aria-labelledby]')].flatMap(e=>['aria-describedby','aria-labelledby'].flatMap(a=>(e.getAttribute(a)||'').split(/\\s+/).filter(Boolean).filter(id=>!document.getElementById(id))));
                  return {open:d.open,plates,duplicatedIds:ids.length!==new Set(ids).size,broken,
                    brokenInternal:[...root.querySelectorAll('a[href^="#"]')].filter(x=>!document.getElementById(x.getAttribute('href').slice(1))).length,
                    ctas:[...root.querySelectorAll('a.cta')].map(a=>({url:a.href,height:a.getBoundingClientRect().height,width:a.getBoundingClientRect().width})),
                    active:root.querySelectorAll('script,form,iframe,object,embed,video,canvas').length,
                    coords:root.querySelectorAll('[data-lat],[data-lon],.map-pin').length,
                    overflow:document.documentElement.scrollWidth>window.innerWidth+2};
                }''')
                ck(not audit['open'] and not audit['duplicatedIds'] and not audit['broken'] and not audit['brokenInternal'],'Closed drawer or accessibility refs')
                ck(len(audit['plates'])==len(custody)==4,'EvidencePlate count')
                for v,e in zip(audit['plates'],custody):
                    ck(v['id']==e['source_id'] and v['link']==e['url'] and v['context']==e['context_anchor'] and v['recorded']==e['date'],'Source/date/anchor drift')
                    ck(v['labels']==['Source kind',e['date_role'],'Can establish','Cannot establish'],'Visible source limits missing')
                ck(len(audit['ctas'])==1 and audit['ctas'][0]['url']==FREE and audit['ctas'][0]['height']>=44 and audit['ctas'][0]['width']>=44,'Free CTA regression')
                ck(not audit['active'] and not audit['coords'] and not audit['overflow'],'Unsafe content or horizontal overflow')
                summary=page.locator('#fv-apollo-source-drawer summary');summary.scroll_into_view_if_needed()
                if mobile:
                    box=summary.bounding_box();ck(bool(box),'Touch summary missing');page.touchscreen.tap(box['x']+min(box['width']/2,60),box['y']+box['height']/2)
                else:
                    summary.focus();page.keyboard.press('Enter')
                ck(page.locator('#fv-apollo-source-drawer').evaluate('x=>x.open'),'No-JS native detail failed')
                route=page.locator('.fv-apollo-plate-links a[href^="#"]').first
                ck(route.is_visible(),'Context link hidden');route.click()
                ck(page.evaluate('location.hash')==custody[0]['context_anchor'],'Native context navigation failed')
                page.emulate_media(media='print')
                ck(page.locator('.fv-apollo-source-drawer .fv-apollo-plate-facts').first.evaluate('x=>x.getBoundingClientRect().height')>0,'Printable evidence hidden')
                page.emulate_media(media='screen',reduced_motion='reduce')
                page.locator('#fv-apollo-source-drawer').scroll_into_view_if_needed()
                path=out/f'{width}-{ "js" if js else "nojs"}-plates.png'
                page.screenshot(path=str(path),animations='disabled')
                results.append({'width':width,'js':js,'native_details':True,'source_context_navigation':True,'print':True,'sha256':sha(path)})
                ctx.close()
        for setting in ({'forced_colors':'active'},{'reduced_motion':'reduce'}):
            ctx=browser.new_context(viewport={'width':390,'height':844},**setting)
            page=ctx.new_page();page.set_content(doc);page.locator('#fv-apollo-source-drawer summary').click()
            ck(page.locator('.fv-apollo-plate-links a').first.is_visible(),'A11y link not visible')
            ctx.close()
        browser.close()
    receipt={'status':'LOCAL_PASS_STAGING_HOLD','manifest_sha256':pin,'playwright_contexts':len(results),'browser':'Chromium','responsive_widths':WIDTHS,'source_records':len(custody),'screenshots':results,'malformed_ledger_fails_open':True,'js_off':True,'axe_core':'NOT_EXECUTED; package unavailable offline','localhost_navigation':'BLOCKED_BY_ADMINISTRATOR','wordpress_staging':'NOT_TESTED','paid_product':'NOT_VERIFIED','sales':'NOT_VERIFIED','production_changes':False}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('R223 PASS',len(results),'contexts, manifest',pin)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--parent',type=Path,required=True);a.add_argument('--builder',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=a.parse_args();run(args.parent,args.builder,args.out)
