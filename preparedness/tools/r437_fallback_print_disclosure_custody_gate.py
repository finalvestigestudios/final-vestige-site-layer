#!/usr/bin/env python3
"""R437: no-JavaScript, print, disclosure and invisible-text custody review.

Read-only synthetic/reviewer gate; never licenses publication, commercial activation,
source accuracy, medical safety or accessible print rendering. Composes R436.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys

MAX_BYTES=1_000_000
CONTROL_CHARS = frozenset(chr(x) for x in (
    list(range(0x200b,0x2010))+list(range(0x202a,0x202f))+
    list(range(0x2060,0x2070))+[0xfeff]))
DANGER_WORDS = re.compile(r'(?i)\b(?:emergen\w*|evacuat\w*|warning|caution|boil|filter|purif\w*|'
                          r'medic\w*|child\w*|contact|carbon monoxide|generator|food safe\w*|'
                          r'check\s*out|buy|payment|subscribe|first aid|911)\b')
PRINT_RULE = re.compile(r'(?is)@media\s*(?:\([^{}]+\)\s*and\s*)?print\b|@page\b')
HIDE_RULE = re.compile(r'(?is)(?:display\s*:\s*none|visibility\s*:\s*hidden|'
                       r'opacity\s*:\s*0\b|content\s*:\s*(?:none|["\']{2}))')
URL_TOKEN = re.compile(r'(?i)(?:https?://|//[^\s/]+|(?:payhip|checkout\.stripe|paypal|gumroad)\.com)')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def norm(s): return ' '.join(str(s or '').split())
def h(value): return sha256(json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class Fallback(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[];self.stack=[];self.noscript=0;self.fallback=[]
        self.print_css=[];self.style=0;self.styles=[]
        self.disclosures=[];self.disclosure_stack=[];self.summary=0
        self.external_print=[];self.visible_text=[]
    def handle_starttag(self,tag,attrs):
        keys=[k.lower() for k,v in attrs if isinstance(k,str)]
        if len(keys)!=len(set(keys)):self.errors.append('DUPLICATE_ATTRIBUTE_IN_FALLBACK_OR_DISCLOSURE')
        d={k.lower():v for k,v in attrs if isinstance(k,str)}
        if tag=='noscript':self.noscript+=1
        if tag=='style':self.style+=1;self.styles.append([d.get('media') or '',[]])
        if tag=='link' and 'stylesheet' in (d.get('rel') or '').lower().split():
            media=(d.get('media') or 'all').lower()
            if media in ('all','print') or 'print' in media:
                self.external_print.append((norm(media),norm(d.get('href'))))
        if tag in ('details','dialog'):
            record={'tag':tag,'open': 'open' in d,'aria-expanded':d.get('aria-expanded'),
                    'aria-controls':d.get('aria-controls'),'summary':'','has_summary':False,
                    'content_has_safety_terms':False}
            self.disclosures.append(record);self.disclosure_stack.append(record)
        if tag=='summary' and self.disclosure_stack:
            self.summary+=1;self.disclosure_stack[-1]['has_summary']=True
        if self.noscript and tag!='noscript':
            self.fallback.append(('tag',tag,tuple(sorted((k,norm(v)) for k,v in d.items()))))
        if tag not in VOID:self.stack.append(tag)
        for k,v in d.items():
            if isinstance(v,str) and any(x in CONTROL_CHARS for x in v):self.errors.append('INVISIBLE_OR_BIDI_ATTRIBUTE_REVIEW')
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if self.noscript and tag!='noscript':self.fallback.append(('end',tag))
        if tag=='summary':self.summary=max(0,self.summary-1)
        if tag=='style':
            self.style=max(0,self.style-1)
            if self.styles:
                media,content=self.styles.pop();css=''.join(content)
                if media.strip().lower()=='print' or PRINT_RULE.search(css):self.print_css.append((norm(media),norm(css)))
        if tag in ('details','dialog'):
            if self.disclosure_stack:self.disclosure_stack.pop()
            else:self.errors.append('DISCLOSURE_CLOSE_WITHOUT_OPEN')
        if tag=='noscript':self.noscript=max(0,self.noscript-1)
        if tag in self.stack:
            if self.stack[-1]!=tag:self.errors.append('FALLBACK_MALFORMED_NESTING')
            while self.stack:
                if self.stack.pop()==tag:break
        else:self.errors.append('FALLBACK_UNEXPECTED_END_TAG')
    def handle_data(self,data):
        t=norm(data)
        if any(ch in CONTROL_CHARS for ch in data):self.errors.append('INVISIBLE_OR_BIDI_TEXT_REVIEW')
        if self.style:
            if self.styles:self.styles[-1][1].append(data)
            return
        if not t:return
        if self.noscript:self.fallback.append(('text',t))
        elif not any(s in ('script','template','head') for s in self.stack):self.visible_text.append(t)
        if self.disclosure_stack:
            if self.summary:self.disclosure_stack[-1]['summary']+=' '+t
            if DANGER_WORDS.search(t):self.disclosure_stack[-1]['content_has_safety_terms']=True
    def result(self):
        if self.stack or self.noscript or self.disclosure_stack:self.errors.append('FALLBACK_UNCLOSED_STRUCTURE')
        fallback_text=' '.join(r[1] for r in self.fallback if r[0]=='text')
        if DANGER_WORDS.search(fallback_text):self.errors.append('NOJS_ACTIONABLE_GUIDANCE_QUALIFIED_REVIEW')
        if URL_TOKEN.search(fallback_text):self.errors.append('NOJS_EMBEDDED_LINK_OR_OFFER_REVIEW')
        for media,css in self.print_css:
            if HIDE_RULE.search(css):self.errors.append('PRINT_STYLE_POTENTIAL_WARNING_CONCEALMENT')
        for rec in self.disclosures:
            rec['summary']=norm(rec['summary'])
            if rec['tag']=='details' and not rec['has_summary']:self.errors.append('DETAILS_SUMMARY_MISSING')
            if rec['content_has_safety_terms'] and not rec['open']:
                self.errors.append('COLLAPSED_SAFETY_DISCLOSURE_REVIEW')
        if self.external_print:self.errors.append('EXTERNAL_PRINT_STYLESHEET_NOT_BYTE_AUTHENTICATED')
        return {'errors':sorted(set(self.errors)),
            'nojs_fallback_sha256':h(self.fallback),'nojs_fragments':len(self.fallback),
            'print_rules_sha256':h(self.print_css),'print_rules_count':len(self.print_css),
            'external_print_sha256':h(self.external_print),'external_print_count':len(self.external_print),
            'disclosure_state_sha256':h(self.disclosures),'disclosure_count':len(self.disclosures),
            'human_review_required':True}

def inspect(raw):
    if not isinstance(raw,bytes) or not 12<=len(raw)<=MAX_BYTES or b'\0' in raw:raise ValueError('INVALID_HTML_BYTES')
    p=Fallback();p.feed(raw.decode('utf-8','strict'));p.close();return p.result()

def pair_review(wordpress,preview):
    a,b=inspect(wordpress),inspect(preview)
    errors=['wordpress:'+e for e in a['errors']]+['preview:'+e for e in b['errors']]
    for key,code in [('nojs_fallback_sha256','NOJS_FALLBACK_COPY_OR_LINK_DRIFT'),
                     ('print_rules_sha256','PRINT_STYLESHEET_RULE_DRIFT'),
                     ('external_print_sha256','EXTERNAL_PRINT_STYLESHEET_DESTINATION_DRIFT'),
                     ('disclosure_state_sha256','DISCLOSURE_DEFAULT_VISIBILITY_DRIFT')]:
        if a[key]!=b[key]:errors.append(code)
    return {'errors':sorted(set(errors)),'wordpress':a,'preview':b,'human_review_required':True}

def load_parent():
    path=Path(__file__).with_name('r436_outside_main_semantic_custody_gate.py')
    if not path.is_file():raise ValueError('R436_PARENT_REQUIRED')
    spec=importlib.util.spec_from_file_location('r436_outside_main_semantic_custody_gate',path)
    if spec is None or spec.loader is None:raise ValueError('R436_PARENT_UNLOADABLE')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def hold(errors,base=None,rows=()):
    base=base if isinstance(base,dict) else {}
    errors=sorted(set(list(errors)+list(base.get('errors',[]))))
    return {'schema':1,'issue':136,'business_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'eligible':False,'publication_approved':False,'qualified_safety_approved':False,
            'paid_offer_approved':False,'merchant_confirmed_orders':None,
            'net_revenue_per_1000_qualified_human_sessions':None,
            'r436_semantic_review_clear':base.get('r436_semantic_review_clear',False),
            'r437_fallback_structure_clear':not errors and len(rows)==35,
            'errors':errors,'review_rows':list(rows),
            'no_js_browser_review':'NOT_PERFORMED','print_browser_review':'NOT_PERFORMED',
            'source_claim_safety':'QUALIFIED_HUMAN_REVIEW_REQUIRED',
            'review_only_digest':h(rows) if rows else None}

def audit(manifest,exports,lock,*,test_only=False):
    try:base=load_parent().audit(manifest,exports,lock,test_only=test_only)
    except (OSError,ValueError,TypeError,AttributeError,ImportError):return hold(['PARENT_R436_AUDIT_UNAVAILABLE'])
    if not isinstance(manifest,dict) or not isinstance(manifest.get('articles'),list) or not isinstance(exports,dict):
        return hold(['AUTHENTIC_MANIFEST_OR_EXPORTS_MISSING'],base)
    errors=[];rows=[];seen=set()
    for item in manifest['articles']:
        if not isinstance(item,dict) or not isinstance(item.get('slug'),str):errors.append('INVALID_ARTICLE_IDENTITY');continue
        slug=item['slug']
        if slug in seen or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
            errors.append('DUPLICATE_OR_INVALID_ARTICLE_IDENTITY');continue
        seen.add(slug);pair=exports.get(slug)
        if not isinstance(pair,(list,tuple)) or len(pair)!=2:errors.append('MISSING_EXPORT_PAIR:'+slug);continue
        try:
            result=pair_review(pair[0],pair[1]);errors.extend(slug+':'+e for e in result['errors'])
            rows.append({'slug':slug,'wordpress':result['wordpress'],'preview':result['preview'],
                         'human_review_required':True})
        except (ValueError,UnicodeError,TypeError,OverflowError):errors.append('INVALID_EXPORT_PAIR:'+slug)
    if seen!=set(exports):errors.append('EXTRA_OR_MISSING_EXPORT_IDENTITY')
    if not test_only and len(rows)!=35:errors.append('INCOMPLETE_35_ARTICLE_SLATE')
    return hold(errors,base,sorted(rows,key=lambda r:r['slug']))

def main(argv=None):
    p=argparse.ArgumentParser(description='R437 no-JS/print/disclosure review, ALWAYS HOLD')
    p.add_argument('manifest',type=Path);p.add_argument('lock',type=Path);p.add_argument('exports',type=Path)
    args=p.parse_args(argv)
    try:
        p425=Path(__file__).with_name('r425_integrated_custody_gate.py')
        spec=importlib.util.spec_from_file_location('r425_integrated_custody_gate',p425)
        if not p425.is_file() or spec is None or spec.loader is None:raise ValueError('R425_READER_MISSING')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        manifest,_=m.read_json(args.manifest,args.manifest.parent)
        lock,_=m.read_json(args.lock,args.lock.parent)
        exports={}
        for item in manifest['articles']:
            slug=item['slug']
            if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in exports:
                raise ValueError('UNSAFE_EXPORT_SLUG')
            exports[slug]=tuple(m.r409.read_original(m.safe_path(args.exports/ch/(slug+'.html'),args.exports),MAX_BYTES)
                                for ch in ('wordpress','preview'))
        report=audit(manifest,exports,lock)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,UnicodeError,OverflowError):
        report=hold(['AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE'])
    print(json.dumps(report,sort_keys=True,indent=2));return 2
if __name__=='__main__':sys.exit(main())
