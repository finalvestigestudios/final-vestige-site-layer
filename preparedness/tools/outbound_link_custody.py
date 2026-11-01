#!/usr/bin/env python3
"""R14 Preparedness Archive: deterministic article hyperlink / provenance custody.

Source bibliography verification (R12) does not account for *ordinary* links
embedded by authors in the article body. They can redirect a reader to an
unreviewed authority without a {{cite:id}} token. Compare original resolved
body anchors to the *actual* rendered reader-body anchors and inventory every
external destination for human source-scope review. No network or CMS access;
no inference that a linked destination is reliable or safe.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

RELEASE_STATE = 'HOLD'
REVIEW = 'PENDING_HUMAN_LINK_AND_CLAIM_REVIEW'
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
BAD = re.compile(r'[\x00-\x20\x7f-\x9f\\\u200b\u200c\u200d\ufeff]')
HEX = re.compile(r'[0-9a-f]{64}\Z')
MAX_HTML_BYTES = 4_000_000
MAX_ANCHORS = 10000
MAX_ITEMS = 36


class LinkCustodyFailure(ValueError):
    """Body/outbound link evidence drifted or contains an unsafe destination."""


def canonical_json(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(o):
    return sha256(canonical_json(o).encode('utf-8')).hexdigest()


def classify_destination(href: str) -> tuple[str, str]:
    """Return classification and host; classification is NOT a safety verdict."""
    if not isinstance(href, str) or not href or len(href) > 4000 or BAD.search(href):
        raise LinkCustodyFailure('empty, control-laden or oversized hyperlink')
    if href != unescape(href):
        raise LinkCustodyFailure('nested HTML entity in hyperlink')
    if href.startswith('//'):
        raise LinkCustodyFailure('scheme-relative hyperlink is forbidden')
    if href.startswith('#'):
        if not re.fullmatch(r'#[A-Za-z][A-Za-z0-9_.:-]{0,127}', href):
            raise LinkCustodyFailure('invalid fragment-only link')
        return 'LOCAL_FRAGMENT', ''
    if href.startswith('/'):
        if href.startswith('//') or '..' in href.split('/') or '#' in href and not re.fullmatch(r'/[a-zA-Z0-9_./-]+#[a-zA-Z0-9_.:-]+', href):
            raise LinkCustodyFailure('unsafe relative path')
        if '%' in href or '?' in href or '<' in href or '>' in href:
            raise LinkCustodyFailure('ambiguous relative path')
        return ('ARCHIVE_INTERNAL' if href.startswith('/preparedness/') else 'SITE_INTERNAL'), ''
    if re.search(r'%(?:0[0-9a-f]|1[0-9a-f]|7f)', href, re.I):
        raise LinkCustodyFailure('URL contains percent-encoded control byte')
    parsed = urlsplit(href)
    if parsed.scheme.lower() not in {'https', 'http'} or not parsed.netloc:
        raise LinkCustodyFailure('unsupported hyperlink scheme or malformed URL')
    if parsed.username is not None or parsed.password is not None or '@' in parsed.netloc:
        raise LinkCustodyFailure('credential-style or deceptive URL authority')
    if parsed.port is not None and (parsed.port <= 0 or parsed.port > 65535):
        raise LinkCustodyFailure('invalid URL port')
    hostname = parsed.hostname or ''
    if (not hostname or not hostname.isascii() or '%' in parsed.netloc or
            any(ch in parsed.netloc for ch in '<>"\'') or
            not re.fullmatch(r'[A-Za-z0-9.-]+', hostname)):
        raise LinkCustodyFailure('ambiguous or non-ASCII URL host')
    if href.split(':', 1)[0] != parsed.scheme:
        raise LinkCustodyFailure('noncanonical URL scheme spelling')
    if hostname.lower() in ('finalvestige.com', 'www.finalvestige.com'):
        return 'SITE_ABSOLUTE', hostname.lower()
    return ('EXTERNAL_HTTPS' if parsed.scheme == 'https' else 'EXTERNAL_HTTP_REVIEW'), hostname.lower()


class LinkParser(HTMLParser):
    """Collect browser-visible anchors and target IDs; optionally limit to #pa-main."""

    def __init__(self, main_only=False):
        super().__init__(convert_charrefs=True)
        self.main_only = main_only
        self.stack: list[tuple[str, bool]] = []
        self.main_depth = 0
        self.main_count = 0
        self.links: list[dict] = []
        self.ids: set[str] = set()
        self.active: dict | None = None
        self.link_depth = 0

    def _inside(self):
        return not self.main_only or self.main_depth > 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = dict(attrs)
        if tag == 'div' and a.get('id') == 'pa-main' and self.main_only:
            if self.main_count:
                raise LinkCustodyFailure('duplicate reader body')
            self.main_count += 1
            self.main_depth = len(self.stack) + 1
        inside = self._inside()
        if len(a) != len(attrs):
            raise LinkCustodyFailure('duplicate HTML attribute on hyperlink candidate')
        if inside:
            dom_id = a.get('id')
            if dom_id:
                if dom_id in self.ids:
                    raise LinkCustodyFailure('duplicate reader-body ID')
                self.ids.add(dom_id)
            if tag == 'a':
                if self.active is not None:
                    raise LinkCustodyFailure('nested hyperlinks')
                href = a.get('href')
                kind, host = classify_destination(href)
                target = (a.get('target') or '').lower()
                rel = set((a.get('rel') or '').lower().split())
                if target == '_blank' and kind.startswith('EXTERNAL') and 'noopener' not in rel:
                    raise LinkCustodyFailure('target=_blank outbound link lacks noopener')
                self.active = {'href': href, 'kind': kind, 'host': host, 'label': '',
                               'aria_label': a.get('aria-label') or '', 'target': target,
                               'rel': sorted(rel)}
                self.link_depth = len(self.stack) + 1
                self.links.append(self.active)
                if len(self.links) > MAX_ANCHORS:
                    raise LinkCustodyFailure('excessive hyperlinks')
            elif tag == 'img' and self.active is not None:
                self.active['label'] += a.get('alt') or ''
        if tag not in VOID:
            self.stack.append((tag, inside))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.active is not None and self._inside():
            self.active['label'] += data

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            raise LinkCustodyFailure('malformed hyperlink or reader HTML nesting')
        depth = len(self.stack)
        if tag == 'a' and self.active is not None and self.link_depth == depth:
            if not ' '.join((self.active['label'] or self.active['aria_label']).split()):
                raise LinkCustodyFailure('hyperlink lacks an accessible label')
            self.active['label'] = ' '.join(self.active['label'].split())
            self.active['aria_label'] = ' '.join(self.active['aria_label'].split())
            self.active = None
            self.link_depth = 0
        if depth == self.main_depth:
            self.main_depth = 0
        self.stack.pop()

    def finish(self):
        if self.stack or self.active is not None:
            raise LinkCustodyFailure('truncated rendered or source HTML')
        if self.main_only and self.main_count != 1:
            raise LinkCustodyFailure('exactly one reader body required')
        for link in self.links:
            if (link['kind'] == 'LOCAL_FRAGMENT' and not re.fullmatch(r'#src-[1-9][0-9]*', link['href'])
                    and link['href'][1:] not in self.ids):
                raise LinkCustodyFailure('reader-body fragment target missing')
        return self


