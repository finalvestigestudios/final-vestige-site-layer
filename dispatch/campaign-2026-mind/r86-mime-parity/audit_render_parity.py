#!/usr/bin/env python3
"""R86: fail-closed, offline MIME parity review for an *authorized* received Jetpack email.

This is not a sender, consent check, unsubscribe clicker, legal signoff, or
substitute for checking a real inbox. Never commit actual .eml or private values.
It supplements, rather than modifies, the R85 inspection utility. All decisions
remain HOLD. Output contains only fixed categorical observations, no PII.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

MAX_BYTES = 2_000_000
DISCLOSURES = (
    "may earn a commission",
    "may receive a commission",
    "might earn a commission",
    "we may receive a commission",
    "we may earn a commission",
)
# Known conservative *screening* thresholds, not proof of an email-client preview.
FIRST_CHARS = 350
NEAR_CTA_CHARS = 220
VOID = {"img", "br", "hr", "input", "meta", "link", "source", "wbr"}


def norm(text: str) -> str:
    return " ".join(text.casefold().split())


def strict_url(url: str) -> str:
    try:
        u = urlsplit(url.strip())
        if (u.scheme != "https" or not u.hostname or u.username or u.password
                or u.query or u.fragment or u.port):
            return ""
        return "https://" + u.hostname.lower() + u.path.rstrip("/")
    except ValueError:
        return ""


class RenderedHTML(HTMLParser):
    """Conservatively inspect text and links visible in simple inline HTML."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.segments = []
        self.links = []
        self.active = []

    def invisible(self):
        return any(hidden for _, hidden in self.stack)

    def pos(self):
        return len("".join(self.segments))

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        css = re.sub(r"\s+", "", a.get("style", "").casefold())
        hidden = (self.invisible() or tag in ("head", "script", "style", "template")
                  or "hidden" in a or a.get("aria-hidden", "").lower() == "true"
                  or "display:none" in css or "visibility:hidden" in css
                  or "opacity:0" in css)
        if tag not in VOID:
            self.stack.append((tag, hidden))
        if hidden:
            return
        if tag in ("div", "p", "li", "tr", "br", "td", "h1", "h2", "h3"):
            self.segments.append(" ")
        if tag == "a":
            link = {"href": a.get("href", ""), "position": self.pos(), "label": ""}
            self.links.append(link)
            self.active.append(link)

    def handle_data(self, data):
        if self.invisible():
            return
        self.segments.append(data)
        for link in self.active:
            link["label"] += data

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a" and self.active:
            self.active.pop()
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def text(self):
        return "".join(self.segments)


def get_parts(message):
    plain, html = [], []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        kind = part.get_content_type()
        if kind not in ("text/plain", "text/html"):
            continue
        try:
            value = part.get_content()
        except (UnicodeError, ValueError, LookupError):
            value = part.get_payload(decode=True).decode("utf-8", "replace")
        if isinstance(value, str):
            (plain if kind == "text/plain" else html).append(value)
    return plain, html


def first_disclosure(text: str):
    text = text.casefold()
    positions = [text.find(phrase) for phrase in DISCLOSURES]
    positions = [pos for pos in positions if pos >= 0]
    return min(positions) if positions else -1


def near_disclosure(text: str, cta_positions: list[int]):
    disclosure = first_disclosure(text)
    if disclosure < 0:
        return False
    return any(0 <= cta - disclosure <= NEAR_CTA_CHARS for cta in cta_positions)


def url_positions_in_plain(text: str, expected: str):
    return [m.start() for m in re.finditer(r"https://[^\s<>'\"]+", text, re.I)
            if strict_url(m.group(0).rstrip(".,);")) == expected]


def plain_unsubscribe(text: str):
    # Keyword+URL are indicators, not evidence of a functioning opt-out.
    return bool(re.search(r"\bunsubscribe\b", text, re.I)
                and re.search(r"https://[^\s<>\"']+", text, re.I))


def html_unsubscribe(parser: RenderedHTML):
    return any("unsubscribe" in norm(x["label"])
               and bool(strict_url(x["href"])) for x in parser.links)


