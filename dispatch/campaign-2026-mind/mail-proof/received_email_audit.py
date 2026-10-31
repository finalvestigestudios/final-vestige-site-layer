"""Offline, read-only MIME audit for an *authorized* Jetpack test email.

Never sends, publishes, contacts, activates an offer, or stores raw message text.
It does not validate actual link functionality, opt-in, merchant rights, or CAN-SPAM
compliance. Those are separate human release gates. Stdlib only.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse

MAX_MIME_BYTES = 2_000_000
COMMERCIAL = {3, 5}
ISSUE_IDS = {1, 2, 3, 4, 5, 6}
DISCLOSURES = ("may earn a commission", "may receive a commission")
PROMOTIONAL_HOSTS = ("inspire3.com", "zen12.com", "hypnosislive.com", "brainwaveshots.com")


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


class VisibleHTML(HTMLParser):
    """Extract text and anchor destinations without executing HTML or fetching assets."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.visible: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.all_links: list[tuple[str, str]] = []
        self.link_prior_visible: list[str] = []
        self._elements: list[tuple[str, bool]] = []
        self._anchor_stack: list[dict] = []

    @staticmethod
    def _explicitly_hidden(tag: str, attrs: dict[str, str | None]) -> bool:
        # This is a conservative DOM-markup check, not computed CSS or a
        # screen-reader/browser certification. Hidden links remain in all_links
        # so a merchant destination can never disappear from a security scan.
        style = re.sub(r"\s+", "", (attrs.get("style") or "").lower())
        return (tag in ("script", "style", "head", "template", "noscript", "svg")
                or "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true"
                or bool(re.search(r"(?:^|;)(?:display:none|visibility:hidden|opacity:0|font-size:0(?:px|pt|em|rem|%|;|$)|color:transparent)(?:;|$)", style)))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        hidden = (any(flag for _, flag in self._elements)
                  or self._explicitly_hidden(tag, attributes))
        if tag == "a":
            self._anchor_stack.append({"href": attributes.get("href") or "", "text": [],
                                       "hidden": hidden,
                                       "preceding": " ".join(self.visible) if not hidden else ""})
        # HTML void elements must not trap subsequent content in a hidden parent.
        if tag not in ("area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"):
            self._elements.append((tag, hidden))

    def handle_endtag(self, tag: str):
        if tag == "a" and self._anchor_stack:
            anchor = self._anchor_stack.pop()
            pair = (" ".join(anchor["text"]), anchor["href"])
            self.all_links.append(pair)
            if not anchor["hidden"]:
                self.links.append(pair)
                self.link_prior_visible.append(anchor["preceding"])
        # Remove through the matching element. Conservatively retain an unmatched
        # hidden ancestor instead of allowing following text to be misread as visible.
        match = next((i for i in range(len(self._elements)-1, -1, -1)
                      if self._elements[i][0] == tag), None)
        if match is not None:
            del self._elements[match:]

    def handle_data(self, data: str):
        if any(flag for _, flag in self._elements):
            return
        self.visible.append(data)
        for anchor in self._anchor_stack:
            if not anchor["hidden"]:
                anchor["text"].append(data)


def parse_mime(raw: bytes) -> tuple[object, str, str, list[tuple[str, str]], list[tuple[str, str]], list[str]]:
    if len(raw) > MAX_MIME_BYTES:
        raise ValueError("MIME exceeds two-megabyte local audit limit")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html_text, links, all_links, before_links = [], [], [], [], []
    for part in message.walk():
        if part.get_content_maintype() != "text" or part.get_content_disposition() == "attachment":
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeError, ValueError) as error:
            raise ValueError("Cannot decode MIME text part") from error
        if isinstance(content, bytes):
            raise ValueError("Nontext MIME content in text part")
        if part.get_content_type() == "text/plain":
            plain.append(content)
        elif part.get_content_type() == "text/html":
            parser = VisibleHTML()
            parser.feed(content)
            parser.close()
            html_text.append(" ".join(parser.visible))
            links += parser.links
            all_links += parser.all_links
            before_links += parser.link_prior_visible
    return message, "\n".join(plain), "\n".join(html_text), links, all_links, before_links


