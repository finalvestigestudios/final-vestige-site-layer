#!/usr/bin/env python3
"""R255: authenticate and escape a human-review-only view of R254 source workorders.

Never calls external URLs, judges claim support, writes WordPress, or grants approval.
The optional CLI writes a local offline HTML review copy ONLY after a strict audit.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import html
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r255-offline-source-review-surface-v1'
UPSTREAM = 'fv-preparedness-r254-readable-claim-workorders-v1'
HOLD = 'DRAFT_HARD_HOLD'
PENDING = 'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW'
SHA = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HELD = {(7, 30, 'cdc-find-clean-water'), (7, 48, 'cdc-find-clean-water'),
        (20, 55, 'start-ready-plan')}
FALSE = ('independent_claim_source_verified', 'independent_qd_pass',
         'medical_safety_verified', 'merchant_approved', 'publication_authorized')


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError('R255 DRAFT HARD HOLD: ' + message)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def is_hash(value: object) -> bool:
    return type(value) is str and SHA.fullmatch(value) is not None


def source_url_annotations(url: str) -> tuple[tuple[str, ...], str]:
    """Identify review questions; never merge, rewrite or approve source URLs."""
    require(type(url) is str and len(url) <= 2048 and not any(
        ord(c) < 33 or ord(c) == 127 or c == '\\' for c in url), 'unsafe URL characters')
    try:
        parts = urlsplit(url)
        host = parts.hostname
        port = parts.port  # Force validation, including malformed ports.
    except ValueError as e:
        raise ValueError('R255 DRAFT HARD HOLD: malformed source URL') from e
    require(parts.scheme in ('http', 'https') and bool(host)
            and not parts.username and not parts.password
            and not parts.netloc.endswith('@'), 'source URL scheme/host/credentials')
    # This is a triage key, NOT a canonical-source equivalence decision.
    alias_key = (parts.scheme.lower(), host.lower(), port,
                 parts.path.rstrip('/') or '/', parts.query, parts.fragment)
    labels = []
    if parts.scheme != 'https':
        labels.append('non_https_review')
    if parts.query:
        labels.append('query_scope_review')
    if parts.fragment:
        labels.append('fragment_scope_review')
    if host.startswith('xn--') or '.xn--' in host or not host.isascii():
        labels.append('idn_host_review')
    try:
        ipaddress.ip_address(host.strip('[]'))
        labels.append('ip_host_review')
    except ValueError:
        pass
    return tuple(labels), repr(alias_key)


def checked(receipt: dict) -> tuple[list[dict], dict]:
    require(type(receipt) is dict and receipt.get('schema') == UPSTREAM
            and receipt.get('state') == HOLD, 'authenticated R254 receipt required')
    recorded_sha = receipt.get('receipt_sha256')
    require(is_hash(recorded_sha) and recorded_sha == digest(canonical({
        k: v for k, v in receipt.items() if k != 'receipt_sha256'})),
        'R254 receipt checksum mismatch')
    for key, expected in [('source_review_groups', 32), ('shared_source_ids', 56),
                          ('article_count', 35), ('citation_count', 2000),
                          ('human_readable_workorders', 562),
                          ('other_citation_occurrences_still_unreviewed', 1438),
                          ('disputed_original_claims', 3)]:
        require(type(receipt.get(key)) is int and receipt[key] == expected,
                'R254 frozen count drift: ' + key)
    for key in FALSE:
        require(receipt.get(key) is False, 'unapproved release flag: ' + key)
    require(receipt.get('shared_disputed_claims') == 1
            and receipt.get('outside_shared_disputed_claims') == 2,
            'original disputed citation membership drift')
    external = receipt.get('outside_shared_disputed_workorders')
    require(type(external) is list and len(external) == 2,
            'outside-shared original citation holds lost')
    groups = receipt.get('review_queue')
    require(type(groups) is list and len(groups) == 32, 'lost shared-source groups')
    seen_url, all_ids, points, disputes = set(), set(), set(), set()
    source_labels, aliases = Counter(), defaultdict(list)
    view = []
    for group in groups:
        require(type(group) is dict, 'source group malformed')
        url = group.get('source_url')
        labels, alias = source_url_annotations(url)
        require(url not in seen_url, 'duplicate exact source URL')
        seen_url.add(url)
        aliases[alias].append(url)
        source_labels.update(labels)
        ids, rows = group.get('source_ids'), group.get('workorders')
        require(type(ids) is list and bool(ids) and all(
            type(s) is str and SLUG.fullmatch(s) for s in ids)
            and len(ids) == len(set(ids)) and not (set(ids) & all_ids),
            'missing, repeated or reassigned source ID')
        all_ids.update(ids)
        require(type(rows) is list and type(group.get('workorder_count')) is int
                and len(rows) == group['workorder_count'], 'lost source workorders')
        require(group.get('state') == PENDING and
                group.get('source_scope_approved') is False and
                group.get('claim_support_approved') is False,
                'source approval was not independently granted')
        require(is_hash(group.get('source_evidence_sha256')),
                'group source evidence checksum missing')
        require(type(group.get('priority')) is str and len(group['priority']) <= 100,
                'priority classification malformed')
        for row in rows:
            require(type(row) is dict and type(row.get('article_n')) is int
                    and 1 <= row['article_n'] <= 35
                    and type(row.get('citation_ordinal')) is int
                    and row['citation_ordinal'] > 0
                    and type(row.get('article_slug')) is str
                    and SLUG.fullmatch(row['article_slug'])
                    and row.get('source_id') in ids,
                    'foreign/invalid citation workorder')
            key = row['article_n'], row['citation_ordinal'], row['source_id']
            point = key[:2]
            require(point not in points, 'citation assigned to multiple groups')
            points.add(point)
            excerpt = row.get('authored_context_excerpt')
            require(type(excerpt) is str and 6 <= len(excerpt) <= 1000
                    and row.get('context_sha256') == digest(excerpt)
                    and is_hash(row.get('author_source_use_note_sha256')),
                    'authored evidence excerpt/checksum changed')
            terms = row.get('review_terms')
            require(type(terms) is list and all(type(v) is str
                    and len(v) <= 100 for v in terms) and terms == sorted(set(terms)),
                    'review-term parity drift')
            require(row.get('source_support_verified') is False
                    and row.get('safety_approved') is False
                    and row.get('disputed_original_citation') is (key in HELD),
                    'citation unexpectedly approved or original dispute concealed')
            if key in HELD:
                disputes.add(key)
        require(rows == sorted(rows, key=lambda x: (x['article_n'], x['citation_ordinal'])),
                'citation workorders reordered')
        view.append({'source_url': url, 'labels': labels, 'workorders': rows})
    external_keys = set()
    for row in external:
        require(type(row) is dict, 'outside-shared disputed claim malformed')
        key = row.get('article_n'), row.get('citation_ordinal'), row.get('source_id')
        require(key in HELD and key not in external_keys
                and key[:2] not in points and key[2] not in all_ids,
                'outside-shared disputed claim lost, repeated or assigned to shared group')
        external_keys.add(key)
        excerpt = row.get('authored_context_excerpt')
        require(type(row.get('article_slug')) is str
                and SLUG.fullmatch(row['article_slug'])
                and type(excerpt) is str and 6 <= len(excerpt) <= 1000
                and row.get('context_sha256') == digest(excerpt)
                and is_hash(row.get('author_source_use_note_sha256')),
                'outside-shared original source witness mismatch')
        terms = row.get('review_terms')
        require(type(terms) is list and terms == sorted(set(terms))
                and all(type(t) is str and len(t) <= 100 for t in terms),
                'outside-shared risk review terms malformed')
        require(row.get('disputed_original_citation') is True
                and row.get('source_support_verified') is False
                and row.get('safety_approved') is False,
                'outside-shared original dispute falsely approved')
    require(external == sorted(external, key=lambda x: (x['article_n'], x['citation_ordinal']))
            and len(seen_url) == 32 and len(all_ids) == 56 and len(points) == 562
            and disputes == {(20, 55, 'start-ready-plan')}
            and external_keys == {(7, 30, 'cdc-find-clean-water'),
                                  (7, 48, 'cdc-find-clean-water')}
            and disputes | external_keys == HELD,
            'frozen 32/56/562 plus two outside-shared held citations drift')
    require([x['source_url'] for x in view] == sorted(seen_url),
            'nondeterministic source URL review order')
    possible_aliases = sum(len(values) - 1 for values in aliases.values() if len(values) > 1)
    facts = {'state': HOLD, 'schema': SCHEMA, 'article_count': 35,
             'source_review_groups': 32, 'review_workorders': 562,
             'unmatched_citations_unreviewed': 1438,
             'original_disputes_visible': 3,
             'shared_disputes_visible': 1, 'outside_shared_disputes_visible': 2,
             'source_url_triage_labels': dict(sorted(source_labels.items())),
             'potential_url_alias_pairs_to_review': possible_aliases,
             'source_support_verified': False, 'independent_qd_pass': False,
             'medical_safety_verified': False, 'merchant_approved': False,
             'publication_authorized': False}
    return view, facts


def render_offline_review(receipt: dict) -> str:
    """Offline, inert, escaped HTML for a human editor; NEVER a live page."""
    groups, _ = checked(receipt)
    esc = lambda text: html.escape(str(text), quote=True)
    chunks = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
              '<meta name="robots" content="noindex,nofollow,noarchive">',
              '<meta http-equiv="Content-Security-Policy" '
              'content="default-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">',
              '<title>R255 UNAPPROVED source review only</title></head><body>',
              '<h1>R255 DRAFT / HARD HOLD — human claim/source review only</h1>',
              '<p>562 authored contexts are unverified. 1,438 other citations remain unreviewed. '
              'No medical, source, QD, product, or publication clearance. '
              'Do not copy this offline document into WordPress.</p>']
    for index, group in enumerate(groups, 1):
        chunks.append('<section><h2>Source group ' + str(index) + '</h2><p>Source URL, '
                      'plain text only: <code>' + esc(group['source_url']) + '</code></p>')
        if group['labels']:
            chunks.append('<p>URL review flags: ' + esc(', '.join(group['labels'])) + '</p>')
        for row in group['workorders']:
            chunks.append('<article><h3>Article ' + str(row['article_n']) + ' — ' +
                          esc(row['article_slug']) + ' — citation ' +
                          str(row['citation_ordinal']) + '</h3><p>Source ID: ' +
                          esc(row['source_id']) + '</p><pre>' +
                          esc(row['authored_context_excerpt']) + '</pre><p>Review terms: ' +
                          esc(', '.join(row['review_terms']) or 'not classified') +
                          '</p><p>UNVERIFIED / HARD HOLD' +
                          (' — original disputed occurrence' if row['disputed_original_citation']
                           else '') + '</p></article>')
        chunks.append('</section>')
    chunks.append('<section><h2>Original disputed citations outside the 32 shared-source groups</h2>')
    for row in receipt['outside_shared_disputed_workorders']:
        chunks.append('<article><h3>Article ' + str(row['article_n']) + ' — ' +
                      esc(row['article_slug']) + ' — citation ' +
                      str(row['citation_ordinal']) + '</h3><p>Original source ID: ' +
                      esc(row['source_id']) +
                      ' (NOT in shared URL review groups)</p><pre>' +
                      esc(row['authored_context_excerpt']) +
                      '</pre><p>HARD HOLD — original disputed citation; '
                      'independent source and safety review required.</p></article>')
    chunks.append('</section></body></html>')
    return '\n'.join(chunks) + '\n'


def audit_offline_review(receipt: dict) -> dict:
    _, facts = checked(receipt)
    document = render_offline_review(receipt)
    require(document.count('<article>') == 564 and document.count('<section>') == 33
            and '<a ' not in document and '<script' not in document
            and '<form' not in document, 'offline review surface exposure drift')
    facts['offline_review_sha256'] = digest(document)
    facts['offline_review_utf8_bytes'] = len(document.encode('utf-8'))
    facts['receipt_sha256'] = digest(canonical(facts))
    return facts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path,
                        help='local R254 JSON review receipt (already authenticated by R220)')
    parser.add_argument('--offline-html', type=Path,
                        help='optional local-only inert HTML, never WordPress output')
    args = parser.parse_args()
    receipt = json.loads(args.input.read_text(encoding='utf-8'))
    result = audit_offline_review(receipt)
    if args.offline_html is not None:
        require(not args.offline_html.is_symlink() and not args.offline_html.exists(),
                'must not overwrite an existing output')
        args.offline_html.write_text(render_offline_review(receipt), encoding='utf-8')
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2  # Review is always HELD, never a success/release signal.


if __name__ == '__main__':
    raise SystemExit(main())
