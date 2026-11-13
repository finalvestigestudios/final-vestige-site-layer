#!/usr/bin/env python3
"""R341: frozen nine-branch source divergence triage, NOT an adjudication or release.

A read-only control that binds the R334 raw-object crosswalk to the R336
41-entry source witness, and generates a human review docket. A matching Git
blob does NOT prove claims, editorial completeness, or suitability for release.
The old 15 editorial conflicts and 17 Article15/Tool104 claims stay separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r341-nine-head-conflict-review-hold-v1'
CROSSWALK_SCHEMA = 'fv-preparedness-r334-frozen-nine-head-source-object-crosswalk-v1'
WITNESS_SCHEMA = 'fv-preparedness-r336-41-entry-frozen-custody-v1'
CROSSWALK_GIT_BLOB = 'c0af8552b17110d4c67d6d20ef9f8744fbb96e90'
WITNESS_GIT_BLOB = 'ff714125b0e785248819acc1358f912b470f4a69'
INTEGRATION_BASE = '74a3d268caccc0a0ae32d9f1c916ddaba3cb6ce7'
ARTICLE15_BODY_BLOB = '8ac8bd7dba3be15d477c15737e54d83364d72527'
HEADS = {
    'start':'2122d856fce9f64887c16df3d52e64be9f59a55b',
    'food':'f911ff7a655de8d81535ea86ec3d65a49ee76648',
    'health':'d5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
    'hist-field':'4e5caf812727953aa45e3bda2d382f2c67b6a09c',
    'hist-food':'67e116e536c7410bed30f8f3b1bb8c166f3c223d',
    'hist-home':'7504a5f099594d635e3dd7332a33a2e1346c43a2',
    'shelter':'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'shelter-continuation':'ac8625faf30dd5538fadc31e06cb5a2cea1defae',
    'shelter-followup':'6a5998ead97eca997e573ce8d3ceacf1c6aabad4',
}
# 14 raw shared-file divergences, not the 15 legacy adjudication claims.
# These pins are derived from the authenticated integrated source tree.
INTEGRATED = {
 'preparedness/content/articles/family-communication-plan.body.html':'8ac8bd7dba3be15d477c15737e54d83364d72527',
 'preparedness/content/articles/family-communication-plan.meta.json':'dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3',
 'preparedness/content/articles/home-fire-escape-plan.body.html':'0412484304a3bcf08f0bb1b170110f617e3c2869',
 'preparedness/content/articles/home-fire-escape-plan.meta.json':'ff1246dcbfb0dd0bc864977f815badb9ad4e7ed8',
 'preparedness/content/articles/outage-heat-cold-generators.body.html':'2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2',
 'preparedness/content/articles/outage-heat-cold-generators.meta.json':'be37b602d0b82593d438083dfc8a1e5ef595dd44',
 'preparedness/content/articles/shelter-or-evacuate.body.html':'de3cb805041904cf22d4f216296bd4c8ddec17c1',
 'preparedness/content/articles/shelter-or-evacuate.meta.json':'cb559141d1e4a39debad16cf5cb796b746a01f19',
 'preparedness/content/tools/power-outage-planner.body.html':'aa8f866aaaaab9253f41c4363d31919029c69234',
 'preparedness/content/tools/power-outage-planner.meta.json':'8796bba2b323cce096639997002c402bd853e50f',
 'preparedness/content/tools/reunification-plan.body.html':'3305578369183edb1d427c8f8f8002eaacee420f',
 'preparedness/content/tools/reunification-plan.meta.json':'10cd57dc8d39e366aaef8fd76cc3f8969b8c5348',
 'preparedness/sources/fragments/shelter.json':'2a3f1a7ddeab2782add875be1e0e378513504aa1',
 'preparedness/taxonomy.json':'15c547bb3018ac182b12a51036389cfa39a59168',
}
# A mechanical source match is expressly not a conflict resolution.
SAME_AS_ONE_CONTRIBUTOR = {
 'preparedness/content/tools/power-outage-planner.body.html',
 'preparedness/content/tools/power-outage-planner.meta.json',
}
GROUPS = {
 'family-communication-plan':('articles', 'P0', 'emergency communication, 911 jurisdiction, reunification, service-animal access'),
 'home-fire-escape-plan':('articles', 'P0', 'household fire and evacuation safety'),
 'outage-heat-cold-generators':('articles', 'P0', 'generator/CO, heat and cold hazards'),
 'shelter-or-evacuate':('articles', 'P0', 'shelter/evacuation scope and local orders'),
 'power-outage-planner':('tools', 'P0', 'tool inputs, electricity and life-safety instructions'),
 'reunification-plan':('tools', 'P0', 'tool privacy, local school procedures and identity separate from Tool #104'),
 'shelter-source-fragment':('sources', 'P0', 'source provenance and citation-to-claim support'),
 'taxonomy':('taxonomy', 'P0', '35-article routes, review state, safety gate identities'),
}
PENDING = 'REQUIRES_QUALIFIED_SOURCE_AND_EDITORIAL_ADJUDICATION'
SERVICE_ANIMAL_KEY = 'article15.shelter.service_animal_pet_assistance_scope'
SERVICE_ANIMAL_ANCHOR = 'Many public shelters allow only service animals'
ALLOWED_RELEASE_FALSE = ('qualified_qd_pass','may_merge','may_publish','source_conflict_human_signoff',
                         'citation_claim_support_verified')
HEX40 = re.compile(r'^[0-9a-f]{40}$')


def git_blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def group_for_path(path:str)->str:
    if path=='preparedness/taxonomy.json':return 'taxonomy'
    if path=='preparedness/sources/fragments/shelter.json':return 'shelter-source-fragment'
    match = re.fullmatch(r'preparedness/content/(articles|tools)/([a-z0-9-]+)\.(?:body\.html|meta\.json)',path)
    if not match or match.group(2) not in GROUPS or GROUPS[match.group(2)][0]!=match.group(1):
        raise ValueError('NONCANONICAL_OR_UNSCOPED_CONFLICT_PATH')
    return match.group(2)


def result(errors:list[str], packets:list[dict]|None=None, counters:dict|None=None)->dict:
    return {
      'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
      'errors':sorted(set(errors)),'raw_object_divergences_expected':14,
      'legacy_editorial_conflicts_unresolved':15,
      'article15_original_claims_unresolved':9,'tool104_original_claims_unresolved':8,
      'newly_identified_article15_service_animal_scope_review':SERVICE_ANIMAL_KEY,
      'requires_independent_disability_access_and_legal_review':True,
      'counts':counters or {},'human_review_packets':packets or [],
      'authenticated_full_checkout_tested':False,'native_100_export_build_tested':False,
      'source_claim_support_verified':False,'independent_qd_pass':False,
      'safety_or_medical_advice_approved':False,'paid_sku_verified':False,
      'verified_net_revenue':False,'may_merge':False,'may_publish':False,
      'may_activate_commerce':False,
    }


def check(crosswalk:dict,witness:dict,article15_body:str|None=None)->dict:
    """Read-only crosswalk/provenance check. Synthetic data never imply QD PASS."""
    errors=[]
    if type(crosswalk) is not dict or type(witness) is not dict:
        return result(['AUTHENTIC_FROZEN_DOCUMENTS_REQUIRED'])
    if crosswalk.get('schema')!=CROSSWALK_SCHEMA: errors.append('CROSSWALK_SCHEMA_DRIFT')
    if witness.get('schema')!=WITNESS_SCHEMA: errors.append('WITNESS_SCHEMA_DRIFT')
    if crosswalk.get('source_heads')!=HEADS or witness.get('source_heads')!=HEADS:
        errors.append('NINE_HEAD_SOURCE_CUSTODY_DRIFT')
    if crosswalk.get('integrated_base_commit')!=INTEGRATION_BASE:
        errors.append('INTEGRATED_BASE_CHANGED')
    if crosswalk.get('distinct_source_divergence_count')!=14 or crosswalk.get('unresolved_legacy_adjudication_conflict_count_from_issue136')!=15 or crosswalk.get('divergence_count_is_not_legacy_docket_count') is not True:
        errors.append('RAW_OBJECT_VS_LEGACY_CONFLICT_COUNT_COLLISION')
    if crosswalk.get('integrated_article_bodies')!=35 or crosswalk.get('integrated_tool_bodies')!=6 or crosswalk.get('integrated_missing_body_metadata_pairs')!=[] or crosswalk.get('source_candidate_paths_missing_from_integrated')!=[] or crosswalk.get('source_tree_truncation_detected') is not False:
        errors.append('INTEGRATED_35_ARTICLE_6_TOOL_COVERAGE_DRIFT')
    if set(crosswalk.get('seven_original_clusters',[]))!=set(list(HEADS)[:7]) or set(crosswalk.get('two_shelter_descendants',[]))!=set(list(HEADS)[7:]):
        errors.append('ORIGINAL_CLUSTER_OR_SHELTER_DESCENDANT_LOST')
    if crosswalk.get('scope')!='READ_ONLY_GIT_TREE_OBJECTS_NOT_MERGE_SAFETY_OR_SOURCE_CLAIM_APPROVAL':
        errors.append('SOURCE_OBJECT_IDENTITY_MISREPRESENTED')
    for key in ALLOWED_RELEASE_FALSE+('word_depth_verified','canonical_url_uniqueness_verified'):
        if crosswalk.get(key) is not False: errors.append('CROSSWALK_FORGED_REVIEW_OR_RELEASE:'+key)
    if witness.get('release_state')!='DRAFT_HARD_HOLD' or witness.get('unresolved_holds')!=[
            '15_contributor_conflicts','17_article15_tool104_claims','independent_qualified_safety_review',
            '50_wp_50_preview_native_exports','real_paid_sku_checkout_and_net_revenue']:
        errors.append('WITNESS_RELEASE_OR_HOLD_LEDGER_DRIFT')
    for key in ('qualified_qd_pass','historical_and_emergency_safety_approved','source_claim_support_verified','published_or_live','commercial_sku_verified'):
        if witness.get(key) is not False: errors.append('WITNESS_FALSE_REVIEW_OR_RELEASE:'+key)
    rows=witness.get('entries')
    if not isinstance(rows,list) or len(rows)!=41:
        return result(errors+['EXACT_41_ENTRY_WITNESS_REQUIRED'])
    pairs={(e.get('kind'),e.get('slug')):e for e in rows if type(e) is dict}
    if len(pairs)!=41 or len([k for k in pairs if k[0]=='articles'])!=35 or len([k for k in pairs if k[0]=='tools'])!=6:
        errors.append('WITNESS_ARTICLE_TOOL_IDENTITY_COLLISION')
    divergences=crosswalk.get('differing_shared_source_paths')
    if type(divergences) is not list or len(divergences)!=14:
        return result(errors+['EXACT_14_RAW_SHARED_OBJECT_DIFFS_REQUIRED'])
    seen={}; groups={key:[] for key in GROUPS}; actual_matched=set()
    for item in divergences:
        if type(item) is not dict: errors.append('NONOBJECT_DIVERGENCE');continue
        path=item.get('path'); sha=item.get('integrated_blob')
        if not isinstance(path,str) or path not in INTEGRATED or not isinstance(sha,str):
            errors.append('UNKNOWN_OR_PATH_TRAVERSAL_SOURCE_DIFF');continue
        if path in seen:errors.append('DUPLICATE_RAW_SOURCE_DIFF:'+path)
        seen[path]=sha
        if sha!=INTEGRATED[path] or not HEX40.fullmatch(sha):errors.append('INTEGRATED_BLOB_PIN_CHANGED:'+path)
        try:g=group_for_path(path)
        except ValueError:errors.append('INVALID_SEMANTIC_SOURCE_GROUP:'+path);continue
        groups[g].append(path)
        match=re.fullmatch(r'preparedness/content/(articles|tools)/([a-z0-9-]+)\.(body\.html|meta\.json)',path)
        if match:
            entry=pairs.get((match.group(1),match.group(2)))
            f='body_blob' if match.group(3)=='body.html' else 'meta_blob'
            if not entry or entry.get(f)!=sha:errors.append('41_ENTRY_GIT_SOURCE_WITNESS_DISAGREEMENT:'+path)
        contributors=item.get('contributors')
        if not isinstance(contributors,list) or not contributors:
            errors.append('CONTRIBUTOR_EVIDENCE_MISSING:'+path);continue
        cl=[]
        for c in contributors:
            if type(c) is not dict or c.get('cluster') not in HEADS or not isinstance(c.get('blob'),str) or not HEX40.fullmatch(c['blob']):
                errors.append('INVALID_CONTRIBUTOR_GIT_OBJECT:'+path);continue
            cl.append(c['cluster'])
        if len(set(cl))!=len(cl):errors.append('DUPLICATE_CONTRIBUTOR:'+path)
        predicted=sorted([c['cluster'] for c in contributors if isinstance(c,dict) and c.get('blob')==sha and c.get('cluster') in HEADS])
        observed=item.get('integrated_matches_contributor')
        if not isinstance(observed,list) or sorted(observed)!=predicted:
            errors.append('FABRICATED_CONTRIBUTOR_MATCH:'+path)
        if predicted:actual_matched.add(path)
        if item.get('resolution')!='NOT_ADJUDICATED_BY_OBJECT_IDENTITY':
            errors.append('SOURCE_MATCH_LAUNDERED_AS_APPROVAL:'+path)
    if set(seen)!=set(INTEGRATED): errors.append('14_PATH_RAW_CROSSWALK_INCOMPLETE_OR_REPLACED')
    if actual_matched!=SAME_AS_ONE_CONTRIBUTOR:
        errors.append('CONTRIBUTOR_MATCH_CANNOT_AUTOMATICALLY_RESOLVE_CONFLICT')
    packets=[]
    for g,(kind,priority,subject) in GROUPS.items():
        paths=sorted(groups[g])
        if len(paths)!=(1 if g in ('taxonomy','shelter-source-fragment') else 2):
            errors.append('SOURCE_BODY_META_OR_LEDGER_HALF_MISSING:'+g)
        packets.append({'semantic_group':g,'kind':kind,'priority':priority,'subject':subject,
                        'raw_source_paths':paths,'disposition':PENDING,
                        'accepted_source_merge':False,'independent_claim_support_verified':False,
                        'human_review_required':True,'may_publish':False})
    # The recently discovered Article #15 accessibility nuance must not disappear
    # inside an older 17-claim docket. Its wording is merely an original anchor.
    if article15_body is not None:
        if type(article15_body) is not str or article15_body.count(SERVICE_ANIMAL_ANCHOR)!=1:
            errors.append('NEW_SERVICE_ANIMAL_ORIGINAL_ANCHOR_MISSING_OR_REPEATED')
        else:
            a=article15_body
            match=re.search(r'<h2\b[^>]*id=["\']special["\'][^>]*>',a,re.I)
            if not match or a.find(SERVICE_ANIMAL_ANCHOR)<match.end():
                errors.append('SERVICE_ANIMAL_CLAIM_SECTION_SCOPE_DRIFT')
            elif re.search(r'<h2\b',a[match.end():a.find(SERVICE_ANIMAL_ANCHOR)],re.I):
                errors.append('SERVICE_ANIMAL_CLAIM_OUTSIDE_SPECIAL_SECTION')
    return result(errors,packets,{'raw_source_paths':len(seen),'human_review_groups':len(packets),
                                  'matching_contributor_paths_still_unresolved':len(actual_matched),
                                  'original_article15_tool104_claim_holds':17})


def audit_native(root:Path)->dict:
    root=root.resolve()
    cw=root/'preparedness/audits/r334_frozen_nine_head_source_object_crosswalk.json'
    wi=root/'preparedness/audits/r336_frozen_41_entry_witness.json'
    try:
        for p,pin in ((cw,CROSSWALK_GIT_BLOB),(wi,WITNESS_GIT_BLOB)):
            if p.is_symlink() or not p.is_file() or git_blob(p.read_bytes())!=pin:
                return result(['AUTHENTIC_FROZEN_WITNESS_GIT_BLOB_REQUIRED:'+p.name])
        crosswalk=json.loads(cw.read_text('utf-8'));witness=json.loads(wi.read_text('utf-8'))
        for name,expected_sha in INTEGRATED.items():
            p=root/name
            if p.is_symlink() or not p.is_file() or git_blob(p.read_bytes())!=expected_sha:
                return result(['NATIVE_INTEGRATED_SOURCE_BLOB_CHANGED_OR_MISSING:'+name])
        body=(root/'preparedness/content/articles/family-communication-plan.body.html').read_bytes()
        if git_blob(body)!=ARTICLE15_BODY_BLOB:return result(['ARTICLE15_ORIGINAL_BODY_CHANGED'])
        r=check(crosswalk,witness,body.decode('utf-8'))
        # An isolated source-object comparison never proves completed native build.
        return r
    except (OSError,UnicodeError,TypeError,ValueError,KeyError):
        return result(['AUTHENTIC_NATIVE_SOURCE_AND_WITNESS_CHECKOUT_REQUIRED'])


def main()->int:
    ap=argparse.ArgumentParser(description='R341 original Git conflict dockets. Read-only, never approve.')
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    out=audit_native(ap.parse_args().repo_root)
    print(json.dumps(out,indent=2,sort_keys=True))
    return 2 if out['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
