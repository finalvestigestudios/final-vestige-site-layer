#!/usr/bin/env python3
"""R112: private, read-only Preparedness source-to-offer handoff. Never publish.

Input values are reviewer-supplied assertions, NOT independent verification of
Payhip, safety, merchant fulfillment, actual website visits, or paid orders.
No network, persistent state, tracking scripts, PII or WordPress API access.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from urllib.parse import urlsplit, parse_qsl

SCHEMA = 'fv-preparedness-r112-funnel-HOLD-v1'
SLUG = 'household-emergency-plan'
SECTION = 'start-here'
LANDING = 'https://finalvestige.com/preparedness/start-here/household-emergency-plan/'
PLATFORMS = {'youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'}
REQUIRED_PROOFS = ('seller_ownership_checked', 'sku_live_checked',
                   'rights_and_license_checked', 'price_terms_checked',
                   'delivery_test_checked', 'returns_and_fees_checked',
                   'merchant_destination_checked', 'human_safety_qualified')
RECEIPT_FIELDS = ('qualified_sessions', 'paid_orders', 'refunded_orders',
                  'gross_paid_usd', 'refunds_usd', 'fees_usd')

class Hold(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Hold(message)

def is_http_link(s, host):
    if not isinstance(s, str) or len(s) > 1500 or any(ord(c) < 33 for c in s):
        return False
    try:
        u = urlsplit(s)
        return (u.scheme == 'https' and u.hostname == host and not u.username and
                not u.password and u.port is None and not u.fragment and
                not u.query and u.path.startswith('/') and u.path != '/')
    except ValueError:
        return False

def article_gate(meta, body, taxonomy):
    require(isinstance(meta, dict) and isinstance(body, str) and
            isinstance(taxonomy, dict), 'missing article input')
    matches = [s for s in taxonomy.get('slate', []) if isinstance(s, dict)
               and s.get('slug') == SLUG]
    require(len(matches) == 1 and matches[0].get('section') == SECTION and
            matches[0].get('gate') is True and
            taxonomy.get('base_path') == '/preparedness/', 'canonical slate drift')
    require(meta.get('slug') == SLUG and meta.get('section') == SECTION and
            meta.get('track') == 'modern', 'wrong source-backed free guide')
    require(meta.get('status') == {'editorial': 'drafted', 'publish': 'draft'} and
            meta.get('safety_review', {}).get('state') == 'pending',
            'draft/pending safety state changed; human reconciliation required')
    support = meta.get('source_use', {})
    cited = re.findall(r'\{\{cite:([a-z0-9-]+)\}\}', body)
    require(isinstance(support, dict) and len(support) >= 3 and
            len(set(cited)) >= 3 and set(cited) <= set(support) and
            all(isinstance(v, str) and v.strip() for v in support.values()),
            'source-use attribution missing or citation scope drift')
    require('<section class="pa-act"' in body and 'What to do now' in body and
            'local officials' in body, 'basic source-context action box missing')
    return {'slug': SLUG, 'source_ids_count': len(set(cited)),
            'article_sha256_NOT_A_SIGNATURE': hashlib.sha256(body.encode()).hexdigest(),
            'current_release_state': 'DRAFT_PENDING_QUALIFIED_SAFETY_REVIEW',
            'source_accuracy_asserted': False, 'may_publish': False}

def campaign_gate(c):
    require(isinstance(c, dict), 'campaign missing')
    blockers = []
    asset = c.get('asset_id')
    if not isinstance(asset, str) or not re.fullmatch(r'FV-[A-Za-z0-9][A-Za-z0-9_-]{5,79}', asset):
        blockers.append('GROK_ASSET_ID_NOT_ACKNOWLEDGED')
    source = c.get('utm_source')
    if source not in PLATFORMS:
        blockers.append('PLATFORM_NOT_CONFIRMED')
    if c.get('utm_medium') != 'organic_social':
        blockers.append('MEDIUM_CONTRACT_MISMATCH')
    if not re.fullmatch(r'preparedness_pilot_20\d\d_(0[1-9]|1[0-2])', str(c.get('utm_campaign', ''))):
        blockers.append('CAMPAIGN_CONTRACT_MISMATCH')
    if c.get('utm_content') != asset:
        blockers.append('UTM_ASSET_ID_MISMATCH')
    if c.get('landing_url') != LANDING:
        blockers.append('NONCANONICAL_OR_UNVERIFIED_LANDING')
    if c.get('post_url'):
        try:
            u = urlsplit(c['post_url'])
            if u.scheme != 'https' or not u.hostname or u.username or u.password:
                blockers.append('POST_URL_INVALID')
        except (ValueError, TypeError):
            blockers.append('POST_URL_INVALID')
    else:
        blockers.append('POST_URL_NOT_SUPPLIED')
    if c.get('posted') is not True:
        blockers.append('GROK_POST_NOT_VERIFIED')
    return blockers

def offer_gate(o):
    if not isinstance(o, dict):
        return ['NO_VERIFIED_PREPAREDNESS_SKU']
    blockers = []
    if not isinstance(o.get('sku'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{3,64}', o['sku']):
        blockers.append('SELLER_SKU_NOT_VERIFIED')
    if o.get('ownership') != 'FINAL_VESTIGE_STUDIOS':
        blockers.append('SELLER_OWNERSHIP_UNVERIFIED')
    if o.get('offer_kind') != 'owned_digital_pack':
        blockers.append('INAPPROPRIATE_OR_UNAPPROVED_OFFER')
    if not is_http_link(o.get('checkout_url'), 'payhip.com'):
        blockers.append('PAYHIP_MERCHANT_URL_UNVERIFIED')
    for k in REQUIRED_PROOFS:
        proof = o.get('receipts', {}).get(k) if isinstance(o.get('receipts'), dict) else None
        if not isinstance(proof, dict) or proof.get('reviewed') is not True or not isinstance(proof.get('evidence_id'), str) or not re.fullmatch(r'[A-Za-z0-9/_-]{6,100}', proof['evidence_id']):
            blockers.append('EVIDENCE_MISSING_' + k.upper())
    if o.get('core_emergency_info_free') is not True:
        blockers.append('ESSENTIAL_SAFETY_CONTENT_CANNOT_BE_GATED')
    if o.get('matches_household_plan') is not True:
        blockers.append('AUDIENCE_OFFER_MISMATCH')
    if o.get('disclosure') != 'Optional paid download; the emergency guide is free.':
        blockers.append('PAID_OPTION_DISCLOSURE_MISSING')
    return blockers

def evaluate(meta, body, taxonomy, campaign, offer):
    article = article_gate(meta, body, taxonomy)
    blockers = campaign_gate(campaign) + offer_gate(offer)
    return {'schema': SCHEMA, 'issue': 136, 'commercial_issue': 820,
            'business_issue': 818, 'source_guide': article,
            'landing_url': LANDING, 'landing_deployed': False,
            'release_state': 'HOLD', 'may_publish': False,
            'may_edit_wordpress': False, 'may_change_navigation': False,
            'may_approve_safety_or_QD': False,
            'checkout_verified_by_tool': False,
            'candidate_for_manual_draft_review': not blockers,
            'buyer_click_target_enabled': False,
            'hold_reasons': sorted(set(blockers)),
            'events': ['qualified_human_session', 'relevant_cta_click',
                       'confirmed_opt_in', 'merchant_checkout_start_observed',
                       'merchant_confirmed_paid_order', 'merchant_confirmed_refund',
                       'merchant_reported_fees'],
            'disclaimer': 'Pure synthetic/reviewer-supplied status; no live visits, leads or orders independently observed.'}

def _nonnegative_decimal(value, label):
    require(type(value) in (str, int), label + ': use exact decimal strings or integers')
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        raise Hold(label + ': invalid number') from None
    require(d.is_finite() and d >= 0 and d.as_tuple().exponent >= -2,
            label + ': negative, nonfinite or >2 decimal places')
    return d

def cohort_metrics(cohort):
    """Accept ONLY merchant-confirmed aggregate receipts; never clicks as sales."""
    require(isinstance(cohort, dict) and cohort.get('window_days') in (7, 30),
            'only seven or thirty day cohorts accepted')
    require(cohort.get('human_qualification_method') == 'documented_approved',
            'human session denominator not documented')
    require(cohort.get('merchant_origin') == 'payhip_export_confirmed',
            'merchant source of truth absent')
    require(cohort.get('attribution_method') == 'same_asset_id_campaign_confirmed',
            'merchant order attribution unsupported')
    for key in RECEIPT_FIELDS:
        require(cohort.get(key + '_source_verified') is True,
                key + ' not source verified')
    sessions = _nonnegative_decimal(cohort.get('qualified_sessions'), 'sessions')
    orders = _nonnegative_decimal(cohort.get('paid_orders'), 'orders')
    refunded = _nonnegative_decimal(cohort.get('refunded_orders'), 'refunds')
    require(all(x == x.to_integral_value() for x in (sessions, orders, refunded)),
            'counts must be integers')
    require(refunded <= orders <= sessions, 'count reconciliation failed')
    gross = _nonnegative_decimal(cohort.get('gross_paid_usd'), 'gross')
    refunds = _nonnegative_decimal(cohort.get('refunds_usd'), 'refund amounts')
    fees = _nonnegative_decimal(cohort.get('fees_usd'), 'fees')
    require(refunds + fees <= gross, 'net cannot be inferred from invalid merchant totals')
    require(sessions > 0, 'zero qualified sessions; KPI is N/A')
    net = gross - refunds - fees
    return {'window_days': cohort['window_days'],
            'qualified_human_sessions': int(sessions), 'paid_orders': int(orders),
            'refunded_orders': int(refunded), 'realized_net_usd': str(net),
            'paid_order_rate': str(orders / sessions),
            'net_usd_per_1000_qualified_sessions': str(net * 1000 / sessions),
            'small_sample_warning': sessions < 100 or orders < 10,
            'source_confirmation': 'REVIEWER_REPORTED_NOT_INDEPENDENTLY_OBSERVED',
            'never_conflate_clicks_with_sales': True}
