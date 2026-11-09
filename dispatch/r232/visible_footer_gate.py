"""Conservative, offline MIME footer QA layered on R231; NEVER a send authorization.

A false positive in R231 can occur when the publisher address and opt-out are
present solely in HTML that is hidden (or only in text/plain while the HTML
version lacks a footer). This module requires each visible channel independently.
It does not establish actual inbox appearance, legal validity or opt-out behavior.
"""
from __future__ import annotations

from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "r231"))
from received_email_gate import inspect_received_email, MAX_EML_BYTES

HOLD = "HOLD_UNSENT_REVIEW_ONLY"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SUPPRESS = {"script", "style", "head", "template", "noscript"}
NOTICE = re.compile(r"\b(?:unsubscribe|opt[\s-]?out|stop (?:receiving )?(?:marketing )?emails?)\b", re.I)


def norm(value: str) -> str:
    return " ".join(str(value or "").casefold().split())


def safe_https(href: str) -> bool:
    href = (href or "").strip()
    if re.search(r"[\s<>\x00-\x1f]", href):
        return False
    try:
        parts = urlsplit(href)
        return parts.scheme.lower() == "https" and bool(parts.hostname) and not (parts.username or parts.password)
    except ValueError:
        return False


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.text: list[str] = []
        self.link_candidates: list[dict] = []
        self.active_anchor: dict | None = None
        self.hidden_elements = 0

    def _hidden(self) -> bool:
        return bool(self.stack and self.stack[-1][1])

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        tag = tag.casefold()
        a = dict(attrs)
        style = re.sub(r"\s+", "", (a.get("style") or "").casefold())
        hidden = (self._hidden() or tag in SUPPRESS or "hidden" in a or
                  "inert" in a or (a.get("aria-hidden") or "").casefold() == "true" or
                  (tag == "input" and a.get("type") == "hidden") or
                  bool(re.search(r"(?:^|;)(?:display:none|visibility:hidden|opacity:0)(?:;|$)", style)))
        if hidden:
            self.hidden_elements += 1
        if tag == "a" and not hidden:
            if self.active_anchor is not None:
                self.link_candidates.append(self.active_anchor)
            self.active_anchor = {"href": a.get("href") or "", "label": a.get("aria-label") or ""}
        if tag not in VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str):
        tag = tag.casefold()
        if tag == "a" and self.active_anchor is not None:
            self.link_candidates.append(self.active_anchor)
            self.active_anchor = None
        for n in range(len(self.stack) - 1, -1, -1):
            if self.stack[n][0] == tag:
                del self.stack[n:]
                break

    def handle_data(self, data: str):
        if not self._hidden():
            self.text.append(data)
            if self.active_anchor is not None:
                self.active_anchor["label"] += " " + data


def inspect_footer_channels(raw: bytes, *, expected_subject: str = "",
                            verified_publisher_address: str = "") -> dict:
    """Private input, public booleans only. Always HOLD; never calls a network endpoint."""
    base = inspect_received_email(raw, expected_subject=expected_subject,
                                  verified_publisher_address=verified_publisher_address)
    report = {"state": HOLD, "proof_level": "OFFLINE_BYTES_ONLY",
              "checks": {"plaintext_address_present": False, "html_visible_address_present": False,
                         "plaintext_visible_optout": False, "html_visible_optout": False,
                         "html_has_hidden_elements": False,
                         "r231_technical_candidate": not bool(base["blockers"])},
              "blockers": [], "manual_checks_required": [
                  "Actual Jetpack received message provenance and visual inbox rendering",
                  "Publisher postal ownership/validity and authorized opt-out/suppression proof",
                  "Consent and actual recipient eligibility, merchant EMAIL rights and final founder approval"]}
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_EML_BYTES:
        report["blockers"].append("INVALID_EML")
        return report
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        report["blockers"].append("UNPARSEABLE_EML")
        return report
    plains: list[str] = []
    htmls: list[str] = []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        try:
            value = part.get_content()
        except Exception:
            continue
        if not isinstance(value, str):
            continue
        if part.get_content_type() == "text/plain":
            plains.append(value)
        elif part.get_content_type() == "text/html":
            htmls.append(value)
    plain = "\n".join(plains)
    reader = VisibleHTML()
    for h in htmls:
        reader.feed(h)
    visible = norm(" ".join(reader.text))
    address = norm(verified_publisher_address)
    address_attested = bool(len(address) >= 16 and "[[" not in address and "automattic" not in address)
    checks = report["checks"]
    checks["plaintext_address_present"] = address_attested and address in norm(plain)
    checks["html_visible_address_present"] = address_attested and address in visible
    checks["html_has_hidden_elements"] = reader.hidden_elements > 0
    checks["html_visible_optout"] = any(
        safe_https(l["href"]) and bool(NOTICE.search(l["label"]))
        for l in reader.link_candidates)
    # An isolated URL or an unsupported header alone cannot replace a visible
    # "Unsubscribe: HTTPS..." instruction in the plain-text alternative.
    checks["plaintext_visible_optout"] = any(
        NOTICE.search(line) and any(safe_https(u.rstrip(".,;")) for u in
                                    re.findall(r"https://[^\s<>\"']+", line, re.I))
        for line in plain.splitlines())
    for k in ("plaintext_address_present", "html_visible_address_present",
              "plaintext_visible_optout", "html_visible_optout", "r231_technical_candidate"):
        if not checks[k]:
            report["blockers"].append(k.upper() + "_NOT_PROVEN")
    return report
