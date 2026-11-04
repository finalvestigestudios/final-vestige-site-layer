#!/usr/bin/env python3
"""Private R111 seven-branch/35-article source custody convergence — HOLD only.

Independent earlier evidence is re-derived by scan(); compose() checks cross-layer
referential consistency without treating any checksum as a signature or safety PASS.
Never writes to WordPress, the repository, or any generated article draft.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = 'r111-converged-source-citation-review-HOLD-v1'
EXPECTED = {'changed': 23, 'bodies': 7, 'articles': 35, 'urls': 30,
            'branches': 7, 'safety': 15, 'editorial': 22, 'unfinished_tools': 5}
MAX_CHANGED = 200
MAX_GROUPS = 1000

class Hold(ValueError):
    """Reject inconsistent or incomplete author evidence without publication."""

def need(ok, message):
    if not ok:
        raise Hold(message)

def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)

def digest(data):
    return hashlib.sha256(canonical(data).encode('utf-8')).hexdigest()

def verify(report, schema, seal, scope):
    need(type(report) is dict and report.get('schema') == schema,
         scope + ' schema mismatch')
    need(report.get('release_state') == 'HOLD' and
         report.get('may_publish') is False, scope + ' cannot be released')
    need(type(report.get(seal)) is str and len(report[seal]) == 64 and
         digest({k: v for k, v in report.items() if k != seal}) == report[seal],
         scope + ' custody fingerprint changed (not a signature)')

def unique_rows(rows, label, key=lambda x:(x['origin'],x['path'])):
    need(type(rows) is list and len(rows) <= MAX_CHANGED,
         label + ' excessive/missing rows')
    keys = []
    for row in rows:
        need(type(row) is dict, label + ' malformed row')
        keys.append(key(row))
    need(len(set(keys)) == len(keys), label + ' duplicate identity')
    return {key(row): row for row in rows}

def compose(lineage, impacts, claims, caveats, collisions):
    """Pure cross-layer integrity gate; cannot produce a publication clearance."""
    verify(lineage, 'r107-seven-contributor-lineage-adoption-hold-v1',
           'sha256_NOT_A_SIGNATURE', 'R107')
    verify(impacts, 'r108-source-citation-change-impact-HOLD-v1',
           'sha256_NOT_A_SIGNATURE', 'R108')
    verify(claims, 'r109-citation-neighborhood-custody-HOLD-v1',
           'sha256_NOT_A_SIGNATURE', 'R109')
    verify(caveats, 'r110-adjacent-uncited-caveat-custody-HOLD-v1',
           'sha256_NOT_A_SIGNATURE', 'R110')
    verify(collisions, 'r102-author-scoped-citation-collision-workorder-v1',
           'sha256_seal', 'R102')
    need(impacts.get('R107_queue_sha256_NOT_A_SIGNATURE') == lineage['sha256_NOT_A_SIGNATURE'] and
         claims.get('R108_sha256_NOT_A_SIGNATURE') == impacts['sha256_NOT_A_SIGNATURE'] and
         caveats.get('R109_sha256_NOT_A_SIGNATURE') == claims['sha256_NOT_A_SIGNATURE'],
         'cross-stage parent evidence fingerprint mismatch')
    need(lineage.get('changed_path_count') == EXPECTED['changed'] and
         impacts.get('row_count') == EXPECTED['changed'] and
         claims.get('changed_body_review_count') == EXPECTED['bodies'] and
         caveats.get('changed_body_review_count') == EXPECTED['bodies'],
         'contributor change census drift; human reconciliation required')
    need(lineage.get('moved_branch_count') == 5 and
         lineage.get('original_evidence_paths') == 72 and
         lineage.get('distinct_original_articles') == 29 and
         lineage.get('frozen_R14_historical_exception_open') is True and
         lineage.get('mandatory_R15_seven_cluster_parity') == 'FAIL_CLOSED_ON_MOVED_REFS' and
         lineage.get('source_or_claim_accuracy_verified') is False and
         lineage.get('qualified_emergency_or_medical_safety_review') is False and
         lineage.get('independent_QD_PASS') is False,
         'historical contributor provenance must remain unresolved')
    need(impacts.get('factual_claim_support_approved') is False and
         impacts.get('qualified_emergency_safety_approved') is False and
         impacts.get('independent_QD_PASS') is False and
         claims.get('independent_QD_PASS') is False and
         claims.get('qualified_emergency_safety_approved') is False and
         caveats.get('independent_QD_PASS') is False and
         caveats.get('qualified_emergency_safety_approved') is False,
         'unexpected source, qualified safety, or QD approval marker')
    need(collisions.get('original_article_drafts') == EXPECTED['articles'] and
         collisions.get('actual_buildable_tools') == 1 and
         collisions.get('additional_planned_tools_not_buildable') == EXPECTED['unfinished_tools'] and
         collisions.get('literal_url_collision_groups_pending_human_review') == EXPECTED['urls'] and
         collisions.get('may_merge') is False and
         collisions.get('source_claim_support_review') == 'NOT_REVIEWED' and
         collisions.get('qualified_safety_review') == 'NOT_REVIEWED' and
         collisions.get('independent_QD') == 'NOT_REVIEWED',
         'full 35-article/one-tool unpublished source census drift')
    need(lineage.get('unreviewed_shared_url_groups') == EXPECTED['urls'] and
         lineage.get('human_safety_exceptions_unresolved') == EXPECTED['safety'] and
         lineage.get('editorial_decisions_unresolved') == EXPECTED['editorial'] and
         impacts.get('unreviewed_shared_source_url_groups') == EXPECTED['urls'],
         'human source/safety/editorial backlog cannot be silently erased')
    tips = lineage.get('seven_contributor_commit_ancestry')
    need(type(tips) is list and len(tips) == EXPECTED['branches'] and
         len({t['origin'] for t in tips}) == EXPECTED['branches'] and
         all(t.get('human_lineage_approval') == 'NOT_REVIEWED' and
             t.get('is_direct_descendant') is True for t in tips),
         'seven-contributor lineage not author-scoped or marked reviewed')
    before = unique_rows(lineage.get('contributor_reviewer_queue_NOT_APPROVED'), 'R107')
    after = unique_rows(impacts.get('rows_NOT_APPROVED'), 'R108')
    own = unique_rows(claims.get('rows_NOT_APPROVED'), 'R109')
    adjacency = unique_rows(caveats.get('rows_NOT_APPROVED'), 'R110')
    need(set(before) == set(after), 'R108 dropped/added an original contributor item')
    body_keys = {key for key, row in after.items() if row.get('category') == 'body'}
    need(len(body_keys) == EXPECTED['bodies'] and set(own) == body_keys and
         set(adjacency) == body_keys, 'R109/R110 body reviewer coverage incomplete')
    review_queue = []
    for key in sorted(before):
        original, changed = before[key], after[key]
        need(original.get('classification') == changed.get('category') and
             original.get('frozen_blob_sha') == changed.get('frozen_oid') and
             original.get('current_blob_sha') == changed.get('observed_oid') and
             original.get('human_provenance_review') == 'NOT_REVIEWED' and
             original.get('human_source_and_claim_review') == 'NOT_REVIEWED' and
             changed.get('human_source_or_claim_review') == 'NOT_REVIEWED' and
             changed.get('human_safety_review') == 'NOT_REVIEWED' and
             changed.get('may_publish') is False and
             original.get('may_publish') is False,
             'original/revised contributor identity, claim or safety state altered')
        row = {'origin': key[0], 'path': key[1],
               'category': changed['category'],
               'frozen_oid': changed['frozen_oid'],
               'observed_oid': changed['observed_oid'],
               'human_review': 'NOT_REVIEWED', 'may_publish': False,
               'requires_original_and_current_readings': True}
        if key in body_keys:
            c, a = own[key], adjacency[key]
            need(c.get('frozen_oid') == row['frozen_oid'] == a.get('frozen_oid') and
                 c.get('observed_oid') == row['observed_oid'] == a.get('observed_oid') and
                 c.get('human_claim_review') == 'NOT_REVIEWED' and
                 a.get('human_source_review') == 'NOT_REVIEWED' and
                 c.get('may_publish') is False and a.get('may_publish') is False and
                 c.get('citation_neighborhood_review_NOT_APPROVED', {}).get('may_publish') is False and
                 a.get('cross_paragraph_review_NOT_APPROVED', {}).get('may_publish') is False,
                 'changed article citation/adjacent caveat custody disagreement')
            row['citation_neighborhood'] = 'REQUIRES_HUMAN_SOURCE_REVIEW'
            row['uncited_adjacency'] = 'REQUIRES_HUMAN_SAFETY_REVIEW'
        review_queue.append(row)
    groups = collisions.get('groups')
    need(type(groups) is list and len(groups) == EXPECTED['urls'] <= MAX_GROUPS,
         'missing or additional shared literal URL group')
    seen_url = set()
    collision_queue = []
    total_occurrences = 0
    for group in groups:
        need(type(group) is dict and type(group.get('literal_url')) is str and
             group['literal_url'] and group['literal_url'] not in seen_url and
             group.get('review_state') == 'pending-human-source-and-reading-scope-review' and
             group.get('human_review') == 'NOT_REVIEWED' and
             group.get('same_url_is_not_shared_claim_authority') is True,
             'shared source URL identity collision or approval-state drift')
        url = group['literal_url']
        seen_url.add(url)
        variants, cited = group.get('variants'), group.get('author_bound_citation_contexts')
        need(type(variants) is list and len(variants) >= 2 and
             type(cited) is list and group.get('variant_count') == len(variants) and
             group.get('citation_occurrences') == len(cited),
             'source variants or author-bound citation occurrences lost')
        names = {(v['origin'], v['source_id']) for v in variants}
        need(len(names) == len(variants) and
             all(type(v.get('variant_sha256')) is str and len(v['variant_sha256']) == 64 for v in variants),
             'duplicate source variant or missing custody fingerprint')
        need(all((x.get('selected_source_origin'), x.get('source_id_as_authored')) in names and
                 type(x.get('author_scoped_source_use')) is str and
                 x['author_scoped_source_use'].strip() and
                 x.get('existing_article_safety_state_without_new_approval') in
                    ('pending', 'approved', 'not-required')
                 for x in cited),
             'citation detached from original author-specific source/reading scope')
        citations_in = {x['article_slug'] for x in cited}
        need(type(group.get('citing_articles')) is list and
             group['citing_articles'] == sorted(citations_in),
             'article citation roster drift in shared-URL group')
        total_occurrences += len(cited)
        collision_queue.append({'literal_url_sha256_NOT_A_SIGNATURE': hashlib.sha256(url.encode('utf-8')).hexdigest(),
                                'variant_count': len(variants),
                                'citation_occurrences': len(cited),
                                'citing_articles': sorted(citations_in),
                                'human_source_scope_review': 'NOT_REVIEWED',
                                'may_publish': False})
    need(collisions.get('collision_citation_occurrences') == total_occurrences,
         'crosswalk lost shared-source citation occurrences')
    result = {'schema': SCHEMA, 'issue': 136, 'release_state': 'HOLD',
              'may_publish': False, 'may_merge': False,
              'independent_QD_PASS': False, 'qualified_safety_review_approved': False,
              'source_factual_support_verified': False,
              'wordpress_writes': False, 'source_rewrites': False,
              'article_count': EXPECTED['articles'], 'complete_tools': 1,
              'unfinished_tools': EXPECTED['unfinished_tools'],
              'contributor_branch_count': EXPECTED['branches'],
              'advanced_branches_pending_review': 5,
              'changed_contributor_paths_pending_review': len(review_queue),
              'changed_article_bodies_pending_review': len(body_keys),
              'shared_url_groups_pending_review': len(collision_queue),
              'shared_url_citation_occurrences_pending_review': total_occurrences,
              'safety_exceptions_unresolved': EXPECTED['safety'],
              'editorial_decisions_unresolved': EXPECTED['editorial'],
              'upstream_sha256_NOT_SIGNATURES': {
                  'R107': lineage['sha256_NOT_A_SIGNATURE'],
                  'R108': impacts['sha256_NOT_A_SIGNATURE'],
                  'R109': claims['sha256_NOT_A_SIGNATURE'],
                  'R110': caveats['sha256_NOT_A_SIGNATURE'],
                  'R102': collisions['sha256_seal']},
              'contributor_worklist_NOT_APPROVED': review_queue,
              'shared_url_worklist_NOT_APPROVED': sorted(collision_queue, key=lambda x:x['literal_url_sha256_NOT_A_SIGNATURE']),
              'release_requirements': ['Human adjudication of 23 changed paths and 30 shared-URL groups',
                                        '15 safety exceptions and 22 editorial decisions',
                                        'five unfinished tools', 'qualified emergency/medical guidance review',
                                        'browser/print QA', 'mandatory 13-stage integrity', 'independent QD'],
              'disclaimer': 'Hash fingerprints prove neither source support nor medical safety. This worklist NEVER approves publication.'}
    result['sha256_NOT_A_SIGNATURE'] = digest(result)
    return result

def scan(root: Path):
    """Re-derive all custody layers against private exact checkout; no writes."""
    tools_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(tools_dir))
    import r102_author_scoped_collision_workorder as r102
    import r107_exact_branch_progression_adjudication as r107
    import r108_source_citation_change_impact_crosswalk as r108
    import r109_citation_context_custody as r109
    import r110_uncited_caveat_custody as r110
    import build, validate
    lib = build.Library()
    need(lib.root.resolve() == (root / 'preparedness').resolve(),
         'cannot read a different repository without isolated checkout')
    errors, _ = validate.validate(lib)
    need(not errors, 'original native article/source validator blocked')
    return compose(r107.scan(root), r108.scan(root), r109.scan(root),
                   r110.scan(root), r102.workorder(lib))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--json', action='store_true', help='Local private reviewer queue; does not print prose')
    args = parser.parse_args(argv)
    result = scan(args.repo_root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps({key: val for key, val in result.items() if key in
                          ('schema', 'release_state', 'may_publish', 'article_count',
                           'changed_contributor_paths_pending_review', 'changed_article_bodies_pending_review',
                           'shared_url_groups_pending_review', 'sha256_NOT_A_SIGNATURE')}, sort_keys=True))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Hold, OSError, KeyError, TypeError, ValueError) as exc:
        print('R111 PRIVATE SOURCE REVIEW HOLD: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
