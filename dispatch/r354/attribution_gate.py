"""Offline, fail-closed Dispatch funnel evidence validator. No network, PII, or sends.

Separate Grok's canonical organic_social first touch, Jetpack consent, email last
 touch, and authenticated merchant settlement. Never equate one with another.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
from urllib.parse import urlparse, parse_qs
from typing import Any
import re

CHANNELS = frozenset({'youtube','tiktok','instagram','facebook','pinterest','x','bluesky'})
TOPICS = frozenset({'mind','mysteries','history','preparedness'})
SOCIAL_MEDIUM = 'organic_social'  # Source: Grok/Praxxis TASK-008, not the older 'social' alias
CAMPAIGN_SUFFIX = '_pilot_2026_11'
EMAIL_CAMPAIGN = 'dispatch_pilot_2026_11'
ASSET_ID = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{5,99}$')

@dataclass(frozen=True)
class Verdict:
    state: str
    reasons: tuple[str, ...]
    details: dict[str, Any] | None = None
    def to_dict(self):
        return asdict(self)


def social_touch(e: dict | None) -> Verdict:
    """Trust only an actual, reviewed Grok asset and the exact TASK-008 convention."""
    if not isinstance(e, dict):
        return Verdict('HOLD', ('MISSING_SOCIAL_RECEIPT',))
    missing=[]
    if e.get('utm_source') not in CHANNELS: missing.append('UNKNOWN_SOCIAL_CHANNEL')
    if e.get('utm_medium') != SOCIAL_MEDIUM: missing.append('NONCANONICAL_SOCIAL_MEDIUM')
    if e.get('topic_cluster') not in TOPICS or e.get('utm_campaign') != str(e.get('topic_cluster'))+CAMPAIGN_SUFFIX:
        missing.append('NONCANONICAL_CAMPAIGN')
    if not isinstance(e.get('asset_id'),str) or not ASSET_ID.fullmatch(e['asset_id']): missing.append('UNVERIFIED_ASSET_ID_SHAPE')
    if e.get('utm_content') != e.get('asset_id'): missing.append('ASSET_ID_MISMATCH')
    if not isinstance(e.get('publication_time'),str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d\d:\d\d:\d\d(?:Z|[+-]\d\d:\d\d)',e['publication_time']): missing.append('PUBLICATION_TIMESTAMP_REQUIRED')
    if e.get('owner_verified_asset') is not True or not e.get('rights_qa_reference'):
        missing.append('GROK_ASSET_AND_RIGHTS_NOT_PROVEN')
    for label in ('public_post_url','fv_landing_url'):
        u=e.get(label)
        if not isinstance(u,str) or not u.startswith('https://') or not urlparse(u).hostname:
            missing.append(label.upper()+'_MISSING')
    landing=e.get('fv_landing_url','')
    if isinstance(landing,str) and urlparse(landing).hostname != 'finalvestige.com':
        missing.append('LANDING_NOT_FIRST_PARTY')
    if isinstance(landing,str) and any(k in parse_qs(urlparse(landing).query) for k in ('email','subscriber_id','gclid')):
        missing.append('PERSONAL_OR_AD_IDENTIFIER_IN_LANDING')
    return Verdict('QA_ELIGIBLE' if not missing else 'HOLD',tuple(dict.fromkeys(missing)), {'acquisition_only': True})


def provider_counts(s: dict | None) -> Verdict:
    """Counts are diagnostics, never an additive list or the recipient denominator."""
    if not isinstance(s,dict) or any(type(s.get(k)) is not int or s[k]<0 for k in ('total','confirmed','unconfirmed','wpcom_followers','email_followers')):
        return Verdict('HOLD',('INVALID_AGGREGATE_COUNTS',))
    flags=[]
    if s['total'] != s['confirmed']+s['unconfirmed']:
        flags.append('OVERLAPPING_OR_INCONSISTENT_CATEGORIES')
    return Verdict('DIAGNOSTIC_ONLY',tuple(flags), {'eligible_recipients':None,'confirmed_events':None,'categories_not_additive':True,'counts':dict(s)})


def confirmed_signup(event: dict | None, seen: set[str]) -> Verdict:
    """One confirmed lead per provider-authoritative transition; never store email."""
    if not isinstance(event,dict): return Verdict('HOLD',('NO_PROVIDER_EVENT',))
    reasons=[]
    if event.get('provider') != 'jetpack': reasons.append('WRONG_PROVIDER')
    if event.get('event_type') != 'subscription_confirmed': reasons.append('NOT_CONFIRMATION_TRANSITION')
    if event.get('newsletter_permission') is not True: reasons.append('CONSENT_NOT_ATTESTED')
    if event.get('unsubscribed') is not False: reasons.append('OPTOUT_UNKNOWN_OR_ACTIVE')
    if not isinstance(event.get('consent_proof_ref'),str) or not event.get('consent_proof_ref'): reasons.append('CONSENT_PROVENANCE_MISSING')
    opaque=event.get('provider_confirmation_id')
    if not isinstance(opaque,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{8,128}',opaque): reasons.append('INVALID_OPAQUE_EVENT_ID')
    if 'email' in event or 'ip' in event or 'name' in event: reasons.append('PII_IN_ANALYTICS_EVENT')
    if opaque in seen: reasons.append('DUPLICATE_CONFIRMATION')
    if reasons: return Verdict('HOLD',tuple(reasons),{'count_new_confirmed_leads':0})
    seen.add(opaque)
    return Verdict('ACCEPT_ONE_CONFIRMED_LEAD',(),{'count_new_confirmed_leads':1})


def email_touch(e: dict | None) -> Verdict:
    """No usable last-touch until approved campaign AND verified live CTA."""
    if not isinstance(e,dict): return Verdict('HOLD',('MISSING_EMAIL_TOUCH',))
    reasons=[]
    if e.get('utm_source')!='dispatch' or e.get('utm_medium')!='email' or e.get('utm_campaign')!=EMAIL_CAMPAIGN:
        reasons.append('NONCANONICAL_EMAIL_UTM')
    if e.get('utm_content') not in {f'issue_{i:02}' for i in range(1,7)}: reasons.append('INVALID_ISSUE_CONTENT')
    if e.get('approved_live_cta') is not True: reasons.append('CTA_NOT_APPROVED_LIVE')
    if e.get('founder_send_approval') is not True: reasons.append('NO_SEND_APPROVAL')
    if e.get('actually_delivered') is not True: reasons.append('DELIVERY_UNPROVEN')
    return Verdict('ATTRIBUTABLE_LAST_TOUCH' if not reasons else 'HOLD',tuple(reasons), {'do_not_overwrite_verified_first_touch':True})


def paid_outcome(e: dict | None) -> Verdict:
    """Merchant-verified money in USD minor units; do not infer from click data."""
    if not isinstance(e,dict): return Verdict('HOLD',('NO_MERCHANT_RECEIPT',))
    reasons=[]
    if e.get('merchant_attested') is not True or e.get('settlement_status')!='settled': reasons.append('SETTLEMENT_UNVERIFIED')
    if e.get('order_status') not in ('paid','completed'): reasons.append('NOT_PAID')
    if e.get('currency')!='USD': reasons.append('UNSUPPORTED_CURRENCY')
    if not isinstance(e.get('order_token'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,128}',e['order_token']): reasons.append('PRIVATE_OPAQUE_ORDER_TOKEN_REQUIRED')
    if any(type(e.get(k)) is not int or e[k]<0 for k in ('gross_cents','fees_cents','refund_cents')): reasons.append('INVALID_MONEY')
    if 'customer_email' in e or 'customer_name' in e: reasons.append('PII_FORBIDDEN')
    return Verdict('SETTLED_RECEIPT' if not reasons else 'HOLD',tuple(reasons))


def revenue_per_1000(sessions: int | None, receipts: list[dict] | None, attestation: bool=False) -> Verdict:
    if attestation is not True or type(sessions) is not int or sessions<=0 or not isinstance(receipts,list) or not receipts:
        return Verdict('NOT_COMPUTABLE',('QUALIFIED_SESSIONS_OR_SETTLEMENT_MISSING',))
    ids=set();net=0;reasons=[]
    for item in receipts:
        v=paid_outcome(item)
        if v.state!='SETTLED_RECEIPT': reasons.extend(v.reasons);continue
        if item['order_token'] in ids: reasons.append('DUPLICATE_ORDER');continue
        ids.add(item['order_token']);net+=item['gross_cents']-item['fees_cents']-item['refund_cents']
    if reasons: return Verdict('NOT_COMPUTABLE',tuple(dict.fromkeys(reasons)))
    rate=Decimal(net)*Decimal(10)/Decimal(sessions) # cents * 1000 / 100 / sessions
    return Verdict('COMPUTABLE_WITH_TINY_SAMPLE_WARNING' if sessions<1000 or len(ids)<30 else 'COMPUTABLE',(),{'net_revenue_per_1000_usd':str(rate.quantize(Decimal('.01'))),'unique_settled_orders':len(ids),'net_cents':net,'qualified_human_sessions':sessions,'tiny_sample':sessions<1000 or len(ids)<30})


def edition_hold(number: int, evidence: dict | None=None) -> Verdict:
    if number not in range(1,7): return Verdict('HOLD',('INVALID_ISSUE',))
    keys=('founder_campaign_approval','provider_eligible_audience','welcome_received','native_jetpack_preview','fv_qualifying_postal_address','functional_optout')
    if number in (3,5): keys+=('publisher_specific_merchant_acceptance','email_promotion_rights','issued_earning_url','approved_live_warmup','checkout_and_refund_truth','offer_disclosure_verified')
    missing=tuple(x for x in keys if not isinstance(evidence,dict) or evidence.get(x) is not True)
    return Verdict('HOLD_UNSENT',missing,{'edition':number,'merchant_hold':number in (3,5),'founder_approval_required':True})
