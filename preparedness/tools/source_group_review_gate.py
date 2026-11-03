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
# R22 trust anchors: the R21 audit alone permits a coordinated replacement of
# crosswalk + inventories; the native CLI must never trust hashes supplied by
# the mutable crosswalk. These are original, independently inspected Git blobs.
FROZEN_BLOBS = {
    'preparedness/sources/crosswalk.json': 'da823671f06e63873e0264dbc0206ac5dad74d08',
    'preparedness/taxonomy.json': '15c547bb3018ac182b12a51036389cfa39a59168',
    'preparedness/sources/register.json': 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
    'preparedness/sources/fragments/start.json': '96140d6d1872588e5d20d9052445c9157e88934d',
    'preparedness/sources/fragments/shelter.json': '2a3f1a7ddeab2782add875be1e0e378513504aa1',
    'preparedness/sources/fragments/food.json': 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'preparedness/sources/fragments/health.json': 'cc29c439372b9d49debf78e63020ffe4d62baeb8',
    'preparedness/sources/fragments/hist-food.json': 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    'preparedness/sources/fragments/hist-home.json': '8d85fd868508c5caba14a839d119d55f31f14f72',
    'preparedness/sources/fragments/hist-field.json': '88d4face1385caabb26349b4864679b45fa81f37',
}
FROZEN_HEADS = {
    'base': 'ee591e2df5de08aea7603fc4cbf3c5249361e119',
    'start': '2122d856fce9f64887c16df3d52e64be9f59a55b',
    'shelter': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'food': AUTHOR_FOOD,
    'health': 'd2212d0ca0750817d3929865d3069835980faf20',
    'hist-food': '2acf65ca3efa9b4b5db7976f379b9ea693be43a4',
    'hist-home': 'f654e600f89c321a480dd8f055be4d13d0673490',
    'hist-field': 'a5ce8a62f168db05c95232e3eb385dccd0d19e7f',
}


# Stage 3b (2026-11-03): the live-checkout path pins the integrated candidate, the
# synthetic-fixture path keeps the original corpus values as its defaults.
ORIGINAL_COUNTS = {'rows': 224, 'urls': 186, 'groups': 30, 'id_groups': 15}
INTEGRATED_COUNTS = {'rows': 244, 'urls': 202, 'groups': 32, 'id_groups': 15}
ORIGINAL_TOOLS = frozenset({'water-planner'})
INTEGRATED_TOOLS = frozenset({'water-planner', 'home-fire-escape-worksheet',
                              'power-outage-planner', 'family-reunification-card',
                              'reunification-plan', 'kit-builder'})


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


def audit(crosswalk, taxonomy, source_bytes, *, counts=ORIGINAL_COUNTS, tools=ORIGINAL_TOOLS):
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
    check(type(origins) is dict and set(origins) == set(slugs) | set(tools) and
          set(origins.values()) <= set(SOURCE_FILES), 'article origin or water planner loss')
    check(any(t.get('slug') == 'water-planner' and t.get('gate') is True
              for t in taxonomy.get('tools', []) if type(t) is dict),
          'water planner safety gate missing')
    check(all(any(t.get('slug') == s and t.get('gate') is True
                  for t in taxonomy.get('tools', []) if type(t) is dict) for s in tools),
          'a built tool lost its safety gate in the taxonomy')
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
    check(len(all_rows) == crosswalk.get('raw_source_rows') == counts['rows'] and
          len(by_url) == crosswalk.get('unique_source_urls') == counts['urls'] and
          len(repeated) == crosswalk.get('duplicate_url_groups') == counts['groups'] and
          len(id_repeated) == crosswalk.get('duplicate_id_groups') == counts['id_groups'],
          'source total, URL or ID duplicate accounting drift')
    groups = crosswalk.get('groups')
    check(type(groups) is list and len(groups) == counts['groups'],
          f"{counts['groups']} review groups required")
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
              'source_rows': counts['rows'], 'distinct_urls': counts['urls'],
              'shared_url_review_groups': counts['groups'],
              'duplicate_id_groups': counts['id_groups'], 'article_slugs': 35,
              'water_planner_safety_gate': True,
              'known_food_provenance_exception': head['food'] == FIXTURE_FOOD,
              'review_queue': queue}
    result['sha256'] = hashlib.sha256(canonical(result)).hexdigest()
    return result



