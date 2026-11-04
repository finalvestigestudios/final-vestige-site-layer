#!/usr/bin/env python3
"""Private fail-closed git-object source/article difference reconciler, Issue #136.

Nine frozen GitHub directory snapshots are evidence of blob identity, not human
validation of the underlying words, sources or safety. Never grants QD/release.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1'
ORDER_SCHEMA = 'fv-preparedness-r117-reviewer-source-and-author-diff-workorders-HOLD-v1'
HEX = re.compile(r'[0-9a-f]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CLUSTERS = {'food', 'health', 'historical-field', 'historical-food',
            'historical-home', 'shelter', 'start-here'}

class Hold(ValueError):
    pass

def require(test, message):
    if not test:
        raise Hold(message)

def valid_files(mapping, kind):
    require(type(mapping) is dict and len(mapping) > 0, 'EMPTY_OR_INVALID_' + kind)
    for name, oid in mapping.items():
        require(type(name) is str and type(oid) is str and HEX.fullmatch(oid), 'BAD_FILE_OBJECT_ID')
        if kind == 'article_files':
            stem = name.removesuffix('.body.html').removesuffix('.meta.json')
            require(name in (stem+'.body.html', stem+'.meta.json') and SLUG.fullmatch(stem), 'UNSAFE_ARTICLE_PATH')
        else:
            require(name == 'README.md' or (name.endswith('.json') and SLUG.fullmatch(name[:-5])), 'UNSAFE_FRAGMENT_PATH')

def paired_articles(files):
    bodies = {p[:-10] for p in files if p.endswith('.body.html')}
    meta = {p[:-10] for p in files if p.endswith('.meta.json')}
    require(bodies == meta, 'ORPHAN_ARTICLE_BODY_OR_METADATA')
    return bodies

def reconstruct(manifest):
    require(type(manifest) is dict and manifest.get('schema') == SCHEMA, 'BAD_SNAPSHOT_SCHEMA')
    require(manifest.get('issue') == 136 and manifest.get('business_issue') == 820, 'BAD_ISSUE_SCOPE')
    g = manifest.get('governance')
    require(type(g) is dict and g.get('release_state') == 'HOLD' and
            all(g.get(k) is False for k in ('may_publish', 'may_merge', 'independent_QD_PASS',
                                           'medical_safety_verified', 'merchant_offer_verified')),
            'UNAUTHORIZED_GOVERNANCE_UPGRADE')
    snaps = manifest.get('snapshots')
    require(type(snaps) is list and len(snaps) == 9, 'NOT_NINE_SNAPSHOTS')
    require([x.get('role') for x in snaps] == ['baseline', 'candidate'] + ['contributor']*7,
            'ROLE_ORDER_INVALID')
    baseline, candidate, *contributors = snaps
    require({x.get('cluster') for x in contributors} == CLUSTERS and
            len({x.get('cluster') for x in contributors}) == 7, 'MISSING_CONTRIBUTOR_CLUSTER')
    require(len({x.get('ref') for x in snaps}) == 9 and
            all(type(x.get('ref')) is str and x['ref'] and
                type(x.get('sha')) is str and HEX.fullmatch(x['sha']) for x in snaps),
            'DUPLICATE_OR_INVALID_BRANCH_IDENTITY')
    for snap in snaps:
        valid_files(snap.get('article_files'), 'article_files')
        valid_files(snap.get('source_fragments'), 'source_fragments')
        paired_articles(snap['article_files'])
    original = paired_articles(baseline['article_files'])
    proposed = paired_articles(candidate['article_files'])
    require(len(original) == len(proposed) == 35 and original == proposed,
            'NOT_ORIGINAL_35_UNIQUE_ROUTES')
    require(all(set(x['article_files']) <= set(baseline['article_files']) and
                set(x['source_fragments']) <= set(baseline['source_fragments'])
                for x in contributors), 'NEW_UNREVIEWED_CONTRIBUTOR_PATH')
    rows = []
    by_path = defaultdict(list)
    for snap in contributors:
        for kind, root in [('article_files', 'preparedness/content/articles/'),
                           ('source_fragments', 'preparedness/sources/fragments/')]:
            for name, oid in snap[kind].items():
                old = baseline[kind].get(name)
                if oid == old:
                    continue
                now = candidate[kind].get(name)
                disposition = ('EXACT_IN_RELEASE_CANDIDATE' if oid == now else
                               'RELEASE_CANDIDATE_RETAINS_BASELINE' if now == old else
                               'RELEASE_CANDIDATE_DIFFERS_FROM_BOTH')
                row = dict(cluster=snap['cluster'], contributor_head=snap['sha'],
                           path=root+name, kind=kind, contributor_git_blob=oid,
                           frozen_original_git_blob=old, release_candidate_git_blob=now,
                           disposition=disposition, requires_human_source_or_safety_adjudication=True)
                rows.append(row)
                by_path[row['path']].append(row)
    return baseline, candidate, contributors, rows, by_path

def verify(snapshot, docket):
    baseline, candidate, contributors, rows, by_path = reconstruct(snapshot)
    require(type(docket) is dict and docket.get('schema') == ORDER_SCHEMA and
            docket.get('issue') == 136 and docket.get('business_issue') == 820,
            'BAD_WORKORDER_SCHEMA')
    require(docket.get('release_state') == 'HOLD' and
            all(docket.get(k) is False for k in ('may_publish', 'may_merge', 'independent_QD_PASS')),
            'WORKORDER_APPROVAL_TAMPER')
    require(docket.get('baseline_sha') == baseline['sha'] and
            docket.get('candidate_sha') == candidate['sha'] and
            docket.get('seven_contributor_heads') == {x['cluster']: x['sha'] for x in contributors},
            'STALE_BRANCH_HEAD_OR_REFERENCE')
    actual = docket.get('rows')
    require(type(actual) is list and len(actual) == len(rows), 'WORKORDER_ROW_COUNT_MISMATCH')
    def keyed(items):
        output = {}
        for row in items:
            require(type(row) is dict and type(row.get('path')) is str and
                    type(row.get('cluster')) is str, 'BAD_WORKORDER_ROW')
            key = (row['cluster'], row['path'])
            require(key not in output, 'DUPLICATE_WORKORDER')
            output[key] = row
        return output
    require(keyed(actual) == keyed(rows), 'WORKORDER_PROVENANCE_OR_DISPOSITION_DRIFT')
    require(docket.get('observation_count') == len(rows) and
            docket.get('unique_changed_paths') == len(by_path) and
            docket.get('non_exact_candidate_observations') ==
                sum(x['disposition'] != 'EXACT_IN_RELEASE_CANDIDATE' for x in rows),
            'WORKORDER_TOTALS_DRIFT')
    expected_collisions = {p: sorted(x['cluster'] for x in group) for p, group in by_path.items() if len(group)>1}
    listed = docket.get('overlapping_paths')
    require(type(listed) is list and len(listed) == len(expected_collisions), 'COLLISION_LIST_DRIFT')
    for collision in listed:
        require(type(collision) is dict and collision.get('path') in expected_collisions and
                sorted(collision.get('contributors',[])) == expected_collisions[collision['path']] and
                collision.get('distinct_contributor_git_blobs') ==
                    len({x['contributor_git_blob'] for x in by_path[collision['path']]}),
                'COLLISION_PROVENANCE_DRIFT')
    return {'schema': ORDER_SCHEMA, 'release_state': 'HOLD', 'may_merge': False,
            'may_publish': False, 'independent_QD_PASS': False,
            'snapshot_heads_verified_locally': False, 'human_review_complete': False,
            'original_article_routes': 35, 'contributor_branches': 7,
            'observations_requiring_review': len(rows),
            'unique_changed_paths': len(by_path),
            'candidate_non_exact_observations': sum(x['disposition'] != 'EXACT_IN_RELEASE_CANDIDATE' for x in rows),
            'source_fragment_observations': sum(x['kind'] == 'source_fragments' for x in rows)}

def require_local_head_objects(snapshot, root):
    """Optional strictly local Git object/ref proof; absence FAILS CLOSED."""
    require((Path(root)/'.git').exists(), 'NO_CHECKED_OUT_GIT_OBJECT_DATABASE')
    for entry in snapshot['snapshots']:
        branch = entry['ref']
        cmd = ['git', '-C', str(root), 'rev-parse', '--verify', 'refs/remotes/origin/'+branch+'^{commit}']
        response = subprocess.run(cmd, capture_output=True, text=True, check=False)
        require(response.returncode == 0 and response.stdout.strip() == entry['sha'],
                'LOCAL_BRANCH_HEAD_UNAVAILABLE_OR_DRIFTED_'+entry.get('role','unknown'))
        for kind in ('article_files','source_fragments'):
            for name, sha in entry[kind].items():
                path = 'preparedness/content/articles/' if kind == 'article_files' else 'preparedness/sources/fragments/'
                p = subprocess.run(['git','-C',str(root),'rev-parse',entry['sha']+':'+path+name],
                                   capture_output=True,text=True,check=False)
                require(p.returncode == 0 and p.stdout.strip() == sha,
                        'LOCAL_OBJECT_NOT_EXACT_'+name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--require-local-git-heads', action='store_true')
    a = parser.parse_args()
    root = Path(a.repo_root)
    try:
        snapshot = json.loads((root/'preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json').read_text())
        workorders = json.loads((root/'preparedness/docs/R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json').read_text())
        out = verify(snapshot, workorders)
        if a.require_local_git_heads:
            require_local_head_objects(snapshot, root)
            out['snapshot_heads_verified_locally'] = True
        print(json.dumps(out, sort_keys=True, indent=2))
        return 0
    except (Hold, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'release_state': 'HOLD', 'may_publish': False,
                          'integrity': 'FAILED_CLOSED', 'reason': str(exc)},sort_keys=True))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
