#!/usr/bin/env python3
"""Read-only source-scope crosswalk receipt; NEVER human safety or QD approval."""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

HOLD = 'DRAFT_HARD_HOLD'
PENDING = 'pending-human-source-and-reading-scope-review'

def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result

def strict_json(raw):
    def nonfinite(value):
        raise ValueError('nonfinite JSON value: ' + value)
    value = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=_object,
                       parse_constant=nonfinite)
    if type(value) is not dict:
        raise ValueError('expected JSON object')
    return value

def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def review_alias(url):
    """Terminal slash equivalence for REVIEW only, never source substitution."""
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, (p.path or '/').rstrip('/') or '/',
                       p.query, p.fragment))

def audit_crosswalk(root: Path, safe_read) -> dict:
    """Verify every frozen source variant and emit deterministic review queue.

    No network fetch, author rewrite, cross-cluster scope merging or source
    approval. All outcomes explicitly DRAFT_HARD_HOLD.
    """
    doc = strict_json(safe_read(root, 'sources/crosswalk.json'))
    if doc.get('schema_version') != 1 or type(doc.get('groups')) is not list:
        raise ValueError('unexpected crosswalk schema')
    files = doc.get('source_files')
    if type(files) is not list or not files:
        raise ValueError('crosswalk source file inventory absent')
    rows, origin_set, path_set = [], set(), set()
    for entry in files:
        if type(entry) is not dict or set(entry) != {'origin','path','git_blob_sha','count'}:
            raise ValueError('invalid source inventory record')
        origin, path = entry['origin'], entry['path']
        if (type(origin) is not str or type(path) is not str or origin in origin_set or
                path in path_set or not path.startswith('preparedness/sources/') or
                type(entry['count']) is not int or entry['count'] < 0):
            raise ValueError('duplicate or unsafe source inventory')
        origin_set.add(origin)
        path_set.add(path)
        raw = safe_read(root, path.removeprefix('preparedness/'))
        if git_blob(raw) != entry['git_blob_sha']:
            raise ValueError('source Git identity drift: ' + path)
        sources = strict_json(raw).get('sources')
        if type(sources) is not list or len(sources) != entry['count']:
            raise ValueError('source inventory row count mismatch: ' + path)
        for index, source in enumerate(sources):
            if type(source) is not dict or not all(
                    type(source.get(k)) is str and source[k] for k in ('id', 'url')):
                raise ValueError('invalid raw source')
            rows.append({'origin': origin, 'source_file': path,
                         'row_index': index, 'source': source})
    if len(rows) != doc.get('raw_source_rows'):
        raise ValueError('raw source row census drift')
    by_url, by_alias, by_id = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in rows:
        by_url[row['source']['url']].append(row)
        by_alias[review_alias(row['source']['url'])].append(row)
        by_id[row['source']['id']].append(row)
    shared = {url: variants for url, variants in by_alias.items() if len(variants) > 1}
    exact = {url: variants for url, variants in by_url.items() if len(variants) > 1}
    if (len(by_url) != doc.get('unique_source_urls') or
            len(exact) != doc.get('duplicate_url_groups') or
            sum(len(v) > 1 for v in by_id.values()) != doc.get('duplicate_id_groups')):
        raise ValueError('source census / duplicate-ID mismatch')
    if any(len({v['source']['url'] for v in versions}) > 1 for versions in by_id.values()):
        raise ValueError('one source id assigned to multiple URLs')
    seen, queue = set(), []
    for group in doc['groups']:
        if type(group) is not dict or type(group.get('url')) is not str:
            raise ValueError('malformed shared source group')
        url = review_alias(group['url'])
        if url in seen or url not in shared:
            raise ValueError('duplicate or foreign crosswalk URL: ' + url)
        seen.add(url)
        actual = shared[url]
        recorded = group.get('variants')
        identities = group.get('identities')
        if type(recorded) is not list or type(identities) is not list:
            raise ValueError('missing per-origin evidence')
        identity = lambda v: (v['origin'], v['source']['id'], v['row_index'])
        expected = {identity(v): v for v in actual}
        observed = {identity(v): v for v in recorded}
        if len(expected) != len(actual) or len(observed) != len(recorded):
            raise ValueError('repeated per-origin evidence row')
        if expected != observed:
            raise ValueError('source scope changed or suppressed: ' + url)
        id_rows = {(v['origin'], v['id'], v['row_index']) for v in identities}
        if len(id_rows) != len(identities) or id_rows != set(expected):
            raise ValueError('crosswalk identities do not match variants: ' + url)
        status = group.get('review_status')
        if status != PENDING:
            resolution = group.get('resolution') or {}
            if status != 'resolved' or not all(resolution.get(k) for k in
                                               ('reviewer','date','scope_notes')):
                raise ValueError('unsubstantiated crosswalk resolution: ' + url)
        scopes = sorted({v['source'].get('supports', '') or '' for v in actual})
        reviewed = sorted({str(v['source'].get('verified_on')) for v in actual})
        queue.append({'url': url, 'status': status,
                      'source_ids': sorted({v['source']['id'] for v in actual}),
                      'origins': sorted({v['origin'] for v in actual}),
                      'row_count': len(actual),
                      'scope_variants': len(scopes),
                      'verification_date_variants': len(reviewed),
                      'all_human_link_checked': all(
                          v['source'].get('human_link_check') is True for v in actual),
                      'evidence_sha256': hashlib.sha256(
                          canonical(actual).encode('utf-8')).hexdigest(),
                      'human_scope_review_required': status == PENDING})
    if seen != set(shared):
        raise ValueError('shared URL omitted from crosswalk')
    if len(queue) != len(doc['groups']):
        raise ValueError('crosswalk group count changed')
    queue.sort(key=lambda row: row['url'])
    return {'state': HOLD, 'independent_qd_pass': False, 'release_authorized': False,
            'source_or_medical_safety_approved': False, 'merchant_approved': False,
            'raw_source_rows': len(rows), 'unique_urls': len(by_url),
            'duplicate_id_groups': sum(len(v) > 1 for v in by_id.values()),
            'shared_url_groups': len(shared), 'exact_duplicate_url_groups': len(exact),
            'pending_human_groups': sum(g['human_scope_review_required'] for g in queue),
            'review_queue': queue}
