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
    r"\b(?:Final\s+Vestige|we)\b.{0,100}\b(?:may|might)\s+"
    r"(?:earn|receive)\s+(?:a\s+)?commission\b", re.I | re.S
)
PLACEHOLDER = re.compile(r"\[\[[^\]]+\]\]")
URL = re.compile(r"https?://[^\s<>]+", re.I)


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def domain_is_seller(value: str) -> bool:
    try:
        host = (urlsplit(value).hostname or "").casefold().rstrip(".")
    except ValueError:
        return False
    return any(host == d or host.endswith("." + d) for d in SELLER_DOMAINS)


def safe_url_scheme(href: str) -> str:
    """Untrusted MIME links must never crash a privacy-safe inspector."""
    try:
        return urlsplit(href).scheme.casefold()
    except ValueError:
        return ""


class VisibleHTML(HTMLParser):
    """Conservative approximation of visible HTML; NOT an email-client renderer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.words: list[str] = []
        self.links: list[str] = []  # legacy visible href inventory
        self.visible_anchors: list[dict] = []  # href plus actual visible anchor text
        self._active_anchor: dict | None = None
        self.all_links: list[str] = []  # hidden merchant links still count as routes
        self.remote_images = 0
        self.unsafe_links = 0
        self.malformed_links = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        style = a.get("style") or ""
        css = re.sub(r"\s+", "", style.casefold())
        # CSS invisibility is approximate: a genuine mail-client visual preview
        # is still necessary. Do not certify a financially important disclosure.
        zero_opacity = re.search(r"(?:^|;)opacity:0(?:\.0+)?(?:;|$)", css) is not None
        zero_font = re.search(r"(?:^|;)font-size:0(?:px|pt|em|rem|%|;|$)", css) is not None
        self_hidden = (
            tag in HIDDEN or "hidden" in a
            or (a.get("aria-hidden") or "").strip().casefold() == "true"
            or "display:none" in css or "visibility:hidden" in css
            or zero_opacity or zero_font
        )
        hidden = self_hidden or (self.stack[-1][1] if self.stack else False)
        # Clickable/navigation-bearing HTML is not limited to <a>. Preserve
        # destinations privately as fixed counts only, never in the report.
        routes = {
            "a": a.get("href") or "",
            "area": a.get("href") or "",
            "form": a.get("action") or "",
            "button": a.get("formaction") or "",
            "input": a.get("formaction") or "",
            "iframe": a.get("src") or "",
            "object": a.get("data") or "",
        }
        href = routes.get(tag, "")
        if tag == "meta" and (a.get("http-equiv") or "").casefold() == "refresh":
            found = re.search(r"(?:^|;)\s*url\s*=\s*['\"]?([^;'\"]+)", a.get("content") or "", re.I)
            href = found.group(1).strip() if found else ""
        if href:
            self.all_links.append(href)
            try:
                scheme = urlsplit(href).scheme.casefold()
            except ValueError:
                self.malformed_links += 1
                scheme = ""
            if scheme in {"javascript", "file", "data"}:
                self.unsafe_links += 1
        if tag == "a" and not hidden:
            self.links.append(href)
            self._active_anchor = {"href": href, "text": []}
            self.visible_anchors.append(self._active_anchor)
        if tag == "img" and (a.get("src") or "").lower().startswith(("http://", "https://")):
            self.remote_images += 1
        # Remote CSS backgrounds may trigger fetches in some email clients.
        if re.search(r"url\(\s*['\"]?https?://", style, re.I):
            self.remote_images += 1
        if tag not in VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._active_anchor = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        # A hidden <style> element can still request remote images when read
        # by a mail client. This is a risk indicator, not proof of retrieval.
        if self.stack and self.stack[-1][0] == "style":
            self.remote_images += len(re.findall(r"url\(\s*['\"]?https?://", data, re.I))
        if not self.stack or not self.stack[-1][1]:
            self.words.append(data)
            if self._active_anchor is not None:
                self._active_anchor["text"].append(data)

    @property
    def text(self) -> str:
        return " ".join(self.words)


def _reader_body_parts(part: object, omitted: dict):
    """Analyze reader-facing top-level MIME content, not attached/forwarded mail.

    email.message.walk() descends into attached message/rfc822 objects; checking
    only the leaf's disposition can falsely count a forwarded disclosure as
    a disclosure present in the actual newsletter.
    """
    if part.get_content_disposition() == "attachment" or part.get_filename():
        omitted["attachments"] += 1
        return
    if part.get_content_type() == "message/rfc822":
        omitted["encapsulated"] += 1
        return
    if part.is_multipart():
        for child in part.iter_parts():
            yield from _reader_body_parts(child, omitted)
        return
    if part.get_content_type() in {"text/plain", "text/html"}:
        yield part


def parse_parts(raw: bytes) -> tuple[object, str, str, VisibleHTML]:
    if len(raw) > MAX_BYTES:
        raise ValueError("MESSAGE_TOO_LARGE")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    plain: list[str] = []
    html: list[str] = []
    omitted = {"attachments": 0, "encapsulated": 0}
    for part in _reader_body_parts(message, omitted):
        try:
            content = part.get_content()
        except (UnicodeError, LookupError, ValueError):
            continue
        if not isinstance(content, str):
            continue
        (html if part.get_content_type() == "text/html" else plain).append(content)
    scan = VisibleHTML()
    scan.plain_body_part_count = len(plain)
    scan.html_body_part_count = len(html)
    scan.attachment_count = omitted["attachments"]
    scan.encapsulated_message_count = omitted["encapsulated"]
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
    # Neither the presence of a List-Unsubscribe header nor a plausible
    # visible link proves functional opt-out; reject obvious unrelated URLs.
    unsub_paths = re.compile(r"unsub|opt[._-]?out|subscription|follow", re.I)
    header_candidate = any(
        safe_url_scheme(href) in {"https", "mailto"}
        and not domain_is_seller(href)
        and bool(unsub_paths.search(href))
        for href in re.findall(r"<([^<>]+)>", unsub_header)
    )
    visible_unsub_anchor = any(
        safe_url_scheme(anchor["href"]) == "https"
        and not domain_is_seller(anchor["href"])
        and bool(unsub_paths.search(anchor["href"]))
        and bool(re.search(r"\bunsubscribe\b|\bopt[ -]?out\b",
                           normalize(" ".join(anchor["text"])), re.I))
        for anchor in parsed.visible_anchors
    )
    # Report the real MIME alternatives separately: a beautiful HTML
    # disclosure cannot repair an undisclosed plaintext alternative.
    plain_early_disclosure = bool(DISCLOSURE.search(" ".join(plain.split()[:85])))
    html_early_disclosure = bool(DISCLOSURE.search(" ".join(parsed.text.split()[:85])))
    disclosure_parity = ((not plain.strip() or plain_early_disclosure)
                         and (not html.strip() or html_early_disclosure)
                         and parsed.plain_body_part_count <= 1
                         and parsed.html_body_part_count <= 1)
    links = set(parsed.all_links)
    links.update(URL.findall(plain))
    sellers = sum(1 for link in links if domain_is_seller(link))
    commercial = edition.get("number") in {3, 5}
    duplicate_headers = sum(
        max(0, len(message.get_all(name, [])) - 1)
        for name in ("From", "Subject", "List-Unsubscribe")
    )
    observed = {
        "schema_version": 1,
        "issue": edition["number"],
        "sample_origin_declared_by_operator": origin,
        "source_is_received_message_independently_attested": False,
        "has_text_plain": bool(plain.strip()),
        "has_text_html": bool(html.strip()),
        "top_level_text_plain_part_count": parsed.plain_body_part_count,
        "top_level_text_html_part_count": parsed.html_body_part_count,
        "ignored_attachment_or_named_part_count": parsed.attachment_count,
        "ignored_inline_forwarded_message_count": parsed.encapsulated_message_count,
        "duplicate_relevant_header_count": duplicate_headers,
        "subject_equals_canonical": subject == normalize(edition.get("subject", "")),
        "from_display_equals_final_vestige": sender_display == "final vestige",
        "commercial_slot": commercial,
        "disclosure_in_visible_first_85_words": bool(DISCLOSURE.search(prefix)),
        "disclosure_in_visible_body": bool(DISCLOSURE.search(body)),
        "disclosure_in_text_plain_first_85_words": plain_early_disclosure,
        "disclosure_in_text_html_first_85_words": html_early_disclosure,
        "commercial_disclosure_parity_across_mime_alternatives": (
            disclosure_parity if commercial else True
        ),
        "postal_exact_match_to_local_private_value": postal_seen,
        "list_unsubscribe_header_candidate": header_candidate,
        "visible_unsubscribe_link_candidate": visible_unsub_anchor,
        "unsubscription_functionally_verified": False,
        "remote_image_count": parsed.remote_images,
        "unsafe_link_scheme_count": parsed.unsafe_links,
        "malformed_link_count": parsed.malformed_links,
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
    if not plain.strip() and not html.strip():
        holds.append("NO_READABLE_TOP_LEVEL_MESSAGE_BODY")
    if parsed.attachment_count:
        holds.append("ATTACHMENT_PRESENT_HUMAN_REVIEW")
    if parsed.encapsulated_message_count:
        holds.append("INLINE_FORWARDED_MESSAGE_IGNORED")
    if parsed.plain_body_part_count > 1 or parsed.html_body_part_count > 1:
        holds.append("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS")
    if duplicate_headers:
        holds.append("AMBIGUOUS_DUPLICATE_MESSAGE_HEADERS")
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
    if observed["malformed_link_count"]:
        holds.append("MALFORMED_LINK_HUMAN_REVIEW")
    if observed["unreplaced_placeholder_in_visible_body"]:
        holds.append("UNREPLACED_RELEASE_PLACEHOLDER")
    if commercial:
        holds.extend(["HOLD_MERCHANT_NAMED_SKU_EMAIL_RIGHTS_UNVERIFIED",
                      "HOLD_MERCHANT_GUIDE_AND_TRACKING_UNVERIFIED"])
        if not observed["disclosure_in_visible_first_85_words"]:
            holds.append("EARLY_COMMERCIAL_DISCLOSURE_MISSING")
        if plain.strip() and html.strip() and not disclosure_parity:
            holds.append("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES")
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
