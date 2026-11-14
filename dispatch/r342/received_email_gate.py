"""No-send, read-only MIME QA. Never treat offline/synthetic mail as Jetpack proof."""
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from urllib.parse import urlparse
import re

BLOCKED = 'HOLD_UNSENT'
COMMERCIAL = {'03', '05'}

class HTMLSummary(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.text, self.hidden = [], [], 0
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a': self.links.append((d.get('href', ''), d.get('aria-label', '')))
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden: self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.text.append(data)

def _body_parts(message):
    plain, html = [], []
    for part in message.walk():
        if part.get_content_maintype() == 'multipart': continue
        if part.get_content_disposition() == 'attachment': continue
        try: content = part.get_content()
        except Exception: continue
        if not isinstance(content, str): continue
        if part.get_content_type() == 'text/plain': plain.append(content)
        if part.get_content_type() == 'text/html': html.append(content)
    return '\n'.join(plain), '\n'.join(html)

def evaluate_mime(raw, edition, *, provenance='SYNTHETIC', approvals=None):
    """Return only opaque PASS/FAIL state; no raw body, addresses or tokens are echoed.

    Provenance is caller-supplied, NOT authenticated. A LIVE_RECEIVED claim must be
    separately established with secure audit evidence and founder-approved testing.
    """
    if edition not in {'01','02','03','04','05','06'}: raise ValueError('invalid edition')
    if not isinstance(raw, bytes) or len(raw) > 1_000_000: raise ValueError('invalid MIME bytes')
    message = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html = _body_parts(message)
    h = HTMLSummary(); h.feed(html)
    combined = (plain + '\n' + ' '.join(h.text)).lower()
    subject = str(message.get('Subject', '')).strip()
    sender = str(message.get('From', '')).strip().lower()
    failures = []
    if not subject or re.search(r'placeholder|\[subject\]|test message', subject, re.I): failures.append('SUBJECT_INVALID')
    if not sender or 'final vestige' not in sender: failures.append('SENDER_IDENTITY_UNVERIFIED')
    if not plain.strip(): failures.append('PLAIN_PART_MISSING')
    if not html.strip(): failures.append('HTML_PART_MISSING')
    if not h.links: failures.append('HTML_LINKS_MISSING')
    if not ('unsubscribe' in combined or 'opt out' in combined): failures.append('OPT_OUT_TEXT_MISSING')
    unsub_links = [u for u,desc in h.links if ('unsubscribe' in desc.lower() or 'unsubscribe' in u.lower() or 'opt-out' in desc.lower())]
    if not unsub_links: failures.append('OPT_OUT_LINK_MISSING')
    if any(not urlparse(u).scheme in ('https','http') for u in unsub_links): failures.append('OPT_OUT_LINK_MALFORMED')
    # An address in a third-party vendor email is not evidence of FV publisher identity.
    addr_markers = ('[publisher postal', '[physical address', '[fv mailing address', 'address to be verified', 'postal address pending')
    if any(x in combined for x in addr_markers): failures.append('POSTAL_PLACEHOLDER')
    if not re.search(r'final vestige.{0,80}\b(?:p\.?o\.? box|street|avenue|road|suite|boulevard|[0-9]{3,5}\s+\w+)\b', combined, re.I|re.S):
        failures.append('FV_POSTAL_NOT_VERIFIABLE')
    main_links = [u for u,desc in h.links if urlparse(u).hostname in ('finalvestige.com','www.finalvestige.com') and 'unsubscribe' not in u.lower()]
    if len(main_links) != 1: failures.append('SINGLE_FIRST_PARTY_CTA_NOT_ESTABLISHED')
    if edition in COMMERCIAL:
        if not re.search(r'final vestige may earn a commission', combined, re.I): failures.append('NEAR_OFFER_DISCLOSURE_MISSING')
        if not re.search(r'(independent|seller|advertis|not proof|not established)', combined, re.I): failures.append('MERCHANT_CLAIM_BOUNDARY_MISSING')
    if provenance != 'LIVE_RECEIVED': failures.append('NOT_AUTHENTIC_RECEIVED_EMAIL')
    a = approvals or {}
    required = ['founder_final_approval','native_jetpack_preview_attested','fv_postal_ownership_verified','unsubscribe_function_tested','provider_confirmed_eligible_recipients']
    if edition in COMMERCIAL: required += ['named_affiliate_approval','email_channel_permission','issued_tracking_link','guide_live_and_approved','merchant_claims_checked']
    for k in required:
        if a.get(k) is not True: failures.append('PROOF_REQUIRED_' + k.upper())
    return {'edition': edition, 'decision': BLOCKED, 'syntax_checks_pass': not any(x for x in failures if not x.startswith(('PROOF_REQUIRED_', 'NOT_AUTHENTIC_'))), 'gate_failures': sorted(set(failures)), 'provenance_is_self_attested': True, 'send_authorized': False}