def audit_frozen(root, *, counts=ORIGINAL_COUNTS, tools=ORIGINAL_TOOLS):
    """R22 real-checkout trust boundary; never read network or change CMS.

    Source blobs and the taxonomy are checked against *external* reviewed
    identities before accepting the R21 structural audit. Includes the entire
    36-origin mapping and all original article gate states within pinned blobs.
    """
    root = Path(root)
    check(root.is_dir() and not root.is_symlink(), 'trusted root missing or linked')
    root = root.resolve(strict=True)
    raw = {}
    for name, expected in FROZEN_BLOBS.items():
        path = root / name
        check(path.is_file() and not path.is_symlink() and
              path.resolve(strict=True).is_relative_to(root),
              'missing or linked frozen source: ' + name)
        check(0 < path.stat().st_size <= 500_000, 'oversized frozen source: ' + name)
        data = path.read_bytes()
        check(git_blob(data) == expected, 'unreviewed frozen source change: ' + name)
        raw[name] = data
    def strict_json(data):
        def no_duplicates(pairs):
            obj = {}
            for key, val in pairs:
                check(key not in obj, 'duplicate JSON key: ' + key)
                obj[key] = val
            return obj
        def no_nonfinite(value):
            raise SourceGateHold('nonfinite JSON constant: ' + value)
        obj = json.loads(data.decode('utf-8', 'strict'), object_pairs_hook=no_duplicates,
                         parse_constant=no_nonfinite)
        check(type(obj) is dict, 'frozen JSON root must be object')
        return obj
    crosswalk = strict_json(raw['preparedness/sources/crosswalk.json'])
    taxonomy = strict_json(raw['preparedness/taxonomy.json'])
    heads = crosswalk.get('source_head_commits')
    check(type(heads) is dict and set(heads) == set(FROZEN_HEADS),
          'source contributor heads removed or inserted')
    for group, author in FROZEN_HEADS.items():
        check(heads[group] == author or (group == 'food' and heads[group] == FIXTURE_FOOD),
              'wrong frozen source contributor SHA: ' + group)
    result = audit(crosswalk, taxonomy, {name: raw[name] for name in SOURCE_FILES.values()},
                   counts=counts, tools=tools)
    check(result.get('release_state') == HOLD and result.get('may_publish') is False,
          'crosswalk gate declared unsupported approval')
    return {'schema_version': 1, 'issue': 136, 'release_state': HOLD,
            'may_publish': False, 'independent_qd_pass': False,
            'medical_safety_approved': False, 'human_source_review_complete': False,
            'source_inputs_pinned': 10, 'article_slugs': 35,
            'shared_source_groups_pending_human_review': counts['groups'],
            'food_author_head': AUTHOR_FOOD,
            'food_crosswalk_head': heads['food'],
            'food_provenance_alias_unresolved': heads['food'] == FIXTURE_FOOD,
            'source_review_queue_sha256': result['sha256'],
            'machine_authority': 'FROZEN_GIT_BLOB_AND_CROSSWALK_PARITY_ONLY'}


import re

# R23: independently frozen 81-file author corpus and source snapshot.
# A mutable manifest cannot authorize changes to itself: this Git blob is
# pinned outside the R20 evidence document. Passing means custody, not safety.
R23_MANIFEST = 'preparedness/docs/R20-REMOTE-GIT-OBJECT-CUSTODY-HOLD.json'
R23_MANIFEST_BLOB = '121d8f918c46ab55c666b540f74992bc9ff6e95d'


