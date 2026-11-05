"""Non-sending, read-only Dispatch received-email QA. No network, SMTP, PII output.

This tool audits a *locally saved* .eml. Raw MIME is untrusted input and never
qualifies as proof of actual inbox delivery. A reviewer must separately attest
mailbox origin, opt-out behavior, legal address, and partner authorization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 1_500_000
ALLOWED_CONTENT = {"text/plain", "text/html"}
REVIEW_MARKERS = ("UNSENT FIXTURE", "OFFLINE QA ONLY", "NEVER SEND", "X-FV-REVIEW-ONLY")
FORBIDDEN_ACTIVATION = ("[[VALID_POSTAL_ADDRESS_REQUIRED]]", "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", "[[APPROVED_")

class HTMLFacts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []
        self._anchor = []
        self._href = None
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a":
            self._anchor = []
            self._href = d.get("href")
    def handle_data(self, data):
        self.parts.append(data)
        if self._href is not None:
            self._anchor.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._anchor).strip()))
            self._href = None
            self._anchor = []

def _safe_url(url: str) -> bool:
    try:
        u = urlsplit(url)
        return u.scheme == "https" and bool(u.hostname) and not u.username and not u.password
    except ValueError:
        return False

def inspect_bytes(data: bytes, *, expected_subject: str = "", approved_postal_text: str = "") -> dict:
    """Produce privacy-safe structural diagnostics only. Never return raw addresses or URLs."""
    if not data or len(data) > MAX_BYTES:
        raise ValueError("Missing or oversized message")
    msg = BytesParser(policy=policy.default).parsebytes(data)
    subject = str(msg.get("Subject", ""))
    from_header = str(msg.get("From", ""))
    plain, html = [], []
    for part in msg.walk():
        if part.is_multipart():
            continue
        typ = part.get_content_type()
        if typ not in ALLOWED_CONTENT:
            continue
        try:
            body = part.get_content()
            if isinstance(body, str):
                (plain if typ == "text/plain" else html).append(body[:300_000])
        except (UnicodeError, LookupError, ValueError):
            continue
    visible_html = HTMLFacts()
    visible_html.feed("\n".join(html))
    text = "\n".join(plain + visible_html.parts)
    upper = (subject + "\n" + text).upper()
    is_fixture = (str(msg.get("X-FV-Review-Only", "")).upper() == "TRUE" or
                  any(marker in upper for marker in REVIEW_MARKERS))
    unsub_header = str(msg.get("List-Unsubscribe", ""))
    one_click = str(msg.get("List-Unsubscribe-Post", "")).strip().lower() == "list-unsubscribe=one-click"
    link_unsub = any(_safe_url(url) and ("unsubscribe" in label.lower() or "unsubscribe" in url.lower())
                     for url, label in visible_html.links)
    header_unsub = "https://" in unsub_header.lower() or "mailto:" in unsub_header.lower()
    valid_address = bool(approved_postal_text.strip()) and approved_postal_text.strip().casefold() in text.casefold()
    missing_placeholders = not any(mark in upper for mark in FORBIDDEN_ACTIVATION)
    candidate_cta = any(_safe_url(url) and "unsubscribe" not in (label+url).lower()
                        and "privacy" not in (label+url).lower() for url,label in visible_html.links)
    subject_matches = bool(expected_subject) and subject.strip() == expected_subject.strip()
    safety = {
        "not_fixture": not is_fixture,
        "expected_subject_matches": subject_matches,
        "both_mime_alternatives": bool(plain and html),
        "no_release_placeholders": missing_placeholders,
        "unsubscribe_candidate_present": bool(link_unsub or header_unsub),
        "unsubscribe_one_click_header": bool(one_click),
        "approved_publisher_postal_text_present": valid_address,
        "https_editorial_cta_candidate": candidate_cta,
        "from_header_present": bool(from_header),
        "has_received_header": bool(msg.get_all("Received")),
        "has_authentication_results": bool(msg.get_all("Authentication-Results")),
    }
    outstanding = [k for k,v in safety.items() if not v]
    # This tool can NEVER itself attest real inbox delivery, actual unsubscribe,
    # rightful subscriber consent, authenticity or legal compliance.
    return {
        "schema": "fv.dispatch.received_audit.v1",
        "sha256": hashlib.sha256(data).hexdigest(),
        "message_bytes": len(data),
        "checks": safety,
        "fail_or_unknown": outstanding,
        "requires_external_attestation": [
            "mailbox_owner_authorized_saved_received_message",
            "genuine_wordpress_delivery_provenance",
            "publisher_postal_address_authorized_and_current",
            "unsubscribe_link_operational_and_honors_optout",
            "consent_and_email_subscription_eligibility",
            "merchant_email_rights_and_disclosure_if_commercial",
            "founder_final_campaign_approval"],
        "release_status": "HOLD_UNSENT",
        "actual_delivered": "NOT_ESTABLISHED_BY_EML_ALONE",
        "raw_headers_or_subscriber_pii_in_report": False,
    }

def inspect_file(path: Path, **kw) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized file")
    return inspect_bytes(path.read_bytes(), **kw)

def main() -> None:
    parser = argparse.ArgumentParser(description="Offline read-only, privacy-safe received-email QA")
    parser.add_argument("--eml", type=Path, required=True)
    parser.add_argument("--expected-subject", required=True)
    parser.add_argument("--approved-postal-text", default="", help="Local reviewer-only substring: NEVER commit")
    parser.add_argument("--report", type=Path, help="Writes sanitized report only; no raw headers/addresses/links")
    args = parser.parse_args()
    report = inspect_file(args.eml, expected_subject=args.expected_subject,
                          approved_postal_text=args.approved_postal_text)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered)

if __name__ == "__main__":
    main()
