#!/usr/bin/env python3
"""R113: private, read-only source/citation/landing HOLD gate. No CMS or network."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

GUIDE = 'household-emergency-plan'
CANONICAL = 'https://finalvestige.com/preparedness/start-here/household-emergency-plan/'
PINS = {
    'body': '8ca5c261dba56eeaf79c445332381a74867233de',
    'meta': '0681d51e6e29166eaae27ac2b7f1fbde3f836787',
    'taxonomy': 'eea601e53e16e36cd4fc890876bc249b39632370',
}
CITES = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TOKENS = re.compile(r'\{\{[^{}]*\}\}')
VOID = {'br','hr','img','input','meta','link','area','base','source','track','wbr'}
HIDDEN = {'script','style','template','noscript','iframe','object','svg'}

class Hold(ValueError):
    pass

def demand(ok, reason):
    if not ok:
        raise Hold(reason)

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\x00' + data).hexdigest()

class EvidenceHTML(HTMLParser):
    """Does not pretend to replace browser/assistive technology or source review."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.citations=[]; self.hidden=[]; self.content=[]
        self.errors=[]; self.ids=set(); self.headings=0; self.paragraphs=0; self.actions=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag in HIDDEN: self.errors.append('NONREADING_OR_ACTIVE_ELEMENT')
        for k,v in attrs:
            if v and '{{cite:' in v:
                self.hidden.extend(CITES.findall(v))
                self.errors.append('CITATION_IN_ATTRIBUTE')
        if d.get('id'):
            if d['id'] in self.ids: self.errors.append('DUPLICATE_HTML_ID')
            self.ids.add(d['id'])
        style=(d.get('style') or '').lower().replace(' ','')
        blocked=(tag in HIDDEN or 'hidden' in d or 'inert' in d or
                 (d.get('aria-hidden') or '').lower()=='true' or
                 'display:none' in style or 'visibility:hidden' in style or
                 bool(self.stack and self.stack[-1][1]))
        if tag=='h2' and not blocked: self.headings+=1
        if tag=='p' and not blocked: self.paragraphs+=1
        if tag=='section' and 'pa-act' in (d.get('class') or '').split() and not blocked:
            self.actions+=1
        if tag not in VOID: self.stack.append((tag,blocked))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID: return
        if not self.stack or self.stack[-1][0]!=tag:
            self.errors.append('HTML_NESTING'); return
        self.stack.pop()
    def handle_data(self,data):
        cites=CITES.findall(data)
        if self.stack and self.stack[-1][1]:
            self.hidden.extend(cites); return
        self.citations.extend(cites); self.content.append(data)
        for t in TOKENS.findall(data):
            if not (CITES.fullmatch(t) or re.fullmatch(r'\{\{link:[a-z0-9-]+\|[^{}]*\}\}',t)):
                self.errors.append('UNKNOWN_TEMPLATE_TOKEN')
    def handle_comment(self,data):
        if '{{cite:' in data:
            self.hidden.extend(CITES.findall(data))
            self.errors.append('CITATION_IN_COMMENT')

