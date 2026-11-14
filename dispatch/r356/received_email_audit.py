"""R356: private, offline, non-sending Jetpack received-message evidence classifier.

Never contacts a subscriber, calls the network, or evaluates recipient counts.
No command-line output contains raw mail, addresses, links or tokens.
A synthetic or local EML never authorizes sending or proves a working opt-out.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from email import policy
from email.parser import BytesParser
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

PLACEHOLDERS = ('[[VALID_POSTAL_ADDRESS_REQUIRED]]',
                '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')


def read_parts(msg):
    plain, html = [], []
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            continue
        typ = part.get_content_type()
        if typ in ('text/plain', 'text/html'):
            try:
                content = part.get_content()
            except Exception:
                continue
            (html if typ == 'text/html' else plain).append(str(content))
    return '\n'.join(plain), '\n'.join(html)


def visible(html):
    html = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', html)
    return unescape(re.sub(r'(?s)<[^>]*>', ' ', html))


def inspect_received_eml(data: bytes, *, expected_subject: str = '',
                         publisher_address: str = '') -> dict:
    """Examine evidence shape only. Never returns raw message/address/URL."""
    msg = BytesParser(policy=policy.default).parsebytes(data)
    sub = str(msg.get('Subject', '')).strip()
    from_header = str(msg.get('From', ''))
    plain, html = read_parts(msg)
    text = plain + '\n' + visible(html)
    ltext = text.casefold()
    if 'confirm your subscription' in sub.casefold() or (
        'confirm your subscription' in ltext and 'confirm subscription' in ltext
    ):
        classification = 'CONFIRMATION_ONLY'
    elif ('welcome to the dispatch' in ltext
          and 'fieldbook' in ltext and 'finalvestige.com/' in (plain + html)):
        classification = 'WELCOME_CANDIDATE'
    elif expected_subject and sub == expected_subject:
        classification = 'CAMPAIGN_CANDIDATE'
    else:
        classification = 'UNCLASSIFIED'

    address = publisher_address.strip()
    # Never accept vague publisher identity, provider address, or old placeholders.
    address_usable = (bool(address) and len(address) >= 18
                      and bool(re.search(r'\d', address))
                      and bool(re.search(r'[a-zA-Z]', address))
                      and not any(x in address.lower() for x in (
                          'automattic', 'wenlock street', 'wordpress', 'inspire3')))
    address_visible = bool(address_usable and address.casefold() in ltext)
    list_unsub = str(msg.get('List-Unsubscribe', ''))
    # Structural candidate only; mailto or URL may be dead or unauthenticated.
    header_unsub = bool(re.search(r'<(?:https?://|mailto:)[^<>\s]+>', list_unsub, re.I))
    body_unsub = bool(re.search(r'href\s*=\s*["\'](?:https?://|mailto:)[^"\']+["\'][^>]*>\s*unsubscribe', html, re.I))
    placeholder = any(p in (plain + html) for p in PLACEHOLDERS)
    simulated = 'OFFLINE SIMULATION' in text or 'HOLD · UNSENT' in text
    has_text = bool(plain.strip())
    has_html = bool(html.strip())
    has_issued_recipient = bool(str(msg.get('To','')).strip())
    result = {
        'evidence_sha256': hashlib.sha256(data).hexdigest(),
        'classification': classification,
        'subject_exact': bool(expected_subject and sub == expected_subject),
        'sender_name_match': 'final vestige' in from_header.casefold(),
        'has_to_header': has_issued_recipient,
        'text_part_present': has_text,
        'html_part_present': has_html,
        'publisher_postal_appears': address_visible,
        'unsubscribe_structural_candidate': header_unsub or body_unsub,
        'actual_optout_function': 'NOT_TESTED_BY_THIS_TOOL',
        'actual_delivery_to_target': 'NOT_PROVEN_BY_THIS_TOOL',
        'separate_preheader_supported': 'NOT_PROVEN_BY_THIS_TOOL',
        'is_offline_simulation': simulated,
        'has_release_placeholders': placeholder,
        'release_state': 'HOLD_UNSENT',
    }
    failed = []
    for k in ('subject_exact','sender_name_match','has_to_header',
              'publisher_postal_appears','unsubscribe_structural_candidate'):
        if not result[k]: failed.append(k)
    if classification != 'CAMPAIGN_CANDIDATE':
        failed.append('not_received_campaign_evidence')
    if simulated: failed.append('offline_simulation_cannot_prove_delivery')
    if placeholder: failed.append('unreplaced_compliance_placeholders')
    result['evidence_gaps'] = failed
    return result


def evaluate_private_attestations(attestations: dict) -> dict:
    """Evidence receipts are references, never a delivery or send grant."""
    required = ('provider_optin_confirmation','real_native_preview',
                'welcome_received','publisher_postal_identity',
                'received_optout_function','merchant_email_rights',
                'approved_mind_guide','verified_order_settlement',
                'founder_final_approval')
    valid = {k: (isinstance(attestations.get(k), dict)
                 and attestations[k].get('state') == 'verified'
                 and isinstance(attestations[k].get('proof_ref'), str)
                 and len(attestations[k]['proof_ref']) > 12
                 and 'synthetic' not in attestations[k]['proof_ref'].lower())
             for k in required}
    return {'evidence_keys': valid, 'unmet': [k for k,v in valid.items() if not v],
            'send_authorized_by_tool': False, 'release_state': 'HOLD_UNSENT'}


def main():
    p = argparse.ArgumentParser(description='Offline EML evidence classifier; never sends')
    p.add_argument('eml', type=Path, help='Local EML; never uploaded or persisted')
    p.add_argument('--subject', default='', help='Exact expected subject')
    p.add_argument('--publisher-address', default='', help='Locally approved FV address')
    args=p.parse_args()
    result=inspect_received_eml(args.eml.read_bytes(),
              expected_subject=args.subject,publisher_address=args.publisher_address)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':main()
