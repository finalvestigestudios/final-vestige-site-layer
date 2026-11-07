#!/usr/bin/env python3
"""R191: draft-only six-tool CSS/resource/structured-commerce boundary.

Read-only, deterministic, complementary to R189's JavaScript and HTML gates.
A passing structural inventory is NEVER independent safety/privacy/QD clearance
and NEVER permission to publish or enable commerce. Refuses external CSS URLs,
CSS loaders, external SVG/media resource references, and commercial JSON-LD
in all six authored tool bodies and all six disposable WordPress exports.
This is a static screening tool, not a browser/network noninterference proof.
"""
from __future__ import annotations

import argparse
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
from urllib.parse import unquote

SCHEMA='fv-preparedness-r191-resource-offer-boundary-v1'
HOLD='DRAFT_HARD_HOLD'
INVALID='INVALID_HARD_HOLD'
TOOLS=('family-reunification-card','home-fire-escape-worksheet',
       'kit-builder','power-outage-planner','reunification-plan','water-planner')
MAX_SIZE=8_000_000
# Only local SVG fragment references (e.g., url(#fw-pat)) are necessary in
# the six canonical tool sources. Any file/data/HTTP URL needs explicit review.
CSS_URL=re.compile(r'url\s*\(\s*([^)]*)\)',re.I|re.S)
CSS_UNSAFE=re.compile(r'@\s*(?:import|font-face|namespace)\b|\b(?:image-set|-webkit-image-set|cross-fade|element|expression)\s*\(|(?<![a-z0-9_-])(?:-moz-binding|behavior)\s*:', re.I)
CSS_BACKSLASH=re.compile(r'\\(?:([0-9a-fA-F]{1,6})(?:\s)?|(.))',re.S)
TYPE_OFFER={'product','offer','aggregateoffer','individualproduct','someproducts','buyaction','orderaction'}
OFFER_KEYS={'offers','price','pricecurrency','availability','inventorylevel','eligiblequantity','eligibletransactionvolume','merchant','seller','pricevaliduntil','checkouturl'}
MEDIA_KEYS={'src','srcset','poster','data','cite','background','xlink:href','href','action','formaction'}
MEDIA_TAGS={'audio','video','track','source','picture','image','use','feimage','foreignobject','object','embed','iframe','img','input','script','link','form'}
SVG_STYLES={'fill','stroke','filter','clip-path','mask','marker-start','marker-mid',
            'marker-end','cursor'}


def css_unescape(src: str) -> str:
    def replace(m):
        if m.group(1):
            cp=int(m.group(1),16)
            return chr(cp) if 0 < cp <= 0x10ffff and not (0xd800 <= cp <= 0xdfff) else '\ufffd'
        return m.group(2) or ''
    return CSS_BACKSLASH.sub(replace,src)


def css_strip_comments(src: str) -> tuple[str, bool]:
    """Normalize CSS comments before checking token-spliced remote resource rules.

    Preserve comment markers in quoted strings. Reject malformed boundaries.
    This is conservative static screening, never browser-privacy acceptance.
    """
    out=[]; i=0; quote=None; bad=False
    while i < len(src):
        c=src[i]
        if quote is not None:
            out.append(c)
            if c=='\\' and i+1<len(src):
                i+=1;out.append(src[i])
            elif c==quote:quote=None
            i+=1;continue
        if c in ('"',"'"):
            quote=c;out.append(c);i+=1;continue
        if src.startswith('/*',i):
            end=src.find('*/',i+2)
            if end<0: bad=True;break
            i=end+2;continue
        if src.startswith('*/',i):bad=True
        out.append(c);i+=1
    if quote is not None:bad=True
    return ''.join(out),bad


def css_errors(css: str) -> list[str]:
    """Fail closed on CSS loads, including CSS escape and entity spellings."""
    decoded=css_unescape(unescape(css))
    clean,comment_error=css_strip_comments(decoded)
    errors=[]
    if comment_error:errors.append('malformed CSS comment/string boundary')
    if CSS_UNSAFE.search(clean):
        errors.append('CSS import/font/remote-resource capable construct')
    # A malformed url() with no closing ')' is still suspicious.
    if len(re.findall(r'\burl\s*\(',clean,re.I)) != len(list(CSS_URL.finditer(clean))):
        errors.append('malformed CSS url() token')
    for m in CSS_URL.finditer(clean):
        url=m.group(1).strip().strip('"\'').strip()
        if not re.fullmatch(r'#[A-Za-z_][A-Za-z0-9_.:-]*',url):
            errors.append('CSS resource URL is not a same-document fragment')
    return errors



