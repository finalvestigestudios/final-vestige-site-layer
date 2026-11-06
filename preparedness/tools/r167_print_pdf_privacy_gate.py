#!/usr/bin/env python3
"""R167: synthetic-only Chromium PDF/spool-preview and privacy regression gate.

Authentic mode requires R166 -> R165 -> R164 -> R163 -> R162 -> R161
source/citation custody and real HTML expansion before PDF inspection.
Passing only ever means DRAFT_HARD_HOLD, never a safety or publication PASS.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r167-print-artifact-v1'
WIDTHS = (360, 390, 768, 1440)
FORM_FIELDS = ('hhName','hhPhone','outName','outPhone','meet1','meet2',
               'school','schoolPlan','pickup','careName','carePhone','access','reviewed')
DATA = {'outName':'Fictional Contact Gamma', 'outPhone':'5550100999',
        'school':'Fictional School Delta', 'careName':'Fictional Carer Epsilon',
        'meet2':'Fictional Meeting Zeta', 'access':'Fictional Access Eta'}
PRIVATE = ('Fictional School Delta','Fictional Carer Epsilon',
           'Fictional Meeting Zeta','Fictional Access Eta')


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def static_contract(html: str) -> None:
    require(isinstance(html, str) and len(html) > 250, 'missing source HTML')
    require(html.count('<script>') == 1 and html.count('</script>') == 1,
            'unexpected script boundary')
    require('{{inline-js:' not in html, 'unexpanded JavaScript dependency')
    require('{{cite:' in html, 'citation anchor missing')
    require('<form id="rc" onsubmit="return false"' in html, 'form contract drift')
    for key in FORM_FIELDS:
        require(html.count('id="rc-'+key+'"') == 1, 'field identity drift: '+key)
    for key in ('minimal', 'copies','reset','print'):
        require(html.count('id="rc-'+key+'"') == 1, 'card control drift: '+key)
    require(html.count('id="rc-sheet"') == 1, 'print sheet identity drift')
    require('A printed card can be lost' in html, 'print privacy warning absent')
    require(not re.search(r'<iframe\b|<base\b|<script\b[^>]+src\s*=|<form\b[^>]+action\s*=', html, re.I),
            'untrusted active element in source HTML')


def pdf_visible_text(raw: bytes) -> str:
    """Inspect real browser-produced PDF pages; do not archive test PDFs."""
    import fitz
    require(isinstance(raw, bytes) and raw.startswith(b'%PDF-'), 'Chromium did not produce PDF')
    with fitz.open(stream=raw, filetype='pdf') as doc:
        require(0 < len(doc) < 30, 'unexpected PDF page count')
        return ' '.join(page.get_text(sort=True) for page in doc)


def probe(html: str, *, widths=WIDTHS) -> dict:
    """Headless local preview only; no WordPress/OS printer/extension privacy assertion."""
    static_contract(html)
    from playwright.sync_api import sync_playwright
    executable = shutil.which('chromium') or shutil.which('chromium-browser')
    require(bool(executable), 'Chromium executable unavailable')
    require(len(widths) >= 1 and all(isinstance(w,int) and 320 <= w <= 1920 for w in widths),
            'invalid viewport configuration')
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=executable, headless=True,
                                     args=['--no-sandbox'])
        try:
            for width in widths:
                context = browser.new_context(viewport={'width':width,'height':900},
                                               accept_downloads=False,service_workers='block')
                requests, errors, websocket, secret_console = [], [], [], []
                try:
                    page = context.new_page()
                    def intercept(route):
                        scheme = urlsplit(route.request.url).scheme.lower()
                        if scheme not in ('about','data','file'):
                            requests.append(scheme)
                            route.abort()
                        else:
                            route.continue_()
                    page.route('**/*', intercept)
                    page.on('pageerror', lambda error: errors.append(type(error).__name__))
                    page.on('websocket', lambda ws: websocket.append('attempt'))
                    def console(message):
                        if any(value in message.text for value in DATA.values()):
                            secret_console.append('synthetic form data logged')
                    page.on('console', console)
                    page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
                        '<body><main class="pa-article"><div class="pa-body">'+html+
                        '</div></main></body></html>', wait_until='load')
                    require(page.locator('#rc-live').evaluate('(e)=>!e.hidden'), 'card failed to initialize')
                    for field,value in DATA.items():
                        page.locator('#rc-'+field).fill(value)
                    require(not errors, 'script error during entry')
                    require(DATA['outName'] in page.locator('#rc-sheet').inner_text(),
                            'card preview did not include synthetic contact')
                    # Standard card should print declared non-sensitive and sensitive fields.
                    page.emulate_media(media='print')
                    full = pdf_visible_text(page.pdf(format='A4',print_background=True))
                    require(DATA['outName'] in full and DATA['school'] in full,
                            'standard PDF did not include user-selected card data')
                    page.emulate_media(media='screen')
                    page.locator('#rc-minimal').check()
                    page.locator('#rc-copies').select_option('4')
                    require(page.locator('#rc-sheet .pa-foldcard').count() == 4,
                            'four-copy preview count changed')
                    page.emulate_media(media='print')
                    minimal = pdf_visible_text(page.pdf(format='A4',print_background=True))
                    require(DATA['outName'] in minimal, 'minimal PDF lost selected contact')
                    require(all(s not in minimal for s in PRIVATE),
                            'minimal PDF printed private/restricted fields')
                    require('Fictional School' not in minimal, 'minimal print contains school detail')
                    require('Fictional Carer' not in minimal, 'minimal print contains caregiver detail')
                    page.emulate_media(media='screen')
                    page.locator('#rc-reset').click()
                    require(all(page.locator('#rc-'+f).input_value() == '' for f in FORM_FIELDS),
                            'clear failed to wipe form inputs')
                    page.emulate_media(media='print')
                    cleared = pdf_visible_text(page.pdf(format='A4',print_background=True))
                    require(all(s not in cleared for s in DATA.values()),
                            'cleared PDF still contains synthetic personal data')
                    require(not requests and not websocket and not errors and not secret_console,
                            'browser network, websocket, console, or script privacy regression')
                    require(not context.cookies(), 'cookie state unexpectedly populated')
                    storage = page.evaluate('''async()=>{
                      const out={local:0,session:0,idb:0,caches:0};
                      try{out.local=localStorage.length}catch(e){}
                      try{out.session=sessionStorage.length}catch(e){}
                      try{if(indexedDB.databases)out.idb=(await indexedDB.databases()).length}catch(e){}
                      try{out.caches=(await caches.keys()).length}catch(e){}
                      return out;}''')
                    require(all(value==0 for value in storage.values()),
                            'browser persistent storage unexpectedly populated')
                    results.append({'viewport':width,'status':'SYNTHETIC_PDF_PASS',
                        'standard_pdf_contains_selected_data':True,
                        'minimal_pdf_excludes_private_fields':True,
                        'cleared_pdf_excludes_sentinel':True,
                        'storage_entries':0,'network_attempts':0})
                finally:
                    context.close()
        finally:
            browser.close()
    return {'schema':SCHEMA,'state':'DRAFT_HARD_HOLD',
            'local_chromium_pdf_preflight':results,
            'real_printer_spool_tested':False,'real_wordpress_render_tested':False,
            'real_user_privacy_proven':False,'source_review_pass':False,
            'independent_qd_pass':False,'paid_offer_authorized':False,
            'publication_authorized':False}


def authentic(root: Path) -> dict:
    import sys
    tools = root / 'preparedness' / 'tools'
    sys.path.insert(0, str(tools))
    import r166_family_browser_probe as predecessor
    import r165_inline_dependency_custody as dependency
    previous = predecessor.authentic(root)
    require(previous.get('state') == 'DRAFT_HARD_HOLD' and
            previous.get('complete_source_custody_checked') is True,
            'authentic R166/R165 source custody incomplete')
    template = (root / dependency.STAGED).read_text(encoding='utf-8')
    scripts = {name:(tools/name).read_text(encoding='utf-8') for name in dependency.EXPECTED}
    expanded, evidence = dependency.expand_checked(template,scripts)
    require(evidence['expanded_sha256'] == previous['r165_dependency_hash'],
            'expanded HTML dependency identity changed')
    return {**probe(expanded),'authentic_source_gate_r166_checked':True,
            'expanded_html_sha256': evidence['expanded_sha256']}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--report',type=Path)
    options=parser.parse_args(argv)
    try:
        evidence=authentic(options.repo.resolve(strict=True))
    except Exception as exc:
        evidence={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                  'reason':type(exc).__name__+': '+str(exc)[:180],
                  'source_review_pass':False,'publication_authorized':False,
                  'independent_qd_pass':False}
    output=json.dumps(evidence,sort_keys=True)+'\n'
    if options.report:
        options.report.write_text(output,encoding='utf-8')
    print(output,end='')
    return 2

if __name__=='__main__':
    raise SystemExit(main())
