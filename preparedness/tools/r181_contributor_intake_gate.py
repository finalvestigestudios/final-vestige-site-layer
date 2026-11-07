#!/usr/bin/env python3
"""Read-only admission gate for unmerged Preparedness contributor/QA branches.

An exact SHA and a passing structural check are not human source or safety approval.
This command NEVER returns a release-ready result (exit code 2 for valid HOLD).
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

HOLD='DRAFT_HARD_HOLD'
INVALID='INVALID_HARD_HOLD'
REPO='finalvestigestudios/final-vestige-site-layer'
SCHEMA='fv-preparedness-r181-contributor-intake-v1'
BRANCHES={
 'claude/prep-start-bbfeb8':'2122d856fce9f64887c16df3d52e64be9f59a55b',
 'claude/prep-food-ccdc55':'f911ff7a655de8d81535ea86ec3d65a49ee76648',
 'claude/prep-shelter-5e1e0e':'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
 'claude/prep-health-837444':'d5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
 'claude/prep-hist-field-9db767':'4e5caf812727953aa45e3bda2d382f2c67b6a09c',
 'claude/prep-hist-food-b81f19':'67e116e536c7410bed30f8f3b1bb8c166f3c223d',
 'claude/prep-hist-home-0e0e38':'7504a5f099594d635e3dd7332a33a2e1346c43a2',
}
PR_HEADS={157:'7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
          169:'e9cd7766dac59d47ab467d8945269b9146c2aef5',
          973:'4d40996a559b0124d74a9bb3bdcd481ad1992aa8'}
PR_BASES={157:'10f58fed1ba808056813064ca5f9680589db8da1',
          169:'4b009361277ea1d4617b368f5d45104c7318b284',
          973:'e9cd7766dac59d47ab467d8945269b9146c2aef5'}
PR_FILES={157:{'preparedness/content/articles/household-emergency-plan.body.html',
               'preparedness/content/articles/three-day-kit.body.html',
               'preparedness/sources/fragments/start.json',
               'preparedness/taxonomy.json','preparedness/tests/test_preparedness.py'},
          169:{'preparedness/tests/test_preparedness.py'},
          973:{'preparedness/tests/test_preparedness.py'}}
SAFE_FALSE=('publication_authorized','independent_qd_pass','modern_safety_approved',
            'medical_safety_approved','qualified_food_safety','commercial_offer_verified',
            'verified_paid_preparedness_sku','paid_checkout_enabled')


def require(ok, message):
    if not ok: raise ValueError(message)


def sha40(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{40}',value) is not None


def deep_no_false_clearance(obj, where='root'):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in SAFE_FALSE: require(v is False, f'{where}.{k}: unauthorized clearance')
            deep_no_false_clearance(v,f'{where}.{k}')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): deep_no_false_clearance(v,f'{where}[{i}]')


def inspect(observed):
    require(isinstance(observed,dict) and observed.get('schema')==SCHEMA,'schema mismatch')
    require(observed.get('repo')==REPO,'repository mismatch')
    require(observed.get('state')==HOLD,'release HOLD missing')
    deep_no_false_clearance(observed)
    branches=observed.get('branches')
    require(isinstance(branches,list) and len(branches)==7,'exact seven contributor branches required')
    require(Counter(r.get('ref') for r in branches)==Counter({b:1 for b in BRANCHES}), 'missing or duplicate branch')
    for r in branches:
        require(r.get('sha')==BRANCHES[r['ref']] and sha40(r.get('sha')),
                f'branch head changed: {r["ref"]}')
        require(r.get('status')=='identical' and r.get('ahead')==0 and r.get('behind')==0,
                f'branch drift: {r["ref"]}')
    prs=observed.get('review_prs')
    require(isinstance(prs,list) and len(prs)==3,'exact three independent review PRs required')
    require(Counter(r.get('number') for r in prs)==Counter({n:1 for n in PR_HEADS}),'missing or duplicate PR')
    for p in prs:
        n=p['number']; got=set(p.get('files',[]))
        require(p.get('head_sha')==PR_HEADS[n] and p.get('base_sha')==PR_BASES[n],
                f'PR #{n} head/base change')
        require(p.get('state')=='open' and p.get('draft') is True and p.get('merged') is False,
                f'PR #{n} no longer an unmerged draft')
        require(isinstance(p.get('files'),list) and len(got)==len(p['files']) and got==PR_FILES[n],
                f'PR #{n} unexpected changed-file scope')
    require(PR_BASES[973]==PR_HEADS[169],'fixture successor ancestry invalid')
    collisions={}
    for i in sorted(PR_FILES):
        for j in sorted(PR_FILES):
            if i<j:
                shared=sorted(PR_FILES[i]&PR_FILES[j])
                if shared:collisions[f'{i}/{j}']=shared
    require(collisions=={'157/169':['preparedness/tests/test_preparedness.py'],
                         '157/973':['preparedness/tests/test_preparedness.py'],
                         '169/973':['preparedness/tests/test_preparedness.py']},
            'expected patch-collision inventory changed')
    corpus=observed.get('corpus')
    require(isinstance(corpus,dict) and corpus.get('branch_sha')==
            '532198896128e612e88b3bee36c6368cb825e58b', 'corpus SHA mismatch')
    require((corpus.get('article_meta'), corpus.get('article_bodies'),
             corpus.get('source_uses'), corpus.get('citation_occurrences'))==(35,35,385,2000),
            'authored 35/35/385/2000 inventory not evidenced')
    require(corpus.get('all_draft') is True and corpus.get('unique_urls') is True,
            'article publication/route custody unknown')
    require(corpus.get('qualified_safety_review') is False and
            corpus.get('independent_qd_pass') is False and
            corpus.get('publication_authorized') is False,
            'human safety and QD clearance cannot be inferred')
    business=observed.get('funnel')
    require(isinstance(business,dict) and business.get('audience')==
            'caregivers_school_pickup_reunification','high-intent audience changed')
    require(business.get('free_guide')=='household-emergency-plan' and
            business.get('optional_tool')=='family-reunification-card',
            'authentic free guide/tool lineage changed')
    require(business.get('paid_sku') is None and
            business.get('verified_paid_preparedness_sku') is False and
            business.get('paid_checkout_enabled') is False,
            'no authenticated paid Preparedness SKU/checkout available')
    require(business.get('grok_asset_id') is None and
            business.get('published_destination') is None,
            'Grok asset/destination unverified in TASK-008')
    require(business.get('verified_orders') is None and
            business.get('net_revenue_usd') is None,
            'cannot invent sales or net revenue')
    digest=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':SCHEMA,'state':HOLD,'observation_sha256':digest,
            'claude_branches_intact':7,'independent_prs_held':3,
            'overlap_paths':collisions,'article_meta_count':35,
            'article_body_count':35,'citation_occurrences':2000,
            'authored_source_uses':385,'publication_authorized':False,
            'independent_qd_pass':False,'commercial_offer_verified':False,
            'unresolved':'review #157 safety corrections and #169/#973 test fixture changes require explicit non-destructive integration and independent QA; paid SKU/asset/order not evidenced'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observed',required=True,type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        raw=json.loads(args.observed.read_text(encoding='utf-8'))
        result=inspect(raw)
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as e:
        result={'schema':SCHEMA,'state':INVALID,'error':str(e),'publication_authorized':False}
    report=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:
        try: args.output.write_text(report,encoding='utf-8')
        except OSError as e: print(f'output unavailable: {e}',file=sys.stderr)
    print(report,end='')
    return 2

if __name__=='__main__': sys.exit(main())
