#!/usr/bin/env python3
"""R31: deterministic, read-only review-index integrity gate for Issue #136.

Consumes R25's *unapproved* original evidence packet and binds every citation
relationship, original source record and reading-scope explanation to an
article-level human work queue. A complete queue is NOT a completed review.
Never writes, fetches a link, publishes or awards QD/safety clearance.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date
import hashlib
import ipaddress
import json
import re
from urllib.parse import urlsplit

SHA = re.compile(r'[0-9a-f]{64}\Z')
TOKEN = re.compile(r'\{\{cite:([A-Za-z0-9_.-]+)\}\}')
REQUIRED_COUNTS = ('articles', 'tools', 'citations', 'relationships',
                   'base_fallback_relationships', 'shared_url_groups_unreviewed')

class IndexHold(ValueError):
    """Evidence packet malformed or source/safety custody cannot be proved."""

def require(check, why):
    if not check:
        raise IndexHold(why)

def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()

def sha_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def url_check(value):
    """No fetching or rewriting: retain the original contributor URL verbatim."""
    require(type(value) is str and value.startswith('https://'),
            'non-HTTPS source identity')
    require(not any(ord(c) <= 32 or ord(c) == 127 for c in value)
            and '\\' not in value, 'source URL contains control, space or backslash')
    try:
        u = urlsplit(value)
        host = u.hostname
        port = u.port
    except ValueError as exc:
        raise IndexHold('source URL cannot be parsed') from exc
    try:
        ascii_host = host.encode('ascii').decode('ascii') if host else ''
    except UnicodeError as exc:
        raise IndexHold('Unicode source host requires independent review') from exc
    require(u.scheme == 'https' and bool(host) and
            u.username is None and u.password is None and port is None and
            u.netloc == host and host == ascii_host and
            host.lower() == host and '.' in host and
            not host.endswith('.') and not host.startswith('.') and
            not any(c in host for c in ('%', '@', '_')),
            'ambiguous source host, credentials, port or Unicode authority')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise IndexHold('numeric host cannot establish source provenance')
    return host

def build_index(packet, *, expected=(35, 1, 1959, 367, 43, 30)):
    """Return a tamper-evident review plan; never return approval semantics.

    The source packet is retained separately by the caller. Compact cards here
    reference exact R25 row fingerprints, not potentially truncated evidence.
    """
    require(type(packet) is dict and type(expected) is tuple and len(expected) == 6
            and all(type(n) is int and n >= 0 for n in expected), 'invalid packet contract')
    require(packet.get('schema_version') == 1 and packet.get('issue') == 136 and
            packet.get('release_state') == 'HOLD' and packet.get('may_publish') is False
            and packet.get('machine_authority') ==
            'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY',
            'source packet is not an R25 HOLD review queue')
    for flag in ('qualified_safety_clearance','independent_QD_approval',
                 'human_source_reviews_completed','source_claim_accuracy_verified'):
        require(packet.get(flag) is False, 'fabricated safety/QD/source clearance: ' + flag)
    counts = packet.get('counts')
    require(type(counts) is dict and set(counts) == set(REQUIRED_COUNTS)
            and tuple(counts[k] for k in REQUIRED_COUNTS) == expected,
            'frozen 35+1 source/citation counts drift')
    rows = packet.get('review_queue')
    require(type(rows) is list and len(rows) == expected[3],
            'missing or extra article-source relationships')
    expected_digest = packet.get('fingerprint_sha256')
    without_digest = dict(packet)
    without_digest.pop('fingerprint_sha256', None)
    require(type(expected_digest) is str and SHA.fullmatch(expected_digest)
            and digest(without_digest) == expected_digest,
            'R25 evidence packet fingerprint mismatch')
    seen_relationships = set()
    article_hashes = {}
    articles = defaultdict(lambda: {'relationships': 0, 'citations': 0,
                                    'base_fallbacks': 0, 'shared_url_relationships': 0,
                                    'source_ids': [], 'original_row_sha256': []})
    by_url = defaultdict(list)
    offsets_by_slug = defaultdict(set)
    total_cites = total_fallbacks = 0
    for row in rows:
        require(type(row) is dict, 'non-object relationship')
        slug, sid = row.get('slug'), row.get('source_id')
        require(type(slug) is str and bool(re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug))
                and type(sid) is str and TOKEN.fullmatch('{{cite:' + sid + '}}') is not None,
                'invalid article/source identity')
        key = (slug, sid)
        require(key not in seen_relationships, 'duplicate article-source relationship')
        seen_relationships.add(key)
        origin, source_origin = row.get('article_origin'), row.get('source_origin')
        require(type(origin) is str and origin in {'base','start','shelter','food',
                'health','hist-food','hist-home','hist-field'} and
                type(source_origin) is str and source_origin in {'base','start',
                'shelter','food','health','hist-food','hist-home','hist-field'},
                'unrecognized contributor provenance')
        require(type(row.get('base_fallback_requires_human_scope_review')) is bool and
                row['base_fallback_requires_human_scope_review'] == (origin != source_origin),
                'base-fallback lineage changed')
        require(row.get('shared_url_group_requires_human_review') in (True, False)
                and type(row.get('shared_url_group_requires_human_review')) is bool,
                'ambiguous shared-URL review state')
        require(row.get('human_link_checked_by_this_gate') is False and
                row.get('human_claim_reviewed_by_this_gate') is False,
                'machine packet falsely reports human source verification')
        source = row.get('original_source_record_as_selected')
        require(type(source) is dict and source.get('id') == sid and
                source.get('_origin') == source_origin and
                source.get('url') == row.get('source_url') and
                source.get('supports') == row.get('source_supports_as_recorded') and
                source.get('notes') == row.get('source_notes_as_recorded') and
                source.get('verified_on') == row.get('machine_verified_on'),
                'selected source and original reading-depth metadata differ')
        verified = row.get('machine_verified_on')
        require(type(verified) is str and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', verified)),
                'missing source verification date')
        try:
            date.fromisoformat(verified)
        except ValueError as exc:
            raise IndexHold('impossible verification date') from exc
        host = url_check(row['source_url'])
        require(type(source['supports']) is str and source['supports'].strip(),
                'lost source-reading depth')
        scope = row.get('article_source_use_as_recorded')
        require(type(scope) is str and scope.strip() and
                row.get('frozen_source_use_sha256') == sha_text(scope),
                'article-specific reading-scope fingerprint mismatch')
        require(row.get('original_source_record_sha256') == digest(source),
                'original contributor source fingerprint mismatch')
        body_sha = row.get('frozen_article_html_sha256')
        require(type(body_sha) is str and SHA.fullmatch(body_sha),
                'article body identity is not a frozen digest')
        if slug in article_hashes:
            require(article_hashes[slug] == (body_sha, origin),
                    'article HTML hash or cluster origin differs between citations')
        article_hashes[slug] = (body_sha, origin)
        offsets, contexts = (row.get('citation_token_codepoint_offsets'),
                             row.get('all_citation_contexts_for_human_claim_review'))
        n = row.get('citation_occurrences')
        require(type(n) is int and n > 0 and type(offsets) is list and
                type(contexts) is list and len(offsets) == n == len(contexts) and
                all(type(o) is int and o >= 0 for o in offsets) and
                offsets == sorted(set(offsets)) and
                all(type(c) is str and '[CITATION]' in c for c in contexts),
                'citation occurrence offsets, contexts or counts malformed')
        require(not offsets_by_slug[slug].intersection(offsets),
                'two different source IDs claim the same article citation offset')
        offsets_by_slug[slug].update(offsets)
        a = articles[slug]
        a['relationships'] += 1
        a['citations'] += n
        a['base_fallbacks'] += int(row['base_fallback_requires_human_scope_review'])
        a['shared_url_relationships'] += int(row['shared_url_group_requires_human_review'])
        a['source_ids'].append(sid)
        a['original_row_sha256'].append(digest(row))
        total_cites += n
        total_fallbacks += int(row['base_fallback_requires_human_scope_review'])
        by_url[row['source_url']].append({'slug': slug, 'source_id': sid,
                                         'contributor': source_origin,
                                         'source_record_sha256': row['original_source_record_sha256'],
                                         'source_host': host})
    require(total_cites == expected[2] and total_fallbacks == expected[4],
            '1,959 citation or 43 fallback reconciliation drift')
    require(len(articles) == expected[0] + expected[1],
            'missing article or standalone field tool in review index')
    index = {
        'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
        'may_publish': False, 'human_source_reviews_completed': False,
        'independent_QD_approval': False, 'qualified_safety_clearance': False,
        'source_claim_accuracy_verified': False,
        'machine_authority': 'DETERMINISTIC_HUMAN_REVIEW_WORK_INDEX_ONLY',
        'parent_R25_fingerprint_sha256': expected_digest,
        'counts': dict(counts),
        'article_review_cards': [{
            'slug': slug, 'article_html_sha256': article_hashes[slug][0],
            'contributor_origin': article_hashes[slug][1],
            **{k: (sorted(v) if k == 'source_ids' else sorted(v) if k == 'original_row_sha256' else v)
               for k, v in meta.items()},
            'review_state': 'UNREVIEWED' }
            for slug, meta in sorted(articles.items())],
        'source_url_index': [{
            'source_url': url, 'source_relationships_preserved_without_dedup':
                sorted(rows, key=lambda r: (r['slug'],r['source_id'],r['contributor'])),
            'review_state': 'UNREVIEWED'} for url, rows in sorted(by_url.items())],
        'instructions': 'Human reviewers must open original contributor evidence and verify individual claims, URLs, historical provenance and consequential emergency guidance; no approval is implied.'
    }
    index['fingerprint_sha256'] = digest(index)
    return index

def main(argv=None):
    """Stdout-only private review index; never writes an artifact or changes CMS."""
    import argparse
    import importlib.util
    from pathlib import Path
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path,
                        default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    sibling = Path(__file__).with_name('citation_fallback_review_gate.py')
    try:
        require(sibling.is_file() and not sibling.is_symlink(),
                'citation fallback packet generator missing')
        spec = importlib.util.spec_from_file_location('preparedness_r25_review_packet', sibling)
        require(spec is not None and spec.loader is not None,
                'citation fallback packet generator cannot load')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = build_index(module.audit_checkout(args.repo_root))
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (IndexHold, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Preparedness citation review index HOLD: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
