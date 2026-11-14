"""Read-only Dispatch evidence gate: synthetic records are NEVER send authority.
Run: PYTHONPATH=dispatch/r356 python -m unittest discover -s dispatch/r356 -p test_*.py -v
No network, recipients, CMS calls, email dispatch, or new instrumentation.
"""
from __future__ import annotations
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation

SHARED = (
    'founder_final_campaign_approval', 'provider_recipient_eligibility',
    'confirmed_consent_dedup', 'welcome_fieldbook_received',
    'native_jetpack_preview', 'received_email_render',
    'fv_postal_address', 'working_unsubscribe', 'verified_subject_from',
)
MERCHANT = (
    'named_fv_partner_acceptance', 'explicit_email_channel_permission',
    'issued_earning_link', 'approved_live_guide', 'current_checkout_terms',
    'refund_terms', 'product_claim_review', 'approved_offer_creative',
)
PII_FIELDS = {'email', 'email_address', 'subscriber_email', 'recipient_email',
              'ip_address', 'full_name', 'phone', 'street_address'}
CANONICAL_SOCIAL = {'youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'}

def _verified(x):
    return (isinstance(x, dict) and x.get('verified') is True
            and isinstance(x.get('source_ref'), str)
            and len(x['source_ref'].strip()) >= 12
            and x.get('source_kind') in ('provider', 'signed_contract', 'received_message', 'owner_attestation', 'merchant'))

def _money(v):
    try:
        n = Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return n if n.is_finite() and n >= 0 else None

def pii_paths(data, prefix=''):
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            p = f'{prefix}.{k}' if prefix else k
            if k.lower() in PII_FIELDS:
                found.append(p)
            found.extend(pii_paths(v, p))
    elif isinstance(data, list):
        for n, v in enumerate(data):
            found.extend(pii_paths(v, f'{prefix}[{n}]'))
    return found

def count_confirmed(events):
    """Count only provider-confirmed opt-in records, never signup attempts."""
    seen = set()
    count = 0
    for x in events:
        if not isinstance(x, dict):
            continue
        if x.get('kind') != 'confirmed_signup' or x.get('provider_status') != 'confirmed':
            continue
        if x.get('provider_proof') is not True or x.get('marketing_consent') is not True:
            continue
        if (x.get('provider_source') != 'jetpack' or not isinstance(x.get('provider_receipt_ref'), str)
                or len(x['provider_receipt_ref']) < 12):
            continue
        key = x.get('opaque_subscriber_id')
        if not isinstance(key, str) or not key.startswith('opaque_') or len(key) < 12:
            continue
        if key not in seen:
            seen.add(key)
            count += 1
    return count

def revenue_report(orders, verified_human_sessions=None, sessions_receipt=None):
    """Require independent settled receipts; clicks and checkout starts are not sales."""
    seen = set()
    gross = Decimal('0')
    fees = Decimal('0')
    refunds = Decimal('0')
    count = 0
    rejected = []
    for i, o in enumerate(orders):
        if not isinstance(o, dict) or o.get('status') != 'settled' or o.get('independent_receipt') is not True:
            rejected.append(i)
            continue
        if (o.get('receipt_source') not in ('merchant_settlement_report', 'payhip_settlement_report')
                or not isinstance(o.get('independent_receipt_ref'), str)
                or len(o['independent_receipt_ref']) < 12):
            rejected.append(i)
            continue
        key = o.get('opaque_order_id')
        if not isinstance(key, str) or not key.startswith('order_') or len(key) < 10 or key in seen:
            rejected.append(i)
            continue
        values = [_money(o.get(k)) for k in ('gross', 'fees', 'refunds')]
        if any(v is None for v in values) or values[1] + values[2] > values[0]:
            rejected.append(i)
            continue
        seen.add(key)
        count += 1
        gross += values[0]
        fees += values[1]
        refunds += values[2]
    net = gross - fees - refunds
    denominator = (isinstance(verified_human_sessions, int) and not isinstance(verified_human_sessions, bool)
                   and verified_human_sessions > 0 and isinstance(sessions_receipt, dict)
                   and sessions_receipt.get('source_kind') == 'first_party_analytics'
                   and isinstance(sessions_receipt.get('source_ref'), str)
                   and len(sessions_receipt['source_ref']) >= 12)
    ratio = (net * 1000 / Decimal(verified_human_sessions)).quantize(Decimal('0.01')) if denominator and count > 0 else None
    return {'confirmed_orders': count, 'gross': str(gross), 'fees': str(fees),
            'refunds': str(refunds), 'net': str(net),
            'net_per_1000_verified_human_sessions': str(ratio) if ratio is not None else None,
            'rejected_records': rejected, 'revenue_verified': count > 0,
            'ratio_computable': denominator and count > 0}