def parse_links(markup: str, *, main_only=False) -> LinkParser:
    if not isinstance(markup, str) or not markup or len(markup.encode('utf-8')) > MAX_HTML_BYTES or '\x00' in markup:
        raise LinkCustodyFailure('missing or oversized reader HTML')
    parser = LinkParser(main_only)
    try:
        parser.feed(markup)
        parser.close()
        return parser.finish()
    except (ValueError, OverflowError, UnicodeError) as exc:
        raise LinkCustodyFailure(f'cannot prove hyperlink parity: {exc}') from exc


def anchor_identity(x):
    return (x['href'], x['label'], x['aria_label'], x['target'], tuple(x['rel']))


def audit_article(lib, renderer, slug: str) -> dict:
    meta = lib.articles.get(slug)
    if (not meta or meta.get('slug') != slug or meta.get('status', {}).get('publish') != 'draft'
            or not isinstance(meta.get('_body'), str)):
        raise LinkCustodyFailure(f'{slug}: non-draft or unrecognized source item')
    raw = meta['_body']
    resolved, order = renderer.resolve_tokens(lib, meta)
    if not isinstance(resolved, str):
        raise LinkCustodyFailure(f'{slug}: unresolved reader source body')
    expected = parse_links(resolved)
    built = renderer.build_article(lib, slug)
    if built.get('meta') is not meta or built.get('slug') != slug or built.get('sources') != order:
        raise LinkCustodyFailure(f'{slug}: render identity drift')
    actual = parse_links(built.get('inner'), main_only=True)
    if list(map(anchor_identity, expected.links)) != list(map(anchor_identity, actual.links)):
        raise LinkCustodyFailure(f'{slug}: source/rendered body hyperlink changed, added, removed or reordered')
    registered_sources = {}
    for sid in order:
        src = lib.source_for(meta, sid)
        if not isinstance(src, dict) or not isinstance(src.get('url'), str):
            raise LinkCustodyFailure(f'{slug}: missing contributor-owned source URL')
        registered_sources.setdefault(src['url'], []).append(sid)
    outgoing = []
    for idx, item in enumerate(actual.links, 1):
        kind = item['kind']
        if kind not in {'EXTERNAL_HTTPS', 'EXTERNAL_HTTP_REVIEW', 'SITE_ABSOLUTE'}:
            continue
        ids = registered_sources.get(item['href'], [])
        row = {'article': slug, 'ordinal': idx, 'href': item['href'], 'host': item['host'],
               'link_kind': kind, 'source_ids_in_article': ids,
               'registered_to_article_sources': bool(ids),
               'status': REVIEW, 'never_equates_link_with_claim_support': True}
        row['link_sha256'] = fingerprint(row)
        outgoing.append(row)
    return {'article': slug, 'draft': True, 'body_sha256': sha256(raw.encode('utf-8')).hexdigest(),
            'rendered_inner_sha256': sha256(built['inner'].encode('utf-8')).hexdigest(),
            'reader_links': len(actual.links), 'outbound_links': len(outgoing),
            'outbound_not_in_article_source_register': sum(not x['registered_to_article_sources'] for x in outgoing),
            'outgoing': outgoing}


