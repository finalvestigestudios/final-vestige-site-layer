"""Non-sending, privacy-preserving Jetpack .eml review. No network, sends or subscriber writes.
A passing structural audit is NOT proof of valid postal address or working unsubscribe.
"""
from __future__ import annotations
import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

PLACEHOLDER = re.compile(r'\[\[|\]\]|PLACEHOLDER|URL_REQUIRED|ADDRESS_REQUIRED', re.I)
ADDRESS = re.compile(r'[^\s@<>]+@[^\s@<>]+')

class TextAndLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]; self.links=[]; self.href=None
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a': self.href=dict(attrs).get('href','')
    def handle_data(self, data):
        self.parts.append(data)
        if self.href is not None and data.strip(): self.links.append((self.href,data.strip()))
    def handle_endtag(self, tag):
        if tag.lower() == 'a': self.href=None

def audit(data: bytes, *, edition: str, expected_subject: str, sender_label: str,
          legal_postal_text: str = '', evidence: dict | None = None) -> dict:
    """Only return aggregate tests; never emit message headers, recipient addresses or raw bodies."""
    evidence = evidence or {}
    msg=BytesParser(policy=policy.default).parsebytes(data)
    html=[]; plain=[]
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment': continue
        if part.get_content_type() == 'text/html': html.append(part.get_content())
        if part.get_content_type() == 'text/plain': plain.append(part.get_content())
    p=TextAndLinks()
    for body in html: p.feed(body)
    text=' '.join(p.parts)+' '+' '.join(plain)
    links=p.links
    unsub=[(href,label) for href,label in links if 'unsubscribe' in label.lower() or 'opt out' in label.lower()]
    valid_unsub=bool(unsub) and all(re.match(r'^https://[^\s]+$', href) or re.match(r'^mailto:[^\s]+$',href) for href,_ in unsub)
    checks={
        'subject_exact': str(msg.get('Subject','')).strip()==expected_subject.strip(),
        'sender_label': sender_label.lower() in str(msg.get('From','')).lower(),
        'html_and_plaintext': bool(html) and bool(plain),
        'visible_unsubscribe_url_syntax': valid_unsub,
        'unsubscribe_in_plaintext': bool(re.search(r'unsubscribe|opt out', ' '.join(plain),re.I)),
        'postal_address_present': bool(legal_postal_text.strip()) and legal_postal_text.strip().lower() in text.lower(),
        'no_template_placeholders': not PLACEHOLDER.search(text) and not PLACEHOLDER.search(' '.join(x[0] for x in links)),
        'has_editorial_source': 'doi.org/' in text.lower() or 'nasa.gov' in text.lower() or 'archives.gov' in text.lower(),
        'near_offer_disclosure': True,
        'no_direct_merchant_destination': True,
    }
    if edition in ('03','05'):
        checks['near_offer_disclosure'] = bool(re.search(r'(may earn|earn a commission)', text, re.I))
        checks['no_direct_merchant_destination'] = not any(re.search(r'(zen12|hypnosislive|inspire3)\.com',h,re.I) for h,_ in links)
    # Evidence is independent of syntactic checks; it MUST come from a separately approved, private review.
    attestations=['publisher_postal_address_validated','unsubscribe_click_and_opt_out_verified',
                  'jetpack_native_preview_verified','actual_received_mail_verified',
                  'provider_eligible_unique_count_verified','founder_campaign_approval']
    if edition in ('03','05'):
        attestations += ['named_merchant_email_permission_verified','guide_live_and_approved',
                         'exact_earning_link_verified','merchant_claims_current_verified']
    proof={k: evidence.get(k) is True for k in attestations}
    status='REVIEW_CANDIDATE_ONLY' if all(checks.values()) and all(proof.values()) else 'HOLD_UNSENT'
    return {'edition':edition,'structural_checks':checks,'evidence_attested':proof,
            'status':status,'recipient_count':None,'send_authorized':False,
            'notes':['No emails sent or contacted. Structural syntax is not operational opt-out proof.',
                     'Postal string match is not publisher-address validity proof.',
                     'Do not infer Jetpack rendering, signed consent or paid conversions from this audit.']}

def main():
    ap=argparse.ArgumentParser(description='Offline .eml inspector, never send or post')
    ap.add_argument('eml',type=Path)
    ap.add_argument('--edition',required=True,choices=['01','02','03','04','05','06'])
    ap.add_argument('--subject',required=True)
    ap.add_argument('--sender',default='Final Vestige Studios')
    ap.add_argument('--postal',default='')
    ap.add_argument('--attestations',type=Path)
    args=ap.parse_args()
    ev=json.loads(args.attestations.read_text()) if args.attestations else {}
    print(json.dumps(audit(args.eml.read_bytes(),edition=args.edition,expected_subject=args.subject,
             sender_label=args.sender,legal_postal_text=args.postal,evidence=ev),indent=2))
if __name__=='__main__':main()
