#!/usr/bin/env python3
"""R448: deterministic original 35-article integration/commerce HOLD matrix.

Pure, read-only. This does not select source/fork variants, authenticate advice,
run WordPress, grant QD approval, or assert that an offer or social post exists.
Evidence not in the original docket must remain UNKNOWN, never inferred.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_GIT_BLOB = '86d22a1d504c93db7689b914e2202a7845b648e2'
PACKET_GIT_BLOB = '0e655316ced77212abeff77459898253a1e768fd'
STATE = 'DRAFT_HARD_HOLD'
REPO = 'finalvestigestudios/final-vestige-site-layer'
FAMILY_SOURCE_URL = 'https://www.ready.gov/plan'
FAMILY_SOURCE_IDS = ('start-ready-plan', 'shelter-ready-plan')
SHA = re.compile(r'^[0-9a-f]{40}$')
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
FORK = re.compile(r'^preparedness/content/articles/([a-z0-9-]+)\.(body\.html|meta\.json)$')


def object_unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate JSON key: ' + key)
        value[key] = item
    return value


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def audit(docket, docket_bytes, packet, packet_bytes, observed_heads):
    """Construct a HOLD-only dependency matrix; preserve original multiplicity."""
    errors = []
    def fail(code):
        errors.append(code)

    if not isinstance(docket, dict) or not isinstance(packet, dict) or not isinstance(observed_heads, dict):
        return {'release_state': STATE, 'errors': ['INPUT_NOT_OBJECT'], 'structural_evidence_pass': False,
                'qd_pass': False, 'publication_allowed': False, 'verified_paid_offer': False}
    if not isinstance(docket_bytes, bytes) or git_blob(docket_bytes) != ORIGINAL_GIT_BLOB:
        fail('AUTHENTIC_R397_BLOB_NOT_PROVEN')
    if not isinstance(packet_bytes, bytes) or git_blob(packet_bytes) != PACKET_GIT_BLOB:
        fail('AUTHENTIC_R446_PACKET_NOT_PROVEN')
    if (docket.get('repo') != REPO or docket.get('issue') != 136
            or docket.get('parent_conversion_issue') != 820 or docket.get('schema') != 1):
        fail('ORIGINAL_DOCKET_IDENTITY_DRIFT')
    if (packet.get('repo') != REPO or packet.get('issue') != 136
            or packet.get('business_coordination_issue') != 820
            or packet.get('schema') != 'R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1'):
        fail('REVIEW_PACKET_IDENTITY_DRIFT')
    if (packet.get('original_docket') != {'path': 'preparedness/reviews/r397_original_source_fork_docket.json',
           'commit': 'a22c8797da58ecf186f50fcf47063bd195fd3c17', 'git_blob': ORIGINAL_GIT_BLOB}):
        fail('PACKET_R397_ANCESTRY_DRIFT')
    for obj, fields in ((docket, ('publication_approved', 'qualified_safety_approved',
                                   'automatic_variant_selection', 'merchant_offer_verified')),
                        (packet, ('qualified_review_approved', 'publishable',
                                  'safety_approved', 'merchant_offer_verified'))):
        if obj.get('release_state') != STATE or any(obj.get(k) is not False for k in fields):
            fail('UNSUPPORTED_APPROVAL_OR_RELEASE_STATE')

    articles = docket.get('original_articles', [])
    packet_articles = packet.get('article_identities', [])
    pins = docket.get('branch_pins', [])
    packet_pins = packet.get('branch_pins', [])
    refs = docket.get('all_original_source_id_crosswalk', [])
    groups = docket.get('shared_exact_url_review_groups', [])
    source_reviews = docket.get('source_evidence_disputes', [])
    fork_reviews = docket.get('original_fork_disputes', [])
    packet_reviews = (packet.get('source_scope_review', []), packet.get('manuscript_fork_review', []),
                      packet.get('duplicate_exact_url_review', []))
    if any(not isinstance(v, list) for v in (articles,packet_articles,pins,packet_pins,refs,groups,
                                              source_reviews,fork_reviews,*packet_reviews)):
        fail('NON_LIST_ORIGINAL_INVENTORY')
        return {'release_state': STATE, 'errors': sorted(set(errors)), 'structural_evidence_pass': False,
                'qd_pass': False, 'publication_allowed': False, 'verified_paid_offer': False}
    if tuple(map(len, (articles, refs, groups, source_reviews, fork_reviews, pins))) != (35,203,17,5,9,9):
        fail('ORIGINAL_INVENTORY_COUNT_DRIFT')
    if tuple(map(len, (packet_articles,*packet_reviews,packet_pins))) != (35,5,9,17,9):
        fail('PACKET_INVENTORY_COUNT_DRIFT')

    pin_map = {}
    for row in pins:
        if not isinstance(row, dict) or not isinstance(row.get('branch'), str) or not isinstance(row.get('sha'),str):
            fail('INVALID_CONTRIBUTOR_PIN');continue
        b, s = row['branch'], row['sha']
        if b in pin_map or SHA.fullmatch(s) is None:
            fail('DUPLICATE_OR_INVALID_CONTRIBUTOR_PIN')
        pin_map[b] = s
    if len(pin_map) != 9 or observed_heads != pin_map:
        fail('NINE_CURRENT_CONTRIBUTOR_HEADS_UNVERIFIED')
    if {r.get('branch'):r.get('sha') for r in packet_pins if isinstance(r,dict)} != pin_map:
        fail('PACKET_CONTRIBUTOR_PINS_DRIFT')

    originals = {}
    for row in articles:
        if not isinstance(row,dict) or not isinstance(row.get('slug'),str) or SLUG.fullmatch(row['slug']) is None:
            fail('INVALID_ARTICLE_IDENTITY');continue
        slug = row['slug']
        if slug in originals:
            fail('DUPLICATE_ARTICLE_SLUG');continue
        blobs = row.get('body_candidate_git_blobs')
        if (not isinstance(blobs,list) or not blobs
                or any(not isinstance(b,str) or SHA.fullmatch(b) is None for b in blobs)):
            fail('ARTICLE_BODY_BLOBS_UNVERIFIED');continue
        originals[slug] = blobs
    counterparts = {}
    for row in packet_articles:
        if not isinstance(row,dict) or not isinstance(row.get('slug'),str):
            fail('INVALID_PACKET_ARTICLE');continue
        if row['slug'] in counterparts: fail('DUPLICATE_PACKET_ARTICLE')
        counterparts[row['slug']] = row.get('body_candidate_git_blobs')
    if set(originals) != set(counterparts) or any(
        not isinstance(counterparts.get(s),list) or Counter(blobs) != Counter(counterparts[s])
        for s,blobs in originals.items()
    ):
        fail('ARTICLE_BLOB_MULTIPLICITY_OR_IDENTITY_DRIFT')
    if len(originals) != 35: fail('THIRTY_FIVE_ORIGINAL_ARTICLES_NOT_PROVEN')

    sources, url_ids = {}, defaultdict(set)
    occurrence_count = 0
    for row in refs:
        if not isinstance(row,dict) or not isinstance(row.get('source_id'),str):
            fail('INVALID_SOURCE_ID_ROW');continue
        sid = row['source_id']
        if sid in sources: fail('DUPLICATE_SOURCE_ID')
        variants = row.get('variants')
        if not isinstance(variants,list) or not variants:
            fail('SOURCE_VARIANTS_MISSING');continue
        source_set = set()
        for variant in variants:
            occurrence_count += 1
            if not isinstance(variant,dict): fail('INVALID_SOURCE_VARIANT');continue
            b, h, u = (variant.get(x) for x in ('branch','source_blob','url'))
            if (b not in pin_map or not isinstance(h,str) or SHA.fullmatch(h) is None
                    or not isinstance(u,str) or not u.startswith('https://')):
                fail('SOURCE_PROVENANCE_OR_HTTPS_DRIFT');continue
            source_set.add((b,h,u))
            url_ids[u].add(sid)
        sources[sid] = source_set
    if len(sources) != 203 or occurrence_count != 280 or len(url_ids) != 181:
        fail('SOURCE_COUNTS_OR_OCCURRENCES_DRIFT')
    shared = {u:frozenset(ids) for u,ids in url_ids.items() if len(ids)>1}
    documented = {}
    for row in groups:
        if not isinstance(row,dict) or not isinstance(row.get('url'),str) or not isinstance(row.get('ids'),list):
            fail('MALFORMED_SHARED_URL_GROUP');continue
        if row['url'] in documented: fail('DUPLICATE_SHARED_URL_GROUP')
        if row.get('review_required') is not True: fail('SHARED_URL_REVIEW_WAIVED')
        documented[row['url']] = frozenset(row['ids'])
    if len(shared) != 17 or shared != documented:
        fail('EXACT_SHARED_URL_CROSSWALK_DRIFT')
    review_ids = {r.get('source_id') for r in source_reviews if isinstance(r,dict)}
    p_review_ids = {r.get('source_id') for r in packet_reviews[0] if isinstance(r,dict)}
    if (len(review_ids)!=5 or review_ids!=p_review_ids or
            any(r.get('decision')!='HUMAN_REVIEW_REQUIRED' or r.get('selected_record') is not None
                for r in source_reviews if isinstance(r,dict))):
        fail('SOURCE_DISPUTE_MISSING_OR_SELECTED')
    for row in packet_reviews[0]:
        if not isinstance(row,dict): fail('MALFORMED_PACKET_SOURCE_REVIEW');continue
        sid=row.get('source_id')
        if row.get('original_decision') != 'HUMAN_REVIEW_REQUIRED' or row.get('proposed_selection') is not None:
            fail('SOURCE_PACKET_PRESELECTED')
        for v in row.get('source_variants',[]):
            if not isinstance(v,dict) or tuple(v.get(k) for k in ('branch','source_blob','url')) not in sources.get(sid,set()):
                fail('SOURCE_VARIANT_CROSSWALK_DRIFT')
            elif not v.get('supports_exact') or not v.get('reading_scope_notes_exact'):
                fail('SOURCE_READING_SCOPE_LOST')
    fork_paths = set()
    article_forks = defaultdict(list)
    global_forks = []
    for row in fork_reviews:
        if not isinstance(row,dict) or not isinstance(row.get('path'),str):
            fail('MALFORMED_ORIGINAL_FORK');continue
        path = row['path']
        if path in fork_paths: fail('DUPLICATE_FORK_PATH')
        fork_paths.add(path)
        if (row.get('decision') != 'HUMAN_REVIEW_REQUIRED' or row.get('selected_sha') is not None
                or row.get('requires_reading_depth_review') is not True
                or row.get('requires_source_citation_review') is not True):
            fail('FORK_REVIEW_PRESELECTED_OR_DEPTH_LOST')
        variant_list = row.get('variants',[])
        if not isinstance(variant_list,list) or len(variant_list)<2:
            fail('FORK_COMPETING_VARIANTS_LOST')
        m=FORK.fullmatch(path)
        if m and m.group(1) in originals: article_forks[m.group(1)].append(path)
        else: global_forks.append(path)
    p_forks = {r.get('path'):r for r in packet_reviews[1] if isinstance(r,dict)}
    if len(fork_paths)!=9 or set(p_forks)!=fork_paths:
        fail('NINE_ORIGINAL_FORK_IDENTITIES_DRIFT')
    else:
        for r in fork_reviews:
            if not isinstance(r,dict) or r.get('path') not in p_forks:continue
            counterpart=p_forks[r['path']]
            if Counter(canonical(v) for v in r.get('variants',[])) != Counter(
                    canonical(v) for v in counterpart.get('original_variants',[])):
                fail('FORK_VARIANT_READING_DEPTH_EVIDENCE_DRIFT')
    packet_groups={r.get('url'):r for r in packet_reviews[2] if isinstance(r,dict)}
    if set(packet_groups)!=set(shared) or any(
       frozenset(r.get('source_ids',[])) != shared.get(url) or r.get('decision')!='UNSELECTED'
       or r.get('merge_authorized') is not False for url,r in packet_groups.items()):
        fail('PACKET_SHARED_URL_GROUP_MERGE_OR_LOSS')

    family_refs = {sid:u for u,ids in url_ids.items() for sid in ids if sid in FAMILY_SOURCE_IDS}
    free_link_evidence = (len(family_refs) == 2 and
                          all(family_refs.get(sid)==FAMILY_SOURCE_URL for sid in FAMILY_SOURCE_IDS))
    if not free_link_evidence: fail('FAMILY_FREE_GUIDE_NOT_IN_ORIGINAL_CROSSWALK')

    article_matrix=[]
    for slug,blobs in sorted(originals.items()):
        local_forks=sorted(article_forks[slug])
        holds=['SOURCE_CITATION_USAGE_NOT_AUTHENTICATED',
               'ORIGINAL_SOURCE_REVIEW_NOT_ADJUDICATED',
               'SHARED_URL_IDENTITY_REVIEW_NOT_ADJUDICATED',
               'QUALIFIED_SAFETY_REVIEW_NOT_APPROVED',
               'NATIVE_BUILD_AND_WP_EXPORT_NOT_AUTHENTICATED']
        if local_forks: holds.append('ORIGINAL_MANUSCRIPT_READING_DEPTH_FORK_UNSELECTED')
        if global_forks: holds.append('SHARED_SOURCE_FRAGMENT_FORK_UNSELECTED')
        article_matrix.append({'slug':slug,'body_candidate_appearances':len(blobs),
            'distinct_body_git_blobs':len(set(blobs)),
            'original_body_git_blobs':sorted(set(blobs)),
            'local_fork_paths':local_forks,'unresolved_holds':sorted(holds),
            'article_source_usage_verified':False,'qd_pass':False,
            'publishable':False,'live_url':None})
    return {'schema':'R448_PREPAREDNESS_INTEGRATION_HOLD_MATRIX_v1',
      'release_state':STATE,'structural_evidence_pass':not errors,
      'errors':sorted(set(errors)),'qd_pass':False,'publication_allowed':False,
      'verified_paid_offer':False,'cms_write_allowed':False,'has_authenticated_native_build':False,
      'provenance':{'repo':REPO,'source_issue':136,'commerce_issue':820,
                    'original_docket_git_blob':ORIGINAL_GIT_BLOB,
                    'review_packet_git_blob':PACKET_GIT_BLOB},
      'counts':{'article_identities':len(originals),'source_ids':len(sources),
                'source_occurrences':occurrence_count,'literal_source_urls':len(url_ids),
                'shared_url_review_groups':len(shared),'source_disputes':len(review_ids),
                'original_forks':len(fork_paths),'source_fragment_forks':len(global_forks),
                'contributor_pins':len(pin_map)},
      'article_matrix':article_matrix,
      'global_fork_paths':sorted(global_forks),
      'unresolved_source_ids':sorted(review_ids),
      'shared_url_source_ids':{u:sorted(sids) for u,sids in sorted(shared.items())},
      'campaign_research_only':{'topic':'household family communication and reunification',
        'original_article_slug':'family-communication-plan',
        'original_article_unselected':bool(article_forks['family-communication-plan']),
        'free_external_source_url':FAMILY_SOURCE_URL if free_link_evidence else None,
        'free_source_provenance':'R397 original crosswalk; NOT a current HTTP/browser check',
        'source_ids':list(FAMILY_SOURCE_IDS) if free_link_evidence else [],
        'grok_published_asset_id':None,'grok_post_url':None,
        'on_site_cta_draft_only':'Review the official household emergency checklist',
        'optional_tool_104_status':'UNAPPROVED_CHILD_PRIVACY_AND_PRINT_QD',
        'paid_preparedness_sku':None,'verified_checkout':False,
        'verified_merchant_order':False,'verified_net_revenue':None,
        'qualified_human_sessions':None,'net_revenue_per_1000_qualified_sessions':None,
        'owners':{'social_asset_verification':'Grok/Praxxis',
           'source_and_safety_review':'Preparedness/Qualified QD',
           'paid_offer_authority':'Founder/Commerce',
           'analytics_and_checkout':'Claude/Commerce'},
        'release_state':STATE}}


def main(argv=None):
    p=argparse.ArgumentParser(description='R448 read-only integration matrix; ALWAYS HARD HOLD')
    for name in ('docket','packet','observed-heads','output'):
        p.add_argument('--'+name, type=Path, required=True)
    args=p.parse_args(argv)
    try:
        for name in ('docket','packet','observed_heads'):
            if args.output.resolve()==getattr(args,name).resolve():
                raise ValueError('refuse overwrite input')
        orig=args.docket.read_bytes(); packet_raw=args.packet.read_bytes()
        original=json.loads(orig,object_pairs_hook=object_unique)
        packet=json.loads(packet_raw,object_pairs_hook=object_unique)
        heads=json.loads(args.observed_heads.read_text(encoding='utf-8'),object_pairs_hook=object_unique)
        report=audit(original,orig,packet,packet_raw,heads)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    except (OSError,UnicodeError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'release_state':STATE,'structural_evidence_pass':False,
             'qd_pass':False,'publication_allowed':False,
             'error':'INVALID_OR_MISSING_INPUT:'+type(exc).__name__}))
        return 2
    print(json.dumps({'release_state':STATE,'structural_evidence_pass':report['structural_evidence_pass'],
                       'errors':report['errors'],'counts':report['counts']},sort_keys=True))
    return 2


if __name__=='__main__':
    raise SystemExit(main())
