#!/usr/bin/env python3
"""R180: reconcile held source/safety review dockets without declaring them cleared.

Read-only. Every outcome remains a draft hard hold, even with valid structures.
Never adjudicates food/medical advice, represents a sale, or authorizes publication.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r180-unresolved-decision-packet-v1'
DOCKETS = {
 'r170/source-decision-docket.json': '54b7d61fbd5829c458d125d63c0b171c6f36998e',
 'r171/source-variance-quarantine.json': 'cd757a36e3015b732916ffd6655856a575140350',
 'r172/jerky-source-impact.json': '45963b30ce48a069539c66ace9f1a2d2f5cf1dfd',
 'r173/claim-scope-human-docket.json': '48e1050e815f55c5f2564dc030b8ba2aa24df548',
}
SAFETY_FALSE = ('independent_qd_pass', 'publication_authorized',
                'qualified_food_safety_review', 'human_qualified_safety_approval',
                'qualified_safety_review', 'medical_safety_approved',
                'human_source_equivalence_review_complete',
                'source_alias_equivalence_approved', 'human_checked_links',
                'founder_publication_authorized', 'qualified_food_safety',
                'independent_qd', 'url_equivalence', 'source_claim_scope',
                'commercial_offer_verified')
IMPACT = ('pemmican-and-dried-meats', 'pioneer-travel-rations', 'safe-jerky-dehydration')


def require(ok, explanation):
    if not ok:
        raise ValueError(explanation)


def https_source(url):
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 for c in url):
        return False
    try:
        parts = urlsplit(url)
        return (parts.scheme == 'https' and bool(parts.hostname) and
                parts.username is None and parts.password is None and
                parts.port in (None, 443) and not parts.fragment)
    except ValueError:
        return False


def all_false(obj, labels=SAFETY_FALSE, path='root'):
    """Fail closed on any positive claimed safety/publication flag at any nesting."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in labels:
                require(v is False, path+'.'+k+' requires explicit false')
            all_false(v, labels, path+'.'+k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            all_false(v, labels, path+f'[{i}]')


def reconcile(roster, crosswalk, family, variance, impact, claims):
    """Pure function. Returns 21 *unresolved* decisions and exact custody links."""
    require(roster.get('state') == HOLD and roster.get('expected_articles') == 35 and
            roster.get('expected_citations') == 2000 and
            roster.get('expected_source_use') == 385 and
            roster.get('publication_authorized') is False and
            roster.get('independent_qd_pass') is False,
            'immutable 35/2000/385 roster admission not present')
    rows = roster.get('articles')
    require(isinstance(rows, list) and len(rows) == 35 and
            len({x.get('slug') for x in rows}) == 35,
            '35 unique article identities required')
    require(Counter(x.get('recorded_state') for x in rows) ==
            {'pending':29, 'not-required':4, 'approved':2},
            'historical safety labels changed')
    require(set(roster.get('legacy_approved_unverified', [])) ==
            {'making-water-safer', 'salt-beef-salt-pork-age-of-sail'} and
            set(roster.get('not_required_still_editorial_hold', [])) ==
            {'navigation-before-gps', 'pioneer-supply-chains-failed',
             'root-cellars-cool-storage', 'sanitation-before-germ-theory'},
            'historical label exceptions lost')
    require(crosswalk.get('state') == HOLD and
            crosswalk.get('publication_authorized') is False and
            crosswalk.get('human_source_claim_review_complete') is False and
            crosswalk.get('article_count') == 35 and
            crosswalk.get('citation_occurrences') == 2000 and
            crosswalk.get('article_source_relationships') == 385,
            'R179 crosswalk status or immutable counts invalid')
    uses = crosswalk.get('crosswalk')
    require(isinstance(uses, list) and len(uses) == 385,
            'complete 385 authored relationships required')
    by_article = defaultdict(dict)
    for u in uses:
        a, sid = u.get('article'), u.get('source_id')
        require(a in {x['slug'] for x in rows} and isinstance(sid, str) and
                sid not in by_article[a] and https_source(u.get('source_url')) and
                u.get('independently_reviewed_claim') is False and
                u.get('modern_safety_approved') is False,
                'duplicate, missing, or falsely approved source relationship')
        by_article[a][sid] = u
    require({x['slug']:x['source_use_count'] for x in rows} ==
            {a:len(v) for a,v in by_article.items()},
            'per-article source relationships differ from roster')
    for doc in (family, variance, impact, claims):
        require(doc.get('state') == HOLD, 'review docket lost hard-hold state')
        all_false(doc)
    require(family.get('schema') == 'fv-preparedness-r170-family-source-docket-v1' and
            variance.get('schema') == 'fv-preparedness-r171-source-variance-quarantine-v1' and
            impact.get('schema') == 'fv-preparedness-r172-jerky-source-impact-docket-v1' and
            claims.get('schema') == 'fv-preparedness-r173-claim-scope-human-docket-v1',
            'docket schema mismatch')
    f = family.get('decisions')
    require(isinstance(f, list) and len(f) == 11 and
            len({v.get('id') for v in f}) == 11 and
            family.get('scope') == 'family-reunification-card',
            'family-card docket must preserve all 11 decisions')
    packet = []
    for d in f:
        require(isinstance(d.get('id'), str) and d['id'].startswith('shelter-') and
                d.get('review_state') == 'PENDING' and
                d.get('human_link_check') is False and
                d.get('qualified_safety_review') is False and
                isinstance(d.get('source_scope'), str) and d['source_scope'].strip() and
                https_source(d.get('original_url')) and
                (d.get('alternative_current_page') is None or https_source(d['alternative_current_page'])),
                'Family Card source decision unexpectedly cleared or malformed')
        packet.append({'ticket':'family:'+d['id'], 'kind':'family-source-scope',
                       'article':'family-reunification-card (unpublished tool)',
                       'source_ids':[d['id']], 'original_urls':[d['original_url']],
                       'decision':'PENDING', 'review_required':'qualified source/safety + privacy/print/QD',
                       'independent_approval':False})
    require(variance.get('source_url_group_material_roster_discrepancies') == 1 and
            variance.get('crosswalk_shared_url_groups') == 32 and
            variance.get('shared_id_conflicting_url_groups') == 0 and
            variance.get('human_source_equivalence_review_complete') is False,
            'material NCHFP or shared-URL review group changed')
    v = variance.get('material_discrepancy', {})
    require(v.get('source_id') == 'hist-food-nchfp-jerky' and
            v.get('crosswalk_group_url') == 'https://nchfp.uga.edu/how/dry/recipes/jerky' and
            v.get('current_literal_fragment_url') == 'https://nchfp.uga.edu/how/dry/recipes/jerky/' and
            v.get('crosswalk_group_url') != v.get('current_literal_fragment_url'),
            'NCHFP literal URL variants collapsed or substituted')
    require(impact.get('original_hist_food_source_id') == v['source_id'] and
            impact.get('hist_food_literal_url') == v['current_literal_fragment_url'] and
            impact.get('source_group_human_review') == 'PENDING' and
            impact.get('review_decisions') == {'url_equivalence':False,
             'source_claim_scope':False,'qualified_food_safety':False,
             'independent_qd':False,'founder_publication_authorized':False},
            'NCHFP safety review accidentally promoted')
    affected = impact.get('impacted_articles')
    require(isinstance(affected,list) and len(affected) == 3 and
            {x.get('slug') for x in affected} == set(IMPACT),
            'three affected article identities changed')
    pins = {x['slug']:x for x in rows}
    for a in affected:
        slug,sid = a['slug'],a.get('source_id')
        require(a.get('metadata_blob') == pins[slug].get('meta_git_blob') and
                sid in by_article[slug] and
                by_article[slug][sid].get('source_url') ==
                 (v['current_literal_fragment_url'] if sid == v['source_id']
                  else v['crosswalk_group_url']) and
                a.get('route','').startswith('/preparedness/'),
                'impacted article/source identity inconsistent')
    require({x['slug']:x['source_id'] for x in affected} == {
        'pemmican-and-dried-meats':'hist-food-nchfp-jerky',
        'pioneer-travel-rations':'hist-food-nchfp-jerky',
        'safe-jerky-dehydration':'nchfp-jerky'},
        'three-article source identifier pairing mutated')
    cs = claims.get('claims')
    require(isinstance(cs,list) and len(cs) == 10 and
            len({(c.get('slug'),c.get('claim')) for c in cs}) == 10 and
            Counter(c.get('slug') for c in cs) ==
            {'safe-jerky-dehydration':5, 'pemmican-and-dried-meats':3,
             'pioneer-travel-rations':2},
            '10 distinct jerky safety claims and 5/3/2 partition required')
    for c in cs:
        slug = c['slug']
        ids = c.get('source_ids')
        require(isinstance(ids,list) and len(set(ids)) == len(ids) and
                all(x in by_article[slug] for x in ids) and
                c.get('human_source_scope_decision') == 'PENDING' and
                c.get('qualified_food_safety_decision') == 'PENDING' and
                c.get('independent_qd_decision') == 'PENDING' and
                c.get('reviewer') is None and c.get('reviewed_at') is None and
                c.get('evidence_link') is None,
                'jerky claim source identity or qualified review state changed')
        packet.append({'ticket':'jerky:'+slug+':'+c['claim'],
                       'kind':'jerky-claim-source-scope','article':slug,
                       'source_ids':ids,
                       'original_urls':[by_article[slug][x]['source_url'] for x in ids],
                       'decision':'PENDING','review_required':'qualified food-safety/source + independent QD',
                       'independent_approval':False})
    require(claims.get('previous_source_decisions_pending') == 75 and
            claims.get('crosswalk_shared_url_groups_pending') == 32 and
            impact.get('pending_source_decisions_previously_reported') == 75,
            'historical aggregate source backlog changed')
    packet.sort(key=lambda x:x['ticket'])
    canon=json.dumps(packet, sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    return {'schema':SCHEMA,'state':HOLD,'article_count':35,
            'citation_occurrences':2000,'authored_source_uses':385,
            'family_source_decisions_pending':11,'jerky_claim_decisions_pending':10,
            'review_tickets_pending':21,'legacy_aggregate_source_decisions_pending':75,
            'shared_literal_url_groups_pending':32,
            'legacy_counts_overlap_not_additive':True,
            'historical_approved_labels_verified':False,
            'source_equivalence_verified':False,
            'qualified_safety_review_complete':False,
            'independent_qd_pass':False,'publication_authorized':False,
            'commercial_product_verified':False,'wordpress_ready':False,
            'packet_sha256':hashlib.sha256(canon).hexdigest(), 'tickets':packet}


def inspect_repo(root):
    result={'schema':SCHEMA,'state':INVALID,'errors':[],
            'independent_qd_pass':False,'publication_authorized':False,
            'qualified_safety_review_complete':False,'commercial_product_verified':False}
    try:
        require(root.is_dir() and not root.is_symlink(),'trusted complete checkout unavailable')
        prev_path=Path(__file__).with_name('r179_source_use_crosswalk_gate.py')
        require(prev_path.is_file() and not prev_path.is_symlink(),'R179 crosswalk gate missing')
        spec=importlib.util.spec_from_file_location('fv_r179_required',prev_path)
        prev=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prev)
        cross=prev.inspect_repo(root)
        require(cross.get('state')==HOLD and not cross.get('errors'),
                'full authentic R179 source/citation custody is missing or invalid')
        roster,_=prev.load_json(root/'preparedness/review/r178/safety_state_roster.json')
        dockets=[]
        for rel, expected in DOCKETS.items():
            doc,raw=prev.load_json(root/'preparedness/review'/rel)
            require(prev.git_blob(raw)==expected,'original human docket changed: '+rel)
            dockets.append(doc)
        result=reconcile(roster,cross,*dockets)
        result['errors']=[]
    except (ValueError,KeyError,TypeError,AttributeError,UnicodeError,OSError) as exc:
        result['errors'].append(str(exc))
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--summary',action='store_true',help='omit 21 review tickets')
    args=p.parse_args(argv)
    report=inspect_repo(args.repo)
    if args.summary:report.pop('tickets',None)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2  # Intentionally no publication/approval success state.

if __name__=='__main__':sys.exit(main())
