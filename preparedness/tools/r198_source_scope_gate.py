#!/usr/bin/env python3
"""R198 fail-closed per-article source-origin scope; draft review only."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r198-source-scope-custody-v1'
R197_SHA = '43a31b025e2cfebc1e6dff0302dee330858ea250'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
ORIGINS = frozenset(('base', 'hist-field', 'hist-food', 'hist-home'))
TOTALS = {'frozen': (65, 7), 'observed': (70, 9)}
ARTICLES = (
 ('hist-field', 'navigation-before-gps'),
 ('hist-field', 'pioneer-supply-chains-failed'),
 ('hist-food', 'pemmican-and-dried-meats'),
 ('hist-food', 'pioneer-travel-rations'),
 ('hist-home', 'pickling-fermentation-old-recipes'),
 ('hist-home', 'root-cellars-cool-storage'),
 ('hist-home', 'sanitation-before-germ-theory'),
)
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

class ScopeError(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise ScopeError(reason)

def git_oid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def load_pinned_r197(directory):
    path = Path(directory).resolve() / 'preparedness/tools/r197_source_origin_collision_gate.py'
    raw = path.read_bytes()
    need(git_oid(raw) == R197_SHA, 'R197 producer code is not authenticated')
    spec = importlib.util.spec_from_file_location('fv_preparedness_r197_pinned', path)
    need(spec is not None and spec.loader is not None, 'R197 producer cannot be imported')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.SCHEMA == 'fv-preparedness-r197-origin-collision-custody-v1', 'R197 schema mismatch')
    return module

def verify(custody, *, strict_census=True):
    """Never authorizes publication; received custody MUST originate in authenticated R197."""
    report = {'schema': SCHEMA, 'issue': 136, 'coordination_issue': 820,
              'state': INVALID, 'publication_authorized': False,
              'independent_qd_pass': False, 'medical_safety_verified': False,
              'merchant_offer_verified': False, 'verified_paid_orders': None,
              'realized_net_revenue': None, 'origin_scope_workorders': [],
              'summary': {}, 'errors': []}
    try:
        need(type(custody) is dict and custody.get('schema') == 'fv-preparedness-r197-origin-collision-custody-v1', 'wrong custody producer')
        need(custody.get('state') == HOLD and custody.get('issue') == 136, 'custody is not on hard hold')
        for flag in ('publication_authorized', 'independent_qd_pass', 'human_source_approved',
                     'medical_safety_verified', 'merchant_offer_verified'):
            need(custody.get(flag) is False, 'forged or missing approval flag: ' + flag)
        need(custody.get('verified_paid_orders') is None and custody.get('realized_net_revenue') is None,
             'unverified commercial proof claimed')
        docs = custody.get('article_origin_workorders')
        need(type(docs) is list and len(docs) == 14, 'expected 14 frozen/observed metadata positions')
        expected = {(group, slug, ver) for group, slug in ARTICLES for ver in TOTALS}
        seen = set()
        counts = {ver: {'source_uses': 0, 'ambiguous_uses': 0,
                        'other_cluster_alternatives': 0} for ver in TOTALS}
        for doc in docs:
            need(type(doc) is dict, 'bad article workorder')
            group, slug, ver = (doc.get(k) for k in ('cluster', 'slug', 'version'))
            key = (group, slug, ver)
            need(key in expected and key not in seen, 'unknown or repeated article version')
            seen.add(key)
            need(doc.get('human_review') == 'PENDING', 'article review incorrectly resolved')
            need(type(doc.get('meta_blob')) is str and re.fullmatch('[a-f0-9]{40}', doc['meta_blob']),
                 'missing metadata object identity')
            uses = doc.get('origins')
            need(type(uses) is list and len(uses) == doc.get('source_use_count'), 'citation/source-use census mismatch')
            seen_ids = set()
            for row in uses:
                need(type(row) is dict, 'invalid source-use entry')
                sid = row.get('source_id')
                origins = row.get('source_origins')
                need(type(sid) is str and ID.fullmatch(sid) and sid not in seen_ids,
                     'duplicated or invalid source-use ID')
                seen_ids.add(sid)
                need(type(origins) is list and bool(origins)
                     and origins == sorted(set(origins)) and set(origins) <= ORIGINS,
                     'invalid source-origin candidates')
                need(row.get('ambiguous') is (len(origins) > 1), 'false ambiguity classification')
                need(row.get('human_review') == 'PENDING', 'source-use human review improperly resolved')
                # A Field article may rely on Field or global Base, not solely on Food/Home.
                eligible = sorted(set(origins) & {'base', group})
                need(bool(eligible), 'CROSS-CLUSTER SOURCE LEAK: ' + slug + '/' + sid)
                foreign = sorted(set(origins) - {'base', group})
                ambiguous = len(origins) > 1
                counts[ver]['source_uses'] += 1
                counts[ver]['ambiguous_uses'] += int(ambiguous)
                counts[ver]['other_cluster_alternatives'] += int(bool(foreign))
                report['origin_scope_workorders'].append({
                    'cluster': group, 'slug': slug, 'version': ver,
                    'source_id': sid, 'eligible_origins': eligible,
                    'foreign_alternatives': foreign, 'all_original_origins': origins,
                    'source_scope': 'HUMAN_ORIGIN_ADJUDICATION_PENDING' if ambiguous else 'HUMAN_SOURCE_REVIEW_PENDING',
                    'automatic_origin_selection': False, 'human_review': 'PENDING'})
        need(seen == expected, 'missing article-version workorder')
        if strict_census:
            for ver, (total, ambiguous) in TOTALS.items():
                need(counts[ver]['source_uses'] == total and counts[ver]['ambiguous_uses'] == ambiguous,
                     'historical source-use or ambiguity census changed: ' + ver)
            need(custody.get('versioned_source_rows') == {'frozen': 115, 'observed': 119},
                 'underlying source register totals changed')
            conflicts = custody.get('same_id_conflicts')
            need(type(conflicts) is list
                 and sum(c.get('version') == 'frozen' for c in conflicts) == 6
                 and sum(c.get('version') == 'observed' for c in conflicts) == 7,
                 'cross-origin conflict count drift')
        report['summary'] = counts
        report['state'] = HOLD
    except (ScopeError, KeyError, TypeError, ValueError, AttributeError) as e:
        report['errors'].append(str(e)[:400])
        report['origin_scope_workorders'] = []
    return report

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--report')
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        producer = load_pinned_r197(repo)
        def read_blob(sha):
            return subprocess.run(['git', 'cat-file', 'blob', sha], cwd=repo,
                check=True, timeout=15, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        result = verify(producer.audit(read_blob))
    except (OSError, ScopeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        result = verify({})
        result['errors'] = [str(e)[:400]]
    output = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    if args.report:
        Path(args.report).write_text(output, encoding='utf-8')
    else:
        print(output, end='')
    # HOLD is an explicitly nonzero exit and is not a publish-ready PASS.
    return 2 if result['state'] == HOLD else 3

if __name__ == '__main__':
    raise SystemExit(main())