def is_usable_optout(uri: str) -> bool:
    if not uri or any(ch in uri for ch in ("\r", "\n", "\x00")):
        return False
    parsed = urlparse(uri.strip())
    return bool((parsed.scheme in ("https", "http") and parsed.netloc) or
                (parsed.scheme == "mailto" and "@" in parsed.path))


def is_merchant_url(uri: str) -> bool:
    parsed = urlparse(uri.strip())
    host = (parsed.hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in PROMOTIONAL_HOSTS)


def audit_received(raw: bytes | None, *, issue: int, expected_subject: str,
                   expected_excerpt: str, expected_postal: str | None = None,
                   email_mode: str = "excerpt", full_body_marker: str = "",
                   expected_cta: str | None = None) -> dict:
    """Only safe states: HOLD/UNKNOWN/FAIL/PASS (individual checks), never 'send'."""
    if issue not in ISSUE_IDS:
        raise ValueError("edition must be 1–6")
    if email_mode not in ("excerpt", "full"):
        raise ValueError("email_mode must be excerpt or full")
    checks: dict[str, str] = {}
    if raw is None:
        return {"edition": issue, "status": "HOLD_NO_RECEIVED_EMAIL",
                "checks": {"authorized_received_test": "UNKNOWN"},
                "manual_gates": manual_gates(issue)}
    try:
        message, plain, html_text, links, all_links, before_links = parse_mime(raw)
    except (TypeError, ValueError) as error:
        return {"edition": issue, "status": "HOLD_INVALID_MIME",
                "checks": {"mime_decode": "FAIL"},
                "problem_codes": ["MIME_UNREADABLE"], "manual_gates": manual_gates(issue)}
    checks["mime_decode"] = "PASS"
    visible = norm("\n".join([plain, html_text]))
    displayed = norm(html_text or plain)
    name, email_addr = parseaddr(str(message.get("From", "")))
    checks["sender_display_name"] = "PASS" if norm(name) == "final vestige" else "FAIL"
    checks["wordpress_from_domain"] = "PASS" if email_addr.lower() == "donotreply@wordpress.com" else "FAIL"
    checks["subject_matches_approved_draft"] = "PASS" if norm(str(message.get("Subject", ""))) == norm(expected_subject) else "FAIL"
    checks["nonempty_visible_body"] = "PASS" if len(displayed) >= 35 else "FAIL"
    checks["no_unresolved_tokens"] = "FAIL" if re.search(r"\[\[[^\]]+\]\]", visible) else "PASS"
    if email_mode == "excerpt":
        # Verify enough of the ORIGINAL custom excerpt is visible. This is not a
        # replacement for real WordPress render or a full-body publishing check.
        words = re.findall(r"\S+", norm(expected_excerpt))
        head, tail = " ".join(words[:12]), " ".join(words[-12:])
        checks["custom_excerpt_head"] = "PASS" if head and head in displayed else "FAIL"
        checks["custom_excerpt_tail"] = "PASS" if tail and tail in displayed else "FAIL"
        checks["full_article_in_email"] = "NOT_EXPECTED_EXCERPT_MODE"
    else:
        checks["full_article_in_email"] = ("PASS" if full_body_marker and norm(full_body_marker) in displayed
                                           else "UNKNOWN" if not full_body_marker else "FAIL")
        checks["custom_excerpt_head"] = "NOT_APPLICABLE"
        checks["custom_excerpt_tail"] = "NOT_APPLICABLE"
    checks["onsite_cta_route_present"] = "PASS" if (any(
        (urlparse(uri).hostname or "").lower() in ("finalvestige.com", "www.finalvestige.com")
        for _, uri in links) if html_text else
        bool(re.search(r"https?://(?:www\.)?finalvestige\.com/", plain, re.I))) else "FAIL"
    # A footer/logo/privacy link is NOT the approved edition's CTA.
    # Unpublished product guides intentionally remain UNKNOWN, never PASS.
    if not expected_cta or "[[" in expected_cta or "]]" in expected_cta:
        checks["exact_edition_cta_visible"] = "UNKNOWN_UNAPPROVED_CTA"
        matching_ctas: list[int] = []
    else:
        target = urlparse(expected_cta)
        if (target.scheme != "https" or target.hostname not in
                ("finalvestige.com", "www.finalvestige.com") or not target.path.startswith("/")):
            checks["exact_edition_cta_visible"] = "FAIL"
            matching_ctas = []
        else:
            def same_cta(uri: str) -> bool:
                found = urlparse(uri)
                return (found.scheme == "https" and found.hostname == target.hostname
                        and found.path.rstrip("/") == target.path.rstrip("/")
                        and found.query == target.query and not found.fragment)
            matching_ctas = [i for i, (_, uri) in enumerate(links) if same_cta(uri)]
            if html_text:
                checks["exact_edition_cta_visible"] = "PASS" if matching_ctas else "FAIL"
            else:
                urls = re.findall(r"https?://[^\s<>]+", plain, re.I)
                checks["exact_edition_cta_visible"] = "PASS" if any(
                    same_cta(u.rstrip(".,;!>")) for u in urls) else "FAIL"
    # Both text and HTML representations must be inspected if both exist. A
    # postal address cannot be deduced from an email vendor's own footer.
    if not expected_postal or len(norm(expected_postal)) < 12:
        checks["founder_verified_postal_address"] = "UNKNOWN"
    else:
        checks["founder_verified_postal_address"] = ("PASS" if norm(expected_postal) in displayed else "FAIL")
    anchors = [(label, uri) for label, uri in links if is_usable_optout(uri) and
               re.search(r"unsubscrib|opt.?out|manage subscriptions", label, re.I)]
    plaintext_optout = bool(re.search(r"(?:unsubscrib\w*|opt.?out)\s*(?:here|:|at)?\s*[:\-]?\s*(?:<)?(?:https?://[^\s<>]+|mailto:[^\s<>]+)", plain, re.I))
    checks["visible_optout_mechanism"] = "PASS" if (bool(anchors) if html_text else plaintext_optout) else "FAIL"
    checks["optout_link_functional"] = "UNKNOWN_MANUAL_TEST_REQUIRED"
    checks["actual_recipient_authorized"] = "UNKNOWN_MANUAL_ATTESTATION_REQUIRED"
    checks["preheader_appearance"] = "UNKNOWN_JETPACK_DOES_NOT_GUARANTEE_FIELD"
    checks["affiliate_email_permission"] = ("UNKNOWN_PARTNER_ATTESTATION_REQUIRED" if issue in COMMERCIAL else "NOT_APPLICABLE")
    checks["approved_live_guide_and_earning_link"] = ("UNKNOWN_PRODUCT_REVIEW_REQUIRED" if issue in COMMERCIAL else "NOT_APPLICABLE")
    if issue in COMMERCIAL:
        found = [displayed.find(term) for term in DISCLOSURES if term in displayed]
        checks["commercial_disclosure_visible"] = "PASS" if found else "FAIL"
        # The mere presence of a disclosure elsewhere in the message is not
        # evidence it appears BEFORE the intended commercial recommendation.
        # Without a real, approved onsite guide we CANNOT verify adjacency.
        if checks["exact_edition_cta_visible"] != "PASS":
            checks["commercial_disclosure_before_cta"] = "UNKNOWN_UNAPPROVED_CTA"
        elif html_text:
            checks["commercial_disclosure_before_cta"] = "PASS" if any(
                any(term in norm(before_links[i]) for term in DISCLOSURES)
                for i in matching_ctas) else "FAIL"
        else:
            first_cta = displayed.find(norm(expected_cta or ""))
            checks["commercial_disclosure_before_cta"] = "PASS" if (
                first_cta >= 0 and any(0 <= displayed.find(term) < first_cta for term in DISCLOSURES)
            ) else "FAIL"
        if email_mode == "excerpt":
            checks["disclosure_in_excerpt"] = ("PASS" if any(term in norm(expected_excerpt) for term in DISCLOSURES) and found
                                               else "FAIL")
        else:
            checks["disclosure_in_excerpt"] = "NOT_APPLICABLE"
        checks["no_direct_merchant_link"] = "FAIL" if (any(is_merchant_url(uri) for _, uri in all_links) or
                             any(is_merchant_url(uri.rstrip(".,;>")) for uri in
                                 re.findall(r"https?://[^\s<>()]+", plain, re.I))) else "PASS"
    else:
        checks["commercial_disclosure_visible"] = "NOT_APPLICABLE"
        checks["disclosure_in_excerpt"] = "NOT_APPLICABLE"
        checks["no_direct_merchant_link"] = "FAIL" if (any(is_merchant_url(uri) for _, uri in all_links) or
                             any(is_merchant_url(uri.rstrip(".,;>")) for uri in
                                 re.findall(r"https?://[^\s<>()]+", plain, re.I))) else "PASS"
    # There is intentionally no READY / APPROVED status, and absolutely no
    # mailbox address, body, href token or postal value in the returned report.
    return {"edition": issue, "status": "HOLD_FOR_HUMAN_AND_EXTERNAL_PROOFS",
            "mode_proposed_for_audit": email_mode, "checks": checks,
            "problem_codes": [name.upper() for name, value in checks.items() if value == "FAIL"],
            "manual_gates": manual_gates(issue)}


