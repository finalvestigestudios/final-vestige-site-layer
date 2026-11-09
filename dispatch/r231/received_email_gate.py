"""Privacy-preserving inspection of an ALREADY RECEIVED, authorized Jetpack EML.

This program cannot send mail, confirm a subscription, certify a postal address,
verify a functioning opt-out, approve merchants or clear a campaign for release.
No addresses, mailbox content, link tokens or recipient identifiers are emitted.
"""
from __future__ import annotations

from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
import re

MAX_EML_BYTES = 2_000_000
HOLD = "HOLD_UNSENT_REVIEW_ONLY"


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.suppressed = 0
        self.words = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"style", "script", "head"}:
            self.suppressed += 1
        if tag == "a" and not self.suppressed:
            self.links.append((attrs.get("href") or "", attrs.get("aria-label") or ""))

    def handle_endtag(self, tag):
        if tag in {"style", "script", "head"}:
            self.suppressed = max(0, self.suppressed - 1)

    def handle_data(self, data):
        if not self.suppressed:
            self.words.append(data)


def _normalized(value):
    return " ".join(re.sub(r"\s+", " ", value or "").casefold().split())


def _url_ok(value):
    value = (value or "").strip()
    return bool(re.match(r"^https://[^\s<>\x00-\x1f]+$", value, re.I))


def inspect_received_email(raw: bytes, *, expected_subject: str = "",
                           verified_publisher_address: str = "") -> dict:
    """Return release-blocking booleans only; never materialize provider identities.

    A postal address string is an external attested INPUT, not verification: this
    function only determines whether that exact publisher string is rendered.
    An EML fixture or correctly shaped header cannot demonstrate delivered mail.
    """
    result = {"state": HOLD, "proof_level": "OFFLINE_BYTES_ONLY",
              "checks": {}, "blockers": [], "manual_checks_required": [
                  "Actual received Jetpack message and independent receipt provenance",
                  "Publisher ownership and validity of the postal address",
                  "Live unsubscribe operation and opt-out suppression after request",
                  "Provider-confirmed recipient eligibility and marketing consent",
                  "Affiliate acceptance, email rights, published guides and valid issued links",
                  "Merchant checkout/refunds and independently settled paid conversion",
                  "Founder final campaign, audience, content and send authorization"]}
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_EML_BYTES:
        result["blockers"].append("EML_MISSING_OR_EXCEEDS_LIMIT")
        return result
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        result["blockers"].append("UNPARSEABLE_EML")
        return result

    checks = result["checks"]
    checks["has_sender_header"] = bool(msg.get("From"))
    checks["has_subject_header"] = bool(msg.get("Subject"))
    checks["has_message_id"] = bool(msg.get("Message-ID"))
    checks["subject_exactly_matches_reviewed_copy"] = bool(
        expected_subject and _normalized(str(msg.get("Subject", ""))) == _normalized(expected_subject))
    checks["has_date_header"] = bool(msg.get("Date"))
    checks["contains_header_defects"] = bool(msg.defects)

    plain_parts, html_parts = [], []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        kind = part.get_content_type()
        if kind not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
            if not isinstance(content, str):
                continue
        except Exception:
            continue
        (plain_parts if kind == "text/plain" else html_parts).append(content)

    checks["has_text_plain"] = bool(plain_parts)
    checks["has_text_html"] = bool(html_parts)
    parsed_html = _VisibleText()
    for item in html_parts:
        try:
            parsed_html.feed(item)
        except Exception:
            pass
    plain = "\n".join(plain_parts)
    visible = " ".join(parsed_html.words)
    combined = _normalized(plain + " " + visible)
    address = _normalized(verified_publisher_address)
    checks["verified_publisher_address_visible"] = bool(
        len(address) >= 16 and "[[" not in address and "automattic" not in address
        and address in combined)
    checks["has_unsubscribe_word_in_visible_copy"] = "unsubscribe" in combined or "opt out" in combined
    links = re.findall(r"https://[^\s<>\]\[\"']+", plain, re.I)
    html_unsub = [href for href, label in parsed_html.links
                  if _url_ok(href) and ("unsubscribe" in (href + " " + label).lower()
                                             or "opt-out" in (href + " " + label).lower())]
    plain_unsub = [link for link in links if "unsubscribe" in link.lower() or "opt-out" in link.lower()]
    checks["has_syntactically_valid_body_optout_url"] = bool(html_unsub or plain_unsub)
    header = str(msg.get("List-Unsubscribe", ""))
    checks["has_list_unsubscribe_header"] = bool(re.search(
        r"<(?:(?:https://[^<>\s]+)|(?:mailto:[^<>\s@]+@[^<>\s@]+))>", header, re.I))
    checks["has_one_click_header_claim"] = "List-Unsubscribe-Post" in msg
    checks["syntactic_optout_candidate"] = bool(
        checks["has_syntactically_valid_body_optout_url"] or
        checks["has_list_unsubscribe_header"])
    checks["no_placeholder_tokens_in_visible_copy"] = not any(
        token in combined for token in ("[[valid_postal_address_required]]",
                                  "[[jetpack_unsubscribe_link_must_be_verified]]", "[[approved_"))

    for key in ("has_sender_header", "has_subject_header", "has_message_id", "has_date_header",
                "subject_exactly_matches_reviewed_copy", "has_text_plain", "has_text_html",
                "verified_publisher_address_visible", "syntactic_optout_candidate",
                "no_placeholder_tokens_in_visible_copy"):
        if not checks[key]:
            result["blockers"].append(key.upper() + "_FAILED")
    if checks["contains_header_defects"]:
        result["blockers"].append("HEADER_DEFECT_REQUIRES_REVIEW")
    # Never output the sender address, recipient, URL, HTML, message ID, body,
    # subscription record, price or submitted expected physical address.
    return result