# R193: JSON-LD is only one form of commercial structured data. Microdata,
# RDFa and OpenGraph meta properties can imply a price/offer without JSON-LD.
# Treat these as unapproved commercial claims, not verified product evidence.
COMMERCIAL_TERMS = TYPE_OFFER | OFFER_KEYS | {
    'hasoffercatalog', 'potentialaction', 'purchaseurl', 'saleprice',
    'salesprice', 'paymentaccepted', 'acceptedpaymentmethod',
}

def structured_tail(value: str) -> str:
    """Conservative final vocabulary token for schema URLs, CURIEs and RDFa."""
    if not isinstance(value, str):
        return ''
    normalized = unquote(unescape(value)).strip().rstrip('/')
    normalized = normalized.partition('?')[0]
    return normalized.rsplit('#', 1)[-1].rsplit('/', 1)[-1].rsplit(':', 1)[-1].lower()

def markup_offer_errors(tag: str, attrs: dict) -> list[str]:
    """Block non-JSON-LD commerce claims on the six unpublished tools."""
    errors = []
    for key in ('itemtype', 'typeof'):
        raw = attrs.get(key)
        if raw and any(structured_tail(token) in TYPE_OFFER for token in raw.split()):
            errors.append('unapproved microdata/RDFa commerce type: ' + key)
    for key in ('itemprop', 'property', 'rel'):
        raw = attrs.get(key)
        if raw and any(structured_tail(token) in COMMERCIAL_TERMS
                       for token in raw.split()):
            errors.append('unapproved microdata/RDFa commerce property: ' + key)
    if tag == 'meta':
        for key in ('name', 'property', 'http-equiv'):
            raw = attrs.get(key)
            if not raw:
                continue
            value = unquote(unescape(raw)).strip().lower()
            if (value.startswith(('product:', 'og:price:', 'commerce:'))
                    or structured_tail(value) in COMMERCIAL_TERMS):
                errors.append('unapproved product/price meta declaration: ' + key)
    return errors

def offer_errors(obj: object) -> list[str]:
    errors=[]
    if isinstance(obj,dict):
        typ=obj.get('@type',[])
        types=typ if isinstance(typ,list) else [typ]
        if any(isinstance(t,str) and (structured_tail(t) in TYPE_OFFER) for t in types):
            errors.append('commercial structured-data type')
        if any(isinstance(k,str) and k.lower() in OFFER_KEYS for k in obj):
            errors.append('unapproved structured-data offer claim')
        for x in obj.values():errors.extend(offer_errors(x))
    elif isinstance(obj,list):
        for x in obj:errors.extend(offer_errors(x))
    return errors


