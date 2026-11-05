"""Read-only RFC5322 inspection; never sends, clicks, stores PII or grants release.

All received-email attestations, publisher-address checks, live unsubscribe
functionality, subscriber eligibility and merchant permission require separate
human-authorized, independent source-of-truth review.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit

MAX_BYTES = 2_000_000
MERCHANT_EDITIONS = {"03", "05"}
COMMISSION = re.compile(r"(?:may|might) earn (?:a )?commission", re.I)

class _BodyHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.unsafe: list[str] = []
        self.missing_alt = 0
        self._anchor: list[str] | None = None
        self._href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag in {"script", "iframe", "form", "object", "embed"}:
            self.unsafe.append(tag)
        if tag == "img" and not attrs_d.get("alt") and attrs_d.get("alt") != "":
            self.missing_alt += 1
        if tag == "a":
            self._anchor = []
            self._href = attrs_d.get("href") or ""

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._anchor is not None:
            self._anchor.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor is not None:
            self.links.append((self._href, "".join(self._anchor).strip()))
            self._anchor = None


def _message_parts(raw: bytes) -> tuple[object, str, str]:
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("EML size unsupported")
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html = [], []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() not in {"text/html", "text/plain"}:
            continue
        try:
            content = part.get_content()
        except (UnicodeError, LookupError, ValueError):
            continue
        if part.get_content_type() == "text/html":
            html.append(content)
        else:
            plain.append(content)
    return msg, "\n".join(plain), "\n".join(html)


def _is_site_url(url: str, domain: str, path: str) -> bool:
    u = urlsplit(url.strip())
    return u.scheme == "https" and u.netloc.lower() == domain.lower() and u.path.rstrip("/") == path.rstrip("/")


def _has_unsub_url(links: list[tuple[str, str]], plain: str) -> bool:
    # Presence only. Never follow a live opt-out link: that would change state.
    for url, label in links:
        parsed = urlsplit(url)
        if parsed.scheme in {"https", "http"} and parsed.netloc and ("unsubscribe" in label.lower() or "unsubscribe" in url.lower()):
            return True
    return bool(re.search(r"unsubscribe.{0,120}https?://[^\s<>]+", plain, re.I | re.S))


def audit(raw: bytes, *, edition: str, expected_path: str, publisher_address: str | None = None,
          domain: str = "finalvestige.com", expected_sender: str = "donotreply@wordpress.com") -> dict:
    """Produce an aggregate-only structural report. Never infer a delivery or paid sale.

    publisher_address is a privately attested Final Vestige postal address passed
    by an authorized reviewer; it is never printed or included in results.
    """
    if edition not in {"01", "02", "03", "04", "05", "06"}:
        raise ValueError("Unknown edition")
    if not expected_path.startswith("/") or expected_path.startswith("//") or "?" in expected_path:
        raise ValueError("Expected CTA path must be an absolute local path without query")
    msg, plain, html = _message_parts(raw)
    markup = _BodyHTML()
    if html:
        markup.feed(html)
    combined = (plain + "\n" + " ".join(markup.text)).strip()
    urls_plain = [(m.group(0).rstrip(".,)"), "") for m in re.finditer(r"https?://[^\s<>\"']+", plain)]
    urls = markup.links + urls_plain
    cta_visible = any(_is_site_url(url, domain, expected_path) for url, _ in urls)
    footer_unsub = _has_unsub_url(markup.links, plain)
    list_unsub_header = bool(msg.get("List-Unsubscribe"))
    # Merchant-linked offers require conspicuous disclosure in each representation
    # that contains the CTA. Additional visual proximity needs native preview QA.
    commercial = edition in MERCHANT_EDITIONS
    disclosure_plain = bool(COMMISSION.search(plain)) if plain else None
    disclosure_html = bool(COMMISSION.search(" ".join(markup.text))) if html else None
    disclosure_both = (not commercial or (disclosure_plain is not False and disclosure_html is not False
                                      and (disclosure_plain is True or disclosure_html is True)))
    postal_present = bool(publisher_address and len(publisher_address.strip()) >= 10
                          and publisher_address.casefold().strip() in combined.casefold()
                          and "automattic" not in publisher_address.casefold())
    sender_address = parseaddr(msg.get("From", ""))[1].lower()
    sender_ok = sender_address == expected_sender.lower()
    reply_to_noauth = bool(msg.get("Reply-To") and "wordpress" not in msg.get("Reply-To", "").lower())
    html_safe = not markup.unsafe and markup.missing_alt == 0
    errors = []
    checks = {
        "sender_matches_configured_wordpress_sender": sender_ok,
        "intended_first_party_cta_visible": cta_visible,
        "visible_unsubscribe_url_present": footer_unsub,
        "list_unsubscribe_header_present": list_unsub_header,
        "verified_publisher_postal_address_present": postal_present,
        "commercial_disclosure_in_present_mime_parts": disclosure_both,
        "email_html_has_no_unsafe_elements_or_unlabeled_images": html_safe,
        "plaintext_body_present": bool(plain.strip()),
        "html_body_present": bool(html.strip()),
    }
    for name, passed in checks.items():
        if not passed:
            errors.append(name)
    # Even structurally complete forwarded EML can be synthetic or edited.
    # Native receipt provenance and unsubscribe function must be separately verified.
    return {
        "edition": edition,
        "source": "offline_eml_inspection_only",
        "structural_checks": checks,
        "failed_checks": errors,
        "structural_pass": not errors,
        "native_jetpack_received_email_provenance_verified": False,
        "unsubscribe_functionality_verified": False,
        "subscription_consent_verified": False,
        "affiliate_email_permission_verified": False,
        "merchant_terms_verified": False,
        "independent_paid_sale_verified": False,
        "campaign_release_ready": False,
        "release_status": "HOLD_UNSENT" + ("_HOLD_MERCHANT" if commercial else ""),
    }
