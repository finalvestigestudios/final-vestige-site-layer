"""Privacy-preserving, strictly read-only evidence triage of a Jetpack RFC 5322 message.

NO sending, fetching, WordPress mutations, uploads, links clicked, or subscriber exports.
Only structural observations are emitted; no addresses, bodies or unsubscribe tokens.
A passing structural check NEVER authorizes delivery or proves CAN-SPAM compliance.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 3_000_000
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
HIDDEN = {"head", "script", "style", "template", "title", "svg"}
SELLER_DOMAINS = {"zen12.com", "hypnosislive.com", "inspire3.com"}
DISCLOSURE = re.compile(
    r"\\b(?:Final\\s+Vestige|we)\\b.{0,100}\\b(?:may|might)\\s+"
    r"(?:earn|receive)\\s+(?:a\\s+)?commission\\b", re.I | re.S
)
PLACEHOLDER = re.compile(r"\\[\\[[^\\]]+\\]\\]")
URL = re.compile(r"https?://[^\\s<>\\\"']+", re.I)


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def domain_is_seller(value: str) -> bool:
    try:
        host = (urlsplit(value).hostname or "").casefold().rstrip(".")
    except ValueError:
        return False
    return any(host == d or host.endswith("." + d) for d in SELLER_DOMAINS)


class VisibleHTML(HTMLParser):
    """Conservative approximation of visible HTML; NOT an email-client renderer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.words: list[str] = []
        self.links: list[str] = []
        self.remote_images = 0
        self.unsafe_links = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        css = (a.get("style") or "").replace(" ", "").casefold()
        self_hidden = (
            tag in HIDDEN or "hidden" in a
            or (a.get("aria-hidden") or "").casefold() == "true"
            or "display:none" in css or "visibility:hidden" in css
        )
        hidden = self_hidden or (self.stack[-1][1] if self.stack else False)
        if not hidden and tag == "a":
            href = a.get("href") or ""
            self.links.append(href)
            if urlsplit(href).scheme.casefold() in {"javascript", "file", "data"}:
                self.unsafe_links += 1
        if not hidden and tag == "img":
            if (a.get("src") or "").lower().startswith(("http://", "https://")):
                self.remote_images += 1
        if tag not in VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if not self.stack or not self.stack[-1][1]:
            self.words.append(data)

    @property
    def text(self) -> str:
        return " ".join(self.words)


def parse_parts(raw: bytes) -> tuple[object, str, str, VisibleHTML]:
    if len(raw) > MAX_BYTES:
        raise ValueError("MESSAGE_TOO_LARGE")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    plain: list[str] = []
    html: list[str] = []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
        except (UnicodeError, LookupError, ValueError):
            continue
        if not isinstance(content, str):
            continue
        (html if part.get_content_type() == "text/html" else plain).append(content)
    scan = VisibleHTML()
    if html:
        scan.feed("\n".join(html))
        scan.close()
    return message, "\n".join(plain), "\n".join(html), scan