class Screen(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[]
        self._capture=None
        self._buffer=[]
        self.css_blocks=0
        self.jsonld_blocks=0

    def handle_starttag(self,tag,attrs):
        # Browser HTML parsing usually keeps the first repeated attribute;
        # dict(attrs) keeps the last and could hide a remote CSS/SVG resource.
        names=[key for key,_ in attrs]
        if len(names)!=len(set(names)):
            self.errors.append('duplicate HTML attributes on '+tag)
        attrs=dict(attrs)
        self.errors.extend(markup_offer_errors(tag, attrs))
        if tag in ('style','script'):
            if tag == 'style':
                self._capture='css';self._buffer=[];self.css_blocks+=1
            elif (attrs.get('type') or '').lower().strip()=='application/ld+json':
                self._capture='jsonld';self._buffer=[];self.jsonld_blocks+=1
        if 'style' in attrs:
            self.errors.extend('inline-style: '+e for e in css_errors(attrs['style'] or ''))
        # SVG presentation attributes can fetch an external URL without a
        # CSS style element or an href/src. Existing fill=url(#fw-pat) passes.
        for key in SVG_STYLES.intersection(attrs):
            self.errors.extend('SVG-style '+key+': '+e for e in css_errors(attrs[key] or ''))
        if attrs.get('background'):
            self.errors.append('unreviewed HTML background resource')
        if tag in MEDIA_TAGS:
            for key in MEDIA_KEYS:
                if key not in attrs or not attrs[key]:continue
                val=unescape(attrs[key].strip())
                if key in ('href','xlink:href') and tag in ('use','image','feimage') and re.fullmatch(r'#[A-Za-z_][A-Za-z0-9_.:-]*',val):
                    continue
                # All resource-bearing elements in the Preparedness tools are
                # authored inline. Relative paths, data: and remote references
                # are held pending rights/privacy review; no known required case.
                self.errors.append('media/external-capable element reference: '+tag+'/'+key)
        if tag == 'svg':
            # A remote SVG injected via data or use is covered by the element
            # attribute rule; prohibit script-capable foreignObjects outright.
            pass
        if tag in ('foreignobject','animate','set','animatetransform','animatemotion'):
            self.errors.append('unreviewed active SVG element: '+tag)

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag in ('style','script'): self.handle_endtag(tag)

    def handle_data(self,data):
        if self._capture:self._buffer.append(data)

    def handle_endtag(self,tag):
        expected={'style':'css','script':'jsonld'}.get(tag)
        if self._capture!=expected or expected is None:return
        content=''.join(self._buffer)
        if expected=='css':
            self.errors.extend('style-block: '+e for e in css_errors(content))
        elif expected=='jsonld':
            try:self.errors.extend(offer_errors(json.loads(content)))
            except (ValueError,TypeError):self.errors.append('invalid JSON-LD script')
        self._capture=None;self._buffer=[]

    def finish(self):
        self.close()
        if self._capture:self.errors.append('unterminated style or JSON-LD block')
        return self.errors


def scan(markup: str) -> list[str]:
    screen=Screen()
    screen.feed(markup)
    return screen.finish()


def safe_read(path: Path) -> str:
    if path.is_symlink() or not path.is_file():raise ValueError('missing or symlinked input: '+path.name)
    mode=path.stat().st_mode
    if not stat.S_ISREG(mode) or path.stat().st_size > MAX_SIZE:raise ValueError('untrusted size/file type: '+path.name)
    return path.read_text(encoding='utf-8')


def check(preparedness: Path, *, exports: bool=True) -> dict:
    receipt={'schema':SCHEMA,'state':INVALID,'authored_checked':0,'wp_exports_checked':0,
             'publication_authorized':False,'independent_qd_pass':False,
             'privacy_browser_qa_complete':False,'merchant_offer_verified':False,
             'verified_paid_orders':None,'realized_net_revenue':None,'errors':[]}
    try:
        if not preparedness.is_dir() or preparedness.is_symlink():raise ValueError('unsafe or missing Preparedness root')
        bodies=preparedness/'content/tools'
        if bodies.is_symlink() or not bodies.is_dir():raise ValueError('unsafe tool body directory')
        names={p.name.removesuffix('.body.html') for p in bodies.glob('*.body.html')}
        if names != set(TOOLS):raise ValueError('six tool body roster drift')
        if exports and (preparedness/'build/wp').is_symlink():raise ValueError('unsafe WordPress export directory')
        for slug in TOOLS:
            for kind, path in [('source',bodies/f'{slug}.body.html')]+([('wp',preparedness/'build/wp'/f'{slug}.html')] if exports else []):
                content=safe_read(path)
                if kind=='wp' and (not content.startswith('<!-- wp:html -->') or not content.rstrip().endswith('<!-- /wp:html -->')):
                    raise ValueError('not a draft WordPress wrapper: '+slug)
                problems=scan(content)
                if problems:raise ValueError(f'{slug} {kind}: '+', '.join(problems[:3]))
                if kind=='source':receipt['authored_checked']+=1
                else:receipt['wp_exports_checked']+=1
        if not exports:raise ValueError('source-only scan never permits structural completion')
        receipt['state']=HOLD
    except (ValueError,OSError,TypeError,UnicodeError) as e:
        receipt['errors'].append(str(e)[:300])
    return receipt


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path('.'))
    ap.add_argument('--source-only',action='store_true')
    args=ap.parse_args(argv)
    print(json.dumps(check(args.repo/'preparedness',exports=not args.source_only),sort_keys=True))
    return 2


if __name__=='__main__':raise SystemExit(main())
