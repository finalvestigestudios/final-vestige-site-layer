#!/usr/bin/env python3
"""Read a LOCAL .eml for content-only release evidence. No sending; no raw PII output."""
from __future__ import annotations
import argparse
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html import unescape
from html.parser import HTMLParser
import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

MERCHANTS = ("zen12.com", "hypnosislive.com", "inspire3.com")
REDIRECT_PARAMS = frozenset(("url", "u", "target", "next", "to", "redirect",
                             "redirect_url", "destination", "dest", "continue"))
URL_IN_TEXT = re.compile(r"https?://[^\s<>\)\]\}]+", re.I)
DISCLOSURE = re.compile(r"\bmay\s+earn\s+(?:an?\s+)?commission\b", re.I)
UNSUB = re.compile(r"\b(?:unsubscribe|stop receiving|manage subscriptions?)\b", re.I)
DRAFT_BANNER = re.compile(r"DO\s+NOT\s+(?:PUBLISH|EMAIL|SEND)", re.I)

class ExtractHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.links = [], []
        self.hidden, self.tiny_images = 0, 0

    def handle_starttag(self, tag, attrs):
        a = {str(k).lower(): v for k, v in attrs if k is not None}
        if tag in ("script", "style", "template"):
            self.hidden += 1
        if tag in ("a", "area") and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            src = a.get("src") or ""
            if src.startswith(("http://", "https://")) and str(a.get("width")) == "1" and str(a.get("height")) == "1":
                self.tiny_images += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

def normalized(value):
    return re.sub(r"\W+", "", unescape(value).casefold())

def unsafe_href(href, depth=0):
    """Flag purchase-capable merchant domains, encoded redirect wrappers and active code schemes."""
    if depth > 4:
        return "DEEP_REDIRECT"
    raw = unescape(str(href or "")).strip()
    if re.match(r"(?i)^(?:javascript|data|vbscript)\s*:", raw):
        return "ACTIVE_SCRIPT"
    try:
        parsed = urlsplit(raw)
        host = unquote((parsed.hostname or "").lower().rstrip("."))
    except ValueError:
        return "MALFORMED_URL"
    if any(host == d or host.endswith("." + d) for d in MERCHANTS):
        return "MERCHANT_DESTINATION"
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in REDIRECT_PARAMS and unquote(value).lower().startswith(("http://", "https://", "//")):
            if unsafe_href(unquote(value), depth + 1):
                return "ENCODED_REDIRECT"
    return None

def extract_bodies(message):
    plain, html = [], []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        kind = part.get_content_type()
        if kind not in ("text/plain", "text/html"):
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeError, ValueError):
            continue
        if isinstance(content, str):
            (html if kind == "text/html" else plain).append(content)
    return "\n".join(plain), "\n".join(html)

def inspect_eml(data, issue, expected_subject=None, expected_guide=None,
                expected_postal_address=None):
    """Never say a parsed email is verified receipt, compliance, consent or authorization."""
    n = int(issue)
    if n not in range(1, 7):
        raise ValueError("issue must be in range 1..6")
    if not isinstance(data, bytes) or len(data) < 1 or len(data) > 2_000_000:
        raise ValueError("EML must be nonempty bytes at most 2 MB")
    msg = BytesParser(policy=policy.default).parsebytes(data)
    plain, html = extract_bodies(msg)
    parser = ExtractHTML()
    if html:
        parser.feed(html)
        parser.close()
    visible_html = " ".join(parser.parts)
    text = "\n".join((plain, visible_html))
    parts = {"plain": plain, "html": visible_html}
    present = {"plain": bool(plain.strip()), "html": bool(html.strip())}
    def all_available(predicate):
        return any(present.values()) and all(not present[k] or predicate(parts[k])
                                             for k in ("plain", "html"))
    links = parser.links + URL_IN_TEXT.findall(plain)
    unsafe_count = sum(bool(unsafe_href(h)) for h in links)

    # A matching footer string does not establish business ownership or legal validity.
    address_match = bool(expected_postal_address and len(normalized(expected_postal_address)) >= 10
                         and normalized(expected_postal_address) in normalized(text))
    unsub_candidate = bool(msg.get("List-Unsubscribe") or UNSUB.search(text) or
                           any("unsubscribe" in h.lower() for h in links))
    commercial = n in (3, 5)
    guide_valid, guide_found = False, False
    if expected_guide:
        try:
            guide_valid = (urlsplit(expected_guide).hostname or "").lower() in (
                "finalvestige.com", "www.finalvestige.com")
            guide_found = guide_valid and any(unescape(h).split("?", 1)[0].rstrip("/") ==
                expected_guide.split("?", 1)[0].rstrip("/") for h in links)
        except ValueError:
            guide_valid = False
    result = {
        "schema": "FV_DISPATCH_R45_CONTENT_INSPECTION_ONLY",
        "issue": str(n).zfill(2),
        "type": "COMMERCIAL" if commercial else "EDITORIAL",
        "mime_has_renderable_body": bool(plain or html),
        "expected_subject_matches": expected_subject is not None and
            str(msg.get("Subject", "")).strip() == expected_subject,
        "sender_display_matches": parseaddr(str(msg.get("From", "")))[0].casefold().strip() ==
            "final vestige",
        "native_preheader_verified": False,
        "physical_address": "TEXT_MATCH_NOT_VERIFIED_OWNERSHIP" if address_match else "UNVERIFIED",
        "unsubscribe": "PRESENT_NOT_FUNCTIONALLY_TESTED" if unsub_candidate else "NOT_FOUND",
        "commercial_disclosure_present": bool(DISCLOSURE.search(text)) if commercial else None,
        "mime_plain_present": present["plain"],
        "mime_html_present": present["html"],
        "commercial_disclosure_in_each_present_alternative": (
            all_available(lambda body: bool(DISCLOSURE.search(body))) if commercial else None),
        "postal_text_in_each_present_alternative": (
            all_available(lambda body: bool(expected_postal_address and
                len(normalized(expected_postal_address)) >= 10 and
                normalized(expected_postal_address) in normalized(body)))),
        "unsubscribe_text_in_each_present_alternative": (
            all_available(lambda body: bool(UNSUB.search(body)))),
        "guide_url_first_party": guide_valid if commercial else None,
        "guide_url_present": guide_found if commercial else None,
        "blocked_merchant_or_active_href_count": unsafe_count,
        "draft_instruction_banner_found": bool(DRAFT_BANNER.search(text)),
        "possible_remote_1px_image_count": parser.tiny_images,
        "actual_received_message_verified": False,
        "postal_ownership_verified": False,
        "unsubscribe_function_verified": False,
        "eligible_audience_verified": False,
        "merchant_email_permission_verified": False,
        "final_founder_send_approval": False,
        "release": "HOLD_UNSENT_AND_MERCHANT" if commercial else "HOLD_UNSENT"
    }
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read private EML locally; only emit redacted status.")
    parser.add_argument("eml", type=Path)
    parser.add_argument("--issue", required=True, type=int, choices=range(1, 7))
    parser.add_argument("--expected-subject")
    parser.add_argument("--expected-guide")
    args = parser.parse_args(argv)
    report = inspect_eml(args.eml.read_bytes(), args.issue,
                         args.expected_subject, args.expected_guide,
                         os.environ.get("FV_DISPATCH_MAILING_ADDRESS"))
    print(json.dumps(report, indent=2))
    return 0  # Parser success is NEVER authorization to publish or send.

if __name__ == "__main__":
    raise SystemExit(main())