def inspect_bytes(raw: bytes, edition: dict, *, postal_address: str | None = None,
                  origin: str = "synthetic") -> dict:
    if origin not in {"synthetic", "received"}:
        raise ValueError("UNRECOGNIZED_ORIGIN")
    if edition.get("number") not in range(1, 7):
        raise ValueError("EDITION_NOT_IN_CAMPAIGN")
    message, plain, html, parsed = parse_parts(raw)
    body = parsed.text if html else plain
    prefix = " ".join(body.split()[:85])
    address = normalize(postal_address or "")
    safe_address = len(address) >= 8 and not PLACEHOLDER.search(address)
    postal_seen = bool(safe_address and address in normalize(body))
    subject = normalize(str(message.get("Subject", "")))
    sender_display = normalize(parseaddr(str(message.get("From", "")))[0])
    unsub_header = str(message.get("List-Unsubscribe", ""))
    header_candidate = bool(re.search(r"<(?:https://|mailto:)[^<>]+>", unsub_header, re.I))
    visible_unsub_anchor = any(
        urlsplit(href).scheme.casefold() == "https"
        for href in parsed.links
        if "unsubscribe" in href.casefold() or "follow" in href.casefold()
    ) and "unsubscribe" in normalize(body)
    links = set(parsed.links)
    links.update(URL.findall(plain))
    sellers = sum(1 for link in links if domain_is_seller(link))
    commercial = edition.get("number") in {3, 5}
    observed = {
        "schema_version": 1,
        "issue": edition["number"],
        "sample_origin_declared_by_operator": origin,
        "source_is_received_message_independently_attested": False,
        "has_text_plain": bool(plain.strip()),
        "has_text_html": bool(html.strip()),
        "subject_equals_canonical": subject == normalize(edition.get("subject", "")),
        "from_display_equals_final_vestige": sender_display == "final vestige",
        "commercial_slot": commercial,
        "disclosure_in_visible_first_85_words": bool(DISCLOSURE.search(prefix)),
        "disclosure_in_visible_body": bool(DISCLOSURE.search(body)),
        "postal_exact_match_to_local_private_value": postal_seen,
        "list_unsubscribe_header_candidate": header_candidate,
        "visible_unsubscribe_link_candidate": visible_unsub_anchor,
        "unsubscription_functionally_verified": False,
        "remote_image_count": parsed.remote_images,
        "unsafe_link_scheme_count": parsed.unsafe_links,
        "direct_seller_link_count": sellers,
        "unreplaced_placeholder_in_visible_body": bool(PLACEHOLDER.search(body)),
        "unique_consent_eligible_audience_verified": False,
        "merchant_email_permission_verified": False,
        "approved_first_party_product_guide_live": False,
        "founder_final_send_approval": False,
        "send_allowed": False,
        "legal_compliance_certified": False,
    }
    holds = [
        "FOUNDER_FINAL_SEND_APPROVAL_NOT_PRESENT",
        "DISTINCT_CONSENT_ELIGIBLE_AUDIENCE_UNVERIFIED",
        "POSTAL_AND_UNSUBSCRIBE_FUNCTION_REQUIRE_HUMAN_RECEIPT_QA",
    ]
    if origin == "synthetic":
        holds.append("NO_ACTUAL_RECEIVED_EMAIL_EVIDENCE")
    if not observed["subject_equals_canonical"]:
        holds.append("SUBJECT_MISMATCH")
    if not observed["from_display_equals_final_vestige"]:
        holds.append("SENDER_DISPLAY_MISMATCH")
    if not postal_seen:
        holds.append("VERIFIED_FINAL_VESTIGE_POSTAL_ADDRESS_NOT_PRESENT")
    if not (header_candidate or visible_unsub_anchor):
        holds.append("UNSUBSCRIBE_MARKUP_CANDIDATE_ABSENT")
    if observed["unsafe_link_scheme_count"]:
        holds.append("UNSAFE_LINK_SCHEME")
    if observed["unreplaced_placeholder_in_visible_body"]:
        holds.append("UNREPLACED_RELEASE_PLACEHOLDER")
    if commercial:
        holds.extend(["HOLD_MERCHANT_NAMED_SKU_EMAIL_RIGHTS_UNVERIFIED",
                      "HOLD_MERCHANT_GUIDE_AND_TRACKING_UNVERIFIED"])
        if not observed["disclosure_in_visible_first_85_words"]:
            holds.append("EARLY_COMMERCIAL_DISCLOSURE_MISSING")
        if sellers:
            holds.append("DIRECT_MERCHANT_LINK_BYPASSES_REVIEWED_GUIDE")
    observed["holds"] = holds
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only redacted Jetpack MIME triage.")
    parser.add_argument("--eml", required=True, type=Path,
                        help="Local .eml path. Its contents, name, and headers are NEVER echoed.")
    parser.add_argument("--issue", required=True, type=int, choices=range(1, 7))
    parser.add_argument("--source", choices=["synthetic", "received"], default="synthetic")
    parser.add_argument("--founder-authorized-read", action="store_true",
                        help="Required to inspect actual received-mail material.")
    args = parser.parse_args()
    if args.source == "received" and not args.founder_authorized_read:
        parser.error("received-mail inspection needs separate founder authorization")
    if args.eml.stat().st_size > MAX_BYTES:
        parser.error("message exceeds private local limit")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    edition = next(e for e in manifest["issues"] if e["number"] == args.issue)
    result = inspect_bytes(args.eml.read_bytes(), edition,
                           postal_address=os.environ.get("FV_POSTAL_ADDRESS"),
                           origin=args.source)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