def validate_attribution(event):
    if not isinstance(event, dict):
        return False
    kind = event.get('kind')
    if kind == 'social_visit':
        return (event.get('utm_source') in CANONICAL_SOCIAL
                and event.get('utm_medium') == 'organic_social'
                and isinstance(event.get('utm_content'), str)
                and event['utm_content'].startswith('asset_')
                and event.get('published_asset_proof') is True)
    if kind == 'dispatch_guide_click':
        return (event.get('utm_source') == 'dispatch'
                and event.get('utm_medium') == 'email'
                and event.get('issue') in (3, 5)
                and event.get('actually_sent') is True
                and event.get('recipient_permission_verified') is True)
    return False

def evaluate(proof, manifest, confirmed_events=None, orders=None, qualified_sessions=None, qualified_sessions_proof=None):
    """A source-format diagnostic, NEVER an email-release approval token."""
    confirmed_events = confirmed_events or []
    orders = orders or []
    missing = [k for k in SHARED if not _verified(proof.get('shared', {}).get(k))]
    merchants = {}
    for issue in ('03', '05'):
        source = proof.get('merchant', {}).get(issue, {})
        merchants[issue] = [k for k in MERCHANT if not _verified(source.get(k))]
    issues = manifest.get('issues', [])
    source_valid = (len(issues) == 6 and manifest.get('status') == 'DRAFT_UNSENT_NO_SCHEDULING'
                    and sum(x.get('kind') == 'editorial' for x in issues) == 4
                    and sum(x.get('kind') == 'commercial-review-pending' for x in issues) == 2
                    and all(x.get('publish_state') == 'hold' and x.get('merchant_affiliate_url') is None for x in issues))
    counts = proof.get('provider_aggregate', {})
    aggregate_nonadditive = (counts.get('total') == counts.get('confirmed') and (counts.get('unconfirmed') or 0) > 0)
    private_data_paths = pii_paths(proof) + pii_paths(confirmed_events) + pii_paths(orders)
    money = revenue_report(orders, qualified_sessions, qualified_sessions_proof)
    return {'campaign_source_valid': source_valid, 'all_issues': 'HOLD_UNSENT',
            'commercial_03': 'HOLD_MERCHANT', 'commercial_05': 'HOLD_MERCHANT',
            'shared_missing': missing, 'merchant_missing': merchants,
            'provider_totals_overlap': aggregate_nonadditive,
            'eligible_recipients': None, 'verified_confirmed_signups_in_submitted_sample': count_confirmed(confirmed_events),
            'pii_field_violations': private_data_paths, 'money': money,
            'cannot_infer_actual_list_or_welcome_delivery': True,
            'cannot_authorize_send': True,
            'note': 'Offline source assertions cannot validate evidence receipts or authorize a send.'}

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    doc = json.loads((root / 'PROOFS_ALL_FALSE.json').read_text(encoding='utf8'))
    manifest_path = root.parent / 'campaign-2026-mind' / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    print(json.dumps(evaluate(doc, manifest), indent=2))
