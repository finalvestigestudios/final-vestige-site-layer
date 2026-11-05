"""READ-ONLY Dispatch release truth checker. Never contacts WordPress or recipients.

Input must be a privacy-scrubbed, authenticated WP get_settings/status snapshot
and canonical master manifest. Generates only conservative, unsendable assessments.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

SENTINELS = ('[[VALID_POSTAL_ADDRESS_REQUIRED]]', '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')
UNVERIFIED = 'UNKNOWN_OR_UNVERIFIED'


def assess(snapshot: dict, manifest: dict, manuscripts: dict[int, str]) -> dict:
    """An audit result, NOT a sending authorization or verified consent."""
    s = snapshot.get('settings', {})
    status = snapshot.get('status', {})
    subscribers = status.get('subscribers', {})
    issues = manifest.get('issues', [])
    mode = s.get('email_content_format')
    if mode not in ('excerpt', 'full'):
        mode = UNVERIFIED
    count = {'total': subscribers.get('total'), 'confirmed': subscribers.get('confirmed'),
             'unconfirmed': subscribers.get('unconfirmed'), 'imported_last_24h': subscribers.get('imported_last_24h')}
    previous = snapshot.get('previous_reported', {})
    drift = {}
    for a, b in [('email_content_format', 'email_content_format'), ('from_name', 'from_name'),
                 ('reply_to', 'reply_to')]:
        old, new = previous.get(a), s.get(b)
        if old is not None and old != new:
            drift[a] = {'previously_reported': old, 'current_authenticated_read': new,
                        'change_actor_and_time': UNVERIFIED}
    results = []
    for item in issues:
        n = item['number']
        body = manuscripts.get(n, '')
        commercial = item['kind'] == 'commercial-review-pending'
        findings = []
        if not body: findings.append('NO_CANONICAL_MANUSCRIPT')
        if any(tag in body for tag in SENTINELS): findings.append('LEGAL_FOOTER_PLACEHOLDERS_IN_SOURCE')
        if commercial:
            if item.get('merchant_affiliate_url') is not None: findings.append('ACTIVE_LINK_REQUIRES_REVIEW')
            if '[[APPROVED_' in body: findings.append('NOT_LIVE_GUIDE_PLACEHOLDER')
            if 'Commercial disclosure:' not in body: findings.append('NO_NEAR_OFFER_DISCLOSURE')
            findings.append('NAMED_PARTNER_EMAIL_PERMISSION_NOT_VERIFIED')
        if n == 1: findings.append('CTA_REPEATS_ISSUE_02_DESPITE_DIFFERENT_TOPIC')
        if n == 4: findings.append('FOURTEEN_SECOND_SUBJECT_REQUIRES_SOURCE_REVIEW')
        if n == 6: findings.append('RETURN_SUBSCRIBER_CTA_TO_SIGNUP_PAGE')
        if mode == 'full':
            findings.append('FULL_POST_MAY_DELIVER_ALL_UNREDACTED_CONTENT_AND_LINKS')
        elif mode == 'excerpt':
            findings.append('EXCERPT_MAY_NOT_INCLUDE_INLINE_CTA_OR_DISCLOSURE')
        else: findings.append('UNKNOWN_DELIVERY_MODE')
        findings += ['NO_AUTHORIZED_NATIVE_EMAIL_RENDER', 'NO_VALIDATED_FV_POSTAL_ADDRESS',
                     'NO_RECEIVED_UNSUBSCRIBE_PROOF', 'NO_FOUNDER_SEND_APPROVAL']
        results.append({'issue': n, 'type': 'commercial' if commercial else 'editorial',
                        'status': 'HOLD_MERCHANT_AND_SHARED' if commercial else 'HOLD_SHARED',
                        'findings': findings, 'native_inbox_preview_verified': False})
    return {'snapshot_as_of': snapshot.get('as_of'), 'delivery_mode_authenticated': mode,
            'previous_reported_drift': drift, 'newsletter_enabled': s.get('subscriptions'),
            'auto_post_email_enabled': s.get('email_new_posts_by_default'),
            'reported_nonadditive_counters': count, 'email_eligible_unique_recipients': None,
            'welcome_received': None, 'confirmed_signup_events': None,
            'attributed_paid_orders': None, 'net_revenue_per_1000_qualified_sessions': None,
            'site_can_send_is_not_campaign_authorization': True,
            'all_send_permissions': 'HOLD_UNSENT', 'issues': results}


def safe_attribution(qualified_sessions, settled_orders, refunds, fees):
    """Return revenue KPI ONLY for nonnegative independently verified inputs.

    'settled_orders' is a list of amounts for verified settled transactions, not clicks.
    Fees/refunds must be known numeric sums; use None for missing evidence.
    """
    args = (qualified_sessions, settled_orders, refunds, fees)
    if any(x is None for x in args) or not isinstance(settled_orders, list): return None
    if not isinstance(qualified_sessions, int) or isinstance(qualified_sessions, bool) or qualified_sessions <= 0: return None
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) or x < 0 for x in [*settled_orders, refunds, fees]): return None
    return round((sum(settled_orders) - refunds - fees) * 1000 / qualified_sessions, 2)


def run(snapshot_file: str, manifest_file: str, issue_dir: str):
    snapshot = json.loads(Path(snapshot_file).read_text(encoding='utf-8'))
    manifest = json.loads(Path(manifest_file).read_text(encoding='utf-8'))
    issues = {}
    for p in Path(issue_dir).glob('*.md'):
        m = re.match(r'(\d\d)-', p.name)
        if m: issues[int(m.group(1))] = p.read_text(encoding='utf-8')
    return assess(snapshot, manifest, issues)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('snapshot', 'manifest', 'issues'): parser.add_argument(name)
    args = parser.parse_args()
    print(json.dumps(run(args.snapshot, args.manifest, args.issues), indent=2))
