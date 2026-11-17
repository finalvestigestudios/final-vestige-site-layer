#!/usr/bin/env python3
"""R434: reviewer-only WordPress/preview document-boundary and egress gate.

R433 compares readable <main> content. R434 audits the *entire* supplied HTML
for active elements, redirects, checkout destinations, and canonical/OG
identity drift that can sit outside <main>. It is a deliberately conservative
static check, not a browser sandbox, network test, consent audit, or QD pass.
No egress, external services, publication, or CMS writes; CLI always exits 2.
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
from urllib.parse import unquote, urlsplit
import unicodedata

MAX = 1_000_000
CHECKOUT_HOSTS = ('payhip.com', 'buy.stripe.com', 'checkout.stripe.com', 'paypal.com',
                  'paypal.me', 'gumroad.com', 'buymeacoffee.com', 'ko-fi.com')
URL_ATTRS = {'href','src','action','formaction','poster','cite','data-href','data-url',
             'data-redirect','data-checkout','data-checkout-url','data-target-url','data-src'}
ACTIVE = {'script','iframe','object','embed','applet','form','portal'}
RISKY_CSS = re.compile(r'@import\b|url\s*\(|expression\s*\(|-moz-binding\s*:|behavior\s*:',re.I)
RISKY_HIDING = re.compile(r'(?:^|;)\s*(?:opacity\s*:\s*0(?:\.0*)?(?:\s*!important)?\s*(?:;|$)|font-size\s*:\s*0(?:px|rem|em|pt|%)?\b|clip-path\s*:\s*inset\s*\(\s*100%|text-indent\s*:\s*-\s*\d{4,}px|color\s*:\s*transparent\b)',re.I)
CANONICAL_HOST = 'finalvestige.com'

def clean_url(raw):
    """Conservative classifier: decode attributes, repeat percent decode max 3."""
    if not isinstance(raw,str) or not raw or any(ord(c)<32 or ord(c)==127 for c in raw):
        return 'EMPTY_OR_CONTROL_URL',None
    value=unicodedata.normalize('NFKC',raw.strip())
    for _ in range(3):
        nxt=unquote(value)
        if nxt==value:break
        value=nxt
    value=unicodedata.normalize('NFKC',value)
    if any(ord(c)<32 or ord(c)==127 for c in value) or '\\' in value or value.startswith('//'):
        return 'AMBIGUOUS_URL_ENCODING',None
    if value.startswith('#'):return None,value
    if value.startswith('/'):
        if value.startswith('//') or any(x in value for x in ('<','>')):return 'AMBIGUOUS_URL_ENCODING',None
        return None,value
    try:
        u=urlsplit(value)
        if u.scheme.lower()!='https' or not u.hostname or u.username or u.password or u.port is not None:
            return 'UNSAFE_SCHEME_AUTHORITY_OR_PORT',None
    except ValueError:
        return 'UNSAFE_SCHEME_AUTHORITY_OR_PORT',None
    host=u.hostname.rstrip('.').casefold()
    if not re.fullmatch(r'[a-z0-9.-]+',host) or '..' in host:
        return 'UNSAFE_OR_CONFUSABLE_HOST',None
    if any(host==x or host.endswith('.'+x) for x in CHECKOUT_HOSTS):
        return 'UNAPPROVED_COMMERCE_DESTINATION',None
    return None,value

def canonical_target(raw,slug):
    e,v=clean_url(raw)
    if e:return e
    if v is None:return 'CANONICAL_INVALID'
    try:p=urlsplit(v)
    except ValueError:return 'CANONICAL_INVALID'
    expected='/preparedness/'+slug+'/'
    if p.scheme and p.hostname.rstrip('.').casefold()!=CANONICAL_HOST:
        return 'CANONICAL_FOREIGN_HOST'
    if p.path!=expected or p.query or p.fragment:
        return 'CANONICAL_ROUTE_DRIFT'
    return None

class DocumentBoundary(HTMLParser):
    def __init__(self,slug):
        super().__init__(convert_charrefs=True)
        self.slug=slug;self.errors=[];self.canonicals=[];self.og_urls=[]
        self.head_count=0;self.main_count=0;self.references=0
        self.start_tags=0;self.template_active=0
    def err(self,e):self.errors.append(e)
    def handle_starttag(self,tag,attrs):
        self.start_tags+=1; d={k.lower():v for k,v in attrs if isinstance(k,str)}
        if tag=='head':self.head_count+=1
        if tag=='main':self.main_count+=1
        if tag in ACTIVE:
            self.template_active+=1
            self.err('ACTIVE_ELEMENT_REVIEW:'+tag)
        if tag=='base':self.err('BASE_URL_REWRITE')
        if tag=='meta' and (d.get('http-equiv') or '').strip().lower()=='refresh':
            self.err('META_REFRESH_REDIRECT')
        if tag=='link' and 'canonical' in (d.get('rel') or '').casefold().split():
            self.canonicals.append(d.get('href'))
        if tag=='meta' and (d.get('property') or '').lower()=='og:url':
            self.og_urls.append(d.get('content'))
        if tag=='meta' and (d.get('name') or '').lower()=='twitter:url':
            self.og_urls.append(d.get('content'))
        if tag=='template':self.err('DORMANT_TEMPLATE_REVIEW')
        if tag=='noscript':self.err('NOSCRIPT_FALLBACK_REVIEW')
        for key,value in d.items():
            if key.startswith('on') and re.fullmatch(r'on[a-z]{3,}',key):
                self.err('INLINE_EVENT_HANDLER:'+key)
            if key=='srcdoc':self.err('EMBEDDED_HTML_SRCDOC')
            if key=='style' and isinstance(value,str):
                if RISKY_CSS.search(value):self.err('CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE')
                if RISKY_HIDING.search(value):self.err('POTENTIALLY_CONCEALED_CONTENT_REVIEW')
            if key in URL_ATTRS:
                if not isinstance(value,str):self.err('MISSING_URL_ATTRIBUTE:'+key);continue
                error,_=clean_url(value)
                if error:self.err('URL:'+key+':'+error)
                else:self.references+=1
            if key=='srcset' and isinstance(value,str):
                # srcset has its own parser; conservative static gate requires human review.
                self.err('RESPONSIVE_SRCSET_REVIEW')
            if key.startswith('data-') and any(s in key for s in ('payment','purchase','merchant')):
                self.err('UNREVIEWED_COMMERCE_DATA_ATTRIBUTE')
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_data(self,data):
        # CSS import outside <main> can be hidden in a style block; scan conservatively.
        if RISKY_CSS.search(data) and re.search(r'@import\b|expression\s*\(|-moz-binding\s*:',data,re.I):
            self.err('CSS_OR_SCRIPT_BODY_REVIEW')
    def finish(self):
        if self.head_count!=1:self.err('HEAD_MISSING_OR_DUPLICATE')
        if self.main_count!=1:self.err('MAIN_MISSING_OR_DUPLICATE')
        if len(self.canonicals)!=1:self.err('CANONICAL_MISSING_OR_DUPLICATE')
        for value in self.canonicals:
            e=canonical_target(value,self.slug)
            if e:self.err(e)
        for value in self.og_urls:
            e=canonical_target(value,self.slug)
            if e:self.err('SOCIAL_META_'+e)
        return {'errors':sorted(set(self.errors)),
                'canonical_count':len(self.canonicals),'social_meta_count':len(self.og_urls),
                'active_element_count':self.template_active,'reference_count':self.references,
                'canonical':self.canonicals[0] if len(self.canonicals)==1 else None}

def inspect(raw,slug):
    if not isinstance(raw,bytes) or not 12<=len(raw)<=MAX or b'\0' in raw:
        raise ValueError('UNSAFE_OR_MISSING_EXPORT')
    parser=DocumentBoundary(slug)
    parser.feed(raw.decode('utf-8','strict'))
    parser.close()
    return parser.finish()

def load_r433():
    target=Path(__file__).with_name('r433_paired_export_semantic_gate.py')
    if not target.is_file():raise ValueError('R433_BASE_REQUIRED')
    spec=importlib.util.spec_from_file_location('r433_paired_export_semantic_gate',target)
    if spec is None or spec.loader is None:raise ValueError('R433_LOAD_FAILURE')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def held(extra,base=None,rows=()):
    base=base if isinstance(base,dict) else {}
    combined=sorted(set(base.get('errors',[])+list(extra)))
    return {'schema':1,'issue':136,'business_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'eligible':False,'publication_approved':False,'qualified_safety_approved':False,
            'commercial_offer_verified':False,'merchant_orders_verified':None,'net_revenue_per_1000_qualified_humans':None,
            'r433_structural_pair_parity':bool(base.get('structural_pair_parity',False)),
            'r434_document_boundary_parity':not combined and len(rows)==35,
            'errors':combined,'review_rows':list(rows),
            'source_claim_accuracy':'NOT_ESTABLISHED_BY_STATIC_HTML',
            'review_only_digest':sha256(json.dumps(list(rows),sort_keys=True,separators=(',',':')).encode()).hexdigest() if rows else None}

def audit(manifest,exports,lock,*,test_only=False):
    try:base=load_r433().audit(manifest,exports,lock,test_only=test_only)
    except (OSError,ValueError,TypeError,ImportError,AttributeError) as e:
        return held(['R433_BASE_UNAVAILABLE:'+type(e).__name__])
    errors=[];rows=[]
    if not isinstance(manifest,dict) or not isinstance(exports,dict):return held(['MISSING_DOCUMENT_EVIDENCE'],base)
    items=manifest.get('articles')
    if not isinstance(items,list):return held(['MISSING_ARTICLE_MANIFEST'],base)
    seen=set()
    for item in items:
        if not isinstance(item,dict):errors.append('INVALID_MANIFEST_ITEM');continue
        slug=item.get('slug')
        if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
            errors.append('INVALID_SLUG');continue
        if slug in seen:errors.append('DUPLICATE_SLUG');continue
        seen.add(slug)
        pair=exports.get(slug)
        if not isinstance(pair,(tuple,list)) or len(pair)!=2:
            errors.append('MISSING_PAIR:'+slug);continue
        channel_docs=[]
        for ch,raw in zip(('wordpress','preview'),pair):
            try:
                p=inspect(raw,slug)
                errors.extend(slug+':'+ch+':'+e for e in p['errors'])
                channel_docs.append(p)
            except (ValueError,UnicodeError,TypeError,OverflowError) as exc:
                errors.append(slug+':'+ch+':DOCUMENT_PARSE:'+type(exc).__name__)
        if len(channel_docs)!=2:continue
        wp,preview=channel_docs
        if wp['canonical']!=preview['canonical']:errors.append('CANONICAL_CHANNEL_DRIFT:'+slug)
        if wp['social_meta_count']!=preview['social_meta_count']:errors.append('SOCIAL_META_COUNT_DRIFT:'+slug)
        rows.append({'slug':slug,'wordpress_canonical':wp['canonical'],'preview_canonical':preview['canonical'],
                     'wordpress_active_elements':wp['active_element_count'],
                     'preview_active_elements':preview['active_element_count'],
                     'human_review_required':True})
    if set(exports)!=seen:errors.append('EXTRA_OR_MISSING_EXPORT_SLUGS')
    if not test_only and len(rows)!=35:errors.append('INCOMPLETE_DOCUMENT_BOUNDARY_SLATE')
    return held(errors,base,sorted(rows,key=lambda x:x['slug']))

def main(argv=None):
    ap=argparse.ArgumentParser(description='Review-only complete HTML boundary gate; never publication approval')
    ap.add_argument('manifest',type=Path);ap.add_argument('lock',type=Path);ap.add_argument('exports',type=Path)
    args=ap.parse_args(argv)
    try:
        # Native evidence loading delegated to R425; no broad file recursion or writes.
        source=Path(__file__).with_name('r425_integrated_custody_gate.py')
        if not source.is_file():raise ValueError('R425_CUSTODY_READER_REQUIRED')
        spec=importlib.util.spec_from_file_location('r425_integrated_custody_gate',source)
        if spec is None or spec.loader is None:raise ValueError('R425_LOADER_REQUIRED')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        manifest,_=module.read_json(args.manifest,args.manifest.parent)
        lock,_=module.read_json(args.lock,args.lock.parent)
        if not isinstance(manifest,dict) or not isinstance(manifest.get('articles'),list):raise ValueError('MANIFEST_REQUIRED')
        exports={}
        for item in manifest['articles']:
            slug=item['slug']
            if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in exports:
                raise ValueError('INVALID_EXPORT_IDENTITY')
            exports[slug]=tuple(module.r409.read_original(module.safe_path(args.exports/ch/(slug+'.html'),args.exports),MAX)
                                for ch in ('wordpress','preview'))
        result=audit(manifest,exports,lock)
    except (OSError,ValueError,TypeError,AttributeError,ImportError,KeyError,UnicodeError,OverflowError) as exc:
        result=held(['AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE:'+type(exc).__name__])
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2
if __name__=='__main__':sys.exit(main())
