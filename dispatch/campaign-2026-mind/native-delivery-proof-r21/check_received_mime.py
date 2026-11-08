#!/usr/bin/env python3
"""Read-only, offline, privacy-safe reviewer of an ALREADY AUTHORISED received Jetpack .eml.

This does not request/send mail, visit links, import contacts, or certify legal compliance.
No raw headers, identities, unsubscribe tokens, postal addresses, or email bodies
are emitted to stdout or JSON. Never commit a real .eml or private postal file.
"""
from __future__ import annotations
import argparse
import email
from email import policy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOLD = 'HOLD_UNSENT_UNVERIFIED'
LIMIT_BYTES = 2_000_000


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
        self.links = []
        self._active_anchor = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ('script', 'style', 'head', 'template', 'noscript'):
            self.hidden += 1
        if tag == 'a' and not self.hidden:
            self._active_anchor = {'href': d.get('href', ''), 'text': []}
        if tag in ('br', 'p', 'div', 'li', 'td', 'tr'):
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head', 'template', 'noscript') and self.hidden:
            self.hidden -= 1
        if tag == 'a' and self._active_anchor is not None:
            self.links.append((self._active_anchor['href'], ''.join(self._active_anchor['text'])))
            self._active_anchor = None
        if tag in ('p', 'div', 'li', 'td', 'tr'):
            self.parts.append(' ')

    def handle_data(self, data):
        if self.hidden:
            return
        self.parts.append(data)
        if self._active_anchor is not None:
            self._active_anchor['text'].append(data)

    def normalized(self):
        return ' '.join(''.join(self.parts).split())


