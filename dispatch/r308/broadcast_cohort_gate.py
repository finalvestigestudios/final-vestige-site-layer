"""FV Dispatch R308. Pure OFFLINE broadcast vs signup-relative drip eligibility model.

Nothing here contacts Jetpack, sends mail, schedules messages, or sees PII.
Results mean potential eligibility at publication, never confirmed delivery.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

ISSUE_KINDS = ('editorial', 'editorial', 'commercial', 'editorial', 'commercial', 'editorial')
STATUS = frozenset({'subscribed', 'reader_only', 'pending', 'paused', 'bounced', 'unsubscribed', 'unknown'})

@dataclass(frozen=True)
class SyntheticMember:
    opaque_id: str
    confirmed_at: Optional[datetime]
    email_status: str = 'unknown'
    opted_out_at: Optional[datetime] = None
    consent_for_commercial: bool = False


def _timestamp(value):
    if value is not None and (not isinstance(value, datetime) or value.tzinfo is None):
        raise ValueError('All timestamps must be timezone-aware')


def review_notification(member: SyntheticMember, publication_at: datetime, kind: str,
                        *, email_rights=False, final_send_approval=False, physical_footer=False,
                        working_unsubscribe=False, verified_live_guide=False):
    """Conservative outcome for one HYPOTHETICAL WordPress post.

    `eligible_but_held` is NOT a delivery forecast or permission to send.
    Even all-true evidence cannot create or send a message.
    """
    _timestamp(publication_at)
    _timestamp(member.confirmed_at)
    _timestamp(member.opted_out_at)
    if kind not in {'editorial', 'commercial'} or member.email_status not in STATUS:
        raise ValueError('Unrecognized kind or email status')
    if not member.opaque_id or '@' in member.opaque_id:
        raise ValueError('Opaque synthetic IDs only; do not input email addresses')
    if member.confirmed_at is None:
        return 'unverified_confirmation'
    if publication_at < member.confirmed_at:
        return 'joined_after_publication'
    if member.opted_out_at is not None and publication_at >= member.opted_out_at:
        return 'opted_out'
    if member.email_status != 'subscribed':
        return 'not_verified_email_eligible'
    if kind == 'commercial' and not (member.consent_for_commercial and email_rights and verified_live_guide):
        return 'merchant_or_consent_hold'
    if not (final_send_approval and physical_footer and working_unsubscribe):
        return 'eligible_but_held'
    return 'theoretically_eligible_not_sent'


def hypothetical_broadcast_matrix(members, start_at: datetime, *, spacing_days=7):
    """Six calendar publication events; never a signup-relative drip schedule.

    Deliberately passes NO authorizations: this function cannot show send-ready.
    """
    _timestamp(start_at)
    if not isinstance(spacing_days, int) or spacing_days < 1:
        raise ValueError('Spacing must be positive whole days')
    result = {}
    for member in members:
        if member.opaque_id in result:
            raise ValueError('Duplicate synthetic member ID')
        result[member.opaque_id] = [
            review_notification(member, start_at + timedelta(days=spacing_days*i), kind)
            for i, kind in enumerate(ISSUE_KINDS)
        ]
    return result


def digest_readout(matrix):
    """Diagnostic counts only; cannot infer sends, opens, sales or real subscribers."""
    return {key: sum(1 for outcomes in matrix.values() for outcome in outcomes if outcome == key)
            for key in sorted({status for outcomes in matrix.values() for status in outcomes})}
