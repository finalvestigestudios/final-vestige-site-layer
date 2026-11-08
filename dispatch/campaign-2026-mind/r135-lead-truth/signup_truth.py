"""Offline-only, fail-closed Dispatch/Focus acquisition QA. No network, PII or writes."""
from __future__ import annotations
from urllib.parse import urlparse, parse_qs
from collections import Counter
import re

ALLOWED_SUBMISSION_TOKEN = 'success'
# Jetpack URL feedback is never proof of completed opt-in or delivered welcome.


def audit_projection(html: str, page_id: int) -> dict:
    """Observes the WP connector content projection; never claims visitor DOM."""
    if not isinstance(html, str) or not isinstance(page_id, int):
        raise ValueError('Required CMS projection and page ID')
    # Narrow first subscribe-block extraction; avoid misreading CSS selectors.
    match = re.search(r'<div\s+class\s*=\s*["\'][^"\']*\bwp-block-jetpack-subscriptions\b[^"\']*["\']', html, flags=re.I)
    start = match.start() if match else -1
    fragment = html[start:start+1250] if start >= 0 else ''
    email_inputs = len(re.findall(r'<input\b[^>]*type\s*=\s*["\']?email\b', fragment, re.I))
    forms = len(re.findall(r'<form\b', fragment, re.I))
    anchors = re.findall(r'<a\b[^>]*href\s*=\s*["\']([^"\']+)', fragment, re.I)
    same_page = any(f'p={page_id}' in x.replace('&#038;', '&') for x in anchors)
    if start < 0: state = 'SUBSCRIBE_BLOCK_NOT_PRESENT_IN_PROJECTION'
    elif email_inputs: state = 'INPUT_PRESENT_IN_CMS_PROJECTION_NOT_LIVE_PROOF'
    elif same_page: state = 'LINK_TO_SAME_PAGE_IN_CMS_PROJECTION'
    else: state = 'NO_EMAIL_INPUT_IN_CMS_PROJECTION'
    return {'page_id': page_id, 'state': state, 'subscription_block_in_projection': start >= 0,
            'email_input_count': email_inputs, 'form_count': forms,
            'same_page_subscribe_link': same_page,
            'actual_signed_out_dom_verified': False,
            'eligible_email_recipients_verified': False}


def classify_signup_ui(url: str, native_subscriber_class: bool = False) -> dict:
    """Return UI state ONLY; never infer confirmed_signup from URL or CSS."""
    q = parse_qs(urlparse(url).query, keep_blank_values=True)
    tokens = q.get('subscribe', [])
    # Exact one-token match, never any truthy arbitrary string or multi-token.
    acknowledged = tokens == [ALLOWED_SUBMISSION_TOKEN]
    if acknowledged: status = 'SUBMISSION_ACKNOWLEDGED_CONFIRMATION_UNKNOWN'
    elif native_subscriber_class: status = 'NATIVE_UI_SUBSCRIBER_MARKER_ONLY'
    else: status = 'NO_VERIFIED_SUBMISSION'
    return {'state': status, 'show_public_download_prompt': acknowledged or bool(native_subscriber_class),
            'confirmed_signup': False, 'welcome_delivered': False, 'email_reachable': None}


def count_verified_new_leads(events: list[dict]) -> dict:
    """Only count authoritative first transitions with opaque ids; duplicate-safe.

    IDs are opaque pseudonyms, never addresses or raw emails.
    An individual consent event must originate from independently verified
    newsletter provider evidence, not a URL, download or client click.
    """
    unique = set()
    rejects = Counter()
    for e in events:
        if not isinstance(e, dict):
            rejects['bad_shape'] += 1; continue
        uid = e.get('opaque_subscription_key')
        valid_uid = isinstance(uid, str) and bool(re.fullmatch(r'sub_[a-f0-9]{32,64}', uid))
        if (e.get('event') != 'confirmed_signup' or
                e.get('source') != 'native_jetpack_subscriber_status' or
                e.get('previous_status') not in {'not_confirmed', 'not_subscribed'} or
                e.get('new_status') != 'subscribed' or
                not e.get('consent_provenance_checked') or not valid_uid):
            rejects['unverified_or_unattributable'] += 1
            continue
        if uid in unique:
            rejects['duplicate'] += 1
            continue
        unique.add(uid)
    return {'verified_new_leads': len(unique), 'rejected_by_reason': dict(rejects),
            'email_addresses_processed': 0, 'purchase_claims': 0}


def email_reachable_aggregate(statuses: dict | None) -> dict:
    """Only native status-filter counts qualify, not total/confirmed/followers."""
    if not isinstance(statuses, dict) or statuses.get('source') != 'native_email_subscription_filter':
        return {'eligible_email_recipients': None, 'status': 'UNKNOWN'}
    x = statuses.get('subscribed')
    if type(x) is not int or x < 0:
        return {'eligible_email_recipients': None, 'status': 'UNKNOWN'}
    return {'eligible_email_recipients': x, 'status': 'PROVIDER_REPORTED_NOT_DELIVERY_PROOF'}
