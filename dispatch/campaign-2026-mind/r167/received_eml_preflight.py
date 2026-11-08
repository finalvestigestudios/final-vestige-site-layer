#!/usr/bin/env python3
"""Offline, privacy-preserving evidence lint for an *authorized* received Jetpack .eml.

NEVER sends mail, reaches the network, alters subscriber records or authorizes release.
Always fail-closed on missing or synthetic evidence. Python standard library only.
"""
import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

MAX_BYTES = 2_000_000
HARD_HOLD = 'HOLD_UNSENT'
PLACEHOLDER = re.compile(r'\[\[[^]\r\n]{3,120}\]\]|\[(?:INSERT|TBD|PENDING|UNSUBSCRIBE|POSTAL|MERCHANT|LINK)[^\]]*\]|\{\{[^}]+\}\}', re.I)

class LinkText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.visible = []
        self.current = None
        self.suppressed = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.suppressed += 1
        if tag == 'a':
            self.current = {'href': a.get('href', ''), 'text': ''}
    def handle_data(self, data):
        if not self.suppressed:
            self.visible.append(data)
            if self.current is not None:
                self.current['text'] += data
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.suppressed:
            self.suppressed -= 1
        if tag == 'a' and self.current is not None:
            self.links.append(self.current)
            self.current = None

def _body_parts(message):
    plain, html = [], []
    for part in message.walk():
        if part.get_content_maintype() == 'multipart' or part.get_content_disposition() == 'attachment':
            continue
        try:
            value = part.get_content()
        except (UnicodeError, LookupError, ValueError):
            continue
        if not isinstance(value, str):
            continue
        if part.get_content_type() == 'text/plain':
            plain.append(value)
        elif part.get_content_type() == 'text/html':
            html.append(value)
    return '\n'.join(plain), '\n'.join(html)

def inspect(raw, kind='editorial', attest=None):
    """Return redacted aggregate checks ONLY, never echo email addresses or content."""
    if kind not in ('editorial', 'commercial'):
        raise ValueError('kind must be editorial or commercial')
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('input must be at most 2MB of bytes')
    a = attest if isinstance(attest, dict) else {}
    m = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html = _body_parts(m)
    parser = LinkText()
    parser.feed(html)
    visible = plain + '\n' + ' '.join(parser.visible)
    links = parser.links
    text_unsub = bool(re.search(r'\bunsubscribe\b|\bopt\s*out\b', visible, re.I))
    linked_unsub = any(re.search(r'\bunsubscribe\b|\bopt\s*out\b', l['text'], re.I) and
                       urlparse(l['href']).scheme == 'https' for l in links)
    listed_unsub = bool(m.get('List-Unsubscribe'))
    oneclick = 'List-Unsubscribe=One-Click' in str(m.get('List-Unsubscribe-Post', ''))
    affiliate_hrefs = [l for l in links if re.search(r'awin1\.com|clickbank|inspire3\.com/aff|zen12\.com/checkout', l['href'], re.I)]
    native_firstparty = any(urlparse(l['href']).hostname in ('finalvestige.com', 'www.finalvestige.com') for l in links)
    commercial_disclosure = bool(re.search(r'\b(may earn|earn a commission|affiliate link|paid partnership)\b', visible, re.I))
    from_label = str(m.get('From', ''))
    checks = {
        'has_from_header': bool(m.get('From')),
        'sender_identifies_studio': 'Final Vestige' in from_label,
        'has_subject': bool(str(m.get('Subject', '')).strip()),
        'has_mime_body': bool(visible.strip()),
        'has_plain_text_part': bool(plain.strip()),
        'has_html_part': bool(html.strip()),
        'first_party_cta_present': native_firstparty,
        'has_no_placeholders': not bool(PLACEHOLDER.search(plain + '\n' + html)),
        'unsubscribe_visible': text_unsub,
        'unsubscribe_clickable_in_html': linked_unsub,
        'list_unsubscribe_header_present': listed_unsub,
        'one_click_header_present_optional': oneclick,
        'commercial_disclosure_visible': commercial_disclosure,
        'no_activated_affiliate_href': not bool(affiliate_hrefs),
        'evidence_is_genuine_received_mail_attested': a.get('genuine_received_mail') is True and a.get('synthetic_fixture') is False,
        'postal_line_observed_attested': a.get('fv_postal_line_observed') is True,
        'postal_address_valid_and_fv_owned_attested': a.get('fv_postal_address_verified') is True,
        'unsubscribe_completed_in_authorized_browser_attested': a.get('unsubscribe_worked') is True,
        'provider_email_eligibility_attested': a.get('provider_email_eligible') is True,
        'welcome_fieldbook_received_attested': a.get('welcome_received') is True,
        'founder_campaign_release_approval_attested': a.get('founder_final_approval') is True,
        'named_merchant_email_permission_attested': a.get('merchant_email_permission') is True,
        'named_merchant_earning_link_attested': a.get('merchant_earning_link') is True,
    }
    required = ['has_from_header','sender_identifies_studio','has_subject','has_mime_body','has_plain_text_part',
                'has_html_part','first_party_cta_present','has_no_placeholders','unsubscribe_visible',
                'unsubscribe_clickable_in_html','evidence_is_genuine_received_mail_attested',
                'postal_line_observed_attested','postal_address_valid_and_fv_owned_attested',
                'unsubscribe_completed_in_authorized_browser_attested','provider_email_eligibility_attested',
                'welcome_fieldbook_received_attested','founder_campaign_release_approval_attested']
    if kind == 'commercial':
        required += ['commercial_disclosure_visible','named_merchant_email_permission_attested',
                     'named_merchant_earning_link_attested','no_activated_affiliate_href']
    failed = [key for key in required if not checks[key]]
    return {
        'type': 'dispatch_received_email_evidence_check', 'version': 1,
        'message_class': kind, 'release_decision': HARD_HOLD,
        'review_readiness': 'NEEDS_EVIDENCE' if failed else 'STRUCTURE_AND_ATTESTATIONS_REVIEWED_NOT_APPROVED',
        'failed_gates': failed,
        'checks': checks,
        'notes': [
            'This file does not validate actual legal sufficiency, subscription permission or real opt-out execution.',
            'Visible unsubscribe and List-Unsubscribe headers do not establish that opt-out works.',
            'Jetpack static Preview email is not a received .eml; any local fixture is synthetic.',
            'No email addresses, names, subject lines, message bodies or header values are emitted.',
            'No output from this tool authorizes sending or publishing.'
        ]
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--eml', type=Path, required=True, help='Authorized local .eml only; never a live mailbox')
    ap.add_argument('--kind', choices=['editorial','commercial'], required=True)
    ap.add_argument('--attestations', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    a = json.loads(args.attestations.read_text(encoding='utf-8'))
    report = inspect(args.eml.read_bytes(),args.kind,a)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('HOLD_UNSENT; aggregate redacted report written locally; no message sent')

if __name__ == '__main__':
    main()