def is_optout_href(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return (parsed.scheme == 'https' and bool(parsed.netloc)) or (parsed.scheme == 'mailto' and bool(parsed.path))


def parse_received(raw, issue, private_postal=None):
    # Reject huge/unparseable payloads without showing potentially private content.
    if not isinstance(raw, bytes) or not 0 < len(raw) <= LIMIT_BYTES:
        return {'status': HOLD, 'error_code': 'INVALID_OR_OVERSIZED_SAMPLE'}
    try:
        msg = email.parser.BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        return {'status': HOLD, 'error_code': 'UNREADABLE_MIME'}
    if not msg.get('Subject') or not msg.get('From') or not msg.get('Date'):
        return {'status': HOLD, 'error_code': 'MISSING_ESSENTIAL_HEADERS'}

    plain, html, html_links, parts = [], [], [], 0
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == 'attachment':
            continue
        kind = part.get_content_type()
        if kind not in ('text/plain', 'text/html'):
            continue
        parts += 1
        try:
            value = part.get_content()
        except Exception:
            continue
        if kind == 'text/plain':
            plain.append(value)
        else:
            parser = VisibleText()
            try:
                parser.feed(value)
                html.append(parser.normalized())
                html_links += parser.links
            except Exception:
                continue

    plaintext = '\n'.join(plain)
    htmltext = ' '.join(html)
    visible = ' '.join([plaintext, htmltext])
    visible_normalized = ' '.join(visible.split())
    low = visible_normalized.casefold()
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        entry = next(i for i in manifest['issues'] if i['number'] == issue)
    except Exception:
        return {'status': HOLD, 'error_code': 'MISSING_LOCAL_CAMPAIGN_MANIFEST'}

    subject = str(msg.get('Subject', '')).strip()
    all_urls = [href for href, _ in html_links]
    header_list = [str(x) for x in msg.get_all('List-Unsubscribe', [])]
    header_one_click = [str(x) for x in msg.get_all('List-Unsubscribe-Post', [])]
    # Header presence is a useful signal, not a legal substitute for an actual working opt-out.
    list_unsub_syntax = any(re.search(r'<(?:https://[^>]+|mailto:[^>]+)>', x, re.I) for x in header_list)
    one_click_claim = any('List-Unsubscribe=One-Click' in x for x in header_one_click)
    # The anchor text or nearby visible text must say 'unsubscribe' to qualify as a visible link.
    clickable_unsub = any('unsubscribe' in text.casefold() and is_optout_href(href) for href, text in html_links)
    plaintext_unsub = bool(re.search(r'unsubscribe.{0,180}(?:https://\S+|mailto:\S+)', plaintext, re.I | re.S))
    visible_optout = clickable_unsub or plaintext_unsub
    placeholder_present = bool(re.search(r'\[\[(?:VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED|APPROVED_[A-Z0-9_]+)\]\]|\[UNVERIFIED:', visible, re.I))
    commercial = entry['kind'] == 'commercial-review-pending'
    product_disclosure = ('may earn a commission' in low) if commercial else None
    has_exact_postal = None
    if private_postal is not None:
        address = ' '.join(str(private_postal).split()).casefold()
        has_exact_postal = bool(len(address) > 12 and address in low)
    # No inference that the address is legally valid is made even when matching.
    checks = {
        'matches_planned_subject': subject == entry['subject'],
        'has_plaintext_part': bool(plain),
        'has_html_part': bool(html),
        'contains_visible_optout_in_received_content': visible_optout,
        'has_list_unsubscribe_header_syntax': list_unsub_syntax,
        'has_one_click_header_claim': one_click_claim,
        'contains_unapproved_placeholder': placeholder_present,
        'contains_commercial_disclosure': product_disclosure,
        'postal_text_matches_private_input': has_exact_postal,
        'contains_meaningful_body': len(visible_normalized) >= 300,
        'contains_expected_site_domain': 'finalvestige.com' in low or any(urlparse(u).hostname == 'finalvestige.com' for u in all_urls),
    }
    codes = []
    if not checks['matches_planned_subject']:
        codes.append('SUBJECT_NOT_EXACT')
    if not checks['has_plaintext_part']:
        codes.append('PLAIN_TEXT_MISSING')
    if not checks['contains_visible_optout_in_received_content']:
        codes.append('VISIBLE_OPTOUT_NOT_ESTABLISHED')
    if checks['contains_unapproved_placeholder']:
        codes.append('UNSENT_TOKEN_LEAK')
    if commercial and not checks['contains_commercial_disclosure']:
        codes.append('COMMERCIAL_DISCLOSURE_MISSING')
    if private_postal is None:
        codes.append('POSTAL_PRIVATE_ATTESTATION_ABSENT')
    elif not checks['postal_text_matches_private_input']:
        codes.append('POSTAL_NOT_VISIBLE_IN_RECEIVED_BODY')
    if not checks['contains_meaningful_body']:
        codes.append('SHORT_OR_EXCERPT_RISK')
    if not checks['contains_expected_site_domain']:
        codes.append('FIRST_PARTY_DESTINATION_NOT_IDENTIFIED')
    # Never include source message, URLs, sender identity, email, personal info, or address.
    return {
        'schema_version': 1,
        'status': HOLD,
        'issue_number': issue,
        'classification': entry['kind'],
        'checks': checks,
        'blocker_codes': codes,
        'external_verifications_still_required': [
            'Founder permission to obtain/send a separate WordPress test email',
            'Authenticated provenance and actual sender identity, not inferable from an .eml alone',
            'Manual confirmation of working unsubscribe for this exact rendered message',
            'Legal validation of the Final Vestige business mailing address',
            'Actual eligible opted-in recipient cohort, content and date authorization',
            'Platform excerpt/full-format decision and actual displayed CTA',
        ] + (['Account-specific Inspire3 email permission and earning-link eligibility',
              'Published independent product guide and adjacent disclosure verified'] if commercial else []),
        'conclusion': 'Content observations only. This script NEVER authorizes publication or sending.',
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description='OFFLINE, no-send, redacted received-email inspection')
    ap.add_argument('--eml', type=Path, required=True, help='Private, previously authorized local .eml only')
    ap.add_argument('--issue', type=int, choices=range(1, 7), required=True)
    ap.add_argument('--private-postal-file', type=Path, help='Private local file; never check into Git')
    ap.add_argument('--json-report', type=Path, help='Optional privacy-safe summary output')
    args = ap.parse_args(argv)
    try:
        raw = args.eml.read_bytes()
        private_postal = args.private_postal_file.read_text(encoding='utf-8').strip() if args.private_postal_file else None
        result = parse_received(raw, args.issue, private_postal)
    except Exception:
        result = {'status': HOLD, 'error_code': 'PRIVATE_INPUT_READ_FAILURE'}
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_report:
        args.json_report.write_text(output + '\n', encoding='utf-8')
    print(output)
    return 0  # HOLD status is intentionally non-authorizing, even with successful parsing.


if __name__ == '__main__':
    raise SystemExit(main())
