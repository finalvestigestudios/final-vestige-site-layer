"""Privacy-minimizing, non-sending auditor for *received* Jetpack RFC822 emails.

Never returns, logs, or persists recipient identities, tokenized links or raw bodies.
A pass only means review evidence exists, NEVER that sending is authorized.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

COMMERCIAL = {3, 5}
DISCLOSURE = re.compile(r"final vestige.{0,65}(?:may|might) earn (?:a )?commission", re.I | re.S)


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._anchor_words: list[str] = []
        self.images_have_alt = True
        self.prohibited_markup = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "form", "iframe", "object"}:
            self.prohibited_markup = True
        if tag == "img" and not attrs.get("alt", "").strip():
            self.images_have_alt = False
        if tag == "a":
            self._current_href = attrs.get("href", "")
            self._anchor_words = []

    def handle_data(self, data):
        self.words.append(data)
        if self._current_href is not None:
            self._anchor_words.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._current_href is not None:
            self.links.append((self._current_href, " ".join(self._anchor_words).strip()))
            self._current_href = None
            self._anchor_words = []


def is_http(url: str) -> bool:
    try:
        u = urlsplit(url)
        return u.scheme in {"https", "http"} and bool(u.netloc)
    except ValueError:
        return False


def content_parts(msg):
    plain, html = [], []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        typ = part.get_content_type()
        if typ not in {"text/plain", "text/html"}:
            continue
        try:
            body = part.get_content()
        except Exception:
            continue
        if not isinstance(body, str):
            continue
        (plain if typ == "text/plain" else html).append(body)
    return "\n".join(plain), "\n".join(html)


def inspect(raw: bytes, *, issue: int, subject: str, cta_url: str,
            publisher_address: str | None = None, authorized_inbox: bool = False,
            native_consent: bool = False, optout_checked: bool = False,
            source_proof: bool = False, merchant_email_permission: bool = False) -> dict:
    """Return BOOL-only evidence (no PII, no identifying URLs, no raw email text)."""
    if issue not in range(1, 7):
        raise ValueError("issue must be 1..6")
    if not is_http(cta_url) or urlsplit(cta_url).hostname not in {"finalvestige.com", "www.finalvestige.com"}:
        raise ValueError("CTA must be a first-party HTTPS/HTTP destination")
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    from_name, from_addr = parseaddr(str(msg.get("From", "")))
    plain, html = content_parts(msg)
    parsed = Markup()
    parsed.feed(html)
    html_text = " ".join(parsed.words)
    combined = " ".join([plain, html_text])
    body_links = parsed.links
    found_cta = any(href == cta_url and bool(label.strip()) for href, label in body_links)
    # Plaintext fallback may print the bare destination rather than an HTML anchor.
    plain_cta = cta_url in plain
    unsub_links = [href for href, label in body_links if "unsubscribe" in label.casefold() and is_http(href)]
    primary_labels = [label for href, label in body_links if href == cta_url and label.strip()]
    anchor_pos = html_text.find(primary_labels[0]) if primary_labels else -1
    url_pos = plain.find(cta_url)
    # An affiliate disclosure elsewhere in the message is not a near-offer disclosure.
    html_near = anchor_pos >= 0 and bool(DISCLOSURE.search(html_text[max(0, anchor_pos - 300):anchor_pos + 180]))
    plain_near = url_pos >= 0 and bool(DISCLOSURE.search(plain[max(0, url_pos - 300):url_pos + 180]))
    has_unsub_header = bool(msg.get("List-Unsubscribe", ""))
    # An automated tool cannot establish the link actually functions or belongs to FV.
    flags = {
        "subject_matches_campaign": str(msg.get("Subject", "")).strip() == subject.strip(),
        "sender_display_matches": from_name.casefold().strip() == "final vestige studios",
        "sender_domain_matches_documented_jetpack": from_addr.casefold() == "donotreply@wordpress.com",
        "substantive_full_text": len(re.sub(r"\s+", " ", combined).strip()) >= 400,
        "first_party_cta_in_html_with_label": found_cta,
        "first_party_cta_in_plaintext": plain_cta,
        "visible_optout_indicator": bool(unsub_links or has_unsub_header),
        "actual_optout_test_attested": bool(optout_checked),
        "publisher_address_in_body": bool(publisher_address and publisher_address.strip() in combined),
        "publisher_address_confirmed_by_owner": bool(publisher_address),
        "affiliate_disclosure_adjacent_html": html_near if issue in COMMERCIAL else True,
        "affiliate_disclosure_adjacent_plaintext": plain_near if issue in COMMERCIAL else True,
        "html_images_have_alt": parsed.images_have_alt,
        "html_no_scripts_or_forms": not parsed.prohibited_markup,
        "accessed_in_authorized_received_inbox": bool(authorized_inbox),
        "native_opt_in_eligibility_evidence": bool(native_consent),
        "independently_checked_source": bool(source_proof),
        "merchant_email_permission_attested": bool(merchant_email_permission) if issue in COMMERCIAL else True,
    }
    # The non-commercial messages may not need an affiliate notice; commercial issues do.
    # No booleans in this tool can authorize a future send, regardless of input.
    if not flags["subject_matches_campaign"]:
        verdict = "NOT_A_CAMPAIGN_MESSAGE"
    elif all(flags.values()):
        verdict = "RECEIVED_COPY_QA_CANDIDATE_ONLY_NOT_SEND_APPROVAL"
    else:
        verdict = "RECEIVED_COPY_QA_HOLD"
    return {"issue": issue, "commercial": issue in COMMERCIAL, "verdict": verdict,
            "send_authorized": False, "commercial_link_authorized": False,
            "checks": flags, "failed_checks": [k for k, v in flags.items() if not v],
            "privacy": "No addresses, raw bodies, email tokens or recipient links are returned."}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="RECEIVED-EMAIL-ONLY forensic QA; never sends or changes a list")
    p.add_argument("--eml", type=Path, required=True)
    p.add_argument("--issue", type=int, choices=range(1, 7), required=True)
    p.add_argument("--expected-subject", required=True)
    p.add_argument("--first-party-cta", required=True)
    p.add_argument("--authorized-inbox", action="store_true")
    p.add_argument("--native-consent", action="store_true")
    p.add_argument("--optout-checked", action="store_true")
    p.add_argument("--source-proof", action="store_true")
    p.add_argument("--merchant-email-permission", action="store_true")
    args = p.parse_args(argv)
    # The publisher address is supplied only out-of-band and never printed.
    result = inspect(args.eml.read_bytes(), issue=args.issue, subject=args.expected_subject,
                     cta_url=args.first_party_cta,
                     publisher_address=os.getenv("FV_VERIFIED_BUSINESS_POSTAL_TEXT"),
                     authorized_inbox=args.authorized_inbox, native_consent=args.native_consent,
                     optout_checked=args.optout_checked, source_proof=args.source_proof,
                     merchant_email_permission=args.merchant_email_permission)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "RECEIVED_COPY_QA_CANDIDATE_ONLY_NOT_SEND_APPROVAL" else 3


if __name__ == "__main__":
    sys.exit(main())
