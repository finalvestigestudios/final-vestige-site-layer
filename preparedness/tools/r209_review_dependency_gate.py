#!/usr/bin/env python3
"""R209: independent QA-patch dependency custody for 35 draft Preparedness articles.

Read-only, offline, deterministic. SHA and file ancestry protect QA carry-forward,
NOT the accuracy or medical safety of source claims. Never yields a PASS or release flag.
Issue #136; conversion coordination #820. No network, CMS, merchant or analytics writes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r209-qa-dependency-custody-v1'
SHA = re.compile(r'[0-9a-f]{40}\Z')
FROZEN_HEADS = {
    'start': '2122d856fce9f64887c16df3d52e64be9f59a55b',
    'shelter': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'food': 'f911ff7a655de8d81535ea86ec3d65a49ee76648',
    'health': 'd5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
    'hist-field': '4e5caf812727953aa45e3bda2d382f2c67b6a09c',
    'hist-food': '67e116e536c7410bed30f8f3b1bb8c166f3c223d',
    'hist-home': '7504a5f099594d635e3dd7332a33a2e1346c43a2',
}
# Immutable, separately fetched GitHub PR and file evidence (not approval).
REVIEW_PRS = {
    '157': {
        'base_sha': '10f58fed1ba808056813064ca5f9680589db8da1',
        'head_sha': '7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
        'files': {
            'preparedness/content/articles/household-emergency-plan.body.html': ('8ca5c261dba56eeaf79c445332381a74867233de','6407a31a882211e62c00f4e07ec7dc4d5abf99c6'),
            'preparedness/content/articles/three-day-kit.body.html': ('ef5463ca668166766ca3d868908bc0bcb6040a23','f578cdbae602c1ad58a9237c8dea0fd74c99f7da'),
            'preparedness/sources/fragments/start.json': ('29574c328cbab0548e6e5d4a026694857d56b6b4','d5a5087042381227d840675d9eb08ddc375d21e8'),
            'preparedness/taxonomy.json': ('eea601e53e16e36cd4fc890876bc249b39632370','d20ff18bc6f243e08796c0505981979a10fca2d9'),
            'preparedness/tests/test_preparedness.py': ('dd1e7bc35cc83da6174c56464583cbbadfd6751f','32627489b7727d97ac54663d87ac8d112911c811'),
        },
    },
    '169': {
        'base_sha': '4b009361277ea1d4617b368f5d45104c7318b284',
        'head_sha': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
        'files': {'preparedness/tests/test_preparedness.py': ('50926c2f77bf783a682a4d1ee25ed14de9ff7995','e80d622c2fd32bf6c9752e375c1208c1d47d8e7c')},
    },
    '973': {
        'base_sha': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
        'head_sha': '4d40996a559b0124d74a9bb3bdcd481ad1992aa8',
        'files': {'preparedness/tests/test_preparedness.py': ('e80d622c2fd32bf6c9752e375c1208c1d47d8e7c','a66aa6f76cbae869f1327ff06ea5f13fd3845a64')},
    },
}
REVIEW_CASES = (
    ('homemade-water-filters', 'cdc-find-clean-water', 2),
    ('preparedness-real-households', 'start-ready-plan', 1),
)

class Violation(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise Violation(message)

def safe_json(path):
    def pairs_unique(pairs):
        out = {}
        for k, v in pairs:
            need(k not in out, 'duplicate JSON key: '+k)
            out[k] = v
        return out
    def bad_constant(s):
        raise Violation('invalid JSON constant: '+s)
    return json.loads(Path(path).read_text('utf-8'), object_pairs_hook=pairs_unique, parse_constant=bad_constant)

def audit(manifest, observations, candidate_oids=None):
    result = dict(schema=SCHEMA, issue=136, conversion_issue=820, state=INVALID,
                  publication_authorized=False, independent_qd_pass=False,
                  source_safety_verified=False, medically_safe=False,
                  merchant_checkout_verified=False, verified_paid_orders=None,
                  realized_net_revenue=None, errors=[], articles=[], qa_requirements=[],
                  source_exceptions=[], summary={})
    try:
        need(type(manifest) is dict and manifest.get('schema') == 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1', 'wrong frozen manifest schema')
        need(manifest.get('issue')==136 and manifest.get('conversion_issue')==820 and manifest.get('state')==HOLD, 'wrong custody scope/state')
        for flag in ('publication_authorized','independent_qd_pass','human_source_approved','medical_safety_verified','merchant_offer_verified'):
            need(manifest.get(flag) is False, 'unsafe manifest approval: '+flag)
        need(manifest.get('verified_paid_orders') is None and manifest.get('realized_net_revenue') is None,'fabricated revenue')
        rows = manifest.get('articles')
        need(type(rows) is list and len(rows)==35 and manifest.get('artifact_count')==35 and manifest.get('export_target_count_with_six_tools')==41, '35 article / 41 output custody drift')
        need(manifest.get('branch_heads') == FROZEN_HEADS,'unexpected Claude branch provenance')
        slugs=set(); routes=set(); body_oids={}
        for i, row in enumerate(rows, 1):
            need(type(row) is dict and row.get('n')==i,'missing/reordered article')
            slug=row.get('slug'); section=row.get('section'); cluster=row.get('source_cluster')
            need(type(slug) is str and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) is not None, 'invalid article slug')
            need(type(section) is str and type(cluster) is str and cluster in FROZEN_HEADS, 'bad source cluster/section')
            route=f'/preparedness/{section}/{slug}/'
            need(row.get('route')==route and slug not in slugs and route not in routes, 'duplicate or changed article route')
            need(row.get('branch_sha')==FROZEN_HEADS[cluster], 'article source branch drift: '+slug)
            need(all(type(row.get(k)) is str and SHA.fullmatch(row[k]) for k in ('body_oid','meta_oid')), 'missing original Git object: '+slug)
            need(type(row.get('body_bytes')) is int and row['body_bytes']>0 and type(row.get('meta_bytes')) is int and row['meta_bytes']>0, 'invalid article source length: '+slug)
            slugs.add(slug);routes.add(route);body_oids[slug]=row['body_oid']
        need(type(observations) is dict and set(observations)==set(REVIEW_PRS), 'missing or extra independent QA PR observations')
        for pr, expected in REVIEW_PRS.items():
            observed=observations[pr]
            need(type(observed) is dict and observed.get('state')=='open' and observed.get('draft') is True, 'review PR must remain open draft: '+pr)
            need(observed.get('base_sha')==expected['base_sha'] and observed.get('head_sha')==expected['head_sha'], 'independent PR commit drift: '+pr)
            files=observed.get('files')
            need(type(files) is dict and files == {k: list(v) for k,v in expected['files'].items()},'independent PR changed-path or blob drift: '+pr)
            result['qa_requirements'].append({'pr':int(pr), 'head_sha':expected['head_sha'],
                 'paths':sorted(files), 'decision':'PENDING_INDEPENDENT_REVIEW', 'merge_authorized':False})
        need(REVIEW_PRS['973']['base_sha']==REVIEW_PRS['169']['head_sha'], 'broken fixture PR chain')
        for slug, sid, count in REVIEW_CASES:
            need(slug in slugs,'missing cited article '+slug)
            result['source_exceptions'].append({'article':slug,'source_id':sid,
                'affected_citation_occurrences':count,'state':'HUMAN_SUPPORT_REVIEW_REQUIRED'})
        result['source_exceptions'].append({'category':'historical_source_identifier_collisions',
                                            'recorded_count':7,'state':'HUMAN_ADJUDICATION_REQUIRED'})
        if candidate_oids is not None:
            need(type(candidate_oids) is dict and set(candidate_oids)==slugs, 'missing or extraneous integration article')
        for slug in sorted(slugs):
            chosen = candidate_oids.get(slug) if candidate_oids is not None else None
            original=body_oids[slug]
            qa_path=f'preparedness/content/articles/{slug}.body.html'
            proposal=REVIEW_PRS['157']['files'].get(qa_path)
            if chosen is None: disposition='NOT_RENDERED_OR_NOT_INTEGRATED'
            else:
                need(type(chosen) is str and SHA.fullmatch(chosen), 'invalid proposed article identity: '+slug)
                if chosen==original: disposition='FROZEN_ORIGINAL_UNREVIEWED'
                elif proposal is not None and chosen==proposal[1]: disposition='INDEPENDENT_QA_PROPOSAL_NOT_APPROVED'
                else: raise Violation('unknown integration article blob (requires separate review): '+slug)
            result['articles'].append({'slug':slug,'original_oid':original,
                'candidate_oid':chosen,'status':disposition,'safety_review':'PENDING'})
        result['summary']={'original_article_count':35,'export_targets_requiring_native_validation':41,
           'independent_qa_prs_preserved':3,'qa_changed_path_witnesses':7,
           'unexplained_citation_occurrences':3,'historical_shared_source_conflicts':7,
           'candidate_articles_supplied':candidate_oids is not None,
           'complete_native_build_or_qd_approved':False}
        result['state']=HOLD
    except (ValueError, KeyError, TypeError, IndexError) as e:
        result['errors'].append(str(e))
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True)
    p.add_argument('--observations',required=True)
    p.add_argument('--candidates',help='Optional complete slug:Git-blob-ID integration map')
    p.add_argument('--report',required=True)
    args=p.parse_args(argv)
    try:
        result=audit(safe_json(args.manifest),safe_json(args.observations),
                     safe_json(args.candidates) if args.candidates else None)
    except (OSError, ValueError, UnicodeError) as e:
        result={'schema':SCHEMA,'state':INVALID,'errors':[str(e)],
                'publication_authorized':False,'independent_qd_pass':False}
    Path(args.report).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n','utf-8')
    print(result['state']+'; '+', '.join(result.get('errors',[])))
    return 2 if result['state']==HOLD else 3
if __name__ == '__main__':
    raise SystemExit(main())
