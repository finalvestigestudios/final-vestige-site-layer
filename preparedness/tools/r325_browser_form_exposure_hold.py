#!/usr/bin/env python3
"""Fail-closed Preparedness form-submission browser gate; never a release approval.

Read-only against authenticated R324 source snapshots. Browser checks use offline
Chromium DOM semantics, without actual submission, personal values, or network.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from preparedness.tools import r324_tool_privacy_egress_hold as r324
from preparedness.tools import r319_three_way_custody_hold as custody

SCHEMA = 'fv-preparedness-r325-browser-form-exposure-draft-hard-hold-v1'
RELEASE = {'publication_authorized':False,'privacy_approved':False,
           'independent_qd_pass':False,'emergency_safety_approved':False,
           'commercial_offer_approved':False}
SENSITIVE_TYPES={'text','tel','email','search','date','datetime-local','number','password','textarea','url'}
FORM_METHODS={'GET','POST','DIALOG'}

class FormTree(HTMLParser):
    """Conservative parser: a handler never counts as a no-JS safeguard."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms=[];self.fields=[];self.submits=[];self.base=[];self.scripts=[]
        self.open_form=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); tag=tag.lower()
        if tag=='form':
            f={'id':a.get('id'),'method':str(a.get('method') or 'GET').strip().upper(),
               'action':a.get('action'),'target':a.get('target'),'onsubmit':a.get('onsubmit')}
            self.forms.append(f);self.open_form=len(self.forms)-1
        if tag in ('input','textarea','select'):
            typ='textarea' if tag=='textarea' else ('select' if tag=='select' else str(a.get('type') or 'text').lower())
            self.fields.append({'tag':tag,'type':typ,'name':a.get('name'),
                                'form':a.get('form'),'inside':self.open_form,
                                'disabled':'disabled' in a,'hidden':typ=='hidden'})
            if tag=='input' and typ in ('submit','image'):
                self.submits.append({'tag':tag,'type':typ,'form':a.get('form'),
                                     'inside':self.open_form,'formaction':a.get('formaction'),
                                     'formmethod':a.get('formmethod')})
        if tag=='button':
            self.submits.append({'tag':tag,'type':str(a.get('type') or 'submit').lower(),
                                 'form':a.get('form'),'inside':self.open_form,
                                 'formaction':a.get('formaction'),'formmethod':a.get('formmethod')})
        if tag=='base':self.base.append(a.get('href'))
        if tag=='script':self.scripts.append(a.get('src'))
    def handle_endtag(self,tag):
        if tag.lower()=='form':self.open_form=None
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)

def inspect_html(raw:bytes)->dict:
    if not isinstance(raw,bytes):raise TypeError('BYTES_REQUIRED')
    doc=raw.decode('utf-8','strict')
    if '\x00' in doc:raise ValueError('NUL_FORBIDDEN')
    tree=FormTree();tree.feed(doc);tree.close()
    errors=[]; form_entries=[]
    ids=[f['id'] for f in tree.forms if f['id']]
    if len(ids)!=len(set(ids)):errors.append('DUPLICATE_FORM_ID_HOLD')
    for n,f in enumerate(tree.forms):
        fid=f['id'];fields=[v for v in tree.fields if v['inside']==n or (fid and v['form']==fid)]
        buttons=[v for v in tree.submits if v['inside']==n or (fid and v['form']==fid)]
        named=[v for v in fields if v['name'] and not v['disabled']]
        personal=[v for v in named if v['type'] in SENSITIVE_TYPES]
        flags=[]
        if f['method'] not in FORM_METHODS:flags.append('UNSUPPORTED_FORM_METHOD_HOLD')
        if f['method']=='GET':flags.append('GET_QUERY_FORM_HOLD')
        if f['method']=='POST':flags.append('POST_NETWORK_FORM_HOLD')
        if f['method']=='DIALOG':flags.append('DIALOG_CONTEXT_NOT_PROVEN_HOLD')
        if f['action'] and str(f['action']).strip():flags.append('ACTION_DESTINATION_REVIEW')
        if f['target'] and f['target']!='_self':flags.append('TARGET_CONTEXT_REVIEW')
        if f['onsubmit']:flags.append('INLINE_JS_NOT_NOJS_PROTECTION')
        if named and f['method'] in ('GET','POST'):flags.append('NAMED_DATA_TRANSMISSION_SURFACE')
        if personal and f['method']=='GET':flags.append('POTENTIAL_PRIVATE_QUERY_STRING')
        if not buttons and named:flags.append('ENTER_IMPLICIT_SUBMIT_REVIEW')
        if any(b['type'] in ('submit','image') for b in buttons):flags.append('EXPLICIT_SUBMIT_CONTROL_REVIEW')
        if any(b['formaction'] or b['formmethod'] for b in buttons):flags.append('BUTTON_OVERRIDE_DESTINATION_REVIEW')
        form_entries.append({'index':n,'method':f['method'],'named_fields':len(named),
                             'sensitive_named_fields':len(personal),
                             'buttons':Counter(b['type'] for b in buttons),
                             'flags':sorted(set(flags))})
    if tree.base:errors.append('BASE_URI_REVIEW')
    if any(v for v in tree.scripts):errors.append('EXTERNAL_SCRIPT_REVIEW')
    if tree.forms and not all(v['flags']==[] for v in form_entries):errors.append('FORM_BROWSER_PRIVACY_HARD_HOLD')
    # A no-form tool still needs independent interaction/accessibility review.
    return {'forms':len(tree.forms),'fields':len(tree.fields),'form_entries':form_entries,
            'errors':sorted(set(errors)), 'browser_privacy_approved':False}