def audit_archive_corpus(root, *, manifest_pin=R23_MANIFEST_BLOB):
    """Verify all 35 original articles, water planner and nine source files.

    Read only, no Git fetch, no network, no CMS writes. The supplied override
    exists solely to exercise synthetic manifests under adversarial tests;
    the normal CLI always uses R23_MANIFEST_BLOB.
    """
    root = Path(root)
    check(root.is_dir() and not root.is_symlink(), 'R23 trusted root missing or linked')
    root = root.resolve(strict=True)

    def read_checked(name, cap):
        check(type(name) is str and name.startswith('preparedness/') and
              '..' not in name.split('/') and '\\' not in name and '//' not in name,
              'R23 untrusted path')
        target = root
        for part in name.split('/'):
            target = target / part
            check(not target.is_symlink(), 'R23 linked path: ' + name)
        check(target.is_file() and target.resolve(strict=True).is_relative_to(root),
              'R23 missing or escaped file: ' + name)
        size = target.stat().st_size
        check(0 < size <= cap, 'R23 missing/oversized input: ' + name)
        data = target.read_bytes()
        check(0 < len(data) <= cap, 'R23 oversized read: ' + name)
        return data

    def parse(data):
        def no_duplicate(pairs):
            obj = {}
            for key, value in pairs:
                check(key not in obj, 'R23 duplicate JSON key: ' + key)
                obj[key] = value
            return obj
        def no_nonfinite(value):
            raise SourceGateHold('R23 nonfinite JSON: ' + value)
        return json.loads(data.decode('utf-8', 'strict'),
                          object_pairs_hook=no_duplicate, parse_constant=no_nonfinite)

    raw = read_checked(R23_MANIFEST, 200_000)
    check(git_blob(raw) == manifest_pin, 'R23 independent manifest Git pin changed')
    taxonomy_raw = read_checked('preparedness/taxonomy.json', 100_000)
    check(git_blob(taxonomy_raw) == FROZEN_BLOBS['preparedness/taxonomy.json'],
          'R23 original taxonomy/safety status changed')
    manifest, taxonomy = parse(raw), parse(taxonomy_raw)
    check(type(manifest) is dict and manifest.get('schema_version') == 1 and
          manifest.get('repository') == 'finalvestigestudios/final-vestige-site-layer' and
          manifest.get('issue') == 136 and manifest.get('release_state') == HOLD and
          manifest.get('may_publish') is False and
          manifest.get('human_source_reviews_completed') is False and
          manifest.get('independent_QD_approval') is False and
          manifest.get('qualified_emergency_or_medical_safety_review') is False and
          manifest.get('link_and_claim_accuracy_independently_verified') is False and
          manifest.get('native_python_validation_build_or_html_parity_executed') is False,
          'R23 manifest authority/hold state changed')
    exceptions = manifest.get('exceptions')
    check(type(exceptions) is list and len(exceptions) == 1 and
          exceptions[0].get('path') ==
              'preparedness/content/articles/preparedness-real-households.meta.json' and
          exceptions[0].get('state') == 'NEEDS_HUMAN_DIFF_REVIEW' and
          exceptions[0].get('is_human_approved') is False,
          'R23 contributor metadata exception may not be cleared by machine')
    slate = taxonomy.get('slate')
    check(type(slate) is list and len(slate) == 35 and
          all(type(x) is dict and type(x.get('slug')) is str and
              re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', x['slug']) and
              type(x.get('gate')) is bool for x in slate),
          'R23 missing/invalid article URL or safety gate')
    slugs = [x['slug'] for x in slate]
    check(len(set(slugs)) == 35, 'R23 duplicate article URL')
    tools = taxonomy.get('tools')
    check(type(tools) is list and len(tools) == 6 and
          any(type(x) is dict and x.get('slug') == 'water-planner' and
              x.get('gate') is True for x in tools),
          'R23 original six-tool slate/water planner gate lost')
    expected = set(SOURCE_FILES.values()) | {'preparedness/sources/crosswalk.json'}
    for slug in slugs:
        expected.update({f'preparedness/content/articles/{slug}.body.html',
                         f'preparedness/content/articles/{slug}.meta.json'})
    expected.update({'preparedness/content/tools/water-planner.body.html',
                     'preparedness/content/tools/water-planner.meta.json'})
    check(len(expected) == 81, 'R23 81 original paths not resolved')
    rows = manifest.get('baseline_corpus_source_blob_pairs')
    check(type(rows) is list and len(rows) == 81, 'R23 81 original blob pairs required')
    actual = {}
    for row in rows:
        check(type(row) is dict and set(row) == {'path', 'baseline_blob', 'current_blob'},
              'R23 invalid Git-blob row')
        path, digest = row['path'], row['baseline_blob']
        check(type(path) is str and path in expected and path not in actual and
              type(digest) is str and re.fullmatch(r'[0-9a-f]{40}', digest) and
              row['current_blob'] == digest, 'R23 missing/duplicate/edited blob assertion')
        actual[path] = digest
    check(set(actual) == expected, 'R23 original input path lost')
    for section, patterns in (
        ('preparedness/content/articles', ('*.body.html', '*.meta.json')),
        ('preparedness/content/tools', ('*.body.html', '*.meta.json')),
        ('preparedness/sources/fragments', ('*.json',)),
    ):
        directory = root / section
        check(directory.is_dir() and not directory.is_symlink(),
              'R23 missing/linked corpus directory: ' + section)
        for pattern in patterns:
            for item in directory.glob(pattern):
                check(item.relative_to(root).as_posix() in expected and
                      item.is_file() and not item.is_symlink(),
                      'R23 unexpected/unreviewed corpus item: ' + str(item))
    for path, digest in sorted(actual.items()):
        check(git_blob(read_checked(path, 2_000_000)) == digest,
              'R23 original article/source bytes changed: ' + path)
    return {'release_state': HOLD, 'may_publish': False,
            'independent_qd_pass': False, 'medical_safety_approved': False,
            'human_source_review_complete': False,
            'original_articles': 35, 'original_water_tools': 1,
            'original_corpus_source_files_pinned': 81,
            'outstanding_metadata_review': 'NEEDS_HUMAN_DIFF_REVIEW',
            'corpus_path_blob_sha256': hashlib.sha256(
                canonical(sorted(actual.items()))).hexdigest()}


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path('preparedness'))
    a = p.parse_args()
    try:
        proof = audit_frozen(a.root.parent, counts=INTEGRATED_COUNTS, tools=INTEGRATED_TOOLS)
        proof.update(audit_archive_corpus(a.root.parent))
        print(json.dumps(proof, sort_keys=True))
        return 0
    except (SourceGateHold, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'release_state': HOLD, 'may_publish': False,
                          'machine_review': 'INCOMPLETE_OR_FAILED', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
