"""Offline, privacy-preserving inspection of a voluntarily provided RFC 5322 email.
No network, email-send, WordPress or subscriber-list capabilities. HOLD is immutable.
"""
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib
import re

class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.parts = []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style') or a.get('hidden') is not None or 'display:none' in a.get('style', '').replace(' ', '').lower():
            self.hidden += 1
        if tag == 'a':
            self.anchors.append(a.get('href', ''))
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.hidden:
            self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

def inspect_eml(raw: bytes, *, expected_sender_name='Final Vestige Studios',
                publisher_postal_address=None, approved_domains=('finalvestige.com',)):
    """Return non-PII summary; never assert a real received-email or legal release.

    The caller must independently authenticate the source mailbox and verify an
    unsubscribe *works*. All evidence remains REVIEW_ONLY, even when checks pass.
    """
    if not isinstance(raw, bytes) or len(raw) > 2_000_000 or not raw:
        raise ValueError('Raw RFC5322 message bytes required, max 2 MB')
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    subject_headers = msg.get_all('Subject', [])
    from_headers = msg.get_all('From', [])
    plain, html = [], []
    parts = list(msg.walk()) if msg.is_multipart() else [msg]
    for p in parts:
        if p.get_content_disposition() == 'attachment':
            continue
        if p.get_content_type() in ('text/plain', 'text/html'):
            try:
                body = p.get_content()
            except (ValueError, UnicodeDecodeError, LookupError):
                continue
            if isinstance(body, str):
                (plain if p.get_content_type() == 'text/plain' else html).append(body)
    plaintext = '\n'.join(plain)
    htmltext = '\n'.join(html)
    parsed = VisibleHTML()
    parsed.feed(htmltext)
    visible_html = ' '.join(parsed.parts)
    combined = (plaintext + '\n' + visible_html).lower()
    headers_ok = len(subject_headers) == 1 and len(from_headers) == 1
    sender_display, _sender_address = parseaddr(str(from_headers[0])) if from_headers else ('', '')
    sender_match = headers_ok and sender_display.strip() == expected_sender_name
    subject = str(subject_headers[0]).strip() if subject_headers else ''
    subject_ok = bool(subject) and '\n' not in subject and len(subject) <= 180
    addr_observed = bool(publisher_postal_address and publisher_postal_address.strip() and
                         publisher_postal_address.lower() in combined)
    # A header-only List-Unsubscribe is not sufficient to prove a visible opt-out.
    unsub = ('unsubscribe' in combined or 'opt out' in combined or 'opt-out' in combined)
    unsub_links = [x for x in parsed.anchors if 'unsub' in x.lower()]
    list_unsub_header = bool(msg.get('List-Unsubscribe'))
    suspicious = []
    for link in parsed.anchors:
        parsed_url = urlparse(link)
        if parsed_url.scheme in ('http', 'https'):
            host = (parsed_url.hostname or '').lower()
            if not any(host == d or host.endswith('.' + d) for d in approved_domains):
                suspicious.append(host)
        elif parsed_url.scheme and parsed_url.scheme not in ('mailto',):
            suspicious.append('unsafe-scheme')
    blockers = []
    if not headers_ok or not sender_match or not subject_ok:
        blockers.append('SENDER_OR_SUBJECT_NOT_AUTHENTICATED')
    if not plaintext or not htmltext:
        blockers.append('MISSING_HTML_OR_PLAINTEXT')
    if not publisher_postal_address or not addr_observed:
        blockers.append('STUDIO_POSTAL_ADDRESS_UNVERIFIED')
    if not unsub or not unsub_links:
        blockers.append('VISIBLE_UNSUBSCRIBE_NOT_ESTABLISHED')
    if suspicious:
        blockers.append('NON_OWNED_OR_UNAPPROVED_DESTINATION')
    blockers += ['UNSUBSCRIBE_FUNCTION_NOT_TESTED', 'SENDER_MAILBOX_NOT_INDEPENDENTLY_AUTHENTICATED',
                 'FOUNDER_FINAL_SEND_APPROVAL_REQUIRED']
    return {
        'release': 'HOLD_UNSENT', 'inspection_kind': 'OFFLINE_RFC5322_REVIEW_NOT_INBOX_PROOF',
        'raw_sha256': hashlib.sha256(raw).hexdigest(), 'byte_size': len(raw),
        'subject_present_and_sane': subject_ok, 'expected_display_name_present': sender_match,
        'has_html': bool(htmltext), 'has_plaintext': bool(plaintext),
        'visible_studio_postal_exact_match': addr_observed,
        'visible_unsubscribe_text': unsub, 'unsubscribe_like_html_anchor': bool(unsub_links),
        'list_unsubscribe_header_present': list_unsub_header,
        'external_or_unsafe_destination_count': len(suspicious),
        'blockers': blockers,
        'note': 'No To, Cc, Bcc, From address, subject text, body, link token or subscriber ID is emitted.'
    }
