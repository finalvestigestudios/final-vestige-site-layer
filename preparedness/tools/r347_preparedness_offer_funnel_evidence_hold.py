#!/usr/bin/env python3
"""R347: read-only Preparedness source-safe offer and campaign evidence gate.

Allow one proposed Grok asset -> live agency-resource Archive ->
held original guide/tool -> optional owned product to be reviewed without
inventing paid orders or exposing private advice. No checkout, analytics, CMS,
merchant, social or network activity; no QD/medical/safety approvals.

A source/merchant record provided by a caller is NEVER independently verified.
Pass/fail refers solely to structural consistency of proposed evidence.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha1
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl
import json
import re

SCHEMA = 'fv-preparedness-r347-source-safe-funnel-contract-v1'
ARCHIVE = 'https://finalvestige.com/preparedness/'
TOPIC = 'family-emergency-contacts'
GUIDE = 'family-communication-plan'
TOOL = 'family-reunification-card'
NEVER_PUBLISH = {
    'may_publish': False, 'may_merge': False, 'qualified_qd_pass': False,
    'medical_or_emergency_advice_approved': False,
    'source_claim_support_verified': False, 'human_source_links_verified': False,
    'family_tool_publicly_approved': False,
    'owned_preparedness_product_authenticated': False,
    'merchant_settled_orders_authenticated': False,
    'realized_net_revenue_verified': False,
    'analytics_attribution_verified': False,
    'native_100_export_build_verified': False,
}
CAMPAIGN_KEYS = frozenset(('topic', 'asset_id', 'published_post_url', 'published_at_utc',
                           'platform', 'utm_campaign', 'utm_content',
                           'landing_url', 'free_guide', 'optional_tool', 'product'))
COHORT_KEYS = frozenset(('window_days', 'as_of_date', 'qualified_human_sessions',
                        'landing_visits', 'relevant_cta_clicks', 'confirmed_leads',
                        'merchant_confirmed_orders', 'gross_usd', 'refunds_usd',
                        'fees_usd', 'asset_id', 'utm_campaign', 'evidence_refs'))
EVIDENCE_KEYS = frozenset(('session_qualification', 'consented_measurement',
                           'lead_confirmation', 'merchant_order_report',
                           'merchant_refund_fee_report', 'deduplication_method'))
PLATFORMS = frozenset(('youtube', 'tiktok', 'instagram', 'facebook'))
SAFE_ID = re.compile(r'[a-zA-Z0-9_-]{4,90}\Z')
SAFE_UTM = re.compile(r'[a-z0-9][a-z0-9_-]{5,100}\Z')
SECRET_KEYS = re.compile(r'(?:email|phone|password|token|cookie|ip_address|name|street|address|child|dob|secret|authorization)', re.I)
PROHIBITED_KEYS = frozenset(('approved', 'qd_pass', 'publish', 'verified_revenue',
                            'conversion_success', 'revenue_per_1000', 'paid_conversion_rate'))


def git_blob(data: bytes) -> str:
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def safe_url(value: str, hosts: set[str] | None = None) -> bool:
    """HTTPS public URLs, no userinfo, credentials, tracking user IDs or port."""
    if not isinstance(value, str) or len(value) > 1200 or any(ord(c) < 33 for c in value):
        return False
    try:
        u = urlsplit(value)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.port is not None:
            return False
        if u.fragment or u.hostname.endswith('.') or u.hostname.startswith('xn--'):
            return False
        if hosts is not None and u.hostname.lower() not in hosts:
            return False
        if SECRET_KEYS.search(u.query):
            return False
        if any(k.lower() in ('gclid', 'fbclid', 'msclkid') for k, _ in parse_qsl(u.query)):
            return False
        if u.path.startswith('//') or '/..' in u.path or '\\' in u.path:
            return False
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def money(v):
    if not isinstance(v, str) or not re.fullmatch(r'(?:0|[1-9]\d{0,10})\.\d{2}', v):
        raise ValueError('MONEY_MUST_BE_FIXED_TWO_DECIMAL_STRING')
    try:
        return Decimal(v)
    except InvalidOperation as ex:
        raise ValueError('BAD_MONEY_VALUE') from ex


def no_sensitive_keys(obj) -> bool:
    """Reject PII-like key names recursively before any report or log echo."""
    if isinstance(obj, dict):
        if any(not isinstance(k, str) or SECRET_KEYS.search(k) for k in obj):
            return False
        return all(no_sensitive_keys(v) for v in obj.values())
    if isinstance(obj, list):
        return all(no_sensitive_keys(v) for v in obj)
    return isinstance(obj, (str, bool, int, type(None)))


def _date(s: str):
    if not isinstance(s, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        raise ValueError('INVALID_COHORT_DATE')
    return date.fromisoformat(s)


def _published(s):
    if not isinstance(s, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', s):
        raise ValueError('PUBLICATION_UTC_TIMESTAMP_REQUIRED')
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def review(campaign=None, cohorts=None):
    """Pure structural preflight; always HARD HOLD regardless of evidence supplied."""
    errors = []
    if campaign is None:
        campaign = {}
    if cohorts is None:
        cohorts = []
    if not isinstance(campaign, dict) or not no_sensitive_keys(campaign):
        return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                'errors': ['INVALID_OR_SENSITIVE_CAMPAIGN'], 'cohorts_checked': 0,
                'structural_acceptance': False, **NEVER_PUBLISH}
    if PROHIBITED_KEYS.intersection(campaign) or set(campaign) != CAMPAIGN_KEYS:
        errors.append('CAMPAIGN_SCHEMA_OR_FORGED_APPROVAL')
    if campaign.get('topic') != TOPIC:
        errors.append('INTENT_TOPIC_MISMATCH')
    aid = campaign.get('asset_id')
    if not isinstance(aid, str) or not SAFE_ID.fullmatch(aid):
        errors.append('UNAUTHENTICATED_OR_MALFORMED_ASSET_ID')
    platform = campaign.get('platform')
    if platform not in PLATFORMS:
        errors.append('UNSUPPORTED_PLATFORM')
    post = campaign.get('published_post_url')
    if not safe_url(post, {'youtube.com','www.youtube.com','youtu.be','tiktok.com','www.tiktok.com','instagram.com','www.instagram.com','facebook.com','www.facebook.com'}):
        errors.append('INVALID_PUBLIC_POST_URL')
    if isinstance(post, str) and isinstance(platform, str) and safe_url(post):
        host = urlsplit(post).hostname.lower()
        u = urlsplit(post)
        domains = {'youtube': ('youtube.com', 'youtu.be'), 'tiktok': ('tiktok.com',),
                   'instagram': ('instagram.com',), 'facebook': ('facebook.com',)}
        if not any(host == d or host.endswith('.'+d) for d in domains.get(platform, ())):
            errors.append('POST_PLATFORM_MISMATCH')
        if isinstance(aid, str):
            parts = [x for x in u.path.split('/') if x]
            video_id = None
            if platform == 'youtube':
                if host == 'youtu.be' and len(parts) == 1:
                    video_id = parts[0]
                elif len(parts) == 2 and parts[0] == 'shorts':
                    video_id = parts[1]
                elif u.path == '/watch':
                    video_id = dict(parse_qsl(u.query)).get('v')
            elif platform == 'tiktok' and 'video' in parts:
                idx = parts.index('video')
                video_id = parts[idx + 1] if idx + 1 < len(parts) else None
            elif platform == 'instagram' and len(parts) == 2 and parts[0] in ('reel', 'p'):
                video_id = parts[1]
            elif platform == 'facebook' and len(parts) == 2 and parts[0] in ('reel', 'watch'):
                video_id = parts[1]
            if video_id != aid:
                errors.append('POST_URL_ASSET_ID_NOT_IDENTICAL')
    try:
        if _published(campaign.get('published_at_utc')) > datetime.now(timezone.utc):
            errors.append('FUTURE_POST_NOT_PUBLISHED')
    except (ValueError, TypeError):
        errors.append('INVALID_PUBLICATION_TIMESTAMP')
    utm = campaign.get('utm_campaign')
    if not isinstance(utm, str) or not SAFE_UTM.fullmatch(utm):
        errors.append('INVALID_CAMPAIGN_UTM')
    if campaign.get('utm_content') != aid:
        errors.append('UTM_ASSET_ID_MISMATCH')
    if campaign.get('landing_url') != ARCHIVE:
        errors.append('ONLY_EXISTING_PUBLIC_AGENCY_ARCHIVE_ALLOWED')
    if campaign.get('free_guide') != {'slug': GUIDE, 'release_state': 'PRIVATE_QD_HOLD'}:
        errors.append('ORIGINAL_GUIDE_MUST_REMAIN_PRIVATE')
    if campaign.get('optional_tool') != {'slug': TOOL, 'release_state': 'PRIVATE_QD_HOLD'}:
        errors.append('ORIGINAL_TOOL_MUST_REMAIN_PRIVATE')
    # Real ownership/rights/checkout/fulfillment must be checked independently.
    product = campaign.get('product')
    if product is not None:
        if not isinstance(product, dict) or set(product) != {'candidate_sku', 'candidate_url', 'release_state', 'rights_review', 'fulfillment_review', 'refund_review'}:
            errors.append('UNVERIFIED_PRODUCT_SCHEMA')
        else:
            if product.get('release_state') != 'UNAUTHENTICATED_HOLD' or any(product.get(x) != 'UNVERIFIED' for x in ('rights_review','fulfillment_review','refund_review')):
                errors.append('FORGED_COMMERCE_APPROVAL')
            if not isinstance(product.get('candidate_sku'), str) or not SAFE_ID.fullmatch(product['candidate_sku']):
                errors.append('INVALID_CANDIDATE_SKU')
            if not safe_url(product.get('candidate_url')):
                errors.append('INVALID_CANDIDATE_PRODUCT_URL')
    if not isinstance(cohorts, list):
        cohorts = []
        errors.append('COHORTS_MUST_BE_LIST')
    if len(cohorts) > 2:
        errors.append('ONLY_7_AND_30_DAY_COHORTS')
    seen = set()
    for c in cohorts:
        if not isinstance(c, dict) or not no_sensitive_keys(c):
            errors.append('INVALID_OR_SENSITIVE_COHORT')
            continue
        if set(c) != COHORT_KEYS or PROHIBITED_KEYS.intersection(c):
            errors.append('COHORT_SCHEMA_OR_FORGED_REVENUE_FIELD')
            continue
        window = c.get('window_days')
        if type(window) is not int or window not in (7,30) or window in seen:
            errors.append('INVALID_OR_DUPLICATE_COHORT_WINDOW')
        else:
            seen.add(window)
        if c.get('asset_id') != aid or c.get('utm_campaign') != utm:
            errors.append('COHORT_ATTRIBUTION_MISMATCH')
        try:
            when = _date(c.get('as_of_date'))
            if when > datetime.now(timezone.utc).date():
                errors.append('FUTURE_COHORT_DATE')
        except ValueError:
            errors.append('INVALID_COHORT_DATE')
        metrics = ('qualified_human_sessions', 'landing_visits', 'relevant_cta_clicks',
                   'confirmed_leads', 'merchant_confirmed_orders')
        vals = [c.get(k) for k in metrics]
        if any(type(v) is not int or not 0 <= v <= 10_000_000 for v in vals):
            errors.append('INVALID_COHORT_COUNT')
        else:
            sess, land, click, leads, orders = vals
            if land > sess or click > land or leads > click or orders > click:
                errors.append('IMPOSSIBLE_FUNNEL_COUNTS')
        try:
            gross, refunds, fees = [money(c.get(k)) for k in ('gross_usd', 'refunds_usd', 'fees_usd')]
            if refunds + fees > gross:
                errors.append('REPORTED_FEES_REFUNDS_EXCEED_GROSS')
            if vals[-1] == 0 and gross > 0:
                errors.append('GROSS_WITHOUT_REPORTED_ORDERS')
            if type(vals[-1]) is int and vals[-1] > 0 and gross == 0:
                errors.append('PAID_ORDERS_WITHOUT_REPORTED_GROSS')
        except (ValueError, TypeError):
            errors.append('INVALID_MONEY_AMOUNTS')
        ev = c.get('evidence_refs')
        if not isinstance(ev, dict) or set(ev) != EVIDENCE_KEYS:
            errors.append('MISSING_REQUIRED_EVIDENCE_REF_TYPES')
        else:
            for k in EVIDENCE_KEYS:
                # References are IDs, NEVER independently authenticated here.
                v = ev[k]
                if v is not None and (not isinstance(v, str) or not SAFE_ID.fullmatch(v)):
                    errors.append('INVALID_EVIDENCE_REFERENCE:' + k)
            if vals[-1] and not ev.get('merchant_order_report'):
                errors.append('ORDERS_WITHOUT_MERCHANT_REPORT_REFERENCE')
            if vals[3] and not ev.get('lead_confirmation'):
                errors.append('LEADS_WITHOUT_CONFIRMATION_REFERENCE')
            if any(vals[:3]) and not ev.get('session_qualification'):
                errors.append('SESSIONS_WITHOUT_QUALIFICATION_REFERENCE')
            if (c.get('refunds_usd') != '0.00' or c.get('fees_usd') != '0.00') and not ev.get('merchant_refund_fee_report'):
                errors.append('UNRECONCILED_FEES_REFUNDS')
    if len(cohorts) == 2 and all(isinstance(c, dict) and set(c) == COHORT_KEYS for c in cohorts):
        by_window = {c.get('window_days'): c for c in cohorts if type(c.get('window_days')) is int}
        if 7 in by_window and 30 in by_window:
            c7, c30 = by_window[7], by_window[30]
            if c7.get('as_of_date') != c30.get('as_of_date'):
                errors.append('CROSS_WINDOW_AS_OF_DATE_MISMATCH')
            for field in ('qualified_human_sessions','landing_visits','relevant_cta_clicks',
                          'confirmed_leads','merchant_confirmed_orders'):
                a, b = c7.get(field), c30.get(field)
                if type(a) is int and type(b) is int and a > b:
                    errors.append('LONGER_WINDOW_FEWER_EVENTS:' + field)
    # Redact campaign URLs and evidence IDs from output. Structure != proof.
    return {
        'schema': SCHEMA,
        'state': 'INVALID_HARD_HOLD' if errors else 'STRUCTURAL_EVIDENCE_ONLY_HARD_HOLD',
        'errors': sorted(set(errors)),
        'cohorts_checked': len(cohorts),
        'structural_acceptance': not errors,
        'audience_topic': TOPIC,
        'public_free_destination': ARCHIVE,
        'private_guide': GUIDE, 'private_tool': TOOL,
        'externally_authenticated_social_asset': False,
        'independently_authenticated_evidence_receipts': False,
        'qualified_human_cohort_verified': False,
        'kpi_net_revenue_per_1000_qualified_sessions': None,
        'outstanding_legacy_editorial_conflicts': 15,
        'outstanding_article15_tool104_reviews': 17,
        'competing_source_ids_unadjudicated': 4,
        'limitations': ['Structure is not merchant/source authentication',
                        'No new tracker, affiliate product or paid service authorized',
                        'Existing agency-resource Archive only; all original drafts private'],
        **NEVER_PUBLISH,
    }


def native_audit(root: Path) -> dict:
    """Authenticate predecessor and preserve R346 source-claim HOLD; no writes."""
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    errors = []
    try:
        from preparedness.tools import r346_source_claim_decision_binding_hold as prior
        p = prep / 'tools' / 'r346_source_claim_decision_binding_hold.py'
        if p.is_symlink() or not p.is_file() or git_blob(p.read_bytes()) != 'ffa0e61d36d954d6e67bc66dadab590d7cd99cc9':
            errors.append('R346_SOURCE_REVIEW_PREDECESSOR_BLOB_DRIFT')
        result = prior.native_audit(root)
        if result.get('state') != 'PENDING_PROPOSALS_HARD_HOLD' or result.get('errors') or len(result.get('docket', [])) != 4:
            errors.append('R346_ORIGINAL_SOURCE_CUSTODY_UNAVAILABLE')
    except (ImportError, OSError, ValueError, TypeError, KeyError) as ex:
        errors.append('R346_NATIVE_SOURCE_REQUIRED:' + type(ex).__name__)
    r = review()
    r['errors'] = sorted(set(r['errors'] + errors))
    r['state'] = 'INVALID_HARD_HOLD'
    return r


def main():
    import argparse
    ap = argparse.ArgumentParser(description='R347 source-safe Preparedness commercial evidence review; HOLD')
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    print(json.dumps(native_audit(args.repo_root), sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
