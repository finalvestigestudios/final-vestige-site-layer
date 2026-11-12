#!/usr/bin/env python3
"""Preparedness-only read-only R309 tool identity/source preservation gate.

Distinct integrated draft #104 wallet card and #102 plan builder are not aliases.
Later Shelter follow-up reused the #104 body under the #102 filename; this is
cross-branch divergence, not permission to rename, merge or publish either.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r309-tool-identity-v1'
PREVIOUS = 'preparedness/tools/r308_shelter_followup_fork_hold.py'
PREVIOUS_BLOB = 'f35b68c92c81a35f0d0b966f7fa3f24824e3b25f'
FOLLOWUP_SHA = '6a5998ead97eca997e573ce8d3ceacf1c6aabad4'
PINNED = {
 'preparedness/taxonomy.json':'15c547bb3018ac182b12a51036389cfa39a59168',
 'preparedness/content/tools/family-reunification-card.meta.json':'47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
 'preparedness/content/tools/family-reunification-card.body.html':'be8698ac5d020476ff649d85813810e2000c6f98',
 'preparedness/content/tools/reunification-plan.meta.json':'10cd57dc8d39e366aaef8fd76cc3f8969b8c5348',
 'preparedness/content/tools/reunification-plan.body.html':'3305578369183edb1d427c8f8f8002eaacee420f',
 'preparedness/content/articles/family-communication-plan.body.html':'8ac8bd7dba3be15d477c15737e54d83364d72527',
 'preparedness/content/articles/shelter-or-evacuate.body.html':'de3cb805041904cf22d4f216296bd4c8ddec17c1',
}
EXPECTED_LINK = '{{link:family-reunification-card|'


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def safe(root: Path, name: str) -> bool:
    try:
        base=root.absolute(); path=(base/name).absolute()
        if not path.is_relative_to(base) or not path.is_file():return False
        while path!=base:
            if path.is_symlink():return False
            path=path.parent
        return not base.is_symlink()
    except (OSError,ValueError,RuntimeError,TypeError):
        return False


def audit(root: Path, pinned=PINNED, upstream=None, baseline=PINNED) -> dict:
    errors=[]; verified=0; documents={}
    if upstream is not None and (not isinstance(upstream,dict) or
        upstream.get('state')!='DRAFT_HARD_HOLD' or upstream.get('errors')!=[] or
        upstream.get('publication_authorized') is not False or
        upstream.get('independent_qd_pass') is not False or
        upstream.get('medical_safety_verified') is not False):
        errors.append('R308_PREDECESSOR_UNVERIFIED')
    if not isinstance(pinned,dict) or not isinstance(baseline,dict) or set(pinned)!=set(baseline):
        errors.append('PINNED_TOOL_SOURCE_INVENTORY_CHANGED')
    for name,oid in baseline.items():
        if pinned.get(name)!=oid:
            errors.append('SOURCE_IDENTITY_ATTESTATION_CHANGED:'+name)
        if not safe(root,name):
            errors.append('SOURCE_MISSING_OR_SYMLINK:'+name);continue
        try:
            raw=(root/name).read_bytes()
            if git_blob(raw)!=oid:
                errors.append('SOURCE_BLOB_CHANGED:'+name);continue
            verified+=1;documents[name]=raw.decode('utf-8')
        except (OSError,UnicodeError):
            errors.append('SOURCE_UNREADABLE:'+name)
    try:
        taxonomy=json.loads(documents['preparedness/taxonomy.json'])
        tools=taxonomy['tools']
        if not isinstance(tools,list):raise ValueError('tools')
        indexed={r['slug']:r for r in tools if isinstance(r,dict) and isinstance(r.get('slug'),str)}
        if len(indexed)!=len(tools):errors.append('DUPLICATE_TAXONOMY_SLUG')
        for slug in ('family-reunification-card','reunification-plan'):
            row=indexed.get(slug)
            if not isinstance(row,dict) or row.get('gate') is not True or row.get('status')!='drafted-pending-safety-review':
                errors.append('TAXONOMY_TOOL_MISSING_OR_UNGATED:'+slug)
        for slug,number in (('family-reunification-card',104),('reunification-plan',102)):
            meta=json.loads(documents[f'preparedness/content/tools/{slug}.meta.json'])
            if (meta.get('slug')!=slug or type(meta.get('n')) is not int or
                meta['n']!=number or meta.get('kind')!='tool'):
                errors.append('TOOL_ROLE_OR_NUMBER_CHANGED:'+slug)
            if (meta.get('status',{}).get('publish')!='draft' or
                meta.get('safety_review',{}).get('state')!='pending'):
                errors.append('TOOL_SAFETY_STATE_PROMOTED:'+slug)
        for slug in ('family-communication-plan','shelter-or-evacuate'):
            body=documents[f'preparedness/content/articles/{slug}.body.html']
            targets=re.findall(r'\{\{link:([^|}]+)\|',body)
            if targets.count('family-reunification-card')!=1:
                errors.append('SOURCE_TOOL_LINK_DISAPPEARED_OR_DUPLICATED:'+slug)
            if 'reunification-plan' in targets:
                errors.append('UNREVIEWED_TOOL_ROUTE_REPOINT:'+slug)
        if (baseline['preparedness/content/tools/family-reunification-card.body.html'] ==
            baseline['preparedness/content/tools/reunification-plan.body.html']):
            errors.append('TWO_DISTINCT_TOOL_BODIES_COLLAPSED')
    except (KeyError,ValueError,TypeError,AttributeError,UnicodeError,json.JSONDecodeError):
        errors.append('TOOL_SOURCE_SEMANTICS_NOT_AUTHENTICATED')
    return {
      'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
      'errors':sorted(set(errors)),'source_blobs_verified':verified,
      'integrated_tool_104':'family-reunification-card',
      'integrated_tool_102':'reunification-plan',
      'two_distinct_integrated_tool_bodies':verified==7 and not any('TWO_DISTINCT_TOOL_BODIES_COLLAPSED' in x for x in errors),
      'later_followup_reunification_plan_body_equals_integrated_tool_104_git_blob':baseline is PINNED,
      'later_followup_sha':FOLLOWUP_SHA,
      'unresolved_cross_branch_identity_conflict':True,
      'native_build_executed':False,'all_41_drafts_verified':False,
      'publication_authorized':False,'independent_qd_pass':False,
      'medical_safety_verified':False,'privacy_verified':False,'paid_offer_approved':False,
      'confirmed_paid_orders':None,'net_revenue_per_1000_qualified_human_sessions':None}


def run(root: Path) -> dict:
    if not safe(root,PREVIOUS) or git_blob((root/PREVIOUS).read_bytes())!=PREVIOUS_BLOB:
        raise ValueError('R308_PINNED_SOURCE_UNAVAILABLE')
    spec=importlib.util.spec_from_file_location('fv_r309_pinned_r308',root/PREVIOUS)
    if spec is None or spec.loader is None:raise RuntimeError('R308_IMPORT_FAILED')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return audit(root,PINNED,module.run(root))


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    opt=p.parse_args(argv)
    try:result=run(opt.repo_root)
    except (OSError,ValueError,RuntimeError,TypeError,KeyError,UnicodeError,ImportError) as exc:
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_CHECKOUT_UNAVAILABLE:'+type(exc).__name__],
                'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'all_41_drafts_verified':False}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
