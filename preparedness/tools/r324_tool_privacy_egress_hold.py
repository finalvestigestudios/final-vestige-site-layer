#!/usr/bin/env python3
"""Read-only six-tool privacy/egress witness. Static indicators are NOT safety or QD approval.

Original article/tool sources stay byte-for-byte pinned. The audit cannot prove
runtime browser privacy, print behavior, child safety, accessibility or delivery.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from preparedness.tools import r319_three_way_custody_hold as custody

SCHEMA = 'fv-preparedness-r324-six-tool-egress-draft-hold-v1'
PINS = {
    'family-reunification-card':'be8698ac5d020476ff649d85813810e2000c6f98',
    'home-fire-escape-worksheet':'01161948b6de6ffbd1b053c9b83a420758e707e4',
    'kit-builder':'2cb531174d6828fa5185c47bd2b742a0befa8353',
    'power-outage-planner':'aa8f866aaaaab9253f41c4363d31919029c69234',
    'reunification-plan':'3305578369183edb1d427c8f8f8002eaacee420f',
    'water-planner':'a738d1f7824437911064d425868ed3d709326027',
}
SINKS = {
    'fetch':r'\bfetch\s*\(',
    'xhr':r'\bXMLHttpRequest\b',
    'beacon':r'\bsendBeacon\s*\(',
    'socket':r'\bWebSocket\s*\(',
    'eventsource':r'\bEventSource\s*\(',
    'storage':r'\b(?:localStorage|sessionStorage|indexedDB|document\s*\.\s*cookie)\b',
    'serviceworker':r'\bserviceWorker\s*\.\s*register\s*\(',
}
PRIVATE_FIELDS = frozenset({'text','tel','email','date','number','password','search','textarea'})
RELEASE = {'publication_authorized':False,'independent_qd_pass':False,
           'medical_or_emergency_safety_verified':False,'child_privacy_verified':False,
           'runtime_browser_privacy_verified':False,'paid_offer_verified':False}

class ToolSurface(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms=[];self.inputs=[];self.buttons=[];self.links=[]
        self.assets=[];self.scripts=[];self.inline_handlers=[]
        self.noscript=0;self.current_script=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form': self.forms.append({'method':str(a.get('method') or 'GET').upper(),
            'action':a.get('action'),'onsubmit':a.get('onsubmit')})
        if tag in ('input','textarea','select'):
            self.inputs.append({'kind':str(a.get('type') or ('textarea' if tag=='textarea' else 'text')).lower(),
                                'name':a.get('name')})
        if tag=='button': self.buttons.append(str(a.get('type') or 'submit').lower())
        if tag=='a': self.links.append(a.get('href'))
        if tag in ('iframe','object','embed','base','link','img','source'):
            self.assets.append({'tag':tag,'uri':a.get('src') or a.get('href') or a.get('data')})
        if tag=='script':
            self.current_script=[]
            self.scripts.append({'src':a.get('src'),'inline':''})
        if tag=='noscript': self.noscript+=1
        for k,v in attrs:
            if k.lower().startswith('on') and v is not None:self.inline_handlers.append(k.lower())
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_data(self,data):
        if self.current_script is not None:self.current_script.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.current_script is not None:
            self.scripts[-1]['inline']=''.join(self.current_script)
            self.current_script=None

def classify_url(raw):
    if raw is None:return 'empty'
    if not isinstance(raw,str):return 'invalid'
    s=raw.strip()
    if not s:return 'empty'
    if re.search(r'[\x00-\x20\x7f]',s):return 'invalid'
    if s.startswith('//'):return 'network'
    p=urlsplit(s)
    if p.scheme.lower() in ('https','http'):return 'network'
    if p.scheme.lower() in ('javascript','data','vbscript','file','blob'):return 'active_or_local'
    if p.scheme:return 'nonweb_scheme'
    return 'relative'

def inspect_body(raw:bytes) -> dict:
    html=raw.decode('utf-8','strict')
    if '\x00' in html:raise ValueError('NUL_IN_TOOL')
    p=ToolSurface();p.feed(html);p.close()
    findings=[]
    for f in p.forms:
        if f['action'] is not None and str(f['action']).strip():findings.append('FORM_ACTION_REQUIRES_PRIVACY_REVIEW')
        if f['method']=='GET':findings.append('GET_FORM_DEFAULT_OR_EXPLICIT_REVIEW')
        if f['onsubmit'] is None:findings.append('FORM_SUBMIT_HANDLER_ABSENT_REVIEW')
    if any(x in ('submit','image') for x in p.buttons):findings.append('SUBMIT_BUTTON_REVIEW')
    for s in p.scripts:
        if s['src'] is not None:findings.append('SCRIPT_SRC_REQUIRES_REVIEW')
        for label,pattern in SINKS.items():
            if re.search(pattern,s['inline'],re.I):findings.append('SCRIPT_SINK_'+label.upper()+'_REVIEW')
    for asset in p.assets:
        if asset['tag'] in ('iframe','object','embed','base'):findings.append('EMBED_OR_BASE_REQUIRES_REVIEW')
        if classify_url(asset['uri']) in ('network','active_or_local','invalid'):
            findings.append('EXTERNAL_OR_ACTIVE_ASSET_REVIEW')
    for url in p.links:
        if classify_url(url) in ('network','active_or_local','invalid'):findings.append('OUTBOUND_OR_ACTIVE_LINK_REVIEW')
    if any(x['kind'] in PRIVATE_FIELDS for x in p.inputs):findings.append('HOUSEHOLD_FIELD_PRIVACY_REVIEW')
    if p.inputs and p.noscript==0:findings.append('NO_NOSCRIPT_WITNESS_REVIEW')
    if p.inputs and not any(x=='button' for x in p.buttons):findings.append('NO_EXPLICIT_SAFE_BUTTON_WITNESS_REVIEW')
    return {'form_count':len(p.forms),'field_count':len(p.inputs),
            'private_field_count':sum(x['kind'] in PRIVATE_FIELDS for x in p.inputs),
            'button_types':sorted(p.buttons),'scripts':len(p.scripts),'noscript_blocks':p.noscript,
            'inline_handler_count':len(p.inline_handlers),
            'review_flags':sorted(set(findings))}

def audit(loader,pins=None) -> dict:
    """Return conservative *review holds*. loader(path)->bytes. No source writes."""
    pins=PINS if pins is None else pins
    errors=[]; rows=[]
    if not isinstance(pins,dict) or set(pins)!=set(PINS):
        return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD','errors':['SIX_TOOL_IDENTITY_SET_CHANGED'],
                'tools_audited':0,'entries':[],'release':RELEASE.copy()}
    for slug in sorted(PINS):
        path='preparedness/content/tools/'+slug+'.body.html'
        try:
            raw=loader(path)
            if not isinstance(raw,bytes) or custody.blob(raw)!=pins[slug] or pins[slug]!=PINS[slug]:
                raise ValueError('AUTHENTIC_PINNED_TOOL_BLOB_MISMATCH')
            rec=inspect_body(raw)
            rows.append({'slug':slug,'path':path,'git_blob':pins[slug],**rec,'qualified_privacy_approved':False})
        except (OSError,UnicodeError,TypeError,ValueError) as e:
            errors.append(path+':'+type(e).__name__)
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'tools_audited':len(rows),
            'entries':rows,'release':RELEASE.copy()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=ap.parse_args()
    root=a.root.resolve()
    try:
        # Require the native pinned 82-source ledger before auditing six embedded tools.
        manifest=custody.safe_bytes(root,custody.MANIFEST_PATH)
        if manifest is None:raise OSError('incomplete native manifest')
        m=json.loads(manifest)
        if custody.validate_manifest(m,root)['errors']:raise ValueError('repository source custody drift')
        result=audit(lambda p:custody.safe_bytes(root,p))
    except (OSError,ValueError,KeyError,TypeError,UnicodeError):
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_REPOSITORY_UNAVAILABLE_OR_INVALID'],
                'tools_audited':0,'entries':[],'release':RELEASE.copy()}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1
if __name__=='__main__':raise SystemExit(main())
