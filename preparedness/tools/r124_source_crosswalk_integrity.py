#!/usr/bin/env python3
"""Read-only candidate source-provenance parity check. Never grants safety/QD/release approval.

Run: python -I preparedness/tools/r124_source_crosswalk_integrity.py --root .
All 32 shared-URL groups remain pending qualified human evidence/safety review.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit

CANDIDATE = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
FILES = {'base': 'register.json', **{k: 'fragments/' + k + '.json' for k in
    ('food', 'health', 'hist-field', 'hist-food', 'hist-home', 'shelter', 'start')}}
PENDING = 'pending-human-source-and-reading-scope-review'
HOLD = 'DRAFT_UNREVIEWED_HOLD'

class IntegrityHold(ValueError):
    """A source variant, URL, evidence identity or review state drifted."""

def require(ok, code):
    if not ok:
        raise IntegrityHold(code)

def unique_pairs(pairs):
    d = {}
    for key, value in pairs:
        require(key not in d, 'DUPLICATE_JSON_KEY:' + key)
        d[key] = value
    return d

def json_file(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)

def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def key_url(value):
    require(type(value) is str and bool(value), 'SOURCE_URL_REQUIRED')
    require(not re.search(r'[\\\x00-\x1f\x7f]', value), 'UNSAFE_SOURCE_URL')
    try:
        p = urlsplit(value)
        host, port = p.hostname, p.port
    except ValueError as e:
        raise IntegrityHold('SOURCE_URL_INVALID') from e
    require(p.scheme == 'https' and host and not p.username and not p.password,
            'HTTPS_HOST_REQUIRED')
    require(port is None or (0 < port < 65536), 'BAD_SOURCE_PORT')
    host = host.lower().rstrip('.')
    require(bool(host) and not host.startswith('.'), 'BAD_SOURCE_HOST')
    authority = '[' + host + ']' if ':' in host else host
    if port not in (None, 443):
        authority += ':' + str(port)
    return urlunsplit(('https', authority, p.path or '/', p.query, p.fragment))

def alias_key_url(value):
    """Conservative review-only alias: preserve query, path case and fragment.

    A terminal slash is only evidence that two records need a shared worklist.
    It NEVER merges author interpretations or changes original source URLs.
    """
    p = urlsplit(key_url(value))
    return urlunsplit((p.scheme, p.netloc, (p.path or '/').rstrip('/') or '/',
                       p.query, p.fragment))


def audit(root, *, expected_groups=32, expected_commit=CANDIDATE):
    root = Path(root)
    source_dir = root / 'preparedness' / 'sources'
    x = json_file(source_dir / 'crosswalk.json')
    require(x.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
            'CROSSWALK_HOLD_MISSING')
    rec = x.get('candidate_reconciliation_20261104')
    require(type(rec) is dict and rec.get('status') == HOLD, 'CANDIDATE_HOLD_MISSING')
    require(rec.get('candidate_commit') == expected_commit, 'CANDIDATE_COMMIT_DRIFT')
    require(rec.get('issue') == 136 and rec.get('business_issue') == 820 and
            rec.get('business_charter') == 818, 'ISSUE_SCOPE_DRIFT')
    for f in ('independent_QD_PASS', 'safety_approved', 'medical_safety_verified',
              'may_publish', 'may_merge', 'merchant_offer_verified'):
        require(rec.get(f) is False, 'UNAUTHORIZED_APPROVAL:' + f)
    historical = x.get('historical_crosswalk_census_20261030')
    require(type(historical) is dict and historical.get('duplicate_url_groups') == 30 and
            historical.get('raw_source_rows') == 224, 'HISTORICAL_EVIDENCE_LOST')

    observed_files = []
    by_url = defaultdict(list)
    by_alias = defaultdict(list)
    by_id = Counter()
    for origin, suffix in FILES.items():
        rel = 'preparedness/sources/' + suffix
        path = root / rel
        raw = path.read_bytes()
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs)
        require(type(obj) is dict and type(obj.get('sources')) is list,
                'INVALID_SOURCE_REGISTER:' + origin)
        rows = obj['sources']
        observed_files.append({'origin': origin, 'path': rel,
                               'git_blob_sha': blob_sha(raw), 'count': len(rows)})
        for index, source in enumerate(rows):
            require(type(source) is dict and type(source.get('id')) is str and
                    re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', source['id']) is not None,
                    'INVALID_SOURCE_ID:' + origin)
            url = key_url(source.get('url'))
            by_id[source['id']] += 1
            evidence = {'origin': origin, 'source_file': rel,
                        'row_index': index, 'source': source}
            by_url[url].append(evidence)
            by_alias[alias_key_url(source['url'])].append(evidence)
    require(observed_files == x.get('source_files'), 'SOURCE_FILE_BLOB_OR_ROW_DRIFT')
    raw_count = sum(f['count'] for f in observed_files)
    exact_collisions = {url: rows for url, rows in by_url.items() if len(rows) > 1}
    collisions = {url: rows for url, rows in by_alias.items() if len(rows) > 1}
    require(raw_count == x.get('raw_source_rows'), 'SOURCE_ROW_COUNT_DRIFT')
    require(len(by_url) == x.get('unique_source_urls'), 'DISTINCT_SOURCE_URL_DRIFT')
    require(len(exact_collisions) == expected_groups == x.get('duplicate_url_groups'),
            'SHARED_URL_GROUP_COUNT_DRIFT')
    require(len(collisions) == expected_groups, 'ALIAS_GROUP_COUNT_DRIFT')
    require(sum(n > 1 for n in by_id.values()) == x.get('duplicate_id_groups'),
            'DUPLICATE_SOURCE_ID_COUNT_DRIFT')
    require(raw_count == rec.get('candidate_source_rows') and
            len(by_url) == rec.get('candidate_distinct_urls') and
            len(exact_collisions) == rec.get('candidate_shared_url_groups'),
            'CANDIDATE_CENSUS_DRIFT')

    declared = {}
    for group in x.get('groups', []):
        require(type(group) is dict and type(group.get('url')) is str,
                'INVALID_SHARED_SOURCE_GROUP')
        url = alias_key_url(group['url'])
        require(url not in declared, 'DUPLICATE_SHARED_URL_GROUP')
        require(group.get('canonical_url') == key_url(group['url']), 'CANONICAL_URL_DRIFT')
        require(group.get('review_status') == PENDING and
                group.get('reviewer') is None and group.get('reviewed_on') is None,
                'PREMATURE_SOURCE_APPROVAL')
        declared[url] = group
    require(set(declared) == set(collisions), 'MISSING_OR_EXTRA_SHARED_URL_GROUP')
    for url, rows in collisions.items():
        group = declared[url]
        expected_variants = {(v['origin'], v['source_file'], v['row_index'],
                              v['source']['id']): v for v in rows}
        recorded = group.get('variants')
        require(type(recorded) is list and len(recorded) == len(rows),
                'SOURCE_VARIANT_ROSTER_DRIFT')
        observed_keys = []
        for row in recorded:
            require(type(row) is dict and type(row.get('source')) is dict,
                    'INVALID_SOURCE_VARIANT')
            key = (row.get('origin'), row.get('source_file'),
                   row.get('row_index'), row['source'].get('id'))
            require(key in expected_variants and key not in observed_keys,
                    'SOURCE_VARIANT_ROSTER_DRIFT')
            observed_keys.append(key)
            require(row['source'] == expected_variants[key]['source'],
                    'SOURCE_VARIANT_CONTENT_DRIFT')
        identities = group.get('identities')
        expected_ids = [{'origin': v['origin'], 'id': v['source']['id'],
                         'row_index': v['row_index']} for v in rows]
        require(type(identities) is list and
                sorted(identities, key=lambda q: (q['origin'], q['id'], q['row_index'])) ==
                sorted(expected_ids, key=lambda q: (q['origin'], q['id'], q['row_index'])),
                'SOURCE_IDENTITY_ROSTER_DRIFT')
    return {'release_state': 'HOLD', 'QD_PASS': False, 'may_publish': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'source_rows': raw_count, 'distinct_urls': len(by_url),
            'shared_url_groups': len(exact_collisions),
            'canonical_shared_groups': len(collisions),
            'canonical_alias_groups': sum(
                len({row['source']['url'] for row in rows}) > 1
                for rows in collisions.values()),
            'unreviewed_groups': len(declared),
            'warning': 'Structural parity only; every source group requires human review.'}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('.'))
    args = p.parse_args(argv)
    try:
        print(json.dumps(audit(args.root), indent=2, sort_keys=True))
        return 0
    except (IntegrityHold, ValueError, OSError, UnicodeError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
