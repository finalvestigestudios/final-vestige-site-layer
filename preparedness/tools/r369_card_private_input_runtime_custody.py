#!/usr/bin/env python3
"""R369: read-only, fail-closed Tool #104 private-input behavior witness.

Only synthetic sentinel data is used. An offline browser probe cannot establish
production privacy, legal compliance, medical safety, or release permission.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys

SCHEMA='fv-preparedness-r369-private-input-custody-v1'
SENTINEL='FV_R369_SYNTHETIC_NO_PERSON_DATA'
BODY='content/tools/family-reunification-card.body.html'
META='content/tools/family-reunification-card.meta.json'
PIN_BODY='be8698ac5d020476ff649d85813810e2000c6f98'
PIN_META='47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
HOLD={k:False for k in ('may_publish','may_merge','qd_pass','actual_private_data_protected',
'privacy_review_approved','emergency_review_approved','physical_print_verified',
'paid_sku_verified','verified_paid_orders','revenue_verified')}


def verdict(errors=(), evidence=None):
    return dict(schema=SCHEMA,status='INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
                errors=sorted(set(errors)),evidence=evidence or {},**HOLD)


class FormInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms=[];self.controls=[];self.scripts=0;self.handlers=[];self.links=[]
        self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if any(k.startswith('on') for k in a):self.handlers.append(tag)
        if tag=='script':self.scripts+=1
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='form':
            self.current={'id':a.get('id'),'method':a.get('method','get').lower(),
                          'action':a.get('action',''),'target':a.get('target','')}
            self.forms.append(self.current)
        if tag in ('input','select','textarea') and self.current is not None:
            self.controls.append({'tag':tag,'type':a.get('type','text').lower(),
                                  'name':a.get('name'),'disabled':'disabled' in a})
    def handle_endtag(self,tag):
        if tag=='form':self.current=None


def static_guard(html):
    errors=[];ev={}
    if not isinstance(html,str) or len(html)>2_000_000:
        return ['INVALID_SOURCE_SIZE_OR_TYPE'],ev
    p=FormInventory()
    try:p.feed(html);p.close()
    except (ValueError,TypeError):return ['INVALID_HTML_PARSER_INPUT'],ev
    ev.update(form_count=len(p.forms),named_controls=sum(bool(c['name']) and not c['disabled'] for c in p.controls),
              script_count=p.scripts,inline_handler_elements=len(p.handlers),link_count=len(p.links))
    if len(p.forms)!=1 or p.forms[0]['id']!='rc':errors.append('TOOL104_FORM_IDENTITY_DRIFT')
    for f in p.forms:
        if f['method']!='get':errors.append('FORM_METHOD_CHANGED_REVIEW')
        if f['target'] not in ('','_self'):errors.append('FORM_TARGET_CHANGED')
        if f['action'] and f['action']!='#':errors.append('FORM_ACTION_REQUIRES_REVIEW')
    if ev['named_controls']:errors.append('FORM_NAMED_FIELDS_CAN_REACH_QUERY_OR_BODY')
    if re.search(r'\b(?:fetch|XMLHttpRequest|sendBeacon|WebSocket)\s*\(',html,re.I):
        errors.append('SOURCE_NETWORK_API_REQUIRES_REVIEW')
    if re.search(r'\b(?:localStorage|sessionStorage|indexedDB|document\.cookie)\b',html,re.I):
        errors.append('SOURCE_PERSISTENT_STORAGE_REQUIRES_REVIEW')
    return sorted(set(errors)),ev


def browser_guard(html,*,executable='/usr/bin/chromium'):
    """All HTTP requests are intercepted. Only an artificial local-origin fixture is served."""
    errors=[];observations={}
    if not isinstance(html,str) or len(html)>2_000_000:
        return ['INVALID_BROWSER_INPUT'],observations
    if not Path(executable).is_file():return ['CHROMIUM_UNAVAILABLE'],observations
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=executable,headless=True,
                args=['--no-sandbox','--disable-background-networking','--disable-gpu'])
            try:
                for enabled in (False,True):
                    ctx=browser.new_context(java_script_enabled=enabled,service_workers='block')
                    attempted=[]
                    def route_handler(route):
                        req=route.request
                        attempted.append({'external':not req.url.startswith('about:blank'),
                                          'has_sentinel':SENTINEL in req.url or SENTINEL in (req.post_data or ''),
                                          'method':req.method})
                        route.abort()
                    ctx.route('**/*',route_handler)
                    page=ctx.new_page()
                    try:
                        if enabled:
                            # Instrument synthetic storage attempts. No actual storage or data persists.
                            page.evaluate('''() => {
                              window.__r369_storage_writes=0;
                              for(const key of ['localStorage','sessionStorage']) {
                                try {Object.defineProperty(window,key,{configurable:true,
                                  get(){return {get length(){return window.__r369_storage_writes},
                                    setItem(){window.__r369_storage_writes++}}}})}catch(e){}
                              }
                            }''')
                        page.set_content(html,wait_until='domcontentloaded',timeout=15000)
                        forms=page.locator('form#rc')
                        if forms.count()!=1:
                            errors.append('RUNTIME_FORM_IDENTITY_DRIFT')
                            continue
                        editable=page.locator('form#rc input[type="text"]:not([disabled]), form#rc input[type="tel"]:not([disabled])')
                        if not editable.count():
                            errors.append('NO_EDITABLE_RUNTIME_FIELD')
                            continue
                        editable.first.fill(SENTINEL)
                        initial=page.url
                        try:editable.first.press('Enter',timeout=3000)
                        except Exception:errors.append('ENTER_SUBMISSION_PROBE_INCOMPLETE')
                        try:page.wait_for_load_state('domcontentloaded',timeout=1500)
                        except Exception:pass
                        # Do not collect actual form values, input content or storage payloads.
                        try:
                            if enabled:
                                writes=page.evaluate('window.__r369_storage_writes')
                                storage={'synthetic_write_attempts':writes}
                                if not isinstance(writes,int):errors.append('BROWSER_STORAGE_INSPECTION_INCOMPLETE')
                            else:storage={'synthetic_write_attempts':None}
                        except Exception:
                            storage=None;errors.append('BROWSER_STORAGE_INSPECTION_INCOMPLETE')
                        key='js_on' if enabled else 'js_off'
                        observations[key]={'attempted_requests':len(attempted),
                            'external_requests':sum(x['external'] for x in attempted),
                            'sentinel_requests':sum(x['has_sentinel'] for x in attempted),
                            'navigated':page.url!=initial,'synthetic_input_in_url':SENTINEL in page.url,
                            'storage_keys':storage}
                        if attempted:errors.append('UNEXPECTED_NETWORK_REQUEST:'+key)
                        if any(x['has_sentinel'] for x in attempted):errors.append('SYNTHETIC_INPUT_TRANSMISSION_ATTEMPT:'+key)
                        if page.url!=initial:errors.append('UNEXPECTED_BROWSER_NAVIGATION:'+key)
                        if SENTINEL in page.url:errors.append('SYNTHETIC_INPUT_IN_BROWSER_URL:'+key)
                        if storage and storage['synthetic_write_attempts']:errors.append('BROWSER_STORAGE_WRITE_OBSERVED:'+key)
                    finally:page.close();ctx.close()
            finally:browser.close()
    except Exception as exc:
        errors.append('ISOLATED_RUNTIME_FAILURE:'+type(exc).__name__+':'+str(exc)[:240])
    return sorted(set(errors)),observations


def audit(root,build=None,*,executable='/usr/bin/chromium'):
    root=Path(root);build=Path(build) if build is not None else root/'build'
    ev={};errors=[]
    if not root.is_dir() or root.is_symlink():return verdict(['AUTHENTIC_ROOT_MISSING'])
    try:
        import hashlib
        raw=[]
        for name in (BODY,META):
            p=root/name
            if p.is_symlink() or not p.is_file():return verdict(['ORIGINAL_TOOL104_FILES_MISSING'])
            raw.append(p.read_bytes())
        blobs=[hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest() for b in raw]
        ev['original_git_blobs']=dict(zip(('body','meta'),blobs))
        if blobs!=[PIN_BODY,PIN_META]:errors.append('ORIGINAL_SOURCE_PIN_CHANGED')
        meta=json.loads(raw[1].decode('utf-8'))
        if (meta.get('slug')!='family-reunification-card' or meta.get('n')!=104
          or meta.get('status',{}).get('publish')!='draft'
          or meta.get('safety_review',{}).get('state')!='pending'):
            errors.append('ORIGINAL_TOOL104_DRAFT_SAFETY_IDENTITY_DRIFT')
        source=raw[0].decode('utf-8')
        # Require the preceding R368 provenance and private-output gate, not synthetic pass.
        p368=root/'tools/r368_family_card_print_disclosure_gate.py'
        if p368.is_symlink() or not p368.is_file():return verdict(errors+['R368_PREREQUISITE_MISSING'],ev)
        modspec=importlib.util.spec_from_file_location('_r368_r369',p368)
        mod=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(mod)
        prior=mod.audit(root,build,executable=executable)
        ev['r368_status']=prior.get('status')
        ev['r368_errors']=prior.get('errors',[])
        if prior.get('status')!='REVIEW_REQUIRED_HARD_HOLD':errors.append('R368_PRECONDITIONS_UNSATISFIED')
        paths=[build/'wp/family-reunification-card.html',build/'preview/family-reunification-card.html']
        if any(p.is_symlink() or not p.is_file() for p in paths):
            return verdict(errors+['AUTHENTIC_PRIVATE_OUTPUTS_MISSING'],ev)
        for name,html in [('original',source),('wp',paths[0].read_text('utf-8')),
                          ('preview',paths[1].read_text('utf-8'))]:
            e,static=static_guard(html);errors.extend(name+':'+v for v in e)
            br,rendered=browser_guard(html,executable=executable)
            errors.extend(name+':'+v for v in br)
            ev[name]={'static':static,'runtime':rendered}
    except Exception as exc:errors.append('AUDIT_FAILURE:'+type(exc).__name__)
    return verdict(errors,ev)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path);p.add_argument('--build',type=Path)
    p.add_argument('--chromium',default='/usr/bin/chromium')
    a=p.parse_args(argv)
    print(json.dumps(audit(a.root,a.build,executable=a.chromium),indent=2,sort_keys=True))
    return 2

if __name__=='__main__':sys.exit(main())
