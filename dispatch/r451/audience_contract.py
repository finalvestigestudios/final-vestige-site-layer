"""Offline, PII-free reconciliation and release controls for FV Dispatch.

No network calls, writes, sends, exports, or subscriber identifiers.
Provider counts are evidence about *different surfaces*, not interchangeable events.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

CAMPAIGN_KIND = ('editorial', 'editorial', 'commercial', 'editorial', 'commercial', 'editorial')


class AuditError(ValueError):
    """An observed snapshot or purported sales proof is unusable."""


def _nonnegative(value, label):
    if type(value) is not int or value < 0:
        raise AuditError(f'{label}: expected nonnegative integer')
    return value


def reconcile(newsletter: dict, subscribers: dict, followers: dict) -> dict:
    """Compare authenticated source surfaces without inventing reader identities.

    Subscriber list `all_total` excludes separate `unconfirmed_total`.
    Followers stats is a distinct feed and may disagree with subscriber list.
    """
    for key in ('total', 'confirmed', 'unconfirmed'):
        _nonnegative(newsletter.get(key), f'newsletter.{key}')
    for key in ('all_total', 'email_eligible', 'unconfirmed_total'):
        _nonnegative(subscribers.get(key), f'subscribers.{key}')
    for key in ('total', 'email', 'wpcom'):
        _nonnegative(followers.get(key), f'followers.{key}')
    if followers.get('partial') is not False:
        raise AuditError('followers feed partial or unknown')
    if newsletter['total'] != newsletter['confirmed']:
        raise AuditError('newsletter total and confirmed diverge: investigate, do not aggregate')
    if newsletter['total'] != subscribers['all_total']:
        raise AuditError('subscriber total differs from newsletter total')
    if newsletter['unconfirmed'] != subscribers['unconfirmed_total']:
        raise AuditError('unconfirmed detail differs from newsletter count')
    if subscribers['email_eligible'] > subscribers['all_total']:
        raise AuditError('email eligible exceeds subscriber all total')
    if followers['total'] < followers['email'] or followers['total'] < followers['wpcom']:
        raise AuditError('follower total lower than reported component')
    return {
        'confirmed_email_eligible_records': subscribers['email_eligible'],
        'unconfirmed_records_excluded': subscribers['unconfirmed_total'],
        'follower_feed_email': followers['email'],
        'follower_feed_reader': followers['wpcom'],
        'source_count_disagreement': followers['email'] != subscribers['email_eligible'],
        'proven_new_external_leads': None,
        'proven_welcome_receipts': None,
        'email_deliveries': None,
        'interpretation': 'Do not add unconfirmed to newsletter total or treat follower stats as delivery evidence.',
    }


def confirmed_signup_transition(before: dict | None, after: dict, evidence: dict) -> bool:
    """An existing account, Reader-only follow, or click cannot be counted as a new lead."""
    if after.get('status') != 'Subscribed' or after.get('email_subscriber') is not True:
        return False
    if not evidence.get('provider_confirmation_record') or not evidence.get('timestamped_first_confirmation'):
        return False
    if before is None:
        return evidence.get('newly_created_provider_record') is True
    return before.get('status') == 'Not confirmed' and before.get('email_subscriber') is True


def release_decision(issues: list[dict], proof: dict) -> dict:
    """Founder selection is not final send approval; every edition is initially held."""
    if len(issues) != 6 or tuple(i.get('type') for i in issues) != CAMPAIGN_KIND:
        raise AuditError('campaign must preserve four editorial / two commercial positions')
    global_gates = (
        'founder_final_send_approval', 'native_jetpack_preview_witness',
        'verified_publisher_postal', 'rendered_functional_unsubscribe',
        'consent_and_delivery_evidence',
    )
    comm_gates = (
        'named_partner_acceptance', 'product_specific_email_permission',
        'issued_earning_url', 'vetted_published_guide',
        'current_checkout_and_refund_witness',
    )
    rows = []
    for num, issue in enumerate(issues, 1):
        missing = [k for k in global_gates if proof.get(k) is not True]
        if issue['type'] == 'commercial':
            missing.extend(k for k in comm_gates if proof.get(k) is not True)
        if issue.get('founder_selected') is not True:
            missing.append('founder_editorial_selection')
        rows.append({'issue': num, 'type': issue['type'], 'release': 'HOLD_UNSENT' if missing else 'REVIEW_ELIGIBLE_NOT_SENT', 'missing': missing})
    return {'issues': rows, 'all_held': all(r['release'] == 'HOLD_UNSENT' for r in rows)}


def revenue_per_1000(qualified_sessions, settlement_rows, *, denominator_verified=False, ledger_verified=False):
    """Return None for absent proof, NEVER infer revenue from click/signup counts.

    Rows must be independently reported and have settled status, fees and refunds.
    A 0 is reportable only with both an audited denominator and complete settlement ledger.
    """
    if qualified_sessions is None or settlement_rows is None or not (denominator_verified is True and ledger_verified is True):
        return None
    _nonnegative(qualified_sessions, 'qualified_sessions')
    if qualified_sessions == 0:
        return None
    if not isinstance(settlement_rows, list):
        raise AuditError('settlement_rows must be a complete ledger list')
    net = Decimal('0')
    for row in settlement_rows:
        if row.get('independently_reported') is not True or row.get('status') != 'settled':
            raise AuditError('order lacks independent settled proof')
        try:
            gross = Decimal(str(row['gross']))
            fees = Decimal(str(row['fees']))
            refunds = Decimal(str(row['refunds']))
        except (KeyError, InvalidOperation, TypeError):
            raise AuditError('missing or nonnumeric net revenue components') from None
        if any(x < 0 or not x.is_finite() for x in (gross, fees, refunds)):
            raise AuditError('negative or nonfinite amounts')
        net += gross - fees - refunds
    return (net * Decimal(1000) / Decimal(qualified_sessions)).quantize(Decimal('0.01'))
