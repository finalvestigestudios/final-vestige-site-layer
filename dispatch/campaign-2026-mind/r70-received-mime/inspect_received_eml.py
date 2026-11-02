#!/usr/bin/env python3
"""Read-only, privacy-minimising analysis of a founder-authorized received .eml.

This is NOT a send tool, mail client, inbox connector, opt-out tester or
legal certification. It deliberately returns no address, full header,
message body, URL, unsubscribe token or source-file hash.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

MAX_BYTES = 4 * 1024 * 1024
MERCHANT_DOMAINS = ("inspire3.com", "zen12.com", "hypnosislive.com")
DISCLOSURE = re.compile(r"\b(?:final\s+vestige\s+)?may\s+earn\s+(?:a\s+)?commission\b", re.I)
OPT_OUT = re.compile(r"\bunsubscribe\b|\bopt[\s-]?out\b", re.I)
HOLD = "HOLD_UNSENT"

def normal(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text).lower()).strip()

def valid_url(value: str) -> bool:
    """We count URL syntax only; live reachability is NEVER claimed."""
    try:
        p = urlsplit(value.strip())
        return p.scheme.lower() == "https" and bool(p.hostname) and not p.username and not p.password
    except (ValueError, AttributeError):
        return False

def merchant_url(value: str) -> bool:
    if not valid_url(value):
        return False
    host = (urlsplit(value).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in MERCHANT_DOMAINS)

class VisibleHTML(HTMLParser):
    """Extract visible body text and link *properties*, never raw href in results."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_label: list[str] = []
        self.skip_depth = 0
        self.html_lang_en = False
        self.has_interactive_or_script = False
        self.remote_image = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        props = dict(attrs)
        if tag == "html" and (props.get("lang") or "").lower().startswith("en"):
            self.html_lang_en = True
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1
        if tag in ("script", "form", "iframe", "object", "embed"):
            self.has_interactive_or_script = True
        if any(k.lower().startswith("on") for k, _ in attrs):
            self.has_interactive_or_script = True
        if tag == "img" and str(props.get("src") or "").startswith(("https:", "http:")):
            self.remote_image = True
        if tag == "a":
            self._current_href = str(props.get("href") or "")
            self._current_label = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("script", "style", "noscript") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "a" and self._current_href is not None:
            self.links.append((self._current_href, normal(" ".join(self._current_label))))
            self._current_href = None
            self._current_label = []

    def handle_data(self, data):
        if not self.skip_depth:
            self.fragments.append(data)
            if self._current_href is not None:
                self._current_label.append(data)

    @property
    def visible_text(self) -> str:
        return " ".join(self.fragments)

def part_text(part) -> str:
    """Decode safely; errors are swallowed without outputting sensitive bytes."""
    try:
        content = part.get_content()
        if isinstance(content, str):
            return content
        if isinstance(content, bytes):
            return content.decode("utf-8", "replace")
    except (LookupError, UnicodeError, ValueError, TypeError):
        pass
    payload = part.get_payload(decode=True)
    if isinstance(payload, bytes):
        return payload.decode("utf-8", "replace")
    return ""

