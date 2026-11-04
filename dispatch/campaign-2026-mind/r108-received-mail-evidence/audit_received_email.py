"""Read-only, PII-suppressing audit of a locally supplied RFC 5322 email.

Does NOT send email, contact any server, verify subscriber identity, or approve release.
Report aggregates only, never raw message text, recipients, links, tokens or addresses.
"""
from __future__ import annotations

import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PDF_NAME = "Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"
DISCLOSURE = re.compile(r"\b(?:may earn (?:a )?commission|affiliate (?:links?|relationship)|commission[- ]earning)\b", re.I)
EMAIL_TYPES = ("confirmation", "welcome", "editorial", "commercial")


class VisibleLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._active_href = None
        self._active_words = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._active_href = dict(attrs).get("href", "")
            self._active_words = []

    def handle_data(self, data):
        if self._active_href is not None:
            self._active_words.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._active_href is not None:
            self.links.append((self._active_href, " ".join(self._active_words)))
            self._active_href = None
            self._active_words = []


def _payloads(message):
    plain, html = [], []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        typ = part.get_content_type()
        if typ not in ("text/plain", "text/html"):
            continue
        try:
            value = part.get_content()
        except (LookupError, UnicodeDecodeError, ValueError):
            continue
        if isinstance(value, str):
            (plain if typ == "text/plain" else html).append(value)
    return "\n".join(plain), "\n".join(html)


def audit_bytes(data: bytes, expected: str) -> dict:
    if expected not in EMAIL_TYPES:
        raise ValueError("Invalid expected message type")
    if len(data) > 3_000_000:
        raise ValueError("Email exceeds offline evidence-size limit")
    msg = BytesParser(policy=policy.default).parsebytes(data)
    plain, html = _payloads(msg)
    links = VisibleLinks()
    links.feed(html)
    urls = [u for u, _ in links.links]
    full = f"{plain}\n{html}"
    # Identifying fields and unsubscribe tokens MUST NEVER enter the report.
    header_unsub = bool(msg.get("List-Unsubscribe"))
    header_oneclick = "list-unsubscribe=one-click" in str(msg.get("List-Unsubscribe-Post", "")).lower()
    visible_unsub = any(
        "unsubscribe" in label.lower() and urlparse(u).scheme.lower() == "https"
        for u, label in links.links
    )
    pdf_link = any(PDF_NAME in urlparse(u).path for u in urls) or PDF_NAME in plain
    firstparty_link = any(urlparse(u).hostname in ("finalvestige.com", "www.finalvestige.com") for u in urls)
    explicit_disclosure = bool(DISCLOSURE.search(plain) or DISCLOSURE.search(re.sub(r"<[^>]*>", " ", html)))
    result = {
        "schema": "fv.dispatch.received-mail-evidence.v1",
        "expected_type": expected,
        "processing": "offline_read_only_no_send",
        "has_plaintext": bool(plain.strip()),
        "has_html": bool(html.strip()),
        "has_list_unsubscribe_header": header_unsub,
        "has_one_click_header_signal": header_oneclick,
        "has_visible_https_unsubscribe_anchor": visible_unsub,
        "has_fieldbook_pdf_reference": pdf_link,
        "has_first_party_html_link": firstparty_link,
        "has_inline_commission_disclosure": explicit_disclosure,
        "has_subject_header": bool(msg.get("Subject")),
        "needs_independent_receipt_provenance": True,
        "needs_live_unsubscribe_function_test": True,
        "needs_verified_fv_postal_address": True,
        "needs_authoritative_email_subscription_status": True,
        "needs_founder_send_approval": True,
        "confirmed_signup_observable_from_email": False,
        "actual_merchant_sale_observable_from_email": False,
        "decision": "HOLD_UNSENT",
    }
    checks = []
    if not result["has_subject_header"]:
        checks.append("NO_SUBJECT")
    if not result["has_plaintext"]:
        checks.append("NO_PLAINTEXT_PART")
    if expected == "welcome" and not pdf_link:
        checks.append("WELCOME_FIELD_BOOK_NOT_OBSERVED")
    if expected == "commercial" and not explicit_disclosure:
        checks.append("COMMISSION_DISCLOSURE_NOT_OBSERVED_IN_EMAIL")
    if expected in ("editorial", "commercial") and not (header_unsub or visible_unsub):
        checks.append("UNSUBSCRIBE_SIGNAL_NOT_OBSERVED")
    if expected in ("editorial", "commercial") and not firstparty_link:
        checks.append("FIRST_PARTY_HTML_LINK_NOT_OBSERVED")
    result["review_flags"] = sorted(checks)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eml", type=Path, help="Already-authorized local email evidence. Not transmitted or stored.")
    parser.add_argument("--expect", choices=EMAIL_TYPES, required=True)
    args = parser.parse_args()
    report = audit_bytes(args.eml.read_bytes(), args.expect)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
