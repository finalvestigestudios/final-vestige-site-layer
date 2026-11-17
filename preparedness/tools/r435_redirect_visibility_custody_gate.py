#!/usr/bin/env python3
"""R435: independent full-document destination and visibility custody (review ONLY).

This additive gate composes R434, audits duplicate HTML attributes, nested URL
redirect parameters, hidden/aria-inert content, stylesheet hiding and complete
cross-channel anchor inventories. Static and conservative: not browser security,
source truth, accessibility, purchase verification, or a publication approval.
CLI exits 2 even if synthetic checks pass. No network/CMS/file writes.
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
from urllib.parse import parse_qsl, unquote, urlsplit

MAX = 1_000_000
REDIRECT_KEYS = frozenset(('url','uri','u','to','go','next','return','return_url',
    'returnurl','redirect','redirect_uri','redirect_url','destination','dest',
    'target','out','link','continue','checkout','checkout_url','payment_url'))
MERCHANTS = ('payhip.com','buy.stripe.com','checkout.stripe.com','paypal.com',
             'paypal.me','gumroad.com','buymeacoffee.com','ko-fi.com')
STYLE_HIDING = re.compile(r'(?i)(?:display\s*:\s*none|visibility\s*:\s*hidden|'
    r'opacity\s*:\s*0(?:\D|$)|clip-path\s*:\s*inset\s*\(\s*100%|'
    r'font-size\s*:\s*0(?:px|rem|em|pt|%)?\b|color\s*:\s*transparent)')
STRUCTURAL = {'html','head','body','main'}
ANCHOR_ATTRS = {'href'}
URL_LIKE = re.compile(r'(?i)(?:https?\s*:\s*[/\\]{2}|(?:%25)*%2f%2f|payhip\.com|'
    r'checkout\.stripe\.com|paypal\.com|gumroad\.com)')

def decoded(value: str) -> str:
    """Finite bounded decoding for review, never a browser interpretation."""
    if not isinstance(value,str): return ''
    for _ in range(5):
        newer = unquote(value)
        if newer == value: break
        value = newer
    return value

def merchant(host: str) -> bool:
    h=host.rstrip('.').casefold()
    return any(h == d or h.endswith('.'+d) for d in MERCHANTS)

def nested_destination_errors(value: str) -> list[str]:
    """Flag opaque click-tracker redirect targets and concealed commerce URLs."""
    if not isinstance(value,str): return []
    text=decoded(value)
    try:
        parsed=urlsplit(text)
        params=parse_qsl(parsed.query,keep_blank_values=True,max_num_fields=70)
    except (ValueError,TypeError): return ['UNREADABLE_DESTINATION_PARAMETERS']
    errors=[]
    for k,v in params:
        key=decoded(k).strip().casefold().replace('-','_')
        target=decoded(v).strip()
        looks_link = target.startswith(('https://','http://','//','javascript:','/'))
        if key in REDIRECT_KEYS or looks_link or URL_LIKE.search(target):
            if looks_link or URL_LIKE.search(target):
                errors.append('NESTED_DESTINATION_REVIEW')
                try:
                    u=urlsplit(target)
                    if u.hostname and merchant(u.hostname):
                        errors.append('NESTED_COMMERCE_DESTINATION')
                except ValueError: errors.append('NESTED_DESTINATION_UNPARSEABLE')
            elif key in REDIRECT_KEYS and target:
                errors.append('OPAQUE_REDIRECT_PARAMETER_REVIEW')
    return sorted(set(errors))

class CompleteDocument(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[];self.anchors=[];self.count=0;self.structural=[]
        self.in_style=0;self.style_text=[];self.comments=0
    def err(self,code): self.errors.append(code)
    def handle_starttag(self,tag,attrs):
        self.count+=1
        names=[k.casefold() for k,_ in attrs if isinstance(k,str)]
        for k in set(names):
            if names.count(k)>1:self.err('DUPLICATE_HTML_ATTRIBUTE:'+tag+':'+k)
        d={k.lower():v for k,v in attrs if isinstance(k,str)}
        if tag in STRUCTURAL:
            if tag in self.structural:self.err('DUPLICATE_OPEN_STRUCTURAL:'+tag)
            self.structural.append(tag)
        if tag=='style':self.in_style+=1
        if 'hidden' in d or 'inert' in d or str(d.get('aria-hidden','')).strip().lower()=='true':
            self.err('POTENTIALLY_HIDDEN_OR_INERT_CONTENT_REVIEW')
        if tag=='meta' and ((d.get('name') or '').strip().casefold() in ('robots','googlebot')):
            if 'noindex' in (d.get('content') or '').casefold() or 'nofollow' in (d.get('content') or '').casefold():
                self.err('ROBOT_DIRECTIVE_REVIEW')
        for k,v in attrs:
            if not isinstance(k,str) or not isinstance(v,str):continue
            key=k.lower()
            if key in ANCHOR_ATTRS and tag=='a':
                self.anchors.append(v)
            if key in ('href','src','action','formaction','data-href','data-url','data-redirect',
                'data-checkout','data-checkout-url','data-target-url','data-src'):
                self.errors.extend(nested_destination_errors(v))
            elif key.startswith('data-') and URL_LIKE.search(decoded(v)):
                self.err('UNCLASSIFIED_DYNAMIC_URL_ATTRIBUTE_REVIEW')
            if key=='style' and STYLE_HIDING.search(v):
                self.err('STYLESHEET_OR_INLINE_HIDING_REVIEW')
    def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag=='style':self.in_style=max(0,self.in_style-1)
        if tag in STRUCTURAL:
            if not self.structural or self.structural[-1]!=tag:
                self.err('STRUCTURAL_NESTING_OR_CLOSE_ERROR:'+tag)
            else:self.structural.pop()
    def handle_data(self,data):
        if self.in_style and STYLE_HIDING.search(data):
            self.err('STYLESHEET_OR_INLINE_HIDING_REVIEW')
    def handle_comment(self,data):
        self.comments+=1
        if URL_LIKE.search(decoded(data)) or re.search(r'(?i)\b(?:warning|caution|evacuat\w*|medicine|medical|poison|carbon monoxide)\b',data):
            self.err('COMMENT_CONTAINS_URL_OR_SAFETY_TEXT_REVIEW')
    def finish(self):
        if self.structural:self.err('UNCLOSED_STRUCTURAL_HTML')
        return {'errors':sorted(set(self.errors)),
                'anchor_inventory':sorted(self.anchors),
                'anchor_digest':sha256(json.dumps(sorted(self.anchors),ensure_ascii=True,separators=(',',':')).encode()).hexdigest(),
                'anchor_count':len(self.anchors),'comment_count':self.comments,
                'tag_count':self.count}

def inspect(raw):
    if not isinstance(raw,bytes) or not 12<=len(raw)<=MAX or b'\0' in raw:
        raise ValueError('INVALID_HTML_BYTES')
    parser=CompleteDocument()
    parser.feed(raw.decode('utf-8','strict'));parser.close()
    return parser.finish()

def load_parent():
    path=Path(__file__).with_name('r434_document_boundary_gate.py')
    if not path.is_file():raise ValueError('R434_PARENT_REQUIRED')
    spec=importlib.util.spec_from_file_location('r434_document_boundary_gate',path)
    if spec is None or spec.loader is None:raise ValueError('R434_PARENT_UNLOADABLE')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def held(errors,base=None,rows=()):
    base=base if isinstance(base,dict) else {}
    errors=sorted(set(errors+list(base.get('errors',[]))))
    return {'schema':1,'issue':136,'business_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'eligible':False,'publication_approved':False,'qualified_safety_approved':False,
            'commercial_offer_verified':False,'merchant_orders_verified':None,
            'net_revenue_per_1000_qualified_humans':None,
            'r434_document_boundary_parity':base.get('r434_document_boundary_parity',False),
            'r435_complete_link_and_visibility_parity':not errors and len(rows)==35,
            'errors':errors,'review_rows':list(rows),'authentic_source_accuracy':'NOT_VERIFIED',
            'authentic_export_status':'NOT_ESTABLISHED_BY_STATIC_GATE',
            'review_only_digest':sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest() if rows else None}

def audit(manifest,exports,lock,*,test_only=False):
    try:base=load_parent().audit(manifest,exports,lock,test_only=test_only)
    except (OSError,ValueError,TypeError,ImportError,AttributeError):
        return held(['PARENT_AUDIT_UNAVAILABLE'])
    if not isinstance(manifest,dict) or not isinstance(exports,dict) or not isinstance(manifest.get('articles'),list):
        return held(['MISSING_AUTHENTIC_MANIFEST_OR_EXPORTS'],base)
    errors=[]; rows=[]; seen=set()
    for item in manifest['articles']:
        if not isinstance(item,dict) or not isinstance(item.get('slug'),str):
            errors.append('INVALID_ARTICLE_IDENTITY');continue
        slug=item['slug']
        if slug in seen:errors.append('DUPLICATE_ARTICLE_IDENTITY');continue
        seen.add(slug)
        pair=exports.get(slug)
        if not isinstance(pair,(tuple,list)) or len(pair)!=2:
            errors.append('MISSING_COMPLETE_HTML_PAIR:'+slug);continue
        parsed=[]
        for channel,raw in zip(('wordpress','preview'),pair):
            try:
                view=inspect(raw);parsed.append(view)
                errors.extend(slug+':'+channel+':'+e for e in view['errors'])
            except (ValueError,UnicodeError,TypeError,OverflowError):
                errors.append('INVALID_FULL_DOCUMENT:'+slug+':'+channel)
        if len(parsed)!=2:continue
        a,b=parsed
        if a['anchor_inventory']!=b['anchor_inventory']:
            errors.append('FULL_DOCUMENT_ANCHOR_DESTINATION_DRIFT:'+slug)
        rows.append({'slug':slug,'wp_all_anchor_sha256':a['anchor_digest'],
                     'preview_all_anchor_sha256':b['anchor_digest'],
                     'wp_anchor_count':a['anchor_count'],'preview_anchor_count':b['anchor_count'],
                     'human_review_required':True})
    if seen!=set(exports):errors.append('EXPORT_IDENTITY_DRIFT')
    if not test_only and len(rows)!=35:errors.append('INCOMPLETE_35_ARTICLE_REVIEW')
    return held(errors,base,sorted(rows,key=lambda x:x['slug']))

def main(argv=None):
    ap=argparse.ArgumentParser(description='R435 additive full HTML link/visibility review; always HOLD')
    ap.add_argument('manifest',type=Path);ap.add_argument('lock',type=Path);ap.add_argument('exports',type=Path)
    a=ap.parse_args(argv)
    try:
        parent=load_parent();p=Path(__file__).with_name('r425_integrated_custody_gate.py')
        if not p.is_file():raise ValueError('R425_READER_MISSING')
        spec=importlib.util.spec_from_file_location('r425_integrated_custody_gate',p)
        if spec is None or spec.loader is None:raise ValueError('R425_READER_UNLOADABLE')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        manifest,_=m.read_json(a.manifest,a.manifest.parent)
        lock,_=m.read_json(a.lock,a.lock.parent)
        exports={}
        for item in manifest['articles']:
            slug=item['slug']
            if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in exports:
                raise ValueError('INVALID_EXPORT_SLUG')
            exports[slug]=tuple(m.r409.read_original(m.safe_path(a.exports/ch/(slug+'.html'),a.exports),MAX)
                                for ch in ('wordpress','preview'))
        result=audit(manifest,exports,lock)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,UnicodeError,OverflowError):
        result=held(['AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE'])
    print(json.dumps(result,sort_keys=True,indent=2));return 2
if __name__=='__main__':sys.exit(main())
