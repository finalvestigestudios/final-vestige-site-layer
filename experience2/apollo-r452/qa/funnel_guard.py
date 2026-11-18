#!/usr/bin/env python3
"""Apollo independent conversion receipt. Offline, read-only, standard-library only.
Amounts in USD cents; never turns clicks or externally unverified inputs into sales.
"""
import argparse
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = 'fv-apollo-conversion-proof-v1'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
LANDING = 'https://finalvestige.com/apollo-1-evidence-atlas/'
ALLOWED_SOURCES = {'youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'}
PROHIBITED_KEYS = {'email', 'ip', 'ip_address', 'phone', 'name', 'full_name', 'visitor_id', 'cookie', 'user_agent', 'customer_email'}

class Hold(ValueError):
    pass

def nonnegative_int(value, name):
    if type(value) is not int or value < 0:
        raise Hold(f'{name}: nonnegative integer required, not an estimate')
    return value

def safe_ref(value, name):
    if not isinstance(value, str) or not (8 <= len(value) <= 256) or any(ord(c) < 32 for c in value):
        raise Hold(f'{name}: reviewed provenance reference required')
    return value

def exact_url(value, host=None):
    try:
        u = urlsplit(value)
        if not (u.scheme == 'https' and u.hostname and not u.username and not u.password
            and not u.port and not u.fragment and not u.query):
            return False
        return host is None or u.hostname == host
    except (ValueError, TypeError):
        return False

