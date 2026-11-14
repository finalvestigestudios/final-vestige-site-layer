"""Final Vestige Dispatch: offline, privacy-minimizing funnel receipt classifier.

No network, WordPress, merchant, email, subscriber APIs, or side effects.
This code never authorizes sending and never promotes input claims to paid sales.
"""
from __future__ import annotations
from collections import Counter
from decimal import Decimal, InvalidOperation

EVENTS = {'landing_view', 'pdf_download', 'signup_attempt', 'confirmed_signup',
          'welcome_received', 'dispatch_click', 'merchant_click', 'order_claim'}
ALLOWED_CHANNELS = {'youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'}


def safe_counts(status: dict) -> dict:
    """WordPress aggregates are overlapping surfaces, NOT address counts."""
    subs = status.get('subscribers', {})
    fields = ('total', 'confirmed', 'unconfirmed', 'suppressed')
    if not isinstance(subs, dict) or any(type(subs.get(k)) is not int or subs[k] < 0 for k in fields):
        raise ValueError('Invalid subscriber snapshot')
    if not isinstance(status.get('site_can_send'), bool):
        raise ValueError('Missing technical send status')
    return {'provider_aggregate': {k: subs[k] for k in fields},
            'labels_nonadditive': True,
            'total_less_than_confirmed_plus_unconfirmed': subs['total'] < subs['confirmed'] + subs['unconfirmed'],
            'technical_can_send': status['site_can_send'],
            'verified_eligible_email_recipients': None,
            'provider_authoritative_recipient_proof': 'MISSING',
            'release': 'HOLD_UNSENT'}


def classify_receipts(events: list[dict]) -> dict:
    """Only provider-sourced confirmation is a *candidate* lead, not an audited subscriber.

    Never emit event identifiers, recipient hashes or raw event objects. A supplied
    claim of a sale is NOT an independently verified settlement.
    """
    if not isinstance(events, list):
        raise ValueError('Expected list')
    seen_event_ids, provider_confirmations = set(), set()
    counts = Counter()
    rejected = Counter()
    for event in events:
        if not isinstance(event, dict) or event.get('kind') not in EVENTS:
            rejected['invalid_kind'] += 1
            continue
        uid = event.get('event_id')
        if not isinstance(uid, str) or not 4 <= len(uid) <= 120 or uid in seen_event_ids:
            rejected['missing_or_duplicate_event_id'] += 1
            continue
        seen_event_ids.add(uid)
        kind = event['kind']
        if kind == 'confirmed_signup':
            ref = event.get('provider_receipt_key')
            if event.get('source_system') != 'jetpack' or not isinstance(ref, str) or not ref.strip():
                rejected['no_provider_confirmation_receipt'] += 1
                continue
            if ref in provider_confirmations:
                rejected['duplicate_provider_confirmation'] += 1
                continue
            provider_confirmations.add(ref)
            counts['provider_labelled_confirmation_candidates'] += 1
        elif kind == 'order_claim':
            # Not a payable conversion without an independent settlement/fee/refund proof.
            counts['unverified_order_claims'] += 1
        else:
            counts[kind] += 1
        if kind == 'landing_view':
            if event.get('utm_medium') == 'organic_social' and event.get('utm_source') in ALLOWED_CHANNELS and event.get('asset_id'):
                counts['canonical_social_tagged_landing_candidates'] += 1
            else:
                counts['unattributed_landing_candidates'] += 1
    return {'event_counts_are_unverified_inputs': True,
            'counts': dict(sorted(counts.items())),
            'rejections': dict(sorted(rejected.items())),
            'verified_confirmed_signups': None,
            'verified_paid_orders': None,
            'recognized_net_revenue': None,
            'net_revenue_per_1000_qualified_human_sessions': None,
            'release': 'HOLD_UNSENT'}


def hypothetical_net_per_thousand(qualified_human_sessions: int | None,
                                   gross_cents: int | None,
                                   refunded_cents: int | None,
                                   fees_cents: int | None) -> str | None:
    """Pure arithmetic for *externally audited* inputs; NEVER proof of actual sales."""
    nums = (qualified_human_sessions, gross_cents, refunded_cents, fees_cents)
    if any(type(x) is not int or x < 0 for x in nums):
        return None
    if qualified_human_sessions == 0 or refunded_cents > gross_cents:
        return None
    try:
        result = Decimal(gross_cents - refunded_cents - fees_cents) * 10 / Decimal(qualified_human_sessions)
        return str(result.quantize(Decimal('0.01')))
    except (InvalidOperation, ZeroDivisionError):
        return None


def release_state() -> dict:
    return {'editorial_slots': [1, 2, 4, 6], 'merchant_slots': [3, 5],
            'all_six': 'HOLD_UNSENT', 'merchant_03_05': 'HOLD_MERCHANT',
            'proofs_required': ['merchant_named_acceptance', 'merchant_email_rights',
                'issued_earning_link', 'approved_live_guide', 'actual_checkout_terms',
                'native_jetpack_preview', 'publisher_valid_postal_address',
                'functional_unsubscribe', 'confirmed_recipient_eligibility',
                'fieldbook_welcome_received', 'founder_final_campaign_approval'],
            'download_is_not_consent': True, 'configured_welcome_is_not_received': True,
            'report_revenue': 'NOT_COMPUTABLE'}