def audit_corpus(lib, renderer, *, expected_items=MAX_ITEMS) -> dict:
    if len(lib.articles) != expected_items:
        raise LinkCustodyFailure('35 articles plus one planner inventory drifted')
    rows = [audit_article(lib, renderer, slug) for slug in sorted(lib.articles)]
    report = {'schema_version': 1, 'release_state': RELEASE_STATE, 'may_publish': False,
              'authority': 'MACHINE_STRUCTURE_CHECK_ONLY', 'human_link_checks_verified': 0,
              'link_clicks_or_http_verification_performed': False,
              'advice_safety_verified': False, 'items': len(rows),
              'reader_links': sum(row['reader_links'] for row in rows),
              'outbound_links': sum(row['outbound_links'] for row in rows),
              'outbound_not_in_article_source_register': sum(row['outbound_not_in_article_source_register'] for row in rows),
              'articles': rows}
    report['report_sha256'] = fingerprint(report)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--json-out', type=Path, help='private report inside preparedness/build only')
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build, evidence_freeze, validate, source_review_queue
    import claim_occurrence_audit as r8, claim_corpus_release_gate as r10
    import draft_export_custody as r11, rendered_citation_gate as r12
    import high_consequence_claim_triage as r13
    lib = build.Library(root)
    errors = evidence_freeze.verify(lib)
    if errors:
        raise LinkCustodyFailure('evidence freeze: ' + '; '.join(errors[:4]))
    errors, _ = validate.validate(lib)
    if errors:
        raise LinkCustodyFailure('native validator: ' + '; '.join(errors[:4]))
    physical_rows = source_review_queue.source_rows(root)
    canonical = r10.audit_corpus(lib, physical_rows, evidence_freeze.fingerprint)
    r11.audit_export(lib, root / 'build', build, canonical_receipt=canonical)
    rendered = r12.audit_corpus(lib, build, claim_parser=r8.parse_visible_claims)
    if (rendered.get('release_state') != 'HOLD' or rendered.get('may_publish') is not False or
            rendered.get('rendered_citation_occurrences') != 1959 or rendered.get('article_source_pairs') != 367):
        raise LinkCustodyFailure('R12 citation parity not established')
    # R10 is a compact SHA-256 custody receipt, NOT the full R8 ledger.
    # Re-derive and digest-bind all 1,959 claims before handing them to R13.
    full_claims = r13.bind_full_R8_claim_evidence(
        lib, physical_rows, evidence_freeze.fingerprint, canonical,
        make_report=r8.make_report, baseline=r8.BASELINE)
    triage = r13.build_triage(lib, canonical=full_claims)
    if triage.get('release_state') != 'HOLD' or triage.get('may_publish') is not False:
        raise LinkCustodyFailure('R13 action triage not in HOLD state')
    result = audit_corpus(lib, build)
    if args.json_out:
        r8.safe_export(args.json_out, json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + '\n', root / 'build')
    print(json.dumps({k: v for k, v in result.items() if k != 'articles'}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
