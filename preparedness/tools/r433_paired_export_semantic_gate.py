#!/usr/bin/env python3
"""R433: read-only paired WordPress/preview semantics, never a release approval.

Complements R425 exact byte custody. Examines reviewer-supplied HTML only; it
cannot authenticate exporter identity, URL ownership, safety, or purchases.
All CLI executions exit 2 (DRAFT_HARD_HOLD), including structurally clean data.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
ID = SLUG
BLOCK = {'h1','h2','h3','h4','h5','h6','p','li','blockquote','pre','th','td','figcaption'}
SKIP = {'script','style','svg','template','noscript'}
VOID = {'br','hr','img','input','meta','link','source','wbr','area','base','embed','param','track','col'}
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
HASH = re.compile(r'[a-f0-9]{64}\Z')
MAX = 1_000_000

def normal(s):
    return ' '.join(s.split())

class Editorial(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.main_count=0
        self.active=None
        self.parts=[]
        self.blocks=[]
        self.citations=[]
        self.links=[]
        self.hidden_words=0
        self.form_count=0
        self.errors=[]
    def flush(self):
        if self.active is None: return
        t=normal(''.join(self.parts))
        if t: self.blocks.append([self.active,t])
        self.active=None
        self.parts=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='main': self.main_count+=1
        parent=self.stack[-1] if self.stack else ('',False,False)
        hidden=parent[1] or tag in SKIP or 'hidden' in d or d.get('aria-hidden','').lower()=='true' or bool(re.search(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b',d.get('style') or '',re.I))
        inside=tag=='main' or parent[2]
        if inside and not hidden:
            if tag in BLOCK:
                self.flush(); self.active=tag; self.parts=[]
            sid=d.get('data-source-id') or d.get('data-citation-id')
            if sid is not None:
                if ID.fullmatch(sid): self.citations.append(sid)
                else: self.errors.append('INVALID_CITATION_MARKER')
            if tag=='a': self.links.append(d.get('href'))
            if tag=='form': self.form_count+=1
        if tag not in VOID: self.stack.append((tag,hidden,inside))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if self.active==tag: self.flush()
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]
                break
    def handle_data(self,data):
        if not self.stack: return
        _,hidden,inside=self.stack[-1]
        if inside and hidden and normal(data): self.hidden_words+=len(data.split())
        if inside and not hidden and self.active is not None:
            self.parts.append(data)
            self.citations.extend(CITE.findall(data))
    def finish(self):
        self.flush()
        if self.main_count!=1: self.errors.append('MAIN_MISSING_OR_DUPLICATED')
        if not self.blocks: self.errors.append('EMPTY_MAIN_EDITORIAL')
        if self.hidden_words: self.errors.append('HIDDEN_MAIN_TEXT_REVIEW')
        if self.form_count: self.errors.append('UNAPPROVED_FORM_IN_EXPORT')
        return {'blocks':self.blocks,'citations':self.citations,'links':self.links,'errors':sorted(set(self.errors)),
                'words':sum(len(re.findall(r'\b\w+\b',x[1])) for x in self.blocks)}

def parse_html(raw):
    if not isinstance(raw,bytes) or not 10<=len(raw)<=MAX or b'\x00' in raw:
        raise ValueError('UNSAFE_OR_MISSING_HTML')
    p=Editorial()
    p.feed(raw.decode('utf-8','strict'));p.close()
    return p.finish()

def checked_links(links):
    errors=[]
    for link in links:
        if not isinstance(link,str) or not link or any(ord(c)<32 for c in link):
            errors.append('EMPTY_OR_CONTROL_LINK');continue
        if link.startswith(('#','/')) and not link.startswith('//'): continue
        u=urlsplit(link)
        if u.scheme not in ('https','http') or not u.hostname or u.username or u.password:
            errors.append('UNSAFE_LINK_SCHEME_OR_HOST');continue
        if u.scheme!='https': errors.append('NON_HTTPS_EDITORIAL_LINK')
        host=u.hostname.lower()
        if host in ('payhip.com','buy.stripe.com','checkout.stripe.com','paypal.com') or host.endswith('.payhip.com'):
            errors.append('UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT')
    return sorted(set(errors))

def held(errors, rows=()):
    return {'schema':1,'issue':136,'business_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'eligible':False,'publication_approved':False,'qualified_safety_approved':False,
            'merchant_offer_verified':False,'verified_paid_orders':None,'net_revenue_per_1000_qualified_humans':None,
            'structural_pair_parity':not bool(errors) and len(rows)==35,
            'errors':sorted(set(errors)),'review_rows':list(rows),
            'native_build':'NOT_RUN_BY_R433','export_authenticity':'NOT_ESTABLISHED_BY_R433',
            'source_claim_and_medical_safety':'QUALIFIED_HUMAN_REVIEW_REQUIRED',
            'review_only_digest':sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest() if rows else None}

def audit(manifest,exports,lock,*,test_only=False):
    errors=[]; rows=[]
    if not isinstance(manifest,dict) or not isinstance(lock,dict) or not isinstance(exports,dict):
        return held(['INVALID_EVIDENCE_OBJECT'])
    if manifest.get('release_state')!='DRAFT_HARD_HOLD' or manifest.get('approved') is not False or lock.get('release_state')!='DRAFT_HARD_HOLD' or lock.get('approved') is not False:
        errors.append('FORGED_RELEASE_APPROVAL')
    items=manifest.get('articles'); locks=lock.get('articles')
    if not isinstance(items,list) or not isinstance(locks,list): return held(errors+['MISSING_ARTICLES'])
    if not test_only and (len(items)!=35 or len(locks)!=35 or len(exports)!=35): errors.append('NOT_35_COMPLETE_EXPORT_PAIRS')
    if len(items)!=len(locks) or len(items)!=len(exports): errors.append('DIFFERENT_SLATE_SIZES')
    seen=set(); routes=set(); lockmap={}
    for lr in locks:
        if not isinstance(lr,dict) or not isinstance(lr.get('slug'),str) or lr['slug'] in lockmap:
            errors.append('DUPLICATE_OR_INVALID_LOCK_SLUG'); continue
        lockmap[lr['slug']]=lr
    for item in items:
        if not isinstance(item,dict): errors.append('INVALID_ARTICLE_ROW');continue
        slug=item.get('slug');path=item.get('canonical_path')
        if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in seen:
            errors.append('INVALID_OR_DUPLICATE_SLUG');continue
        seen.add(slug)
        if path!=f'/preparedness/{slug}/' or path in routes: errors.append('ROUTE_DRIFT_OR_DUPLICATE:'+slug)
        routes.add(path)
        lr=lockmap.get(slug)
        if not isinstance(lr,dict) or lr.get('source_ids')!=item.get('sources') or lr.get('canonical_path')!=path:
            errors.append('LOCK_SOURCE_OR_ROUTE_DRIFT:'+slug);continue
        pair=exports.get(slug)
        if not isinstance(pair,(tuple,list)) or len(pair)!=2: errors.append('MISSING_EXPORT_PAIR:'+slug);continue
        parses=[]
        for i,(channel,raw,key) in enumerate(zip(('wordpress','preview'),pair,('wordpress_sha256','preview_sha256'))):
            try:
                expected=lr.get(key)
                if not isinstance(expected,str) or not HASH.fullmatch(expected) or sha256(raw).hexdigest()!=expected:
                    errors.append('BYTE_LOCK_MISMATCH:'+slug+':'+channel)
                data=parse_html(raw)
                errors.extend('HTML:'+slug+':'+channel+':'+e for e in data['errors']+checked_links(data['links']))
                parses.append(data)
            except (ValueError,UnicodeError,TypeError,OverflowError) as exc:
                errors.append('PARSE_ERROR:'+slug+':'+channel+':'+type(exc).__name__)
        if len(parses)!=2:continue
        wp,preview=parses
        if wp['blocks']!=preview['blocks']: errors.append('EDITORIAL_PASSAGE_PARITY:'+slug)
        if wp['citations']!=preview['citations']: errors.append('CITATION_ORDER_PARITY:'+slug)
        if wp['links']!=preview['links']: errors.append('LINK_DESTINATION_PARITY:'+slug)
        ids=item.get('sources')
        if not isinstance(ids,list) or not ids or any(not isinstance(x,str) or not ID.fullmatch(x) for x in ids) or len(set(ids))!=len(ids):
            errors.append('INVALID_MANIFEST_SOURCE_IDS:'+slug)
        else:
            for channel,data in zip(('wordpress','preview'),parses):
                if set(data['citations'])!=set(ids): errors.append('CITATION_COVERAGE_DRIFT:'+slug+':'+channel)
        rows.append({'slug':slug,'wordpress_sha256':sha256(pair[0]).hexdigest(),
                     'preview_sha256':sha256(pair[1]).hexdigest(),'main_words_wp':wp['words'],
                     'main_words_preview':preview['words'],'citation_count_wp':len(wp['citations']),
                     'citation_count_preview':len(preview['citations']),'human_review_required':True})
    if seen!=set(lockmap) or seen!=set(exports): errors.append('MISSING_OR_EXTRA_ARTICLE_IDENTITIES')
    return held(errors,sorted(rows,key=lambda r:r['slug']))

def main(argv=None):
    ap=argparse.ArgumentParser(description='R433 reviewer-supplied paired HTML semantics; ALWAYS DRAFT/HOLD')
    ap.add_argument('manifest',type=Path);ap.add_argument('evidence_lock',type=Path);ap.add_argument('export_root',type=Path)
    args=ap.parse_args(argv)
    try:
        from importlib.util import module_from_spec,spec_from_file_location
        source=Path(__file__).resolve().with_name('r425_integrated_custody_gate.py')
        spec=spec_from_file_location('r425_integrated_custody_gate',source)
        if not source.is_file() or spec is None or spec.loader is None: raise ValueError('R425_REQUIRED')
        module=module_from_spec(spec);spec.loader.exec_module(module)
        manifest,_=module.read_json(args.manifest,args.manifest.parent)
        lock,_=module.read_json(args.evidence_lock,args.evidence_lock.parent)
        if not isinstance(manifest,dict) or not isinstance(manifest.get('articles'),list): raise ValueError('MANIFEST_MISSING')
        exports={}
        for item in manifest['articles']:
            slug=item['slug']
            if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in exports:raise ValueError('SLUG_INVALID')
            exports[slug]=tuple(module.r409.read_original(module.safe_path(args.export_root/channel/(slug+'.html'),args.export_root),MAX)
                                for channel in ('wordpress','preview'))
        result=audit(manifest,exports,lock)
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,OverflowError,AttributeError,ImportError) as exc:
        result=held(['AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE:'+type(exc).__name__])
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__': sys.exit(main())