def audit_bytes(
    raw: bytes,
    *,
    edition: str,
    expected_subject: str | None = None,
    publisher_postal_address: str | None = None,
) -> dict:
    if edition not in ("01", "02", "03", "04", "05", "06"):
        raise ValueError("Edition must be a two-digit pilot issue from 01 through 06")
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError("A nonempty .eml smaller than 4 MiB is required")
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception as exc:
        raise ValueError("Could not parse the supplied message") from None

    plain_parts, html_parts = [], []
    for p in msg.walk():
        if p.is_multipart():
            continue
        if p.get_content_disposition() == "attachment":
            continue
        if p.get_content_type() == "text/plain":
            plain_parts.append(part_text(p))
        elif p.get_content_type() == "text/html":
            html_parts.append(part_text(p))
    plain = "\n".join(plain_parts)
    html = "\n".join(html_parts)
    parsed = VisibleHTML()
    if html:
        try:
            parsed.feed(html)
            parsed.close()
        except Exception:
            # Broken markup is a failure of safe preview, not evidence of delivery.
            parsed.has_interactive_or_script = True
    visible = plain if plain.strip() else parsed.visible_text
    all_visible = normal(plain + " " + parsed.visible_text)
    text_55 = " ".join(visible.split()[:55])

    # Do not expose raw headers, addresses, names, links, body or tokens.
    subject = str(msg.get("Subject") or "")
    sender = str(msg.get("From") or "").lower()
    header_unsub = str(msg.get("List-Unsubscribe") or "")
    header_unsub_post = str(msg.get("List-Unsubscribe-Post") or "")
    unsub_anchor = any(OPT_OUT.search(label) and valid_url(href) for href, label in parsed.links)
    plain_unsub = bool(OPT_OUT.search(plain)) and bool(re.search(
        r"https://[^\s<>\"]+", plain, flags=re.I
    ))
    merchant_link = any(merchant_url(href) for href, _ in parsed.links)
    if not merchant_link:
        merchant_link = any(merchant_url(u) for u in re.findall(r"https://[^\s<>\"]+", plain))
    supplied_address = bool(publisher_postal_address and publisher_postal_address.strip())
    postal_match = normal(publisher_postal_address) in all_visible if supplied_address else None
    is_commercial = edition in ("03", "05")
    possible_early_disclosure = bool(DISCLOSURE.search(text_55)) if is_commercial else None

    signals = {
        "subject_present": bool(subject.strip()),
        "subject_matches_selected_copy": (
            subject.strip() == expected_subject.strip()
            if expected_subject is not None else None
        ),
        "wordpress_sending_domain_heuristic": "wordpress.com" in sender,
        "plain_text_part_present": bool(plain.strip()),
        "html_part_present": bool(html.strip()),
        "visible_body_present": bool(visible.strip()),
        "html_lang_en_present": parsed.html_lang_en if html else None,
        "html_interactive_markup_detected": parsed.has_interactive_or_script,
        "remote_image_present": parsed.remote_image if html else None,
        "html_links_count": len(parsed.links),
        "unsubscribe_labeled_https_link_present": unsub_anchor,
        "plain_text_optout_and_https_present": plain_unsub,
        "list_unsubscribe_header_present": bool(header_unsub.strip()),
        "list_unsubscribe_post_one_click_declared": (
            "list-unsubscribe=one-click" in header_unsub_post.lower()
        ),
        "postal_text_matches_private_publisher_reference": postal_match,
        "commercial_disclosure_within_first_55_visible_words": possible_early_disclosure,
        "merchant_domain_link_detected": merchant_link,
        "hard_stop_placeholder_detected": bool(re.search(
            r"\[\[(?:VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE|APPROVED_)",
            plain + html, flags=re.I
        )),
    }

    blockers = [
        "RECEIPT_PROVENANCE_NOT_AUTHENTICATED_BY_LOCAL_PARSER",
        "FOUNDER_FINAL_CAMPAIGN_SEND_APPROVAL_NOT_EVIDENCED",
        "RECIPIENT_CONSENT_AND_ELIGIBLE_COHORT_NOT_EVIDENCED",
        "POSTAL_ADDRESS_OWNERSHIP_AND_LEGAL_VALIDITY_REQUIRE_HUMAN_PROOF",
        "OPT_OUT_REACHABILITY_AND_SUCCESS_REQUIRE_AUTHORIZED_HUMAN_TEST",
        "WORDPRESS_EXCERPT_AND_PREHEADER_REQUIRE_NATIVE_INBOX_REVIEW",
    ]
    if postal_match is not True:
        blockers.append("PUBLISHER_ADDRESS_NOT_MATCHED_IN_RECEIVED_BODY")
    if not (unsub_anchor or plain_unsub):
        blockers.append("NO_VISIBLE_OPT_OUT_DESTINATION_DETECTED")
    if not (subject.strip() and visible.strip()):
        blockers.append("SUBJECT_OR_VISIBLE_BODY_MISSING")
    if expected_subject is None or (subject.strip() != expected_subject.strip()):
        blockers.append("FINAL_SUBJECT_NOT_VERIFIED")
    if is_commercial:
        blockers.extend([
            "MERCHANT_EMAIL_CHANNEL_ACCEPTANCE_NOT_VERIFIED",
            "LIVE_APPROVED_GUIDE_AND_AFFILIATE_LINK_NOT_VERIFIED",
            "MERCHANT_CURRENT_TERMS_AND_CREATIVE_RIGHTS_NOT_VERIFIED",
        ])
        if not possible_early_disclosure:
            blockers.append("DISCLOSURE_NOT_DETECTED_IN_FIRST_55_WORDS")
        if merchant_link:
            blockers.append("MERCHANT_DOMAIN_LINK_REQUIRES_MANUAL_APPROVAL")
    if signals["hard_stop_placeholder_detected"]:
        blockers.append("UNRESOLVED_HARD_STOP_PLACEHOLDER_IN_BODY")
    if parsed.has_interactive_or_script:
        blockers.append("UNSAFE_OR_UNEXPECTED_HTML_ELEMENTS")

    return {
        "schema": "fv-dispatch-received-eml-readonly-v1",
        "edition": edition,
        "evidence_level": "UNAUTHENTICATED_LOCAL_MIME_INSPECTION_ONLY",
        "synthetic_or_real_not_determined": True,
        "signals": signals,
        "blockers": blockers,
        "release_status": HOLD,
        "send_allowed": False,
        "message_sent_by_this_tool": False,
        "unsubscribe_executed_by_this_tool": False,
        "private_data_echoed": False,
    }

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline redacted Jetpack .eml inspection; NEVER authorizes a send")
    parser.add_argument("--eml", required=True, type=Path, help="PRIVATE received .eml file (not uploaded to GitHub)")
    parser.add_argument("--edition", required=True, choices=["01", "02", "03", "04", "05", "06"])
    parser.add_argument("--subject-file", type=Path, help="Privately selected subject on a single line")
    parser.add_argument("--publisher-postal-file", type=Path, help="Private verified business address text")
    args = parser.parse_args(argv)
    # Never include private paths or their content in stdout/stderr.
    try:
        subject = args.subject_file.read_text(encoding="utf-8").strip() if args.subject_file else None
        postal = args.publisher_postal_file.read_text(encoding="utf-8").strip() if args.publisher_postal_file else None
        if not args.eml.is_file() or args.eml.is_symlink():
            raise ValueError("Input is not a regular local file")
        raw = args.eml.read_bytes()
        result = audit_bytes(raw, edition=args.edition, expected_subject=subject,
                             publisher_postal_address=postal)
    except (OSError, ValueError):
        print(json.dumps({"release_status": HOLD, "send_allowed": False,
                          "error": "INPUT_UNAVAILABLE_OR_INVALID_NO_SENSITIVE_DETAILS"}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
