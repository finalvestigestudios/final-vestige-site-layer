#!/usr/bin/env python3
"""R421 read-only Preparedness conversion/source-to-offer acceptance gate.

Evaluates a planning receipt, NOT merchant truth. Even a structurally complete
receipt cannot authenticate social rights, source applicability, checkout or
settlement. ALWAYS returns DRAFT/HARD HOLD, never enables publication/commerce.
No CMS/API/network calls, tracking script, customer identifiers or file writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, parse_qs

SCOPE = 'PREPAREDNESS_ISSUE_136'
FREE_PATH = '/preparedness/'
TOPIC = 'family-emergency-contacts'
SCHEMA = 1
HEX64 = re.compile(r'[a-f0-9]{64}\Z')
TOKEN = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_-]{5,95}\Z')
DOMAIN = re.compile(r'[a-z0-9.-]+\Z')
ALLOWED_PLATFORMS = {'youtube', 'tiktok', 'instagram', 'facebook'}
RETIRED_MARKERS = ('water-resilience-field-manual', 'old-water-guide', 'water-field-manual')
MAX_BYTES = 100000


def exact(obj, keys):
    return isinstance(obj, dict) and set(obj) == set(keys)


def safe_url(url, *, host=None):
    if not isinstance(url, str) or not 0 < len(url) <= 2048:
        return False
    if any(ord(c) < 33 or ord(c) > 126 for c in url):
        return False
    try:
        u = urlsplit(url)
        return (u.scheme == 'https' and bool(u.hostname) and
                bool(DOMAIN.fullmatch(u.hostname)) and
                not u.username and not u.password and u.port in (None, 443) and
                (host is None or u.hostname in host) and not u.fragment)
    except ValueError:
        return False


def validate(receipt):
    errors, holds = [], []
    def fail(code): errors.append(code)
    def hold(code): holds.append(code)
    if not exact(receipt, ('schema','scope','release_state','approvals','campaign',
                           'free_guide','optional_tool','paid_offer','cohorts')):
        fail('R421_RECEIPT_SHAPE')
        return outcome(errors, holds)
    if receipt['schema'] != SCHEMA or receipt['scope'] != SCOPE or receipt['release_state'] != 'DRAFT_HARD_HOLD':
        fail('R421_IDENTITY_OR_RELEASE_STATE')
    a = receipt['approvals']
    if not exact(a, ('publish','site_write','social_post','paid_activation','safety_qd')) or any(v is not False for v in a.values()):
        fail('R421_UNAUTHORIZED_APPROVAL')
    free = receipt['free_guide']
    if not exact(free, ('path','status','source_class','article_15_release')):
        fail('R421_FREE_GUIDE_SHAPE')
    elif (free['path'] != FREE_PATH or free['status'] != 'EXISTING_FREE' or
          free['source_class'] != 'OFFICIAL_LINKED_ARCHIVE' or free['article_15_release'] is not False):
        fail('R421_FREE_GUIDE_OR_SAFETY_DRIFT')
    tool = receipt['optional_tool']
    if not exact(tool, ('id','status','emergency_review','child_privacy_review','accessibility_review')):
        fail('R421_TOOL_SHAPE')
    elif tool != {'id':104,'status':'HARD_HOLD','emergency_review':False,
                  'child_privacy_review':False,'accessibility_review':False}:
        fail('R421_TOOL104_PREMATURE_APPROVAL')
    camp = receipt['campaign']
    if not exact(camp, ('topic','status','asset_id','platform','post_url','asset_rights_checked',
                        'hook_source_checked','mobile_destination','utm_campaign','utm_content')):
        fail('R421_CAMPAIGN_SHAPE')
    else:
        if camp['topic'] != TOPIC: fail('R421_TOPIC_DRIFT')
        if camp['status'] == 'UNMATCHED':
            if any(camp[k] is not None for k in ('asset_id','platform','post_url','mobile_destination','utm_campaign','utm_content')):
                fail('R421_INVENTED_UNMATCHED_CAMPAIGN')
            if camp['asset_rights_checked'] is not False or camp['hook_source_checked'] is not False:
                fail('R421_UNVERIFIED_ASSET_CLAIM')
            hold('ACTUAL_MATCHED_SOCIAL_ASSET_NOT_AUTHENTICATED')
        elif camp['status'] == 'PROPOSED_MATCH':
            if not isinstance(camp['asset_id'],str) or not TOKEN.fullmatch(camp['asset_id']):
                fail('R421_INVALID_SOCIAL_ASSET_ID')
            if camp['platform'] not in ALLOWED_PLATFORMS: fail('R421_UNKNOWN_PLATFORM')
            if not safe_url(camp['post_url']): fail('R421_UNSAFE_POST_URL')
            if camp['asset_rights_checked'] is not True or camp['hook_source_checked'] is not True:
                fail('R421_ASSET_HOOK_RIGHTS_UNVERIFIED')
            if not safe_url(camp['mobile_destination'],host={'finalvestige.com'}):
                fail('R421_BAD_MOBILE_DESTINATION')
            else:
                u = urlsplit(camp['mobile_destination'])
                q = parse_qs(u.query,keep_blank_values=True)
                if u.path != FREE_PATH or any(w in u.path.lower() for w in RETIRED_MARKERS):
                    fail('R421_UNAPPROVED_DESTINATION')
                if set(q) != {'utm_source','utm_medium','utm_campaign','utm_content'} or any(len(v)!=1 for v in q.values()):
                    fail('R421_UTM_CARDINALITY')
                else:
                    if q['utm_source'][0] != camp['platform'] or q['utm_medium'][0] != 'organic_social':
                        fail('R421_UTM_PLATFORM_MEDIUM')
                    if q['utm_campaign'][0] != camp['utm_campaign'] or q['utm_content'][0] != camp['asset_id'] or camp['utm_content'] != camp['asset_id']:
                        fail('R421_UTM_ASSET_MISMATCH')
            hold('SOCIAL_CLAIM_IS_SELF_ATTESTED_NOT_INDEPENDENTLY_AUTHENTICATED')
        else: fail('R421_UNKNOWN_CAMPAIGN_STATUS')
    offer = receipt['paid_offer']
    if not exact(offer, ('status','sku','seller','merchant_checkout','rights_receipt_sha256',
                         'fulfillment_receipt_sha256','refund_terms_url','merchant_confirmation_sha256')):
        fail('R421_PAID_OFFER_SHAPE')
    elif offer['status'] == 'UNVERIFIED':
        if any(offer[k] is not None for k in ('sku','seller','merchant_checkout','rights_receipt_sha256',
                                            'fulfillment_receipt_sha256','refund_terms_url','merchant_confirmation_sha256')):
            fail('R421_UNVERIFIED_OFFER_HAS_SALE_CLAIMS')
        hold('NO_AUTHENTICATED_PURCHASABLE_FV_PREPAREDNESS_SKU')
    elif offer['status'] == 'REVIEW_CANDIDATE':
        if not isinstance(offer['sku'],str) or not TOKEN.fullmatch(offer['sku']): fail('R421_INVALID_SKU')
        if offer['seller'] != 'Final Vestige Studios': fail('R421_UNVERIFIED_SELLER')
        for key in ('merchant_checkout','refund_terms_url'):
            if not safe_url(offer[key]): fail('R421_INVALID_OFFER_URL')
        for key in ('rights_receipt_sha256','fulfillment_receipt_sha256','merchant_confirmation_sha256'):
            if not isinstance(offer[key],str) or not HEX64.fullmatch(offer[key]): fail('R421_MISSING_OFFER_EVIDENCE_HASH')
        hold('OFFER_RECEIPT_METADATA_CANNOT_AUTHENTICATE_CHECKOUT_OR_DELIVERY')
    else: fail('R421_UNSUPPORTED_OFFER_STATUS')
    cohorts = receipt['cohorts']
    if not isinstance(cohorts,list) or len(cohorts)>2:
        fail('R421_INVALID_COHORTS')
    else:
        seen=set()
        for c in cohorts:
            if not exact(c,('days','asset_id','qualified_human_sessions','verified_paid_orders',
                            'gross_cents','refund_cents','fees_cents','merchant_receipt_sha256')):
                fail('R421_COHORT_SHAPE');continue
            if c['days'] not in (7,30) or c['days'] in seen: fail('R421_COHORT_WINDOW')
            seen.add(c['days'])
            if not isinstance(c['asset_id'],str) or not TOKEN.fullmatch(c['asset_id']): fail('R421_COHORT_ASSET')
            if camp.get('status')!='PROPOSED_MATCH' or c['asset_id'] != camp.get('asset_id'):
                fail('R421_COHORT_ASSET_UNMATCHED')
            if offer.get('status')!='REVIEW_CANDIDATE': fail('R421_PAID_ORDER_WITHOUT_OFFER')
            for k in ('qualified_human_sessions','verified_paid_orders','gross_cents','refund_cents','fees_cents'):
                if type(c[k]) is not int or c[k] < 0: fail('R421_INVALID_FINANCIAL_COUNT')
            if all(type(c[k]) is int and c[k]>=0 for k in ('qualified_human_sessions','verified_paid_orders','gross_cents','refund_cents','fees_cents')):
                if c['verified_paid_orders'] > c['qualified_human_sessions'] or c['refund_cents']+c['fees_cents'] > c['gross_cents']:
                    fail('R421_INCONSISTENT_FINANCIALS')
            if not isinstance(c['merchant_receipt_sha256'],str) or not HEX64.fullmatch(c['merchant_receipt_sha256']):
                fail('R421_UNAUTHENTICATED_MERCHANT_AGGREGATE')
        if cohorts: hold('COHORT_RECEIPTS_NOT_INDEPENDENTLY_RECONCILED_NO_REVENUE_KPI')
        else: hold('7_30_DAY_ATTRIBUTED_PAID_COHORTS_MISSING')
    return outcome(errors, holds)


def outcome(errors, holds):
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
            'safety_qd_approved':False,'paid_activation_approved':False,
            'structural_integrity_ok':not errors,'errors':sorted(set(errors)),
            'holds':sorted(set(holds)),'verified_paid_orders':None,'net_revenue_per_1000_qualified_humans':None,
            'revenue_status':'NOT_COMPUTABLE_OR_INDEPENDENTLY_VERIFIED',
            'disclosure':'Synthetic receipts and asserted hashes are not merchant authentication; no orders or sales proved'}


def main():
    p=argparse.ArgumentParser(description='R421 Preparedness funnel acceptance; ALWAYS DRAFT/HARD HOLD')
    p.add_argument('receipt',type=Path)
    a=p.parse_args()
    try:
        if a.receipt.is_symlink(): raise ValueError('symlinked review receipt')
        data=a.receipt.read_bytes()
        if not 0<len(data)<=MAX_BYTES: raise ValueError('unsafe or oversized review receipt')
        result=validate(json.loads(data.decode('utf-8'),object_pairs_hook=unique_pairs))
    except (OSError,ValueError,UnicodeError,TypeError,KeyError) as exc:
        result=outcome(['R421_READ_FAILED_'+type(exc).__name__],[])
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2


def unique_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('duplicate evidence key')
        d[k]=v
    return d

if __name__=='__main__':
    sys.exit(main())
