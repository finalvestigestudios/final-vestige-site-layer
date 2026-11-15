"""Offline, fail-closed Dispatch R383 consent, delivery and merchant gate.
No remote calls, email sends, addresses, customer data or analytics writes.
"""
from decimal import Decimal, InvalidOperation

EDITORIAL = {1, 2, 4, 6}
COMMERCIAL = {3, 5}
SHARED_PROOFS = (
    'founder_final_approval', 'provider_unique_confirmed_recipient_proof',
    'welcome_received_and_pdf_access_verified', 'jetpack_native_preview_verified',
    'subject_matches_native_post_title', 'valid_fv_postal_address_in_render',
    'working_unsubscribe_in_actual_received_message', 'brand_editorial_signoff',
)
MERCHANT_PROOFS = (
    'named_fv_affiliate_acceptance', 'product_email_channel_permission',
    'approved_email_creative_rights', 'issued_earning_link',
    'approved_live_warmup_guide', 'referred_checkout_and_terms_checked',
    'product_claims_substantiated_or_removed', 'adjacent_disclosure_verified',
)

def release_decision(issue, evidence):
    """Accept only explicit True booleans; never infer permissions from public pages."""
    if type(issue) is not int or issue not in EDITORIAL | COMMERCIAL:
        raise ValueError('unknown original pilot issue')
    if not isinstance(evidence, dict):
        raise TypeError('evidence must be a proof dictionary')
    missing = [k for k in SHARED_PROOFS if evidence.get(k) is not True]
    if issue in COMMERCIAL:
        missing += [k for k in MERCHANT_PROOFS if evidence.get(k) is not True]
    # An attested checklist cannot itself authorize a send or production release.
    return {'issue': issue, 'state': 'HOLD_UNSENT',
            'merchant_hold': issue in COMMERCIAL and any(
                evidence.get(k) is not True for k in MERCHANT_PROOFS),
            'missing_proofs': missing, 'automatic_send_authorized': False}

def audience_snapshot(total, confirmed, unconfirmed, wpcom_followers, email_followers):
    values = (total, confirmed, unconfirmed, wpcom_followers, email_followers)
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError('counts must be nonnegative integers')
    return {'reported_total': total, 'reported_confirmed': confirmed,
            'reported_unconfirmed': unconfirmed, 'wpcom_followers': wpcom_followers,
            'email_followers': email_followers, 'unique_eligible_inboxes': None,
            'combined_audience': None}

def net_commission_per_1000(qualified_sessions, order_records):
    """Publisher commission only; never retail sales or raw clicks."""
    if qualified_sessions is None or not isinstance(qualified_sessions, int) \
            or isinstance(qualified_sessions, bool) or qualified_sessions <= 0:
        return None
    if order_records is None or not isinstance(order_records, list):
        return None
    seen = set()
    net = Decimal('0')
    for rec in order_records:
        if not isinstance(rec, dict):
            return None
        if rec.get('merchant_report_verified') is not True or \
                rec.get('settlement_final') is not True or \
                rec.get('refunds_fees_final') is not True:
            return None
        order_id = rec.get('opaque_order_id')
        if not isinstance(order_id, str) or not order_id or order_id in seen:
            return None
        seen.add(order_id)
        try:
            amount = Decimal(str(rec['publisher_commission']))
            refunds = Decimal(str(rec['refunds_and_clawbacks']))
            fees = Decimal(str(rec['publisher_fees']))
            if not all(v.is_finite() and v >= 0 for v in (amount, refunds, fees)):
                return None
        except (KeyError, InvalidOperation, TypeError, ValueError):
            return None
        net += amount - refunds - fees
    return str((net * Decimal('1000') / Decimal(qualified_sessions)).quantize(Decimal('0.01')))
