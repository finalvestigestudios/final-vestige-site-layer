#!/usr/bin/env python3
"""R194: fail-closed, read-only two-version citation custody for seven Claude deltas.

Never merges, rewrites, publishes, equates source IDs, or resolves historical
safety review. Requires both Git objects, verifies their contents, retains
both reading/citation sequences, and returns non-release state even on success.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r194-seven-delta-citation-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
BLOB = re.compile(r'[a-f0-9]{40}\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
EXPECTED = {
    'hist-field': {'navigation-before-gps', 'pioneer-supply-chains-failed'},
    'hist-food': {'pemmican-and-dried-meats', 'pioneer-travel-rations'},
    'hist-home': {'pickling-fermentation-old-recipes', 'root-cellars-cool-storage',
                  'sanitation-before-germ-theory'},
}

class IntegrityError(ValueError):
    pass

def demand(ok, message):
    if not ok:
        raise IntegrityError(message)

def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def strict_json(raw: bytes):
    def pairs(rows):
        obj = {}
        for key, val in rows:
            demand(key not in obj, 'duplicate JSON key')
            obj[key] = val
        return obj
    def invalid_constant(_):
        raise IntegrityError('nonstandard JSON constant')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid_constant)

def citations(raw: bytes):
    text = raw.decode('utf-8')
    seq = CITE.findall(text)
    demand(text.count('{{cite:') == len(seq), 'malformed citation token')
    return seq

def inspect(docket: dict, read_blob):
    """Read both complete article and metadata objects; never silently rebase.

    read_blob(oid) must return exact raw Git blob bytes. The production
    implementation uses git cat-file; synthetic tests can use an object store.
    """
    packet = {'schema': SCHEMA, 'state': INVALID, 'publication_authorized': False,
              'independent_qd_pass': False, 'medical_safety_verified': False,
              'source_claims_human_approved': False, 'merchant_offer_verified': False,
              'verified_paid_orders': None, 'realized_net_revenue': None,
              'articles_checked': 0, 'old_citations': 0, 'new_citations': 0,
              'old_and_new_readings_preserved': [], 'errors': []}
    try:
        demand(type(docket) is dict and docket.get('schema') == SCHEMA, 'docket schema')
        demand(docket.get('state') == HOLD and docket.get('issue') == 136,
               'docket authority is never release approval')
        for key in ('publication_authorized', 'independent_qd_pass',
                    'medical_safety_verified', 'source_claims_human_approved',
                    'merchant_offer_verified'):
            demand(docket.get(key) is False, 'unauthorized approval ' + key)
        demand(type(docket.get('articles')) is list and len(docket['articles']) == 7,
               'seven original changed-article candidates required')
        seen = {k: set() for k in EXPECTED}
        for item in docket['articles']:
            demand(type(item) is dict, 'invalid article row')
            group, slug = item.get('cluster'), item.get('slug')
            demand(group in EXPECTED and type(slug) is str and SLUG.fullmatch(slug)
                   and slug in EXPECTED[group] and slug not in seen[group],
                   'changed article roster/duplicate route')
            seen[group].add(slug)
            demand(item.get('human_source_review') == 'PENDING'
                   and item.get('qualified_safety_review') == 'PENDING',
                   'unreviewed change was marked cleared')
            record = {'cluster': group, 'slug': slug, 'review': 'PENDING'}
            data = {}
            for version in ('frozen', 'observed'):
                obj = item.get(version)
                demand(type(obj) is dict, 'missing version ' + version)
                body_oid, meta_oid = obj.get('body_blob'), obj.get('meta_blob')
                demand(type(body_oid) is str and BLOB.fullmatch(body_oid)
                       and type(meta_oid) is str and BLOB.fullmatch(meta_oid),
                       'malformed Git object identity')
                body, meta = read_blob(body_oid), read_blob(meta_oid)
                demand(type(body) is bytes and type(meta) is bytes and
                       len(body) <= 2_000_000 and len(meta) <= 100_000 and
                       blob_oid(body) == body_oid and blob_oid(meta) == meta_oid,
                       'missing or substituted Git object')
                source = strict_json(meta)
                demand(type(source) is dict and source.get('slug') == slug
                       and type(source.get('source_use')) is dict
                       and type(source.get('status')) is dict
                       and source['status'].get('publish') == 'draft',
                       'untrusted source scope, slug or publication state')
                seq = citations(body)
                demand(type(obj.get('citations')) is int and obj['citations'] == len(seq),
                       'citation occurrence drift')
                demand(len(seq) >= 1 and all(id in source['source_use'] for id in seq),
                       'citation missing source-use explanation')
                data[version] = {'seq': seq, 'meta': source, 'body_oid': body_oid,
                                 'meta_oid': meta_oid}
                record[version + '_body_git_blob'] = body_oid
                record[version + '_meta_git_blob'] = meta_oid
                record[version + '_citation_sequence'] = seq
                packet[('old' if version == 'frozen' else 'new') + '_citations'] += len(seq)
            demand(data['frozen']['meta'].get('safety_review') ==
                   data['observed']['meta'].get('safety_review'),
                   'historical safety-review state was changed')
            old, new = Counter(data['frozen']['seq']), Counter(data['observed']['seq'])
            record['added_citation_ids_UNREVIEWED'] = sorted(new.keys() - old.keys())
            record['removed_citation_ids_UNALIASED'] = sorted(old.keys() - new.keys())
            record['changed_occurrences'] = {k: [old[k], new[k]] for k in sorted(old.keys()|new.keys())
                                             if old[k] != new[k]}
            record['sequence_identical_NOT_CLAIM_APPROVAL'] = data['frozen']['seq'] == data['observed']['seq']
            packet['old_and_new_readings_preserved'].append(record)
            packet['articles_checked'] += 1
        demand(seen == EXPECTED, 'missing original article from changed-source roster')
        demand(packet['old_citations'] == 315 and packet['new_citations'] == 334,
               'frozen/observed seven-article citation totals drifted')
        packet['state'] = HOLD
    except (IntegrityError, ValueError, TypeError, KeyError, OSError, UnicodeError,
            subprocess.CalledProcessError) as exc:
        packet['errors'].append(str(exc)[:250])
    return packet

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path('.'))
    ap.add_argument('--docket', type=Path, required=True)
    opts = ap.parse_args(argv)
    def git_read(oid):
        return subprocess.run(['git', 'cat-file', 'blob', oid], cwd=opts.repo,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=True, timeout=15).stdout
    try:
        docket = strict_json(opts.docket.read_bytes())
        packet = inspect(docket, git_read)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        packet = {'schema': SCHEMA, 'state': INVALID, 'errors': [str(exc)[:250]],
                  'publication_authorized': False, 'independent_qd_pass': False}
    print(json.dumps(packet, sort_keys=True, ensure_ascii=False))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
