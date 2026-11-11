#!/usr/bin/env python3
"""R295 exact-source provenance reconciliation. REVIEW ONLY; NEVER grants release.

Anchors to immutable R200 inventory, not pre-R200 contributor branch ancestors.
No network, publishing, URL rewriting, or source ID alias substitution.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

CLUSTERS = ('start','shelter','food','health','hist-food','hist-home','hist-field')
R294 = ('hist-food', 'hist-home', 'hist-field')
R293_INTEGRATED = 'ffd3d684c143240b64990ab6e898489d085e3558'


def _is_sha(value):
    return isinstance(value, str) and len(value) == 40 and all(c in '0123456789abcdef' for c in value)


def examine(r200, r293, witnesses, receipt):
    """Return deterministic mechanical receipt. No safety, source or release pass."""
    errors, warnings = [], []
    info = {'r200_routes':0,'r294_routes':0,'r294_citations':0,
            'r294_exact_id_substitutions':0,'branches_matching_r200':0,
            'same_witness_articles':0}
    if r200.get('state') != 'DRAFT_HARD_HOLD' or any(r200.get(k) is not False for k in (
        'publication_authorized','independent_qd_pass','human_source_approved','medical_safety_verified')):
        errors.append('R200_RELEASE_HOLD_CORRUPT')
    if r200.get('artifact_count') != 35 or r200.get('export_target_count_with_six_tools') != 41:
        errors.append('R200_SLATE_TOTALS')
    heads = r200.get('branch_heads',{})
    if set(heads) != set(CLUSTERS) or not all(_is_sha(s) for s in heads.values()):
        errors.append('R200_BRANCH_MANIFEST_INCOMPLETE')
    articles = r200.get('articles',[])
    routes = []
    for a in articles:
        slug, sec = a.get('slug'), a.get('section')
        route = a.get('route')
        if route != f'/preparedness/{sec}/{slug}/': errors.append('R200_BAD_ROUTE:'+str(slug))
        routes.append(route)
        if a.get('branch_sha') != heads.get(a.get('source_cluster')):
            errors.append('R200_ARTICLE_CUSTODY:'+str(slug))
        if not _is_sha(a.get('body_oid')) or not _is_sha(a.get('meta_oid')):
            errors.append('R200_BAD_BLOB:'+str(slug))
    info['r200_routes'] = len(set(routes))
    if len(routes) != 35 or len(set(routes)) != 35 or len(set(a.get('slug') for a in articles)) != 35:
        errors.append('R200_DUPLICATE_OR_MISSING_ROUTES')

    clusters = r293.get('clusters',{})
    live_receipts = receipt.get('live_branch_comparisons',{})
    if set(clusters) != set(CLUSTERS) or set(live_receipts) != set(CLUSTERS):
        errors.append('CONTRIBUTOR_SET_INCOMPLETE')
    for cluster in CLUSTERS:
        v = clusters.get(cluster,{})
        live = live_receipts.get(cluster,{})
        r200_head = heads.get(cluster)
        if v.get('head') != r200_head: errors.append('R293_HEAD_NOT_R200:'+cluster)
        if live.get('r200_base') != r200_head or live.get('observed_head') != r200_head or not _is_sha(r200_head):
            errors.append('LIVE_HEAD_NOT_R200:'+cluster)
        elif live.get('ahead_by') == live.get('behind_by') == 0 and live.get('changed_files') == 0 and live.get('status') == 'identical':
            info['branches_matching_r200'] += 1
        else: errors.append('LIVE_BRANCH_CHANGED:'+cluster)
        if v.get('frozen') != r200_head:
            warnings.append('R293_LEGACY_BASELINE_MISLABELED_AS_R200:'+cluster)
        if v.get('status') != 'identical' and v.get('head') == r200_head:
            warnings.append('R293_DRIFT_IS_PRE_R200_HISTORY:'+cluster)

    if set(witnesses) != set(R294): errors.append('R294_MISSING_CLUSTER')
    seen_routes, slugs = [], []
    replacements = 0
    match_count = 0
    for cluster in R294:
        w = witnesses.get(cluster,{})
        if w.get('cluster') != cluster: errors.append('R294_CLUSTER_ID:'+cluster)
        if w.get('witness_commit_refs',{}).get('live') != heads.get(cluster):
            errors.append('R294_LIVE_NOT_R200:'+cluster)
        if w.get('witness_commit_refs',{}).get('integrated') != R293_INTEGRATED:
            errors.append('R294_WRONG_INTEGRATED_WITNESS:'+cluster)
        if w.get('state') != 'DRAFT_HARD_HOLD' or any(w.get(k) is not False for k in (
            'publication_authorized','independent_qd_pass','medical_safety_verified','privacy_approved')):
            errors.append('R294_SAFETY_STATE:'+cluster)
        for a in w.get('articles',[]):
            slug=a.get('slug')
            slugs.append(slug)
            body=a.get('body',{})
            meta=a.get('meta',{})
            r200_body=body.get('live',{})
            integ_body=body.get('integrated',{})
            r200_meta=meta.get('live',{})
            integ_meta=meta.get('integrated',{})
            route=integ_meta.get('canonical_route')
            seen_routes.append(route)
            if route != r200_meta.get('canonical_route') or route != f'/preparedness/{integ_meta.get("section")}/{slug}/':
                errors.append('R294_ROUTE_DRIFT:'+str(slug))
            if not any(a200.get('slug') == slug and a200.get('route') == route for a200 in articles):
                errors.append('R294_NOT_IN_R200:'+str(slug))
            for label, m in (('r200',r200_meta),('integrated',integ_meta)):
                if m.get('status',{}).get('publish') != 'draft' or m.get('safety_review',{}).get('state') not in ('pending','not-required'):
                    errors.append('R294_UNEXPECTED_SAFETY_STATE:'+str(slug)+':'+label)
            counts=integ_body.get('citations',{})
            if not isinstance(counts,dict) or sum(counts.values()) != integ_body.get('citation_count'):
                errors.append('R294_BAD_CITATION_COUNTER:'+str(slug))
            info['r294_citations'] += integ_body.get('citation_count',0)
            if integ_body.get('citation_count',0) < r200_body.get('citation_count',0):
                errors.append('R294_CITATION_LOSS:'+str(slug))
            if integ_body.get('word_tokens',0) < r200_body.get('word_tokens',0):
                errors.append('R294_READING_DEPTH_LOSS:'+str(slug))
            if set(counts) != set(integ_meta.get('source_use_ids',[])):
                errors.append('R294_META_SOURCE_USE_MISMATCH:'+str(slug))
            if a.get('comparisons',{}).get('integrated_equals_live_lf') is True:
                match_count += 1
            if cluster == 'hist-food':
                old = counts.get('hist-food-nchfp-jerky',0)
                new = r200_body.get('citations',{}).get('nchfp-jerky',0)
                if old != new or new < 1:
                    errors.append('R294_NCHFP_ALIAS_COUNT_MISMATCH:'+str(slug))
                replacements += old
                if counts.get('nchfp-jerky',0) or r200_body.get('citations',{}).get('hist-food-nchfp-jerky',0):
                    errors.append('R294_NCHFP_ALIAS_CROSS_CONTAMINATION:'+str(slug))
            elif counts != r200_body.get('citations',{}):
                errors.append('R294_UNREVIEWED_CITATION_DRIFT:'+str(slug))
    info['r294_routes'] = len(set(seen_routes))
    info['r294_exact_id_substitutions'] = replacements
    info['same_witness_articles'] = match_count
    if len(slugs) != 7 or len(set(slugs)) != 7 or len(set(seen_routes)) != 7:
        errors.append('R294_ROUTE_SET_NOT_SEVEN_UNIQUE')
    if info['r294_citations'] != 334: errors.append('R294_334_CITATION_COUNTS_CHANGED')
    if replacements != 8: errors.append('R294_NCHFP_EXPECTED_EIGHT_OCCURRENCES')
    if match_count != 5: errors.append('R294_FIVE_BODY_PARITY_INVARIANT')
    if info['branches_matching_r200'] != 7: errors.append('R200_SEVEN_BRANCH_PARITY_FAILED')
    # Snapshot/metadata agreement does NOT prove the actual online branches remain here.
    return {'schema':'fv-preparedness-r295-provenance-safety-review-v1',
            'state':'DRAFT_HARD_HOLD' if not errors else 'INVALID_HARD_HOLD',
            'mechanical_consistency':not errors,'publication_authorized':False,
            'independent_qd_pass':False,'medical_safety_verified':False,
            'privacy_approved':False,'merchant_offer_verified':False,
            'actual_current_branch_heads_require_fresh_api_comparison':True,
            'no_source_identity_alias_automatically_accepted':True,
            'counts':info,'errors':sorted(set(errors)),'review_warnings':sorted(set(warnings))}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=ap.parse_args()
    root=args.root
    def read(n): return json.loads((root/'audits'/n).read_text(encoding='utf-8'))
    try:
        result=examine(read('r200_seven_cluster_35_article_frozen_custody.json'),
                       read('r293_live_contributor_branch_crosswalk_UNAPPROVED.json'),
                       {c:read('r294_'+c+'_three_witness_UNAPPROVED.json') for c in R294},
                       read('r295_r200_exact_branch_comparison_receipt_UNAPPROVED.json'))
    except (ValueError,KeyError,OSError,TypeError) as ex:
        result={'state':'INVALID_HARD_HOLD','mechanical_consistency':False,
                'publication_authorized':False,'errors':['MISSING_OR_UNREADABLE_EVIDENCE:'+str(ex)]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result.get('mechanical_consistency') else 1

if __name__=='__main__': raise SystemExit(main())
