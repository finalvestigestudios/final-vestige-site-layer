"""Dispatch R281: offline, privacy-minimal RFC5322 structure triage.

This is NOT a sender, delivery verifier, consent verifier or legal ruling.
It never returns email body text, mailbox addresses, URLs, or subjects.
"""
from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from urllib.parse import urlsplit

HOLD = 'HOLD_INBOX_POSTAL_UNSUB_CONSENT_MERCHANT_FOUNDER'
PLACEHOLDER = re.compile(r'\[\[|NOT_VERIFIED|UNVERIFIED|REQUIRED|example\.(?:com|org)', re.I)
ADDRESS = re.compile(r'\b(?:P\.?\s*O\.?\s*Box\s*\d{1,8}|\d{1,8}\s+[\w .\'-]{3,60}\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Way))\b', re.I)
OPT_OUT = re.compile(r'\bunsubscribe\b|\bopt[ -]?out\b|\bstop receiving\b|\bmanage (?:emails?|subscription)\b', re.I)
ALLOWED_HOSTS = {'finalvestige.com', 'www.finalvestige.com', 'wordpress.com', 'subscriptions.wordpress.com', 'public-api.wordpress.com'}


def allowed_url(url: str) -> bool:
    try:
        p = urlsplit(url)
        return (p.scheme == 'https' and p.hostname in ALLOWED_HOSTS
                and not p.username and not p.password and p.port in (None, 443)
                and not PLACEHOLDER.search(url) and all(ord(c) >= 32 for c in url))
    except (TypeError, ValueError):
        return False


class ReviewHTML(HTMLParser):
    """Conservative visible-text approximation; CSS/renderer must still be checked."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.visible = []
        self.anchors = []
        self.unsafe = False
        self.obscured = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or '') for k, v in attrs}
        parent_hidden = any(item[1] for item in self.stack)
        style = re.sub(r'/\*.*?\*/', '', a.get('style', ''), flags=re.S).replace(' ', '').lower()
        is_hidden = (parent_hidden or tag in {'style', 'script', 'iframe', 'form', 'template', 'noscript', 'svg'}
                     or 'hidden' in a or a.get('aria-hidden', '').lower() == 'true'
                     or 'display:none' in style or 'visibility:hidden' in style
                     or 'opacity:0' in style)
        if tag in {'script', 'iframe', 'form', 'object', 'embed', 'meta', 'base'}:
            self.unsafe = True
        if tag in {'style', 'template', 'noscript'} or 'hidden' in a or a.get('aria-hidden','').lower() == 'true' or a.get('style'):
            self.obscured = True  # even permitted inline CSS needs a real renderer's adjudication
        self.stack.append((tag, is_hidden, a.get('href', '') if tag == 'a' else '', []))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        while self.stack:
            opened, hidden, href, text = self.stack.pop()
            if opened == 'a' and not hidden:
                self.anchors.append((href, ''.join(text)))
            if opened == tag:
                break

    def handle_data(self, data):
        if not any(item[1] for item in self.stack):
            self.visible.append(data)
            for item in self.stack:
                if item[0] == 'a':
                    item[3].append(data)


def inspect_bytes(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or len(raw) > 2_000_000:
        raise ValueError('Expected at most 2MB RFC5322 bytes')
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html, attached = [], [], 0
    for p in msg.walk():
        if p.is_multipart():
            continue
        if p.get_content_disposition() == 'attachment' or p.get_content_type() not in {'text/plain', 'text/html'}:
            attached += 1
            continue
        try:
            s = p.get_content()
            if not isinstance(s, str):
                s = ''
        except (LookupError, UnicodeError, ValueError, TypeError):
            s = ''
        (html if p.get_content_type() == 'text/html' else plain).append(s)
    h = ReviewHTML()
    for part in html:
        h.feed(part)
    visible_html = '\n'.join(h.visible)
    visible_plain = '\n'.join(plain)
    both = visible_html + '\n' + visible_plain
    _name, mailbox = parseaddr(str(msg.get('From', '')))
    from_syntax = bool(re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[A-Za-z]{2,}', mailbox))
    label_and_url = any(allowed_url(href) and OPT_OUT.search(label) for href, label in h.anchors)
    checks = {
        'subject_present': bool(str(msg.get('Subject', '')).strip()) and not bool(PLACEHOLDER.search(str(msg.get('Subject', '')))),
        'sender_syntax_candidate': from_syntax,
        'date_present': bool(msg.get('Date')),
        'message_id_present': bool(msg.get('Message-ID')),
        'plaintext_present': bool(visible_plain.strip()),
        'html_present': bool(''.join(html).strip()),
        'publisher_postal_candidate_in_both_parts': bool(ADDRESS.search(visible_html) and ADDRESS.search(visible_plain)) and not bool(PLACEHOLDER.search(both)),
        'optout_instruction_in_both_parts': bool(OPT_OUT.search(visible_html) and OPT_OUT.search(visible_plain)),
        'accessible_https_optout_candidate': bool(label_and_url),
        'no_unsafe_markup': not h.unsafe,
        'no_obscured_html': not h.obscured,
        'no_attachments': attached == 0,
        'no_placeholders': not bool(PLACEHOLDER.search(both)),
        'list_unsubscribe_header_candidate': bool(msg.get('List-Unsubscribe')),
    }
    structural = all(v for k, v in checks.items() if k != 'list_unsubscribe_header_candidate')
    return {
        'version': 'r281-structural-only', 'checks': {k: bool(v) for k,v in checks.items()},
        'structural_checks_pass': structural,
        'real_received_jetpack_message_verified': False,
        'sender_authenticated': False,
        'business_postal_ownership_verified': False,
        'unsubscribe_functional_verified': False,
        'subscriber_eligible_and_consented': False,
        'affiliate_email_permission_verified': False,
        'founder_approved_send': False,
        'release_state': HOLD,
    }