def check_privacy(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in PROHIBITED_KEYS:
                raise Hold('visitor-level personal information prohibited: ' + k)
            check_privacy(v)
    elif isinstance(obj, list):
        for item in obj: check_privacy(item)

def validate_campaign(c):
    required = ('asset_id', 'utm_campaign', 'utm_source', 'utm_medium', 'utm_content')
    if not isinstance(c, dict) or any(not isinstance(c.get(k), str) for k in required):
        raise Hold('missing campaign identifiers; do not infer a creator asset')
    if c['utm_source'] not in ALLOWED_SOURCES or c['utm_medium'] != 'organic_social':
        raise Hold('unexpected platform or medium')
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{5,70}', c['asset_id']) or c['asset_id'] != c['utm_content']:
        raise Hold('immutable asset ID and UTM content must match')
    if not re.fullmatch(r'(history|mysteries)_pilot_20\d{2}_\d{2}', c['utm_campaign']):
        raise Hold('unapproved Apollo campaign namespace')
    return c.get('publication_proof_status') == 'INDEPENDENTLY_CONFIRMED' and (
        isinstance(c.get('platform_post_url'), str) and exact_url(c['platform_post_url'])) and (
        bool(c.get('praxxis_review_ref')) and c.get('approved_landing_url') == LANDING)

def validate_offer(o):
    if not isinstance(o, dict) or o.get('audience') != 'educators' or o.get('offer_type') != 'original_classroom_kit':
        raise Hold('offer must match Apollo documentary educator intent')
    proofs = ('seller_acceptance_ref','sku','rights_manifest_ref','fulfillment_test_ref',
              'refund_policy_ref','founder_release_ref')
    return o.get('status') == 'VERIFIED_PAYABLE' and all(isinstance(o.get(k),str) and len(o[k]) >= 8 for k in proofs) and (
        isinstance(o.get('checkout_url'), str) and exact_url(o['checkout_url']))

def validate_cohort(c):
    if not isinstance(c, dict) or c.get('days') not in (7, 30):
        raise Hold('cohort must be 7 or 30 calendar days')
    try:
        start, end = date.fromisoformat(c['start']), date.fromisoformat(c['end'])
    except (TypeError, ValueError, KeyError):
        raise Hold('explicit ISO date cohort boundaries required')
    if start > end or (end-start).days + 1 != c['days']:
        raise Hold('cohort boundaries do not match window')
    fields = ('qualified_human_sessions', 'landing_visits', 'cta_clicks', 'confirmed_leads')
    nums = {k:nonnegative_int(c.get(k), k) for k in fields}
    if nums['landing_visits'] > nums['qualified_human_sessions'] or nums['cta_clicks'] > nums['landing_visits'] or nums['confirmed_leads'] > nums['cta_clicks']:
        raise Hold('funnel counts exceed previous step; deduplicate and reconcile before scoring')
    rows=c.get('orders')
    if not isinstance(rows,list): raise Hold('actual confirmed order ledger required; never infer sales from click count')
    seen=set(); gross=fees=refunds=0
    for row in rows:
        if not isinstance(row,dict) or row.get('merchant_confirmed') is not True:
            raise Hold('order without independent merchant confirmation')
        ref=safe_ref(row.get('settlement_line_ref'),'settlement_line_ref')
        if ref in seen: raise Hold('duplicate settlement line')
        seen.add(ref)
        if row.get('paid_date') is None: raise Hold('paid date missing')
        try: paid=date.fromisoformat(row['paid_date'])
        except (ValueError,TypeError): raise Hold('invalid paid date')
        if not(start<=paid<=end):raise Hold('order outside paid cohort')
        if row.get('currency')!='USD':raise Hold('USD-only minor-unit ledger')
        g=nonnegative_int(row.get('gross_cents'),'gross_cents')
        f=nonnegative_int(row.get('fees_cents'),'fees_cents')
        r=nonnegative_int(row.get('refunded_cents'),'refunded_cents')
        if g<=0 or r>g: raise Hold('invalid paid gross or refund')
        gross+=g;fees+=f;refunds+=r
    if c.get('settlement_reconciled') is not True or not c.get('source_attestation_ref'):
        raise Hold('settlement and session aggregates require independent reconciliation references')
    paid=len(rows)
    if paid>nums['cta_clicks']:raise Hold('confirmed orders exceed attributed CTA clicks')
    net=gross-fees-refunds
    matched=c.get('lead_attributed_confirmed_customers')
    if matched is not None:
        matched=nonnegative_int(matched, 'lead_attributed_confirmed_customers')
        if matched>paid or matched>nums['confirmed_leads']:
            raise Hold('lead-to-customer numerator cannot exceed paid orders or confirmed leads')
    # Results are explicitly structural calculations, NOT independently authenticated by this code.
    return {'days':c['days'],'start':c['start'],'end':c['end'],**nums,'confirmed_orders':paid,
        'gross_cents':gross,'fees_cents':fees,'refunded_cents':refunds,'realized_net_cents_structural':net,
        'paid_order_conversion_rate_structural': round(paid/nums['qualified_human_sessions'],6) if nums['qualified_human_sessions'] else None,
        'net_usd_per_1000_qualified_sessions_structural': str((Decimal(net)/100*Decimal(1000)/Decimal(nums['qualified_human_sessions'])).quantize(Decimal('0.01'))) if nums['qualified_human_sessions'] else None,
        'lead_to_customer_rate_structural': round(matched/nums['confirmed_leads'],6) if matched is not None and nums['confirmed_leads'] else None,
        'tiny_sample_warning': nums['qualified_human_sessions'] < 1000 or paid < 20}

def assess(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise Hold('schema mismatch')
    check_privacy(doc)
    if doc.get('landing_url')!=LANDING or doc.get('free_cta_url')!=FREE or doc.get('commercial_cta_enabled') is not False:
        raise Hold('landing, single free investigation or disabled commercial CTA contract broken')
    creator = validate_campaign(doc.get('campaign'))
    seller = validate_offer(doc.get('offer'))
    cohorts=doc.get('cohorts',[])
    if not isinstance(cohorts,list) or len(cohorts)>2:raise Hold('at most one 7d and one 30d cohort')
    if len({x.get('days') for x in cohorts if isinstance(x,dict)})!=len(cohorts):
        raise Hold('duplicate cohort window')
    results=[validate_cohort(x) for x in cohorts]
    if len(results)==2 and results[0]['end']!=results[1]['end']:
        raise Hold('7/30-day cohorts require a common ending date for comparison')
    return {'status':'HARD_HOLD','schema':SCHEMA, 'creator_publication': 'STRUCTURALLY_DOCUMENTED_REQUIRES_EXTERNAL_REVIEW' if creator else 'NOT_VERIFIED',
        'paid_offer':'STRUCTURALLY_DOCUMENTED_REQUIRES_EXTERNAL_REVIEW' if seller else 'NOT_VERIFIED',
        'cohorts':results,'paid_revenue_verified_by_this_tool':False,
        'net_revenue_per_1000_qualified_humans_verified':None,
        'axe_core':'NOT_RUN','navigated_LCP_CLS':'NOT_RUN','actual_WordPress_staging':'NOT_RUN',
        'reason':'No input is automatically trusted as an authentic merchant/creator/analytics record. Founder and independent QD remain release authorities.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    try: out=assess(json.loads(args.input.read_text(encoding='utf8')));code=0
    except (Hold,ValueError,KeyError) as e:
        out={'status':'HARD_HOLD','invalid_evidence':str(e),'net_revenue_per_1000_qualified_humans_verified':None};code=2
    payload=json.dumps(out,sort_keys=True,indent=2)+'\n'
    if args.out:args.out.write_text(payload,encoding='utf8')
    print(payload,end='');return code
if __name__=='__main__':raise SystemExit(main())
