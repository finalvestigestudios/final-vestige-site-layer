#!/usr/bin/env python3
"""R168: fail-closed *synthetic* browser print/persistence/privacy preflight.

This is a quality regression test, NOT a security sandbox or guarantee about
WordPress, browser extensions, actual printers, or medical/emergency advice.
Never ingest real household information. Authentic probe requires R167 custody.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil

SCHEMA = 'fv-preparedness-r168-print-persistence-v1'
WIDTHS = (360, 390, 768, 1440)
FIELDS = ('hhName','hhPhone','outName','outPhone','meet1','meet2','school',
          'schoolPlan','pickup','careName','carePhone','access','reviewed')
SENSITIVE = ('school','schoolPlan','pickup','careName','carePhone','access','meet2')
MARKERS = {
    'outName':'FV-SYNTHETIC-OUTNAME-R168',
    'school':'FV-SYNTHETIC-SCHOOL-R168',
    'careName':'FV-SYNTHETIC-CARE-R168',
    'meet2':'FV-SYNTHETIC-MEET2-R168',
}
PRIVATE = tuple(MARKERS[k] for k in ('school','careName','meet2'))
ALL = tuple(MARKERS.values())
# Pre-document API probes collect only API category names. No payload/URL/field value.
SENSOR = r'''(() => {
  const hits=[];
  Object.defineProperty(window,'__fv_r168_events',{value:()=>hits.slice(),configurable:false});
  const deny=(obj,key,label)=>{
    try {const fn=obj[key]; if(typeof fn==='function') {
      obj[key]=function(...args){hits.push(label);throw new DOMException('Blocked by offline probe','SecurityError');};
    }}catch(e){hits.push('probe_install_error');}
  };
  deny(history,'pushState','history.pushState');
  deny(history,'replaceState','history.replaceState');
  deny(window,'open','window.open');
  deny(window,'showSaveFilePicker','showSaveFilePicker');
  deny(window,'showDirectoryPicker','showDirectoryPicker');
  deny(window,'showOpenFilePicker','showOpenFilePicker');
})();'''

# Check *rendered* print-visible nodes (not merely #rc-sheet.innerText).
# Also read CSS pseudo-element content; no user text is returned to Python.
PRINT_CHECK = r'''(secrets) => {
  const present=[];
  const visible=(el)=>{
    while(el && el.nodeType===1){
      const s=getComputedStyle(el);
      if(s.display==='none'||s.visibility==='hidden'||s.visibility==='collapse'||Number(s.opacity)===0)return false;
      el=el.parentElement;
    }return true;
  };
  const walk=(root)=>{
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT);
    while(walker.nextNode()){
      const node=walker.currentNode;
      if(node.nodeType===Node.TEXT_NODE){
        const p=node.parentElement;
        if(p && visible(p) && !['SCRIPT','STYLE','NOSCRIPT'].includes(p.tagName)){
          for(const s of secrets)if(node.textContent.includes(s))present.push('text');
        }
      }else if(node.nodeType===Node.ELEMENT_NODE && visible(node)){
        for(const pseudo of ['::before','::after']) {
          const content=getComputedStyle(node,pseudo).content;
          for(const s of secrets)if(content && content.includes(s))present.push('pseudo');
        }
        if(node.shadowRoot)walk(node.shadowRoot);
      }
    }
  };
  walk(document.documentElement);
  return [...new Set(present)];
}'''

ATTRIBUTE_CHECK = r'''(secrets) => {
  const hits=[];
  for(const el of document.querySelectorAll('*'))for(const a of el.attributes)
    if(secrets.some(s=>a.value.includes(s)))hits.push('attribute');
  return [...new Set(hits)];
}'''

TEXT_CHECK = r'''(secrets) => {
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()) {
    const node=walker.currentNode;
    if(!['STYLE','SCRIPT','NOSCRIPT'].includes(node.parentElement?.tagName) &&
       secrets.some(s=>node.textContent.includes(s)))return true;
  }return false;
}'''

PERSISTENCE_CHECK = r'''(secrets) => {
  const candidates=[window.name,location.href,document.title,
    JSON.stringify(history.state),document.referrer];
  return candidates.some(s=>secrets.some(token=>String(s).includes(token)));
}'''


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def document(html: str) -> str:
    require(isinstance(html,str) and len(html)>200, 'invalid synthetic HTML')
    require('<form' in html and 'id="rc"' in html, 'missing card form')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '</head><body><main class="pa-article">'+html+'</main></body></html>')


def safe_event_types(raw: list[str]) -> list[str]:
    require(isinstance(raw,list),'event list absent')
    require(all(isinstance(e,str) and bool(re.fullmatch(r'[A-Za-z_.]{1,50}',e)) for e in raw),
            'unsafe event telemetry')
    return sorted(set(raw))


def probe(html: str, *, widths=WIDTHS) -> dict:
    """Run synthetic-only offline Chromium tests with no real personal information."""
    require(isinstance(widths,(list,tuple)) and widths, 'invalid widths')
    require(all(type(w) is int and 240<=w<=2200 for w in widths), 'unsafe width')
    require(len(set(widths))==len(widths), 'duplicate widths')
    from playwright.sync_api import sync_playwright
    binary=shutil.which('chromium') or shutil.which('chromium-browser')
    require(bool(binary), 'Chromium unavailable')
    markup=document(html)
    checks=[]
    with sync_playwright() as play:
        browser=play.chromium.launch(headless=True,executable_path=binary,args=['--no-sandbox'])
        try:
            for width in widths:
                ctx=browser.new_context(viewport={'width':width,'height':900},
                    accept_downloads=False,service_workers='block')
                events=[]
                try:
                    ctx.add_init_script(script=SENSOR)
                    # Any routed request in this isolated set_content document is suspicious.
                    def route_handler(route):
                        events.append('network_request')
                        route.abort()
                    ctx.route('**/*',route_handler)
                    page=ctx.new_page()
                    page.on('popup',lambda _: events.append('popup'))
                    page.on('download',lambda _: events.append('download'))
                    page.on('dialog',lambda d:(events.append('dialog'),d.dismiss()))
                    page.on('pageerror',lambda _: events.append('pageerror'))
                    page.on('websocket',lambda _: events.append('websocket'))
                    page.set_content(markup,wait_until='load')
                    require(not events,'browser side effect at initialization')
                    require(page.locator('#rc-live').evaluate('(e)=>!e.hidden'),'card not initialized')
                    require(page.locator('#rc-reset').is_visible(),'clear missing')
                    for key,value in MARKERS.items():
                        page.locator('#rc-'+key).fill(value)
                    require(MARKERS['outName'] in page.locator('#rc-preview').inner_text(),
                            'synthetic card not rendered')
                    require(not events, 'browser side effect during input')
                    require(not page.evaluate(PERSISTENCE_CHECK,list(ALL)),
                            'synthetic contact data in navigation/browser persistence')
                    page.locator('#rc-minimal').check()
                    page.locator('#rc-copies').select_option('4')
                    require(page.locator('#rc-sheet .pa-foldcard').count()==4,'four copies not rendered')
                    page.emulate_media(media='print')
                    require(page.locator('#rc').evaluate('(e)=>getComputedStyle(e).display')=='none',
                            'form exposed in print')
                    require(not page.evaluate(PRINT_CHECK,list(PRIVATE)),
                            'minimal printable document exposes private fields')
                    require(not page.evaluate(ATTRIBUTE_CHECK,list(PRIVATE)),
                            'minimal document stores private fields in attributes')
                    require(not events, 'side effect during print/minimal mode')
                    page.emulate_media(media='screen')
                    page.locator('#rc-reset').click()
                    for k in FIELDS:
                        require(page.locator('#rc-'+k).input_value()=='', 'clear left data in '+k)
                    require(not page.evaluate(ATTRIBUTE_CHECK,list(ALL)),
                            'cleared card persists synthetic data in HTML attributes')
                    require(not page.evaluate(PERSISTENCE_CHECK,list(ALL)),
                            'clear left data in navigation/browser persistence')
                    # Hidden previews count here: after clear, *all* rendered text must lose markers.
                    require(not page.evaluate(TEXT_CHECK,list(ALL)),
                            'clear left synthetic contact data in document text')
                    require(not events,'browser side effect during clear')
                    require(not page.evaluate('window.__fv_r168_events === undefined'),
                            'pre-document sensor absent')
                    require(not safe_event_types(page.evaluate('window.__fv_r168_events()')),
                            'blocked browser persistence/export API attempted')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),
                            'horizontal overflow')
                    checks.append({'width':width,'status':'SYNTHETIC_OFFLINE_ONLY',
                        'private_values_logged':False,'browser_side_effects':0})
                finally:
                    ctx.close()
        finally:
            browser.close()
    return {'schema':SCHEMA,'state':'DRAFT_HARD_HOLD','checks':checks,
            'real_wordpress_verified':False,'actual_print_spool_verified':False,
            'source_safety_approved':False,'independent_qd_pass':False,
            'paid_checkout_authorized':False,'publication_authorized':False}


def authentic(root: Path) -> dict:
    """Never run without exact upstream 35-article citation/source custody."""
    import sys
    scripts_dir=root/'preparedness'/'tools'
    sys.path.insert(0,str(scripts_dir))
    import r167_family_browser_sink_gate as r167
    import r165_inline_dependency_custody as r165
    prior=r167.authentic(root)
    require(prior.get('state')=='DRAFT_HARD_HOLD' and prior.get('source_chain_checked'),
            'R167 full citation/source custody failed')
    source=r165.audit(root)
    require(source.get('state')=='DRAFT_HARD_HOLD','R165 source lock absent')
    scripts={n:(scripts_dir/n).read_text(encoding='utf-8') for n in r165.EXPECTED}
    staged=(root/r165.STAGED).read_text(encoding='utf-8')
    html,expanded=r165.expand_checked(staged,scripts)
    require(expanded.get('expanded_sha256')==prior.get('r165_hash'),
            'R165 staged dependency changed')
    return {**probe(html),'upstream_chain_checked':True,
            'r165_expanded_sha256':expanded['expanded_sha256']}


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--report',type=Path,default=None)
    opts=p.parse_args(argv)
    try:
        report=authentic(opts.repo.resolve(strict=True))
    except Exception as exc:
        # Never promote any failure to a success or leak input / error payloads.
        report={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'error_kind':type(exc).__name__,'publication_authorized':False,
                'independent_qd_pass':False,'real_wordpress_verified':False}
    payload=json.dumps(report,sort_keys=True)
    if opts.report:
        opts.report.write_text(payload+'\n',encoding='utf-8')
    print(payload)
    return 2


if __name__=='__main__':
    raise SystemExit(main())
