"""Offline, PII-free Dispatch release and funnel evidence gate. Never connects or sends.

All verification fields require an independently documented attestation reference;
booleans alone are insufficient. Do not use this as an affiliate authorization engine.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

PROOF = re.compile(r'^(?:github-issue|github-pr|wp-admin-review|merchant-account|received-email-review|settlement-ledger):[A-Za-z0-9_./#@-]{6,}$')
REQUIRED = {
    'common': ('founder_final_approval', 'provider_email_eligible_count', 'double_opt_in_evidence',
               'welcome_received_evidence', 'native_jetpack_mime_review', 'publisher_postal_address',
               'unsubscribe_visible_and_works', 'accurate_sender_and_subject'),
    'commercial': ('named_publisher_accepted', 'email_promotion_permitted', 'issued_affiliate_link',
                   'offer_guide_published_and_qa', 'exact_seller_terms_checked',
                   'approved_near_link_disclosure'),
}
ISSUES = {"01":"editorial", "02":"editorial", "03":"commercial", "04":"editorial", "05":"commercial", "06":"editorial"}


def proof_ok(value):
    return isinstance(value, str) and bool(PROOF.fullmatch(value)) and 'placeholder' not in value.lower()


def evaluate(attestations, issue):
    if issue not in ISSUES:
        raise ValueError('invalid issue')
    requirements = REQUIRED['common'] + (REQUIRED['commercial'] if ISSUES[issue] == 'commercial' else ())
    missing = [key for key in requirements if not proof_ok(attestations.get(key))]
    # A referenced attestation is only a review CANDIDATE. We cannot validate its substance offline.
    return {'issue': issue, 'kind': ISSUES[issue], 'missing': missing,
            'status': 'HOLD' if missing else 'HUMAN_REVIEW_CANDIDATE_ONLY',
            'send_authorized': False}


def confirmed_signup(event):
    """Accept only provider-originated status transition, deduplicated by opaque reference."""
    if not isinstance(event, dict):
        return False
    return (event.get('event') == 'confirmed_signup' and
            event.get('source') == 'jetpack_authoritative' and
            event.get('state_before') == 'unconfirmed' and
            event.get('state_after') == 'subscribed' and
            proof_ok(event.get('evidence_ref')) and
            isinstance(event.get('opaque_transition_id'), str) and
            bool(re.fullmatch('[a-zA-Z0-9_-]{12,128}', event.get('opaque_transition_id'))))


def dedup_confirmed(events):
    seen, valid = set(), []
    for event in events:
        if confirmed_signup(event) and event['opaque_transition_id'] not in seen:
            seen.add(event['opaque_transition_id'])
            valid.append({'opaque_transition_id': event['opaque_transition_id'], 'evidence_ref': event['evidence_ref']})
    return valid


def paid_conversion(record):
    """Only offline review gate; independently reported paid settlement, refunds & fees required."""
    if not isinstance(record, dict):
        return False
    amount_fields = ('gross_cents', 'refund_cents', 'fee_cents')
    if any(type(record.get(k)) is not int or record[k] < 0 for k in amount_fields):
        return False
    if record['refund_cents'] > record['gross_cents']:
        return False
    return (record.get('state') == 'settled' and record.get('source') in ('merchant-settlement', 'payhip-settlement')
            and proof_ok(record.get('settlement_evidence_ref')) and
            isinstance(record.get('opaque_order_id'), str) and
            bool(re.fullmatch('[a-zA-Z0-9_-]{12,128}', record['opaque_order_id'])))


def safe_revenue_report(records, qualified_sessions, denominator_ref):
    if type(qualified_sessions) is not int or qualified_sessions <= 0 or not proof_ok(denominator_ref):
        return {'status': 'NOT_COMPUTABLE', 'reason': 'unverified qualified-human denominator'}
    if not records:
        return {'status': 'NOT_COMPUTABLE', 'reason': 'no independently reconciled zero-sales or settlement evidence'}
    unique = {}
    for r in records:
        if not paid_conversion(r):
            return {'status': 'NOT_COMPUTABLE', 'reason': 'unverified settlement or missing fee/refund evidence'}
        if r['opaque_order_id'] in unique:
            return {'status': 'NOT_COMPUTABLE', 'reason': 'duplicate order reference'}
        unique[r['opaque_order_id']] = r
    net = sum(x['gross_cents'] - x['refund_cents'] - x['fee_cents'] for x in unique.values())
    return {'status': 'REVIEW_ONLY', 'settled_orders': len(unique), 'net_cents': net,
            'net_cents_per_1000_qualified_human_sessions': round(net*1000/qualified_sessions, 2),
            'warning': 'Tiny samples unstable; verify cohort attribution and refund windows before publication.'}


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: python offer_consent_gate.py attestation.json issue_number')
    data = json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    # Never print raw input, even if a future caller accidentally includes PII.
    print(json.dumps(evaluate(data, sys.argv[2]), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
