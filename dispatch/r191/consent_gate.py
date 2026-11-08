"""Source-only, fail-closed Dispatch gate. Never contacts WordPress or recipients."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Gate:
    audience: str
    editorial: str
    commercial: str
    revenue: str
    reasons: tuple[str, ...]

def evaluate(e: dict[str, Any]) -> Gate:
    """Only attested *provider-specific* aggregate evidence can qualify an audience."""
    reasons = []
    provider = e.get('provider_evidence') or {}
    eligibility = provider.get('email_subscription_status') == 'Subscribed'
    count = provider.get('eligible_recipient_count')
    source_ok = provider.get('source') == 'Jetpack Subscribers filtered Email subscription=Subscribed'
    reviewed = provider.get('authorized_read_only_review') is True
    unique = provider.get('deduplicated_by_provider') is True
    corroborated = all((source_ok, eligibility, reviewed, unique, type(count) is int, count > 0 if type(count) is int else False))
    if not corroborated:
        reasons.append('NO_AUTHORITATIVE_EMAIL_ELIGIBLE_AGGREGATE')
    if e.get('received_fieldbook_welcome') is not True:
        reasons.append('FIELD_BOOK_WELCOME_RECEIPT_UNVERIFIED')
    legal = e.get('legal') or {}
    if not (legal.get('actual_jetpack_preview_reviewed') is True and
            legal.get('valid_fv_physical_postal_address_in_received_email') is True and
            legal.get('working_unsubscribe_in_received_email') is True):
        reasons.append('RECEIVED_MIME_AND_CAN_SPAM_UNVERIFIED')
    approved = e.get('founder_final_campaign_approval') is True
    if not approved:
        reasons.append('FOUNDER_FINAL_APPROVAL_MISSING')
    editorial = 'REVIEW_ONLY' if (corroborated and approved and
                 e.get('received_fieldbook_welcome') is True and
                 'RECEIVED_MIME_AND_CAN_SPAM_UNVERIFIED' not in reasons) else 'HOLD_UNSENT'
    merchant = e.get('merchant') or {}
    checked = ['named_fv_affiliate_acceptance','email_channel_permission', 'exact_issued_earning_link',
               'buyer_guide_published_and_verified','seller_terms_checkout_verified',
               'product_claims_qualified','near_link_disclosure_reviewed']
    merchant_ok = all(merchant.get(k) is True for k in checked)
    if not merchant_ok:
        reasons.append('MERCHANT_AND_GUIDE_GATES_UNVERIFIED')
    commercial = 'REVIEW_ONLY' if editorial == 'REVIEW_ONLY' and merchant_ok else 'HOLD_MERCHANT_UNSENT'
    sale = e.get('settled_sale') or {}
    real_sale = (sale.get('source') in ('verified_payhip_settlement','verified_affiliate_partner_report') and
                 sale.get('order_reconciled') is True and sale.get('refunds_fees_reconciled') is True and
                 sale.get('merchant_identity_and_payout_verified') is True)
    denominator = e.get('qualified_human_sessions')
    denominator_ok = type(denominator) is int and denominator > 0 and e.get('qualified_sessions_independently_validated') is True
    if not real_sale or not denominator_ok:
        reasons.append('NET_REVENUE_PER_1000_NOT_COMPUTABLE')
    return Gate('EMAIL_ELIGIBLE_AGGREGATE_REVIEWED' if corroborated else 'UNKNOWN', editorial,
                commercial, 'RECONCILABLE_ONLY' if real_sale and denominator_ok else 'NOT_COMPUTABLE', tuple(reasons))