def audit_bytes(raw: bytes, *, expected_subject: str, expected_cta: str,
                commercial: bool, postal_address: str | None = None):
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError("Input email invalid or too large")
    if not expected_subject or not expected_subject.strip():
        raise ValueError("Expected subject missing")
    target = strict_url(expected_cta)
    if not target or urlsplit(target).hostname not in ("finalvestige.com", "www.finalvestige.com"):
        raise ValueError("Expected CTA must be a first-party exact HTTPS page")
    if postal_address is not None and len(postal_address.strip()) < 8:
        raise ValueError("Postal comparison value insufficient")
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    if not msg.get("From") or not msg.get("Subject"):
        raise ValueError("Not a complete message")
    plain_parts, html_parts = get_parts(msg)
    if not plain_parts and not html_parts:
        raise ValueError("No inspectable HTML/plaintext body")
    # Multiple alternative parts are examined together, but a real reviewer
    # must establish which rendition the client displays.
    plain = "\n".join(plain_parts)
    parser = RenderedHTML()
    for fragment in html_parts:
        parser.feed(fragment)
    html_text = parser.text()
    html_positions = [x["position"] for x in parser.links
                      if strict_url(x["href"]) == target and norm(x["label"])]
    plain_positions = url_positions_in_plain(plain, target)
    postal = norm(postal_address or "")
    plain_has_postal = bool(plain_parts and postal and postal in norm(plain))
    html_has_postal = bool(html_parts and postal and postal in norm(html_text))
    plain_disc_first = first_disclosure(plain) >= 0 and first_disclosure(plain) < FIRST_CHARS
    html_disc_first = first_disclosure(html_text) >= 0 and first_disclosure(html_text) < FIRST_CHARS
    checks = {
        "subject_matches": norm(str(msg.get("Subject"))) == norm(expected_subject),
        "html_present": bool(html_parts),
        "plain_present": bool(plain_parts),
        "html_expected_cta": bool(html_positions),
        "plain_expected_cta": bool(plain_positions),
        "html_commission_visible_early": html_disc_first if commercial else None,
        "plain_commission_visible_early": plain_disc_first if commercial else None,
        "html_disclosure_precedes_and_near_cta": (
            near_disclosure(html_text, html_positions) if commercial else None),
        "plain_disclosure_precedes_and_near_cta": (
            near_disclosure(plain, plain_positions) if commercial else None),
        "html_publisher_postal_string": html_has_postal,
        "plain_publisher_postal_string": plain_has_postal,
        "html_unsubscribe_indicator": html_unsubscribe(parser),
        "plain_unsubscribe_indicator": plain_unsubscribe(plain),
        "list_unsubscribe_header_indicator": bool(msg.get("List-Unsubscribe")),
    }
    flags = []
    if not checks["subject_matches"]:
        flags.append("SUBJECT_MISMATCH")
    if not (checks["html_present"] and checks["plain_present"]):
        flags.append("MIME_PART_MISSING_OR_UNOBSERVED")
    if not (checks["html_expected_cta"] and checks["plain_expected_cta"]):
        flags.append("CTA_NOT_VISIBLE_IN_BOTH_RENDITIONS")
    if commercial and not all((
        checks["html_commission_visible_early"],
        checks["plain_commission_visible_early"],
        checks["html_disclosure_precedes_and_near_cta"],
        checks["plain_disclosure_precedes_and_near_cta"],
    )):
        flags.append("COMMERCIAL_DISCLOSURE_RENDER_PARITY_FAILED")
    if not (html_has_postal and plain_has_postal):
        flags.append("PUBLISHER_POSTAL_UNVERIFIED_IN_RENDITIONS")
    if not (checks["html_unsubscribe_indicator"] and checks["plain_unsubscribe_indicator"]):
        flags.append("UNSUBSCRIBE_INDICATOR_RENDER_PARITY_FAILED")
    return {
        "schema": "fv-dispatch-r86-render-parity-v1",
        "decision": "HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION",
        "checks": checks,
        "risk_flags": flags,
        "limitations": [
            "No delivered email was accessed or sent by this software",
            "HTML CSS stylesheets, client-specific rendering and hidden preheaders require real client review",
            "URL and header presence cannot prove unsubscribe functionality",
            "Postal string comparison cannot prove a lawfully controlled publisher address",
            "No audience, merchant, permission, sender or final founder approval is inferred",
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eml", type=Path, required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--cta", required=True)
    p.add_argument("--commercial", action="store_true")
    p.add_argument("--publisher-postal", default=None)
    opts = p.parse_args()
    report = audit_bytes(opts.eml.read_bytes(), expected_subject=opts.subject,
                         expected_cta=opts.cta, commercial=opts.commercial,
                         postal_address=opts.publisher_postal)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
