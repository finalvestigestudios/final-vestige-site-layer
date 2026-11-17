#!/usr/bin/env python3
"""R439 offline, read-only custody of the CSS asset bytes behind Preparedness exports.

No network, CMS writes, merchant requests, or claim/safety/QD/publication approval.
An exact offline hash proves bytes, not trusted authorship or computed browser safety.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urljoin, urlsplit

MAX_HTML = 1_000_000
MAX_CSS = 200_000
MAX_CSS_NODES = 64
MAX_DEPTH = 12
MAX_JSON = 300_000
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
IMPORT_MARK = re.compile(r"@\s*import\b", re.I)
IMPORT_REF = re.compile(r"@\s*import\s+(?:url\(\s*(['\"]?)([^'\"\s)]+)\1\s*\)|(['\"])(.*?)\3)", re.I | re.S)
URL_MARK = re.compile(r"\burl\s*\(", re.I)
SRI_TOKEN = re.compile(r"(sha256|sha384|sha512)-([A-Za-z0-9+/]+={0,2})\Z")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def scrub_comments(css):
    if css.count('/*') != css.count('*/'):
        raise ValueError('CSS_UNBALANCED_COMMENTS')
    return re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)


def canonical(raw, parent='https://finalvestige.com/preparedness/'):
    if not isinstance(raw, str) or not raw or len(raw) > 2048:
        raise ValueError('CSS_UNSAFE_ASSET_REFERENCE')
    if any(ord(c) <= 32 or ord(c) >= 127 for c in raw) or any(c in raw for c in '\\%?#'):
        raise ValueError('CSS_UNSAFE_ASSET_REFERENCE')
    if raw.startswith('//') or any(part in ('.', '..') for part in urlsplit(raw).path.split('/')):
        raise ValueError('CSS_UNSAFE_ASSET_REFERENCE')
    parsed = urlsplit(urljoin(parent, raw))
    if parsed.scheme != 'https' or parsed.hostname != 'finalvestige.com' or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('CSS_UNTRUSTED_ORIGIN')
    if parsed.query or parsed.fragment or not parsed.path.startswith('/') or '//' in parsed.path:
        raise ValueError('CSS_UNSAFE_ASSET_REFERENCE')
    return 'https://finalvestige.com' + parsed.path


class CSSRefs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.inline = []
        self.active = None
        self.errors = []
    def handle_starttag(self, tag, attrs):
        keys = [a.lower() for a, _ in attrs]
        if len(set(keys)) != len(keys):
            self.errors.append('CSS_DUPLICATE_HTML_ATTRIBUTE')
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'link':
            rel = a.get('rel', '').lower().split()
            if 'stylesheet' in rel or ('preload' in rel and a.get('as', '').lower() == 'style'):
                self.links.append({'href': a.get('href', ''), 'integrity': a.get('integrity', ''), 'media': a.get('media', ''), 'rel': sorted(rel)})
        if tag == 'style':
            if self.active is not None:
                self.errors.append('CSS_NESTED_STYLE')
            self.active = []
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == 'style': self.handle_endtag(tag)
    def handle_data(self, data):
        if self.active is not None: self.active.append(data)
    def handle_endtag(self, tag):
        if tag == 'style' and self.active is not None:
            self.inline.append(''.join(self.active))
            self.active = None
    def summary(self):
        if self.active is not None: self.errors.append('CSS_UNCLOSED_STYLE')
        return self


def extract(html):
    if not isinstance(html, bytes) or not 12 <= len(html) <= MAX_HTML or b'\x00' in html:
        raise ValueError('INVALID_EXPORT_HTML_BYTES')
    p = CSSRefs()
    p.feed(html.decode('utf-8', 'strict'))
    p.close()
    return p.summary()


def check_sri(integrity, raw):
    if not isinstance(integrity, str):
        raise ValueError('CSS_INVALID_SRI')
    if not integrity:
        return ['CSS_SRI_NOT_RECORDED_REVIEW']
    tokens = integrity.split()
    if not tokens: return ['CSS_INVALID_SRI']
    errors = []
    for token in tokens:
        m = SRI_TOKEN.fullmatch(token)
        if not m:
            errors.append('CSS_INVALID_SRI')
            continue
        algo, expected = m.groups()
        try:
            decoded = base64.b64decode(expected, validate=True)
        except ValueError:
            errors.append('CSS_INVALID_SRI')
            continue
        actual = hashlib.new(algo, raw).digest()
        if actual != decoded:
            errors.append('CSS_SRI_MISMATCH')
    return sorted(set(errors))


def verify_asset(url, assets, pins):
    record = pins.get(url)
    body = assets.get(url)
    errors = []
    if not isinstance(record, dict): errors.append('CSS_PIN_MISSING')
    if not isinstance(body, bytes): errors.append('CSS_ASSET_BYTES_MISSING')
    if errors: return None, errors
    if len(body) > MAX_CSS or not body or b'\x00' in body:
        return None, ['CSS_ASSET_SIZE_OR_NUL']
    if set(record) != {'sha256', 'bytes', 'mime', 'capture_id'} or record.get('mime') != 'text/css' or not isinstance(record.get('capture_id'), str) or not record['capture_id'].strip():
        errors.append('CSS_PIN_SCHEMA_INVALID')
    if not isinstance(record.get('sha256'), str) or not HEX64.fullmatch(record['sha256']):
        errors.append('CSS_PIN_HASH_INVALID')
    if type(record.get('bytes')) is not int or record['bytes'] != len(body):
        errors.append('CSS_PIN_LENGTH_MISMATCH')
    if record.get('sha256') != sha(body):
        errors.append('CSS_PIN_HASH_MISMATCH')
    try: css = body.decode('utf-8', 'strict')
    except UnicodeError:
        errors.append('CSS_INVALID_UTF8'); css = None
    return css, sorted(set(errors))


def graph(html, assets, pins):
    """Return deterministic CSS URL+byte graph and flagged review conditions, never a safety pass."""
    parsed = extract(html)
    errors = list(parsed.errors)
    edges = []
    content = []
    visited = set()
    in_progress = set()

    def walk(url, depth):
        if depth > MAX_DEPTH:
            errors.append('CSS_DEPENDENCY_DEPTH_LIMIT'); return
        if url in in_progress:
            errors.append('CSS_IMPORT_CYCLE'); return
        if url in visited: return
        if len(visited) >= MAX_CSS_NODES:
            errors.append('CSS_DEPENDENCY_NODE_LIMIT'); return
        visited.add(url)
        css, errs = verify_asset(url, assets, pins)
        errors.extend(url + ':' + e for e in errs)
        if css is None: return
        content.append((url, sha(assets[url]), len(assets[url])))
        in_progress.add(url)
        imports(css, url, depth)
        in_progress.remove(url)

    def imports(css, parent, depth):
        try: cleaned = scrub_comments(css)
        except ValueError:
            errors.append('CSS_UNBALANCED_COMMENT:'+parent); return
        if re.search(r'\\(?:[a-fA-F0-9]{1,6}\s?|[^\r\n])', cleaned):
            errors.append('CSS_ESCAPE_REQUIRES_BROWSER_REVIEW:'+parent)
        refs = list(IMPORT_REF.finditer(cleaned))
        marks = len(IMPORT_MARK.findall(cleaned))
        if len(refs) != marks:
            errors.append('CSS_UNPARSEABLE_IMPORT:'+parent)
        if URL_MARK.search(IMPORT_REF.sub('', cleaned)):
            errors.append('CSS_NONIMPORT_URL_REQUIRES_BROWSER_REVIEW:'+parent)
        for m in refs:
            raw = m.group(2) if m.group(2) is not None else m.group(4)
            try: child = canonical(raw, parent)
            except ValueError as exc:
                errors.append(str(exc)+':'+parent); continue
            edges.append((parent, child))
            walk(child, depth + 1)

    for link in parsed.links:
        try: target = canonical(link['href'])
        except ValueError as exc:
            errors.append(str(exc)); continue
        edges.append(('html:'+','.join(link['rel'])+':'+link['media'], target))
        walk(target, 0)
        if isinstance(assets.get(target), bytes):
            errors.extend(target+':'+e for e in check_sri(link['integrity'], assets[target]))
    for i, css in enumerate(parsed.inline):
        content.append(('inline:'+str(i), sha(css.encode()), len(css.encode())))
        imports(css, 'https://finalvestige.com/preparedness/', 0)
    unknown = (set(assets) | set(pins)) - visited
    if unknown: errors.append('CSS_SURPLUS_UNREFERENCED_ASSET_OR_PIN')
    result = {'css_graph_sha256':digest({'edges':edges, 'content':sorted(content)}),
              'dependency_count':len(visited), 'sha256_by_asset':sorted(content),
              'edges':edges, 'errors':sorted(set(errors)), 'human_browser_and_provenance_review_required':True}
    return result


def pair_review(wp, preview, assets, pins):
    a = graph(wp, assets, pins)
    b = graph(preview, assets, pins)
    errors = ['wordpress:'+x for x in a['errors']] + ['preview:'+x for x in b['errors']]
    if a['css_graph_sha256'] != b['css_graph_sha256']:
        errors.append('WP_PREVIEW_CSS_BYTE_GRAPH_DRIFT')
    return {'errors':sorted(set(errors)), 'wordpress':a, 'preview':b,
            'release_state':'DRAFT_HARD_HOLD', 'eligible':False,
            'qualified_safety_approved':False, 'publication_approved':False,
            'paid_offer_approved':False}


def load_parent():
    path = Path(__file__).with_name('r438_css_dependency_custody_gate.py')
    if not path.is_file(): raise ValueError('R438_PARENT_MISSING')
    spec = importlib.util.spec_from_file_location('r438_css_dependency_custody_gate', path)
    if spec is None or spec.loader is None: raise ValueError('R438_PARENT_UNLOADABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hold(errors, parent=None, rows=()):
    prior = parent if isinstance(parent, dict) else {}
    return {'schema':1, 'issue':136, 'business_issue':820,
            'release_state':'DRAFT_HARD_HOLD', 'eligible':False,
            'publication_approved':False, 'qualified_safety_approved':False,
            'paid_offer_approved':False, 'merchant_confirmed_orders':None,
            'net_revenue_per_1000_qualified_human_sessions':None,
            'errors':sorted(set(errors + list(prior.get('errors', [])))),
            'asset_byte_custody_review_rows':list(rows), 'review_only_digest':digest(rows),
            'original_sources_validated':False, 'browser_computed_styles_verified':False}


def audit(manifest, exports, lock, assets, pins, *, test_only=False):
    try: parent = load_parent().audit(manifest, exports, lock, test_only=test_only)
    except (OSError, ValueError, TypeError, ImportError, AttributeError):
        return hold(['PARENT_R438_AUDIT_UNAVAILABLE'])
    if not isinstance(manifest, dict) or not isinstance(manifest.get('articles'), list) or not isinstance(exports, dict) or not isinstance(assets, dict) or not isinstance(pins, dict):
        return hold(['AUTHENTIC_EVIDENCE_MISSING'], parent)
    errs, rows, seen = [], [], set()
    for article in manifest['articles']:
        slug = article.get('slug') if isinstance(article, dict) else None
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in seen:
            errs.append('INVALID_OR_DUPLICATE_ARTICLE_IDENTITY'); continue
        seen.add(slug)
        pair = exports.get(slug)
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            errs.append('MISSING_ARTICLE_EXPORT_PAIR:'+slug); continue
        try:
            review = pair_review(pair[0], pair[1], assets, pins)
            errs.extend(slug+':'+e for e in review['errors'])
            rows.append({'slug':slug, 'css_graph_wp':review['wordpress']['css_graph_sha256'],
                         'css_graph_preview':review['preview']['css_graph_sha256'],
                         'css_dependency_count':review['wordpress']['dependency_count']})
        except (ValueError, UnicodeError, TypeError, OverflowError):
            errs.append('INVALID_EXPORT_OR_ASSET_BYTES:'+slug)
    if set(exports) != seen: errs.append('EXPORT_SLUG_SET_MISMATCH')
    if not test_only and len(rows) != 35: errs.append('INCOMPLETE_ORIGINAL_SLATE')
    return hold(errs, parent, sorted(rows, key=lambda x:x['slug']))


def read_safe(root, relative, limit):
    root = Path(root).resolve(strict=True)
    if not isinstance(relative, str) or not relative or '\\' in relative or relative.startswith('/') or any(part in ('', '.', '..') for part in relative.split('/')):
        raise ValueError('UNSAFE_LOCAL_ASSET_PATH')
    target = root / relative
    if not target.resolve(strict=True).is_relative_to(root): raise ValueError('LOCAL_ASSET_ESCAPE')
    fd = os.open(target, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        pre = os.fstat(fd)
        if not stat.S_ISREG(pre.st_mode) or pre.st_nlink != 1 or pre.st_size > limit or pre.st_size <= 0:
            raise ValueError('LOCAL_ASSET_NOT_REGULAR_OR_OVERSIZED')
        data = os.read(fd, limit + 1)
        post = os.fstat(fd)
        if len(data) != pre.st_size or (pre.st_ino, pre.st_dev, pre.st_size, pre.st_mtime_ns) != (post.st_ino, post.st_dev, post.st_size, post.st_mtime_ns):
            raise ValueError('LOCAL_ASSET_CHANGED_DURING_READ')
        return data
    finally: os.close(fd)


def main(argv=None):
    ap = argparse.ArgumentParser(description='R439 read-only offline stylesheet byte custody, always hard hold')
    for n in ('manifest', 'lock', 'exports', 'css_manifest', 'css_dir'): ap.add_argument(n, type=Path)
    args = ap.parse_args(argv)
    try:
        manifest = json.loads(read_safe(args.manifest.parent, args.manifest.name, MAX_JSON))
        lock = json.loads(read_safe(args.lock.parent, args.lock.name, MAX_JSON))
        asset_manifest = json.loads(read_safe(args.css_manifest.parent, args.css_manifest.name, MAX_JSON))
        if not isinstance(asset_manifest, dict) or asset_manifest.get('schema') != 1 or not isinstance(asset_manifest.get('assets'), list):
            raise ValueError('INVALID_CSS_PIN_MANIFEST')
        assets, pins = {}, {}
        for row in asset_manifest['assets']:
            if not isinstance(row, dict) or set(row) != {'url','path','sha256','bytes','mime','capture_id'}:
                raise ValueError('INVALID_CSS_PIN_RECORD')
            key = canonical(row['url'])
            if key in pins: raise ValueError('DUPLICATE_CSS_URL_PIN')
            pins[key] = {k:row[k] for k in ('sha256','bytes','mime','capture_id')}
            assets[key] = read_safe(args.css_dir, row['path'], MAX_CSS)
        exports = {}
        if not isinstance(manifest, dict) or not isinstance(manifest.get('articles'), list): raise ValueError('INVALID_ARTICLE_MANIFEST')
        for item in manifest['articles']:
            slug = item['slug']
            if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in exports: raise ValueError('UNSAFE_ARTICLE_SLUG')
            exports[slug] = tuple(read_safe(args.exports/ch, slug+'.html', MAX_HTML) for ch in ('wordpress','preview'))
        report = audit(manifest, exports, lock, assets, pins)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, ImportError, OverflowError, json.JSONDecodeError):
        report = hold(['AUTHENTIC_OFFLINE_CSS_AND_EXPORT_EVIDENCE_MISSING'])
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
