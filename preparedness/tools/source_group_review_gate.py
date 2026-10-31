#!/usr/bin/env python3
"""Fail-closed deterministic review queue for Preparedness shared-source evidence.

This is provenance/accounting only. Machine success NEVER grants publishing,
factual approval, medical safety clearance, or independent QD approval.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

SOURCE_FILES = {'base': 'preparedness/sources/register.json', **{
    n: f'preparedness/sources/fragments/{n}.json' for n in
    ('start', 'shelter', 'food', 'health', 'hist-food', 'hist-home', 'hist-field')}}
AUTHOR_FOOD = '4b009361277ea1d4617b368f5d45104c7318b284'
FIXTURE_FOOD = 'e9cd7766dac59d47ab467d8945269b9146c2aef5'
HOLD = 'HOLD'


class SourceGateHold(ValueError):
    pass


def check(condition, problem):
    if not condition:
        raise SourceGateHold(problem)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def audit(crosswalk, taxonomy, source_bytes):
    """Require exact row, reading-note and unresolved-state parity with source files."""
    check(type(crosswalk) is dict and crosswalk.get('schema_version') == 1,
          'crosswalk schema unsupported')
    check(crosswalk.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
          'crosswalk falsely claims reviewed status')
    check(type(taxonomy) is dict and taxonomy.get('base_path') == '/preparedness/',
          'incorrect prepared archive taxonomy')
    slate = taxonomy.get('slate')
    check(type(slate) is list and len(slate) == 35, '35-item editorial slate changed')
    slugs = [x.get('slug') for x in slate if type(x) is dict]
    check(len(slugs) == 35 and len(set(slugs)) == 35 and
          all(type(s) is str and s and '/' not in s for s in slugs),
          'duplicate or invalid article URL slug')
    origins = crosswalk.get('article_origins')
    check(type(origins) is dict and set(origins) == set(slugs) | {'water-planner'} and
          set(origins.values()) <= set(SOURCE_FILES), 'article origin or water planner loss')
    check(any(t.get('slug') == 'water-planner' and t.get('gate') is True
              for t in taxonomy.get('tools', []) if type(t) is dict),
          'water planner safety gate missing')
    check(type(source_bytes) is dict and set(source_bytes) == set(SOURCE_FILES.values()),
          'source inventory missing or unexpected file')
    files = crosswalk.get('source_files')
    check(type(files) is list and len(files) == 8, 'eight source files required')
    head = crosswalk.get('source_head_commits')
    check(type(head) is dict and set(head) == set(SOURCE_FILES) and
          head['food'] in (AUTHOR_FOOD, FIXTURE_FOOD),
          'unrecognized contributor source provenance')
    all_rows = []
    seen = set()
    for f in files:
        check(type(f) is dict and f.get('origin') in SOURCE_FILES,
              'unrecognized source origin')
        origin = f['origin']
        check(origin not in seen and f.get('path') == SOURCE_FILES[origin],
              'source file duplicate or path substitution')
        seen.add(origin)
        raw = source_bytes[f['path']]
        check(type(raw) is bytes and len(raw) <= 500_000 and
              git_blob(raw) == f.get('git_blob_sha'), 'source evidence blob drift')
        try:
            source_json = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise SourceGateHold('source inventory malformed') from exc
        rows = source_json.get('sources') if type(source_json) is dict else None
        check(type(rows) is list and f.get('count') == len(rows),
              'source record count drift')
        for i, row in enumerate(rows):
            check(type(row) is dict and type(row.get('id')) is str and
                  type(row.get('url')) is str and row['url'].startswith('https://'),
                  'source row invalid or URL non-HTTPS')
            all_rows.append({'origin': origin, 'source_file': f['path'],
                             'row_index': i, 'source': row})
    check(seen == set(SOURCE_FILES), 'source inventory incomplete')
    by_url, by_id = defaultdict(list), defaultdict(list)
    for row in all_rows:
        by_url[row['source']['url']].append(row)
        by_id[row['source']['id']].append(row)
    repeated = {url: rows for url, rows in by_url.items() if len(rows) > 1}
    id_repeated = {sid for sid, rows in by_id.items() if len(rows) > 1}
    check(len(all_rows) == crosswalk.get('raw_source_rows') == 224 and
          len(by_url) == crosswalk.get('unique_source_urls') == 186 and
          len(repeated) == crosswalk.get('duplicate_url_groups') == 30 and
          len(id_repeated) == crosswalk.get('duplicate_id_groups') == 15,
          'source total, URL or ID duplicate accounting drift')
    groups = crosswalk.get('groups')
    check(type(groups) is list and len(groups) == 30, '30 review groups required')
    grouped = set()
    queue = []
    for g in groups:
        check(type(g) is dict and g.get('url') in repeated and
              g.get('canonical_url') == g.get('url') and
              g['url'] not in grouped, 'missing/duplicate shared URL group')
        grouped.add(g['url'])
        check(g.get('review_status') == 'pending-human-source-and-reading-scope-review' and
              g.get('reviewer') is None and g.get('reviewed_on') is None,
              'unsupported human review completion claim')
        actual = sorted(repeated[g['url']], key=lambda x: (x['origin'], x['row_index']))
        expected = Counter(canonical(x) for x in actual)
        variants = g.get('variants')
        check(type(variants) is list and Counter(canonical(x) for x in variants) == expected,
              'original source variant, reading-depth note or URL lost')
        identities = g.get('identities')
        wanted = Counter((x['origin'], x['source']['id'], x['row_index']) for x in actual)
        check(type(identities) is list and
              Counter((x['origin'], x['id'], x['row_index']) for x in identities) == wanted,
              'source identity crosswalk mismatch')
        queue.append({'url': g['url'], 'variant_count': len(actual),
                      'source_evidence_digest': hashlib.sha256(canonical(actual)).hexdigest(),
                      'decision': 'NEEDS_HUMAN_SOURCE_AND_READING_SCOPE_REVIEW'})
    check(grouped == set(repeated), 'a shared source URL was omitted')
    queue.sort(key=lambda x: x['url'])
    result = {'schema_version': 1, 'release_state': HOLD, 'may_publish': False,
              'independent_qd_pass': False, 'medical_safety_approved': False,
              'human_link_checks_completed_by_gate': 0,
              'source_rows': 224, 'distinct_urls': 186, 'shared_url_review_groups': 30,
              'duplicate_id_groups': 15, 'article_slugs': 35,
              'water_planner_safety_gate': True,
              'known_food_provenance_exception': head['food'] == FIXTURE_FOOD,
              'review_queue': queue}
    result['sha256'] = hashlib.sha256(canonical(result)).hexdigest()
    return result


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path('preparedness'))
    a = p.parse_args()
    try:
        root = a.root
        crosswalk = json.loads((root/'sources/crosswalk.json').read_bytes())
        taxonomy = json.loads((root/'taxonomy.json').read_bytes())
        files = {path: (root.parent/path).read_bytes() for path in SOURCE_FILES.values()}
        print(json.dumps(audit(crosswalk, taxonomy, files), sort_keys=True))
        return 0
    except (SourceGateHold, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'release_state': HOLD, 'may_publish': False,
                          'machine_review': 'INCOMPLETE_OR_FAILED', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
