"""R145: fail-closed, offline editorial and merchant-email contract; NEVER sends email.

Input is a locally reviewed no-PII attestation JSON object. It is *not* a connected
merchant account, WordPress native status feed, or proof of actual paid sales.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

OFFERS = {
    '03': ('Zen12 Premium', '[[APPROVED_LIVE_ZEN12_PREMIUM_FIRST_PARTY_GUIDE_URL_REQUIRED]]'),
    '05': ('Hypnosis Live — Total Focus', '[[APPROVED_LIVE_TOTAL_FOCUS_FIRST_PARTY_GUIDE_URL_REQUIRED]]'),
}
REQUIRED_APPROVALS = (
    'named_final_vestige_partner_accepted',
    'specific_offer_approved',
    'promotional_email_channel_permitted',
    'exact_earning_link_authorized',
    'first_party_guide_live_and_reviewed',
    'current_checkout_refund_verified',
    'native_opt_in_email_eligible_verified',
    'native_jetpack_full_preview_verified',
    'valid_final_vestige_postal_address_verified',
    'received_unsubscribe_function_verified',
    'founder_final_campaign_send_approved',
)
BLOCKS = ('[[', ']]', 'HOLD_UNSENT', 'NOT AN APPROVED REPLACEMENT')
UNSUPPORTED_PROMISES = (
    r'(?i)\bguaranteed?\s+(?:results?|focus|concentration|relaxation)',
    r'(?i)\bclinically proven\b',
    r'(?i)\bwe (?:tested|used) (?:this|the) recording\b',
)

def readiness(offer_id: str, copy: str, attest: dict) -> dict:
    """Fail closed on absent/false/ill-typed evidence. Never infer authorization."""
    if offer_id not in OFFERS: raise ValueError('Unknown specific product slot')
    if not isinstance(attest, dict): raise ValueError('Attestations must be an object')
    if not isinstance(copy, str): raise ValueError('Copy must be a string')
    name, sentinel = OFFERS[offer_id]
    blockers = []
    if name not in copy: blockers.append('specific_product_identity_missing')
    if sentinel not in copy: blockers.append('expected_pending_guide_sentinel_missing')
    if any(re.search(p, copy) for p in UNSUPPORTED_PROMISES): blockers.append('unsupported_claim_language')
    if copy.count(sentinel) != 2: blockers.append('unexpected_number_of_primary_guide_mentions')
    if 'Commercial disclosure' not in copy or 'may earn a commission' not in copy:
        blockers.append('disclosure_missing')
    elif copy.index('Commercial disclosure') - copy.rfind(sentinel) > 400:
        blockers.append('disclosure_not_close_to_offer')
    for k in REQUIRED_APPROVALS:
        v = attest.get(k)
        if type(v) is not bool or v is not True: blockers.append('unverified:'+k)
    # A paper-only candidate is NEVER sendable, even with a fictitious all-true object.
    if any(token in copy for token in BLOCKS): blockers.append('source_only_hard_stop')
    if '[[FINAL_VESTIGE_VERIFIED_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]' in copy:
        blockers.append('postal_address_placeholder')
    if '[[ACTUAL_JETPACK_RENDERED_WORKING_UNSUBSCRIBE_REQUIRED]]' in copy:
        blockers.append('unsubscribe_placeholder')
    if re.search(r'(?i)(?:utm_[a-z]+|aff(?:iliate)?_id|ref=\d+)', copy):
        blockers.append('unapproved_tracking_or_merchant_identifier')
    return {'offer': offer_id, 'product': name,
            'release': 'HOLD_UNSENT', 'merchant': 'HOLD_MERCHANT',
            'blockers': sorted(set(blockers)), 'test_only': True}

def audit(directory: Path, attest: dict) -> dict:
    mapping={'03': '03-ZEN12-PREMIUM-ALTERNATE-UNSENT.md',
             '05': '05-TOTAL-FOCUS-ALTERNATE-UNSENT.md'}
    return {'issues': {i: readiness(i,(directory/f).read_text(encoding='utf-8'),attest)
                       for i,f in mapping.items()},
            'email_sends': 'NOT_PERFORMED',
            'partner_eligibility': 'UNVERIFIED',
            'verified_paid_sales': None, 'realized_net_revenue_per_1000': None}

if __name__=='__main__':
    print(json.dumps(audit(Path(__file__).parent, {}), indent=2))