def manual_gates(issue: int) -> list[str]:
    common = ["FOUNDERS_EXPLICIT_TEST_RECIPIENT_AUTHORIZATION",
              "DELIVERABLE_CONFIRMED_OPTED_IN_AUDIENCE_RECONCILED",
              "FOUNDER_APPROVED_BUSINESS_POSTAL_ADDRESS",
              "ACTUAL_WP_RECEIVED_RENDER_AND_UNSUBSCRIBE_TEST",
              "COPY_EDITOR_AND_EVIDENCE_QA",
              "FINAL_FOUNDER_CREATIVE_AUDIENCE_DATE_AND_SEND_APPROVAL"]
    if issue in COMMERCIAL:
        common += ["AFFILIATE_ACCOUNT_ACCEPTANCE_CONFIRMED",
                   "EMAIL_PROMOTION_CHANNEL_AND_TERMS_APPROVED",
                   "LIVE_PRESSELL_GUIDE_AND_TRACKING_LINK_CONFIRMED",
                   "PRODUCT_CLAIMS_PRICE_REFUND_CHECKED"]
    return common


def load_plan(manifest: Path, excerpts: Path, issue: int) -> tuple[dict, dict]:
    m = json.loads(manifest.read_text(encoding="utf-8"))
    e = json.loads(excerpts.read_text(encoding="utf-8"))
    if m.get("status") != "DRAFT_UNSENT_NO_SCHEDULING" or any(
        entry.get("publish_state") != "hold" or entry.get("merchant_affiliate_url") is not None
        for entry in m.get("issues", [])):
        raise ValueError("Campaign changed from HOLD; refuse unreviewed audit")
    if len(m.get("issues", [])) != 6 or len(e.get("entries", [])) != 6:
        raise ValueError("Manifest/excerpt edition count mismatch")
    entry = next((row for row in m["issues"] if row["number"] == issue), None)
    excerpt = next((row for row in e["entries"] if row["number"] == issue), None)
    if not entry or not excerpt or entry["subject"] != excerpt["subject"]:
        raise ValueError("Edition subject mismatch or missing")
    if (issue in COMMERCIAL) != (entry["kind"] == "commercial-review-pending"):
        raise ValueError("Expected 4:2 editorial/commercial allocation drift")
    return entry, excerpt


def main() -> None:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Offline received Jetpack email proof. NEVER sends email.")
    ap.add_argument("--edition", type=int, required=True, choices=sorted(ISSUE_IDS))
    ap.add_argument("--eml", type=Path, default=None, help="PRIVATE authorized test .eml; never commit or upload")
    ap.add_argument("--mode", choices=["excerpt", "full"], default="excerpt")
    ap.add_argument("--manifest", type=Path, default=here.parent / "manifest.json")
    ap.add_argument("--excerpts", type=Path, default=here.parent / "delivery/wordpress_excerpt_copy.json")
    ap.add_argument("--full-marker", default="", help="Non-sensitive unique clause expected in full body")
    args = ap.parse_args()
    entry, excerpt = load_plan(args.manifest, args.excerpts, args.edition)
    raw = args.eml.read_bytes() if args.eml else None
    result = audit_received(raw, issue=args.edition, expected_subject=entry["subject"],
                            expected_excerpt=excerpt["excerpt"],
                            expected_postal=os.environ.get("FV_COMMERCIAL_POSTAL_EXPECTED"),
                            email_mode=args.mode, full_body_marker=args.full_marker,
                            expected_cta=entry["editorial_cta"])
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
