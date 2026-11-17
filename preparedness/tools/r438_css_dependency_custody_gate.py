#!/usr/bin/env python3
"""R438 read-only CSS dependency and presentation custody across paired draft exports.

NEVER certifies browser accessibility, safety, editorial claims, QD or release.
The original 35 articles and source ledger remain immutable.
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
from urllib.parse import urlsplit

MAX_BYTES=1_000_000
CSS_LIMIT=200_000
CSS_IMPORT=re.compile(r'(?i)@\s*import\b')
CSS_URL=re.compile(r'(?i)\burl\s*\(')
CSS_ESCAPE=re.compile(r'\\(?:[a-fA-F0-9]{1,6}\s?|[^\r\n])')
CSS_CONTENT=re.compile(r'(?i)(?:^|[;{])\s*content\s*:')
CSS_HIDE=re.compile(r'(?i)\b(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse)|opacity\s*:\s*0(?:\D|$)|clip-path\s*:|clip\s*:|font-size\s*:\s*0(?:\D|$))')
CSS_PRINT=re.compile(r'(?i)@\s*(?:media\s+[^{}]*\bprint\b|page\b)')
NONLOCAL=re.compile(r'(?i)\b(?:https?:|data:|javascript:|blob:|file:|//)')
BIDI={chr(k) for k in list(range(0x202a,0x202f))+list(range(0x2066,0x206a))+[0x200b,0x200c,0x200d,0xfeff]}
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def norm(value):return ' '.join(str(value or '').split())
def digest(value):return sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def text_digest(s):return sha256(s.encode('utf-8')).hexdigest()

def analyze_css(css):
    if len(css.encode('utf-8'))>CSS_LIMIT:raise ValueError('CSS_TOO_LARGE')
    # No CSS parser can safely infer final computed visibility without a browser.
    # Strip ordinary comments only for conservative token alerting; retain raw hash for parity.
    cleaned=re.sub(r'/\*.*?\*/',' ',css,flags=re.S)
    errors=[]
    if CSS_IMPORT.search(cleaned):errors.append('CSS_IMPORT_DEPENDENCY_UNAUTHENTICATED')
    if CSS_URL.search(cleaned):errors.append('CSS_URL_DEPENDENCY_REQUIRES_REVIEW')
    if CSS_ESCAPE.search(cleaned):errors.append('CSS_ESCAPED_TOKEN_REQUIRES_BROWSER_REVIEW')
    if CSS_HIDE.search(cleaned):errors.append('CSS_POSSIBLE_SAFETY_COPY_CONCEALMENT')
    if CSS_CONTENT.search(cleaned):errors.append('CSS_GENERATED_COPY_REQUIRES_REVIEW')
    if CSS_PRINT.search(cleaned):errors.append('CSS_PRINT_CONTEXT_REQUIRES_BROWSER_REVIEW')
    if NONLOCAL.search(cleaned):errors.append('CSS_REMOTE_OR_ACTIVE_SCHEME_REQUIRES_REVIEW')
    if any(c in BIDI for c in css):errors.append('CSS_BIDI_OR_ZERO_WIDTH_CHARACTERS')
    if css.count('/*')!=css.count('*/'):errors.append('CSS_UNBALANCED_COMMENT_REQUIRES_REVIEW')
    return {'sha256':text_digest(css),'bytes':len(css.encode('utf-8')),'errors':sorted(set(errors))}

class CSSDoc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[];self.style_depth=0;self.style_chunks=[];self.inline=[];self.links=[]
        self.style_attrs=[];self.styles=[];self.base=[];self.attribute_order=[];self.stack=[]
    def handle_starttag(self,tag,attrs):
        ks=[k.lower() for k,v in attrs if isinstance(k,str)]
        if len(ks)!=len(set(ks)):self.errors.append('CSS_RELEVANT_DUPLICATE_HTML_ATTRIBUTE')
        d={k.lower():v for k,v in attrs if isinstance(k,str)}
        if tag=='style':
            if self.style_depth:self.errors.append('NESTED_STYLE_ELEMENT_REVIEW')
            self.style_depth+=1;self.style_attrs.append(tuple(sorted((k,norm(v)) for k,v in d.items())));self.style_chunks.append([])
        if tag=='link':
            rel=tuple(sorted((d.get('rel') or '').lower().split()))
            if 'stylesheet' in rel or ('preload' in rel and (d.get('as') or '').lower()=='style') or ('modulepreload' in rel):
                record=(rel,norm(d.get('href')),norm(d.get('media')),norm(d.get('integrity')),
                        norm(d.get('crossorigin')),norm(d.get('referrerpolicy')),norm(d.get('as')))
                self.links.append(record)
                if not d.get('href'):self.errors.append('CSS_LINK_WITHOUT_HREF')
                else:self.errors.append('EXTERNAL_CSS_BYTES_UNVERIFIED')
                if d.get('href') and (d['href'].strip().lower().startswith(('javascript:','data:','file:')) or '\\' in d['href']):
                    self.errors.append('CSS_LINK_UNSAFE_SCHEME_OR_ESCAPE')
        if tag=='base':
            self.base.append((norm(d.get('href')),norm(d.get('target'))))
            if d.get('href') or d.get('target'):self.errors.append('HTML_BASE_CHANGES_LINK_RESOLUTION_REQUIRES_REVIEW')
            if len(self.base)>1:self.errors.append('MULTIPLE_HTML_BASE_ELEMENTS')
        if 'style' in d:
            css=d['style'] or ''
            record=(tag,norm(d.get('id')),norm(d.get('class')),analyze_css(css))
            self.inline.append(record)
            if any(x in record[3]['errors'] for x in ('CSS_POSSIBLE_SAFETY_COPY_CONCEALMENT','CSS_GENERATED_COPY_REQUIRES_REVIEW')):
                self.errors.append('INLINE_STYLE_MAY_HIDE_OR_REPLACE_SAFETY_COPY')
            self.errors.extend(record[3]['errors'])
        for attr in ('hidden','inert','aria-hidden','popover','aria-expanded'):
            if attr in d:self.attribute_order.append((tag,norm(d.get('id')),attr,norm(d[attr])))
        if tag not in VOID:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_data(self,data):
        if self.style_depth and self.style_chunks:self.style_chunks[-1].append(data)
    def handle_endtag(self,tag):
        if tag=='style':
            if not self.style_depth or not self.style_chunks:self.errors.append('UNEXPECTED_STYLE_END');return
            chunks=self.style_chunks.pop();css=''.join(chunks);self.styles.append(analyze_css(css));self.errors.extend(self.styles[-1]['errors']);self.style_depth-=1
        if tag in self.stack:
            if self.stack[-1]!=tag:self.errors.append('CSS_DOCUMENT_NESTING_REVIEW')
            while self.stack:
                if self.stack.pop()==tag:break
        elif tag not in VOID:self.errors.append('CSS_UNEXPECTED_HTML_END_TAG')
    def result(self):
        if self.style_depth or self.stack:self.errors.append('CSS_UNCLOSED_HTML_OR_STYLE')
        return {'errors':sorted(set(self.errors)),
                'embedded_css_sha256':digest(self.styles),'embedded_css_count':len(self.styles),
                'inline_css_sha256':digest(self.inline),'inline_css_count':len(self.inline),
                'stylesheet_link_sha256':digest(self.links),'stylesheet_link_count':len(self.links),
                'css_style_attributes_sha256':digest(self.style_attrs),
                'html_base_sha256':digest(self.base),'html_base_count':len(self.base),
                'visibility_attributes_sha256':digest(self.attribute_order),
                'human_review_required':True}

def inspect(raw):
    if not isinstance(raw,bytes) or not 12<=len(raw)<=MAX_BYTES or b'\0' in raw:raise ValueError('INVALID_HTML_BYTES')
    doc=CSSDoc();doc.feed(raw.decode('utf-8','strict'));doc.close();return doc.result()

def pair_review(wordpress,preview):
    a=inspect(wordpress);b=inspect(preview)
    errors=['wordpress:'+e for e in a['errors']]+['preview:'+e for e in b['errors']]
    for key,code in [('embedded_css_sha256','INLINE_STYLESHEET_PARITY_DRIFT'),
                     ('inline_css_sha256','ELEMENT_STYLE_PARITY_DRIFT'),
                     ('stylesheet_link_sha256','CSS_DEPENDENCY_OR_INTEGRITY_PARITY_DRIFT'),
                     ('css_style_attributes_sha256','STYLE_ELEMENT_ATTRIBUTES_PARITY_DRIFT'),
                     ('html_base_sha256','HTML_BASE_PARITY_DRIFT'),
                     ('visibility_attributes_sha256','VISIBILITY_CONTROL_PARITY_DRIFT')]:
        if a[key]!=b[key]:errors.append(code)
    return {'errors':sorted(set(errors)),'wordpress':a,'preview':b,'human_review_required':True}

def load_parent():
    path=Path(__file__).with_name('r437_fallback_print_disclosure_custody_gate.py')
    if not path.is_file():raise ValueError('R437_PARENT_REQUIRED')
    spec=importlib.util.spec_from_file_location('r437_fallback_print_disclosure_custody_gate',path)
    if spec is None or spec.loader is None:raise ValueError('R437_PARENT_UNLOADABLE')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def hold(errors,base=None,rows=()):
    base=base if isinstance(base,dict) else {}
    errors=sorted(set(list(errors)+list(base.get('errors',[]))))
    return {'schema':1,'issue':136,'business_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'eligible':False,'publication_approved':False,'qualified_safety_approved':False,
            'paid_offer_approved':False,'merchant_confirmed_orders':None,
            'net_revenue_per_1000_qualified_human_sessions':None,
            'r437_fallback_review_clear':base.get('r437_fallback_structure_clear',False),
            'r438_css_dependency_review_clear':not errors and len(rows)==35,
            'errors':errors,'review_rows':list(rows),'browser_css_render_verification':'NOT_PERFORMED',
            'css_remote_origin_authentication':'NOT_PERFORMED',
            'source_claim_safety':'QUALIFIED_HUMAN_REVIEW_REQUIRED',
            'review_only_digest':digest(rows) if rows else None}

def audit(manifest,exports,lock,*,test_only=False):
    try:base=load_parent().audit(manifest,exports,lock,test_only=test_only)
    except (OSError,ValueError,TypeError,AttributeError,ImportError):return hold(['PARENT_R437_AUDIT_UNAVAILABLE'])
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
            rows.append({'slug':slug,'wordpress':result['wordpress'],'preview':result['preview'],'human_review_required':True})
        except (ValueError,UnicodeError,TypeError,OverflowError):errors.append('INVALID_EXPORT_PAIR:'+slug)
    if seen!=set(exports):errors.append('EXTRA_OR_MISSING_EXPORT_IDENTITY')
    if not test_only and len(rows)!=35:errors.append('INCOMPLETE_35_ARTICLE_SLATE')
    return hold(errors,base,sorted(rows,key=lambda r:r['slug']))

def main(argv=None):
    parser=argparse.ArgumentParser(description='R438 CSS custody review (always HARD HOLD)')
    parser.add_argument('manifest',type=Path);parser.add_argument('lock',type=Path);parser.add_argument('exports',type=Path)
    args=parser.parse_args(argv)
    try:
        parent=Path(__file__).with_name('r425_integrated_custody_gate.py')
        spec=importlib.util.spec_from_file_location('r425_integrated_custody_gate',parent)
        if not parent.is_file() or spec is None or spec.loader is None:raise ValueError('ORIGINAL_READER_MISSING')
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
