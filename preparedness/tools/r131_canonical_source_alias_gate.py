#!/usr/bin/env python3
"""Read-only URL-alias coverage gate for frozen Preparedness Archive sources.

Canonical URL equivalence is ONLY a review-worklist heuristic, never a license
for automatically merging source IDs, author interpretations or safety states.
A structurally clean run still returns HOLD_HUMAN_SOURCE_SCOPE_REVIEW.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import re
import subprocess
from urllib.parse import urlsplit

RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
CROSSWALK_COMMIT = '6ca388edbed803e64663e8f0ecfa55bda0fe08c3'
ROOT = 'preparedness/sources/'
FILE_PINS = {
    'base': ('register.json', 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'),
    'food': ('fragments/food.json', 'a1f73c8170932d6b3192e9cd506686d516d23d30'),
    'health': ('fragments/health.json', 'cc29c439372b9d49debf78e63020ffe4d62baeb8'),
    'hist-field': ('fragments/hist-field.json', '3dafa9425f3829c0be2e6fea00889aff95124031'),
    'hist-food': ('fragments/hist-food.json', 'd10628342fea5f177a8d1be00dd906d0c9c7850e'),
    'hist-home': ('fragments/hist-home.json', '8d85fd868508c5caba14a839d119d55f31f14f72'),
    'shelter': ('fragments/shelter.json', '2a3f1a7ddeab2782add875be1e0e378513504aa1'),
    'start': ('fragments/start.json', '96140d6d1872588e5d20d9052445c9157e88934d'),
}
CROSSWALK_PIN = 'c8c57c80963580645983402ad2cbed775827586e'


class GateError(ValueError):
    pass


def require(test, message):
    if not test:
        raise GateError(message)


def canonical(url):
    """Conservative alias key: preserve case, path escapes, query and fragment.

    Normalizes only HTTPS scheme/hostname, :443 and terminal path slashes.
    Rejects credentials, unsafe schemes and ambiguous URLs instead of guessing.
    """
    require(isinstance(url, str) and url == url.strip() and bool(url), 'INVALID_URL')
    require(not re.search(r'[\x00-\x20\x7f\\]', url), 'UNSAFE_URL_CHARACTERS')
    try:
        p = urlsplit(url)
        host = p.hostname
        port = p.port
    except ValueError as exc:
        raise GateError('MALFORMED_URL') from exc
    require(p.scheme.lower() == 'https' and host and p.netloc, 'UNSAFE_SCHEME_OR_HOST')
    require(p.username is None and p.password is None and '@' not in p.netloc, 'URL_CREDENTIALS')
    require(port in (None, 443), 'NONDEFAULT_PORT')
    require(host.isascii() and not host.startswith('.') and '..' not in host, 'AMBIGUOUS_HOST')
    require(not p.fragment, 'FRAGMENT_REQUIRES_REVIEW')
    require(not p.path.startswith('//'), 'AMBIGUOUS_PATH')
    require(not re.search(r'%(?:2[fF]|5[cC]|00)', p.path), 'ENCODED_PATH_SEPARATOR')
    hostname = host.lower().rstrip('.')
    require(bool(hostname), 'AMBIGUOUS_HOST')
    hostport = f'[{hostname}]' if ':' in hostname else hostname
    path = p.path.rstrip('/') or '/'
    return 'https://' + hostport + path + ('?' + p.query if p.query else '')


def parse_json(raw):
    def unique(pairs):
        obj = {}
        for key, val in pairs:
            require(key not in obj, 'DUPLICATE_JSON_KEY:' + key)
            obj[key] = val
        return obj
    try:
        return json.loads(raw, object_pairs_hook=unique)
    except (TypeError, json.JSONDecodeError) as exc:
        raise GateError('INVALID_JSON') from exc


def source_rows(documents):
    require(set(documents) == set(FILE_PINS), 'INCOMPLETE_SOURCE_ROSTER')
    output = []
    for origin in FILE_PINS:
        source = documents[origin]
        require(isinstance(source, dict) and isinstance(source.get('sources'), list), 'INVALID_FRAGMENT:' + origin)
        seen = set()
        for index, row in enumerate(source['sources']):
            require(isinstance(row, dict), 'INVALID_SOURCE_ROW')
            sid = row.get('id')
            require(isinstance(sid, str) and bool(re.fullmatch(r'[a-z][a-z0-9-]*', sid)), 'INVALID_SOURCE_ID')
            require(sid not in seen, 'DUPLICATE_ID_WITHIN_FRAGMENT:' + origin + ':' + sid)
            seen.add(sid)
            key = canonical(row.get('url'))
            output.append({'origin': origin, 'id': sid, 'row_index': index,
                           'url': row['url'], 'canonical_key': key,
                           'supports': row.get('supports'), 'notes': row.get('notes')})
    return output


def identity(row):
    return (row['origin'], row['id'], row['row_index'])


def audit(documents, crosswalk):
    """Pure, deterministic audit; review states cannot be upgraded by this gate."""
    rows = source_rows(documents)
    require(isinstance(crosswalk, dict) and isinstance(crosswalk.get('groups'), list), 'INVALID_CROSSWALK')
    exact = defaultdict(list)
    aliases = defaultdict(list)
    for row in rows:
        exact[row['url']].append(row)
        aliases[row['canonical_key']].append(row)
    shared = {key: group for key, group in aliases.items() if len(group) > 1}
    documented = {}
    for group in crosswalk['groups']:
        require(isinstance(group, dict), 'INVALID_CROSSWALK_GROUP')
        key = canonical(group.get('url'))
        require(key not in documented, 'DUPLICATE_CROSSWALK_CANONICAL_GROUP')
        require(group.get('review_status') == 'pending-human-source-and-reading-scope-review',
                'CROSSWALK_PREMATURE_APPROVAL')
        require(group.get('reviewer') is None and group.get('reviewed_on') is None,
                'CROSSWALK_REVIEWER_STATE_CHANGED')
        identities = group.get('identities')
        require(isinstance(identities, list), 'INVALID_GROUP_IDENTITIES')
        actual = []
        for ref in identities:
            require(isinstance(ref, dict), 'INVALID_IDENTITY')
            require(set(ref) == {'origin', 'id', 'row_index'}, 'IDENTITY_SCHEMA_CHANGED')
            require(type(ref['row_index']) is int, 'INVALID_ROW_INDEX')
            actual.append(identity(ref))
        require(len(actual) == len(set(actual)), 'DUPLICATE_CROSSWALK_IDENTITY')
        documented[key] = {'url': group['url'], 'identities': set(actual)}
    missing_groups = sorted(set(shared) - set(documented))
    extra_groups = sorted(set(documented) - set(shared))
    incomplete = []
    for key in sorted(set(shared) & set(documented)):
        expected = {identity(row) for row in shared[key]}
        found = documented[key]['identities']
        if expected != found:
            incomplete.append({'canonical_key': key,
                               'missing': [list(x) for x in sorted(expected-found)],
                               'unexpected': [list(x) for x in sorted(found-expected)]})
    multi_spellings = []
    for key, group in sorted(shared.items()):
        spellings = sorted({r['url'] for r in group})
        if len(spellings) > 1:
            multi_spellings.append({'canonical_key': key, 'spellings': spellings,
                                    'identities': [list(identity(r)) for r in sorted(group, key=identity)]})
    drift = bool(missing_groups or extra_groups or incomplete)
    return {
        'status': 'HOLD_CANONICAL_CROSSWALK_GAP' if drift else 'HOLD_HUMAN_SOURCE_SCOPE_REVIEW',
        'structural_crosswalk_complete': not drift,
        'may_merge': False, 'may_publish': False, 'independent_QD_PASS': False,
        'human_safety_approved': False, 'commercial_offer_approved': False,
        'source_rows': len(rows), 'exact_urls': len(exact),
        'exact_shared_groups': sum(len(v)>1 for v in exact.values()),
        'canonical_urls': len(aliases), 'canonical_shared_groups': len(shared),
        'canonical_alias_groups': multi_spellings,
        'missing_groups': missing_groups, 'extra_groups': extra_groups,
        'incomplete_groups': incomplete,
        'warning': 'Equivalent-looking source URLs still require distinct author and claim-scope review.'
    }


def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()


def load_pinned(repo):
    def show(commit, path, sha):
        try:
            raw = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + path], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise GateError('FROZEN_GIT_OBJECT_UNAVAILABLE:' + path) from exc
        require(blob_sha(raw) == sha, 'FROZEN_GIT_BLOB_CHANGED:' + path)
        return parse_json(raw)
    docs = {origin: show(RC, ROOT + relpath, sha) for origin, (relpath, sha) in FILE_PINS.items()}
    crosswalk = show(CROSSWALK_COMMIT, ROOT + 'crosswalk.json', CROSSWALK_PIN)
    return docs, crosswalk


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    args = parser.parse_args(argv)
    try:
        docs, crosswalk = load_pinned(args.repo)
        report = audit(docs, crosswalk)
        # Historical census is a custody gate, not evidence of source accuracy.
        require((report['source_rows'], report['exact_urls'], report['exact_shared_groups'],
                 report['canonical_urls'], report['canonical_shared_groups']) ==
                (244, 202, 32, 201, 32), 'HISTORICAL_SOURCE_CENSUS_CHANGED')
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2 if not report['structural_crosswalk_complete'] else 0
    except GateError as exc:
        print(json.dumps({'status': 'HOLD_GATE_ERROR', 'reason': str(exc),
                          'may_merge': False, 'may_publish': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
