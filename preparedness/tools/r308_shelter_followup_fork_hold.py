#!/usr/bin/env python3
"""R308: fail-closed, read-only Shelter follow-up fork custody gate.

The seven canonical Claude cluster branches remain frozen to R200. This checks
an *additional*, nine-commit Shelter follow-up against the R307 integrated
candidate. An OID mismatch is evidence of differing bytes, NEVER a license to
merge, change safety wording, or approve publication. No network or file writes.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r308-shelter-fork-custody-v1'
PINNED_R307_PATH = 'preparedness/tools/r307_frozen_normalization_proof_hold.py'
PINNED_R307_BLOB = '057307e4d8696e08308de77d36a95b5ef1d44477'
R307_HEAD = '6a8de471668f37f6dbaffa21d52d0abf6290e55e'
FROZEN_SHELTER_HEAD = '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976'
CONTINUATION_HEAD = 'ac8625faf30dd5538fadc31e06cb5a2cea1defae'
FOLLOWUP_HEAD = '6a5998ead97eca997e573ce8d3ceacf1c6aabad4'
# (relative path below preparedness/, integrated R307 blob, later Shelter blob)
OBSERVED = (
 ('content/articles/family-communication-plan.body.html','8ac8bd7dba3be15d477c15737e54d83364d72527','c97a79761dc3be1c44e5f9322a606ccc7fd11c6e'),
 ('content/articles/family-communication-plan.meta.json','dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3','a8618235711cca039f142ad59962c1153654aa45'),
 ('content/articles/home-fire-escape-plan.body.html','0412484304a3bcf08f0bb1b170110f617e3c2869','b8db7be7e0482334d8356f35616f21f36aaa2d4d'),
 ('content/articles/home-fire-escape-plan.meta.json','ff1246dcbfb0dd0bc864977f815badb9ad4e7ed8','7b76ebe8887c8d673fb4d2c14957ddee5233c4a9'),
 ('content/articles/outage-heat-cold-generators.body.html','2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2','5608a28249a0e351710e0c756d878048c8e41e24'),
 ('content/articles/outage-heat-cold-generators.meta.json','be37b602d0b82593d438083dfc8a1e5ef595dd44','593e7bd6fef0446f05d7a86551e702ceaa38eabb'),
 ('content/articles/shelter-or-evacuate.body.html','de3cb805041904cf22d4f216296bd4c8ddec17c1','a8c36cd63517fdeb723dca201b31802c2a721ddf'),
 ('content/articles/shelter-or-evacuate.meta.json','cb559141d1e4a39debad16cf5cb796b746a01f19','fb1081527e5afdd542299f2087397cf3308716c6'),
 ('content/tools/home-fire-escape-worksheet.body.html','01161948b6de6ffbd1b053c9b83a420758e707e4','01161948b6de6ffbd1b053c9b83a420758e707e4'),
 ('content/tools/home-fire-escape-worksheet.meta.json','397c7d3072fb237b490a5a316c93fc863c101be9','397c7d3072fb237b490a5a316c93fc863c101be9'),
 ('content/tools/power-outage-planner.body.html','aa8f866aaaaab9253f41c4363d31919029c69234','aa8f866aaaaab9253f41c4363d31919029c69234'),
 ('content/tools/power-outage-planner.meta.json','8796bba2b323cce096639997002c402bd853e50f','8796bba2b323cce096639997002c402bd853e50f'),
 ('content/tools/reunification-plan.body.html','3305578369183edb1d427c8f8f8002eaacee420f','be8698ac5d020476ff649d85813810e2000c6f98'),
 ('content/tools/reunification-plan.meta.json','10cd57dc8d39e366aaef8fd76cc3f8969b8c5348','d4776aad104f59cfc50305e8eeed5220ec201cd5'),
 ('sources/fragments/shelter.json','2a3f1a7ddeab2782add875be1e0e378513504aa1','5105f4bbd7d5b2e991f28d4b4ae7c9d5a2804aa9'),
 ('taxonomy.json','15c547bb3018ac182b12a51036389cfa39a59168','4dce806ffd8bac7918645df77d2be8b1fb520aeb'),
)
SHA = re.compile(r'[0-9a-f]{40}\Z')

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def secure_file(root: Path, rel: str) -> bool:
    try:
        if not isinstance(rel, str) or rel.startswith('/') or '..' in Path(rel).parts:
            return False
        base=root.absolute()
        if base.is_symlink(): return False
        path=(base/rel).absolute()
        if not path.is_relative_to(base) or not path.is_file(): return False
        current=path
        while current != base:
            if current.is_symlink():return False
            current=current.parent
        return True
    except (OSError,ValueError,RuntimeError,TypeError):
        return False

def audit(root: Path, rows=OBSERVED, prior=None, heads=None) -> dict:
    """Inspect local R307 bytes; later source OIDs are remote comparison evidence only."""
    errors=[]; checked=0; matching=0; divergent=0; kinds={}
    heads = dict(heads or {'frozen':FROZEN_SHELTER_HEAD,'continuation':CONTINUATION_HEAD,
                           'followup':FOLLOWUP_HEAD,'integrated':R307_HEAD})
    expected_heads={'frozen':FROZEN_SHELTER_HEAD,'continuation':CONTINUATION_HEAD,
                    'followup':FOLLOWUP_HEAD,'integrated':R307_HEAD}
    if heads != expected_heads:errors.append('BRANCH_IDENTITY_DRIFT')
    if not isinstance(prior,dict) or prior.get('state')!='DRAFT_HARD_HOLD' or prior.get('errors')!=[]:
        errors.append('R307_UNVERIFIED')
    else:
        for key,val in (('bound_format_proofs',4),('substantive_body_differences_unadjudicated',10),
                        ('metadata_differences_unadjudicated',12)):
            if type(prior.get(key)) is not int or prior[key]!=val:
                errors.append('R307_LINEAGE_COUNT_MISMATCH:'+key)
        for key in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                    'privacy_verified','paid_offer_approved','all_41_drafts_verified'):
            if prior.get(key) is not False:errors.append('R307_FALSE_RELEASE:'+key)
    if not isinstance(rows,(tuple,list)) or len(rows)!=16:
        errors.append('INCOMPLETE_SHELTER_FORK_MATRIX'); rows=[]
    seen=set()
    for item in rows:
        if not isinstance(item,(tuple,list)) or len(item)!=3:
            errors.append('INVALID_FORK_RECORD');continue
        rel,integrated,followup=item
        if not isinstance(rel,str) or rel in seen:
            errors.append('DUPLICATE_OR_INVALID_PATH');continue
        seen.add(rel)
        if not all(isinstance(v,str) and SHA.fullmatch(v) for v in (integrated,followup)):
            errors.append('INVALID_GIT_BLOB:'+rel);continue
        expected=dict((p,(a,b)) for p,a,b in OBSERVED).get(rel)
        if expected is None or (integrated,followup)!=expected:
            errors.append('UNAPPROVED_FORK_EVIDENCE_DRIFT:'+rel)
        category=('article' if rel.startswith('content/articles/') else
                  'tool' if rel.startswith('content/tools/') else 'registry')
        kinds[category]=kinds.get(category,0)+1
        if integrated==followup:matching+=1
        else:divergent+=1
        file='preparedness/'+rel
        if not secure_file(root,file):
            errors.append('MISSING_OR_SYMLINK_SOURCE:'+rel);continue
        try:
            if git_blob((root/file).read_bytes())!=integrated:
                errors.append('INTEGRATED_CONTENT_DRIFT:'+rel)
            else:checked+=1
        except OSError:errors.append('UNREADABLE_SOURCE:'+rel)
    if seen!=set(p for p,_,_ in OBSERVED):errors.append('FORK_INVENTORY_DRIFT')
    if (checked,matching,divergent)!=(16,4,12):errors.append('FORK_COUNTS_NOT_VERIFIED')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'integrated_git_blobs_verified':checked,
            'matching_followup_oids_observed':matching,'divergent_followup_oids_unadjudicated':divergent,
            'scope_counts':kinds,'canonical_seven_branches_unchanged_by_this_gate':True,
            'followup_branch_sha':FOLLOWUP_HEAD,'source_comparison_scope':'GitHub blob OID comparisons; later content not locally executed',
            'native_build_executed':False,'all_41_drafts_verified':False,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_verified':False,'paid_offer_approved':False,
            'confirmed_paid_orders':None,'net_revenue_per_1000_qualified_human_sessions':None}

def run(root: Path) -> dict:
    if not secure_file(root,PINNED_R307_PATH) or git_blob((root/PINNED_R307_PATH).read_bytes()) != PINNED_R307_BLOB:
        raise ValueError('PINNED_R307_MISSING_OR_MUTATED')
    path=root/PINNED_R307_PATH
    spec=importlib.util.spec_from_file_location('fv_r308_pinned_r307',path)
    if spec is None or spec.loader is None:raise RuntimeError('R307_IMPORT_UNAVAILABLE')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return audit(root,OBSERVED,mod.run(root))

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    args=p.parse_args(argv)
    try:r=run(args.repo_root)
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,UnicodeError) as exc:
        r={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
           'errors':['AUTHENTIC_CHECKOUT_UNAVAILABLE:'+type(exc).__name__],
           'publication_authorized':False,'independent_qd_pass':False,
           'medical_safety_verified':False,'all_41_drafts_verified':False}
    print(json.dumps(r,sort_keys=True,indent=2))
    return 2 if r['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