def inspect(body,meta,tax):
    """Semantic gates do not rely on self-reported approvals or copied URL alone."""
    demand(isinstance(body,str) and isinstance(meta,dict) and isinstance(tax,dict),
           'MISSING_GUIDE_DATA')
    slate=tax.get('slate')
    demand(isinstance(slate,list) and len(slate)==35 and
           tax.get('base_path')=='/preparedness/', 'SLATE_COUNT_OR_BASE_CHANGED')
    demand(all(isinstance(r,dict) for r in slate), 'INVALID_SLATE_ROW')
    demand({r.get('n') for r in slate}==set(range(1,36)), 'SLATE_NUMBER_CHANGED')
    routes=[]
    for row in slate:
        pair=(row.get('section'),row.get('slug'))
        demand(all(isinstance(v,str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',v)
                   for v in pair), 'INVALID_CANONICAL_COMPONENT')
        routes.append('/preparedness/{}/{}/'.format(*pair))
    demand(len(set(routes))==35,'DUPLICATED_ARTICLE_ROUTE')
    hits=[r for r in slate if r.get('slug')==GUIDE]
    demand(len(hits)==1 and hits[0].get('section')=='start-here' and
           hits[0].get('gate') is True,'FROZEN_GUIDE_GATE_CHANGED')
    demand(meta.get('slug')==GUIDE and meta.get('section')=='start-here' and
           meta.get('track')=='modern','GUIDE_IDENTITY_CHANGED')
    review=meta.get('safety_review')
    demand(meta.get('status')=={'editorial':'drafted','publish':'draft'} and
           isinstance(review,dict) and review.get('state')=='pending',
           'UNREVIEWED_SAFETY_OR_PUBLISH_STATE_CHANGED')
    scope=meta.get('source_use')
    demand(isinstance(scope,dict) and len(scope)>=14 and all(
           isinstance(k,str) and re.fullmatch(r'[a-z0-9-]+',k) and
           isinstance(v,str) and v.strip() for k,v in scope.items()),
           'AUTHOR_SOURCE_USE_MISSING')
    p=EvidenceHTML(); p.feed(body); p.close()
    demand(not p.stack and not p.errors and not p.hidden,
           'CITATION_LAUNDERING_OR_HTML_FAULT')
    demand(set(p.citations)==set(scope) and len(p.citations)>=40,
           'VISIBLE_CITATION_SOURCE_SCOPE_CHANGED')
    words=len(re.findall(r"\b[\w'-]+\b",' '.join(p.content)))
    demand(words>=1800 and p.headings>=8 and p.paragraphs>=25,
           'ORIGINAL_READING_DEPTH_LOST')
    visible=' '.join(p.content).lower()
    demand(p.actions==1 and 'what to do now' in visible and
           'local officials' in visible and 'emergency number' in visible,
           'LOCAL_WARNING_OR_ACTION_BOX_REMOVED')
    return {'slate':35,'unique_routes':35,'source_ids':len(set(p.citations)),
            'visible_citation_occurrences':len(p.citations),
            'visible_word_count':words,'readable_h2':p.headings,
            'author_source_support_verified':False,
            'qualified_safety_review':'PENDING','may_publish':False}

def check_checkout(root):
    """Only exact historical raw Git objects; changed source needs human review."""
    p=Path(root)/'preparedness'
    paths={'body':p/'content/articles/household-emergency-plan.body.html',
           'meta':p/'content/articles/household-emergency-plan.meta.json',
           'taxonomy':p/'taxonomy.json'}
    raw={k:v.read_bytes() for k,v in paths.items()}
    for k,v in raw.items():
        demand(git_blob(v)==PINS[k],k.upper()+'_GIT_OBJECT_CHANGED_NEEDS_REVIEW')
    return inspect(raw['body'].decode('utf-8'),json.loads(raw['meta']),
                   json.loads(raw['taxonomy']))

def preview(guide):
    demand(guide.get('may_publish') is False and
           guide.get('qualified_safety_review')=='PENDING','INVALID_REVIEW_STATE')
    return {'schema':'fv-preparedness-r113-HOLD-v1','issues':[136,820,818],
            'guide':guide,'canonical_proposed_NOT_LIVE':CANONICAL,
            'social_asset_id':'AWAITING_GROK_TASK_008',
            'merchant_offer':'NO_VERIFIED_FV_OWNED_PREPAREDNESS_SKU',
            'paid_checkout_link':None,'merchant_paid_orders':'N/A',
            'realized_net_revenue_per_1000_qualified_sessions':'N/A',
            'draft_wordpress_copy':
                '<aside class="pa-preview" data-state="DRAFT-HOLD">'
                '<h2>Household emergency plan — free guide (unpublished)</h2>'
                '<p>Plan an out-of-area contact, a meeting place and a practice day. '
                'The complete, source-linked guide remains free. Follow local emergency '
                'officials during an active emergency.</p>'
                '<p>No FV-owned paid Preparedness toolkit has been verified for this page.</p>'
                '</aside>',
            'release_state':'HOLD','may_publish':False,
            'may_modify_wordpress':False,'qualified_safety_or_qd_pass':False}

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',default='.')
    args=ap.parse_args()
    try:
        print(json.dumps(preview(check_checkout(args.repo_root)),sort_keys=True,indent=2))
        return 0
    except (Hold,FileNotFoundError,UnicodeError,ValueError) as e:
        print(json.dumps({'release_state':'HOLD','integrity':'FAILED_CLOSED','reason':str(e)}))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