def audit(loader, pins=None):
    """Source custody and fail-closed static assessment; no source writes."""
    pins = r324.PINS if pins is None else pins
    if pins != r324.PINS:return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD','errors':['PIN_SET_MISMATCH'],'tools':[],'release':RELEASE.copy()}
    rows=[];errors=[]
    for slug in sorted(r324.PINS):
        path=f'preparedness/content/tools/{slug}.body.html'
        try:
            raw=loader(path)
            if custody.blob(raw)!=pins[slug]:raise ValueError('BLOB_MISMATCH')
            rows.append({'slug':slug,'git_blob':pins[slug],**inspect_html(raw)})
        except (OSError,ValueError,UnicodeError,TypeError) as e:
            errors.append(slug+':'+type(e).__name__)
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':errors,'tools':rows,'release':RELEASE.copy()}

def browser_probe(html:bytes, *, executable='/usr/bin/chromium', timeout_ms=3000)->dict:
    """Offline Chromium form-semantics smoke test: no navigation, submission or PII.

    Confirms computed form method and button defaults with JavaScript disabled and
    enabled under CSP. Does NOT test actual network egress or production privacy.
    """
    try:from playwright.sync_api import sync_playwright
    except ImportError:return {'state':'BROWSER_UNAVAILABLE_HARD_HOLD','reason':'PLAYWRIGHT_NOT_INSTALLED'}
    try:markup=html.decode('utf-8','strict')
    except (AttributeError,UnicodeError):return {'state':'BROWSER_INVALID_INPUT_HARD_HOLD'}
    observations=[]
    try:
        with sync_playwright() as p:
            for js in (False,True):
                browser=p.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
                try:
                    context=browser.new_context(java_script_enabled=js,accept_downloads=False)
                    page=context.new_page()
                    page.route('**/*',lambda route:route.abort())
                    csp="<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'\">"
                    page.set_content(csp+markup,wait_until='domcontentloaded',timeout=timeout_ms)
                    vals=page.locator('form').evaluate_all("""(forms)=>forms.map(f=>({
                      method:f.method.toUpperCase(),actionScheme:f.action.split(':')[0],
                      namedActiveFields:Array.from(f.elements).filter(x=>x.name&&!x.disabled).length,
                      implicitSubmitButtons:Array.from(f.elements).filter(x=>x.tagName==='BUTTON'&&x.type==='submit').length
                    }))""")
                    observations.append({'javascript_enabled':js,'forms':vals})
                    context.close()
                finally:browser.close()
    except Exception as e:
        return {'state':'BROWSER_ERROR_HARD_HOLD','error':type(e).__name__,
                'observations':observations,'browser_privacy_approved':False}
    return {'state':'BROWSER_DOM_SEMANTICS_OBSERVED_STILL_HARD_HOLD',
            'observations':observations,'network_submission_attempted':False,
            'privacy_egress_unverified':True,'browser_privacy_approved':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--browser',action='store_true');args=ap.parse_args()
    root=args.root.resolve()
    try:
        manifest=custody.safe_bytes(root,custody.MANIFEST_PATH)
        if manifest is None or custody.validate_manifest(json.loads(manifest),root)['errors']:raise OSError('SOURCE_CUSTODY_INVALID')
        out=audit(lambda path:custody.safe_bytes(root,path))
        if args.browser and out['state']=='DRAFT_HARD_HOLD':
            out['browser_probes']={slug:browser_probe(custody.safe_bytes(root,f'preparedness/content/tools/{slug}.body.html')) for slug in r324.PINS}
    except (OSError,UnicodeError,ValueError,TypeError,KeyError):
        out={'schema':SCHEMA,'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPOSITORY_UNAVAILABLE_OR_INVALID'],
             'tools':[],'release':RELEASE.copy()}
    print(json.dumps(out,indent=2,sort_keys=True,default=dict))
    return 2 if out['state']=='DRAFT_HARD_HOLD' else 1
if __name__=='__main__':raise SystemExit(main())
