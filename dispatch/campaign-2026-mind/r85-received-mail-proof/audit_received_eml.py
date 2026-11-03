#!/usr/bin/env python3
"""Offline, PII-minimizing inspection of an AUTHORIZED received Jetpack .eml.

This is NOT a sender, unsubscribe tester, consent resolver or legal certification.
The report contains only categorical observations, never message bodies/addresses.
Real received email files must stay outside source control.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

MAX_BYTES = 2_000_000
DISCLOSURE_PHRASES = (
    "may earn a commission",
    "might earn a commission",
    "we may receive a commission",
    "we may earn a commission",
)


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def canonical_url(value: str) -> str:
    """Exact https URL comparison; reject query, fragment, credentials and ports."""
    try:
        parsed = urlsplit(value.strip())
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.port or parsed.query or parsed.fragment):
            return ""
        return "https://" + parsed.hostname.casefold() + parsed.path.rstrip("/")
    except ValueError:
        return ""


class VisibleHTML(HTMLParser):
    """Extract visible text and labeled links without emitting any private values."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.links = []
        self._ignored = 0
        self._active = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        if tag in ("style", "script", "head", "title"):
            self._ignored += 1
        if self._ignored:
            return
        if tag in ("br", "p", "div", "li", "tr"):
            self.text.append(" ")
        if tag == "a":
            entry = {"url": attrs.get("href", ""), "label": ""}
            self.links.append(entry)
            self._active.append(entry)

    def handle_data(self, data):
        if not self._ignored:
            self.text.append(data)
            for entry in self._active:
                entry["label"] += data

    def handle_endtag(self, tag):
        if tag.lower() in ("style", "script", "head", "title") and self._ignored:
            self._ignored -= 1
        if tag.lower() == "a" and self._active:
            self._active.pop()


def extract_parts(message):
    texts, htmls = [], []
    for part in message.walk():
        if part.is_multipart():
            continue
        if part.get_content_disposition() == "attachment":
            continue
        typ = part.get_content_type()
        if typ not in ("text/plain", "text/html"):
            continue
        try:
            val = part.get_content()
        except (UnicodeError, LookupError, ValueError):
            val = part.get_payload(decode=True).decode("utf-8", "replace")
        if isinstance(val, str):
            (texts if typ == "text/plain" else htmls).append(val)
    return texts, htmls


def audit_bytes(
    raw: bytes,
    *,
    expected_subject: str,
    expected_cta: str,
    commercial: bool,
    postal_address: str | None = None,
):
    """Return a fixed-key, redact-safe report; NEVER return a send permission."""
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError("Invalid input size")
    if not expected_subject or not expected_subject.strip():
        raise ValueError("Expected subject is required")
    url = canonical_url(expected_cta)
    if not url or urlsplit(url).hostname not in ("finalvestige.com", "www.finalvestige.com"):
        raise ValueError("Expected CTA must be an exact first-party HTTPS URL")
    if postal_address is not None and len(postal_address.strip()) < 8:
        raise ValueError("Postal address is not a meaningful local comparison string")

    message = BytesParser(policy=policy.default).parsebytes(raw)
    if not message.get("From") or not message.get("Subject"):
        raise ValueError("Not an RFC822 message with From and Subject")
    plains, htmls = extract_parts(message)
    if not (plains or htmls):
        raise ValueError("No readable email body")

    parsed_html = VisibleHTML()
    for fragment in htmls:
        parsed_html.feed(fragment)
    html_visible = " ".join(parsed_html.text)
    combined_visible = normalize(html_visible or " ".join(plains))
    all_text = normalize(" ".join(plains) + " " + html_visible)
    url_in_html = any(canonical_url(item["url"]) == url for item in parsed_html.links)
    url_in_plaintext = any(canonical_url(candidate.rstrip(").,;")) == url
                           for text in plains
                           for candidate in re.findall(r"https://[^\s<>\"']+", text, re.I))
    has_cta = url_in_html or url_in_plaintext

    # The exact CTA label is unknown. A character-count heuristic cannot prove
    # disclosure is immediately beside a specific commercial offer.
    disclosure_positions = [all_text.find(p) for p in DISCLOSURE_PHRASES if p in all_text]
    has_disclosure = bool(disclosure_positions)
    body_unsubscribe = any(
        "unsubscribe" in normalize(item["label"]) and bool(canonical_url(item["url"]))
        for item in parsed_html.links
    ) or bool(re.search(r"\bunsubscribe\b", " ".join(plains), re.I))
    header_unsubscribe = bool(message.get("List-Unsubscribe"))
    header_post = normalize(str(message.get("List-Unsubscribe-Post", "")))
    supplied_address = normalize(postal_address or "")
    address_found = bool(supplied_address and supplied_address in all_text)

    checks = {
        "subject_matches_expected": normalize(str(message.get("Subject"))) == normalize(expected_subject),
        "has_plaintext_part": bool(plains),
        "has_html_part": bool(htmls),
        "expected_first_party_cta_present": has_cta,
        "commission_disclosure_present": has_disclosure if commercial else None,
        "commission_disclosure_in_first_350_visible_chars":
            any(p in combined_visible[:350] for p in DISCLOSURE_PHRASES) if commercial else None,
        "postal_address_string_present": address_found,
        "body_unsubscribe_instruction_or_link_seen": body_unsubscribe,
        "list_unsubscribe_header_seen": header_unsubscribe,
        "list_unsubscribe_one_click_header_seen":
            "list-unsubscribe=one-click" in header_post,
    }
    # Never echo addresses, URLs, recipient identities, subject, MIME,
    # sender strings, tracking tokens, or content hashes.
    return {
        "schema": "fv-dispatch-received-eml-v1",
        "mode": "commercial" if commercial else "editorial",
        "decision": "HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION",
        "checks": checks,
        "requires_external_evidence": [
            "Founder-approved controlled test email and receipt",
            "Exact approved creative and Jetpack post-title/excerpt comparison",
            "Verified Final Vestige-owned qualifying postal address",
            "Real functional opt-out test with appropriate authority",
            "Eligible recipient/consent diagnostics reconciled privately",
            "Final founder approval of each send, audience and timing",
        ] + ([
            "Named-product affiliate approval AND permission to market by email",
            "Published vetted first-party warm-up guide and verified earning URL",
            "FTC near-offer disclosure reviewed in actual received rendering",
            "Current merchant claims and terms independently checked",
        ] if commercial else []),
        "limitations": [
            "Header presence does not prove unsubscribe works",
            "A visible postal string does not prove lawful address ownership",
            "A source-HTML link does not prove a recipient can open it",
            "The excerpt and email client may render differently",
            "A single received message does not establish list eligibility or delivery rate",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eml", type=Path, help="Locally held AUTHORIZED email file (never commit)")
    parser.add_argument("--subject", required=True, help="Approved expected post title / subject")
    parser.add_argument("--cta", required=True, help="Expected first-party full HTTPS CTA URL")
    parser.add_argument("--commercial", action="store_true", help="Require visible commercial disclosure")
    parser.add_argument("--postal-env", default="FV_DISPATCH_POSTAL_ADDRESS",
                        help="Name of environment variable holding private qualified postal address")
    args = parser.parse_args(argv)
    try:
        report = audit_bytes(
            args.eml.read_bytes(),
            expected_subject=args.subject,
            expected_cta=args.cta,
            commercial=args.commercial,
            postal_address=os.environ.get(args.postal_env),
        )
    except (OSError, ValueError) as exc:
        # Deliberately do not print exception values from message/arguments.
        print(json.dumps({"decision": "HOLD_UNSENT", "error": "INPUT_OR_PARSE_INVALID"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
