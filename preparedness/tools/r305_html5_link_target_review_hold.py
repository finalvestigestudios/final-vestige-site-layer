#!/usr/bin/env python3
"""R305: fail-closed HTML5/link/fragment integrity review for 35 original articles.

No page publishing, source rewrites, browser claims, medical certification or paid CTA.
An intact native export can still contain HTML with browser-meaning different from
Python's HTMLParser model, invalid anchors or dangerous URL schemes. This read-only
supplement requires the exact R304-repaired inline predecessor and its full chain.
Six interactive tools have independent privacy/JS gates and are not certified here.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

R303 = 'preparedness/tools/r303_inline_semantic_aria_hold.py'
R303_OID = '9e0ee52782011fcb20bdf87179e775ae47e165a9'
CUSTODY = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CONTROL = re.compile(r'[\x00-\x1f\x7f]')
URL_SCHEME = re.compile(r'^([a-zA-Z][a-zA-Z0-9+.-]*):')
SENSITIVE_ATTRS = ('href', 'src', 'action', 'formaction', 'poster', 'cite', 'data', 'xlink:href')
BLOCKED_ELEMENTS = frozenset(('iframe','object','embed','base'))
BAD_PERCENT_ESCAPE = re.compile(r'%(?![a-fA-F0-9]{2})')


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def safe_file(root: Path, relative: str) -> bool:
    try:
        root = root.absolute(); path = (root / relative).absolute()
        if not path.is_relative_to(root) or not path.is_file(): return False
        while path != root:
            if path.is_symlink(): return False
            path = path.parent
        return True
    except (ValueError, OSError, RuntimeError):
        return False


def url_problem(raw: str | None) -> str | None:
    """Structural URL policy, not publisher credibility/rights verification.

    Allow only ordinary same-document anchors, root paths, HTTPS, mailto or tel.
    Reject deceptive whitespace, control characters, JS/data/file/protocol-relative,
    credential URLs and encoded parent-path traversal. An unresolved URL is held.
    """
    if not isinstance(raw, str) or not raw:
        return 'EMPTY_OR_VALUELESS_URL'
    if CONTROL.search(raw) or raw != raw.strip() or '\\' in raw:
        return 'AMBIGUOUS_URL_ENCODING'
    if raw.startswith('//'):
        return 'PROTOCOL_RELATIVE_URL'
    if raw.startswith('#'):
        return None if len(raw) > 1 else 'EMPTY_FRAGMENT'
    if raw.startswith('/'):
        segments = [unquote(p).lower() for p in raw.split('?',1)[0].split('#',1)[0].split('/')]
        return 'RELATIVE_PATH_TRAVERSAL' if any(s in ('.','..') or '/' in s or '\\' in s for s in segments) else None
    match = URL_SCHEME.match(raw)
    if match is None:
        return 'UNSCOPED_RELATIVE_URL'
    scheme = match.group(1).lower()
    if scheme in ('mailto','tel'):
        return None if raw[len(match.group(0)):].strip() else 'EMPTY_CONTACT_TARGET'
    if scheme != 'https':
        return 'UNAPPROVED_URL_SCHEME'
    try:
        parsed = urlsplit(raw)
        if (not parsed.hostname or parsed.username is not None or parsed.password is not None
            or parsed.port not in (None, 443)):
            return 'HTTPS_HOST_USERINFO_OR_PORT_INVALID'
    except ValueError:
        return 'MALFORMED_HTTPS_URL'
    return None



def decode_same_document_fragment(fragment: str) -> tuple[str | None, str | None]:
    """Resolve URI-encoded #fragments to literal HTML IDs without guessing.

    HTMLParser decodes HTML entities in the attribute. Browser navigation
    percent-decodes UTF-8 in a URI fragment; HTML ids are NOT URL-decoded.
    Invalid or control-character encodings remain an explicit review hold.
    """
    if not isinstance(fragment, str) or not fragment:
        return None, 'EMPTY_FRAGMENT'
    if BAD_PERCENT_ESCAPE.search(fragment):
        return None, 'INVALID_PERCENT_ENCODED_FRAGMENT'
    try:
        decoded = unquote(fragment, encoding='utf-8', errors='strict')
    except (UnicodeError, ValueError):
        return None, 'INVALID_UTF8_FRAGMENT'
    if not decoded or CONTROL.search(decoded):
        return None, 'UNSAFE_DECODED_FRAGMENT'
    return decoded, None


class ReadOnlyMarkupAudit(HTMLParser):
    """Reject browser-unsafe links or broken in-page targets without changing HTML."""
    def __init__(self, mode: str):
        super().__init__(convert_charrefs=True)
        if mode not in ('source','export'): raise ValueError('BAD_SCAN_MODE')
        self.mode = mode
        self.errors: list[str] = []
        self.ids: set[str] = set()
        self.fragments: list[tuple[str, str]] = []
        self.resolved_fragments: list[str] = []
        self.links: list[str] = []
        self.tags = 0

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        names = [k for k,_ in attrs]
        if len(names) != len(set(names)):
            self.errors.append('DUPLICATE_HTML_ATTRIBUTE:' + tag)
        if tag in BLOCKED_ELEMENTS:
            self.errors.append('UNREVIEWED_ACTIVE_EMBED:' + tag)
        if self.mode == 'source' and tag in ('script','form'):
            self.errors.append('ACTIVE_ELEMENT_IN_AUTHORED_ARTICLE:' + tag)
        for k,v in attrs:
            if k.startswith('on') and len(k) > 2:
                self.errors.append('UNREVIEWED_INLINE_EVENT_HANDLER:' + tag + ':' + k)
            if k == 'id':
                if not isinstance(v,str) or not v.strip():
                    self.errors.append('EMPTY_HTML_ID')
                elif v in self.ids:
                    self.errors.append('DUPLICATE_HTML_ID:' + v)
                else:
                    self.ids.add(v)
            if k in SENSITIVE_ATTRS:
                problem = url_problem(v)
                if problem: self.errors.append(problem + ':' + tag + ':' + k)
                elif k in ('href','xlink:href') and v.startswith('#'):
                    target, issue = decode_same_document_fragment(v[1:])
                    if issue:
                        self.errors.append(issue + ':' + tag + ':' + k)
                    else:
                        # HTML selects a literal matching ID first; decoded is fallback.
                        self.fragments.append((v[1:], target))
                if k in ('href','xlink:href') and isinstance(v,str):
                    self.links.append(v)
            elif k == 'srcset':
                # A srcset is a URL-and-descriptor list; reject any unsafe member.
                # Data URLs (containing commas) are intentionally held, not parsed.
                if not isinstance(v,str) or not v.strip():
                    self.errors.append('EMPTY_SRCSET')
                else:
                    for token in v.split(','):
                        bits = token.strip().split()
                        problem = url_problem(bits[0]) if bits else 'EMPTY_OR_VALUELESS_URL'
                        if problem:self.errors.append(problem + ':' + tag + ':srcset')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def finish(self):
        for raw, decoded in self.fragments:
            # Browser fragment navigation tries the raw fragment ID before the
            # UTF-8 percent-decoded variant. The decoded form is not equivalent
            # when both IDs exist. Keep strict malformed/control policy upstream.
            if raw in self.ids:
                self.resolved_fragments.append(raw)
            elif decoded in self.ids:
                self.resolved_fragments.append(decoded)
            else:
                self.errors.append('MISSING_SAME_DOCUMENT_TARGET:' + decoded)
        return sorted(set(self.errors))


def scan(html: str, mode: str) -> tuple[list[str], dict]:
    parser = ReadOnlyMarkupAudit(mode)
    parser.feed(html)
    errors = parser.finish()
    return errors, {'tag_count':parser.tags,'link_count':len(parser.links),
                    'unique_ids':len(parser.ids),'in_page_links':len(parser.fragments),
                    'resolved_fragment_ids':list(parser.resolved_fragments)}


def audit(root: Path, custody: dict, previous: dict | None = None) -> dict:
    errors=[];matched=0;matrix=[]
    rows = custody.get('articles') if isinstance(custody,dict) else None
    if not isinstance(rows,list) or len(rows)!=35:
        errors.append('35_ARTICLE_CUSTODY_INVALID');rows=[]
    if previous is not None and (
        not isinstance(previous,dict) or previous.get('state')!='DRAFT_HARD_HOLD'
        or previous.get('errors') != [] or previous.get('article_inline_semantic_matches') != 35
        or previous.get('publication_authorized') is not False
        or previous.get('independent_qd_pass') is not False
        or previous.get('medical_safety_verified') is not False
        or previous.get('privacy_verified') is not False
        or previous.get('all_41_exports_independently_approved') is not False
    ):
        errors.append('R304_UPSTREAM_NOT_RECONCILED')
    slugs=set()
    for row in rows:
        slug=row.get('slug') if isinstance(row,dict) else None
        if not isinstance(slug,str) or not SLUG.fullmatch(slug):
            errors.append('INVALID_CUSTODY_SLUG');continue
        if slug in slugs:errors.append('DUPLICATE_CUSTODY_SLUG:'+slug);continue
        slugs.add(slug)
        inp='preparedness/content/articles/'+slug+'.body.html'
        out='preparedness/build/wp/'+slug+'.html'
        if not safe_file(root,inp): errors.append('SOURCE_MISSING_OR_SYMLINK:'+slug);continue
        if not safe_file(root,out): errors.append('DRAFT_MISSING_OR_SYMLINK:'+slug);continue
        try:
            a,am=scan((root/inp).read_text('utf-8'),'source')
            b,bm=scan((root/out).read_text('utf-8'),'export')
            errors.extend(x+':source:'+slug for x in a)
            errors.extend(x+':draft:'+slug for x in b)
            matrix.append({'slug':slug,'source':am,'draft':bm,
                'static_integrity_state':'REVIEW_ONLY_HOLD' if not a and not b else 'INVALID_HARD_HOLD'})
            if not a and not b:matched+=1
        except (UnicodeError,OSError,ValueError,RuntimeError) as exc:
            errors.append('ARTICLE_UNREADABLE:'+slug+':'+type(exc).__name__)
    if len(slugs)!=35:errors.append('INCOMPLETE_CUSTODY_SLATES')
    return {'schema':'fv-preparedness-r305-browser-url-fragment-static-gate-v1',
            'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)), 'article_link_target_checks':matched,
            'source_and_draft_inspection':matrix,
            'upstream_r304_required':True,'browser_executed':False,
            'links_currently_resolve_verified':False,
            'source_claim_support_approved':False,'independent_safety_review_approved':False,
            'all_41_exports_independently_approved':False,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_verified':False,
            'merchant_approved':False,'confirmed_paid_orders':None,
            'realized_net_revenue_per_1000_qualified_sessions':None}


def run(root: Path) -> dict:
    for relative,want in ((R303,R303_OID),(CUSTODY,CUSTODY_OID)):
        if not safe_file(root,relative) or blob((root/relative).read_bytes())!=want:
            raise ValueError('PINNED_UPSTREAM_FILE_UNAVAILABLE_OR_CHANGED:'+relative)
    spec=importlib.util.spec_from_file_location('fv_r305_pinned_r304',root/R303)
    if spec is None or spec.loader is None:raise RuntimeError('UPSTREAM_IMPORT_UNAVAILABLE')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    prior=mod.run(root)
    custody=json.loads((root/CUSTODY).read_bytes())
    return audit(root,custody,prior)


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args(argv)
    try:r=run(args.repo_root)
    except (OSError,ValueError,RuntimeError,UnicodeError,KeyError,TypeError,ImportError) as exc:
        r={'schema':'fv-preparedness-r305-browser-url-fragment-static-gate-v1',
           'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_BUILD_UNAVAILABLE:'+type(exc).__name__],
           'publication_authorized':False,'independent_qd_pass':False,
           'medical_safety_verified':False,'privacy_verified':False,
           'all_41_exports_independently_approved':False}
    print(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False))
    return 2 if r['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
