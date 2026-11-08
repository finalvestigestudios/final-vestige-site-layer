"""Offline evidence intake for a founder-authorized, already-received Jetpack email.

No network, WordPress writes, SMTP, subscriber export, recipient disclosure or
send capability. A syntactically convincing .eml NEVER establishes actual
delivery, lawful mailing address, working unsubscribe, or campaign permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

MAX_MIME_BYTES = 5_000_000
DRAFT_SENTINEL = re.compile(
    r"DO NOT PUBLISH|HOLD_UNSENT|HOLD_MERCHANT|"
    r"\[\[[A-Z0-9_]*REQUIRED\]\]|"
    r"APPROVED_[A-Z0-9_]*_REQUIRED",
    flags=re.IGNORECASE,
)
HTTP_UNSUB = re.compile(r"<(https://[^<> \r\n]+)>", flags=re.IGNORECASE)
PLAIN_UNSUB = re.compile(
    r"(?:unsubscribe|opt[\s-]?out)\s*(?::|at|here|via)?\s*"
    r"(https://[^\s<>'\"]+)",
    flags=re.IGNORECASE,
)


def _web_url(value: str) -> bool:
    """A URL-shaped token is NOT proof that the endpoint works."""
    try:
        parts = urlsplit(value.strip())
        return (parts.scheme == "https" and bool(parts.hostname)
                and not parts.username and not parts.password)
    except ValueError:
        return False


class _HTMLContent(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words: list[str] = []
        self.anchors: list[tuple[str, str]] = []
        self._href: str | None = None
        self._label: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href", "")
            self._label = []

    def handle_data(self, data):
        self.words.append(data)
        if self._href is not None:
            self._label.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, " ".join(self._label)))
            self._href = None
            self._label = []


def analyze_mime(
    data: bytes, *, expected_subject: str, expected_sender: str = "Final Vestige",
    commercial: bool = False, postal_marker: str | None = None,
) -> dict:
    """Return ONLY privacy-safe booleans, a content hash and irrevocable HOLD.

    postal_marker is a founder-verified string supplied OFFLINE for presence
    testing. Never print/store its actual value. This does not validate that
    the address is legally compliant, belongs to FV or is operational.
    """
    if not isinstance(data, bytes) or not data or len(data) > MAX_MIME_BYTES:
        raise ValueError("Missing, invalid or oversized .eml (5 MB limit)")
    if not expected_subject or not expected_subject.strip():
        raise ValueError("An exact expected newsletter subject is required")
    message = BytesParser(policy=policy.default).parsebytes(data)
    if not message.get("From") or not message.get("Subject"):
        raise ValueError("Not a usable message: missing From or Subject header")

    plain_parts, html_parts = [], []
    part_count = 0
    for part in message.walk():
        part_count += 1
        if part_count > 50:
            raise ValueError("Message contains too many MIME parts")
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        ctype = part.get_content_type()
        if ctype not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
        except (LookupError, ValueError, UnicodeError) as exc:
            raise ValueError("Cannot safely decode message part") from exc
        if not isinstance(content, str):
            raise ValueError("Unexpected binary text part")
        (plain_parts if ctype == "text/plain" else html_parts).append(content)

    plain = "\n".join(plain_parts)
    html = "\n".join(html_parts)
    parsed = _HTMLContent()
    parsed.feed(html)
    visible = plain + "\n" + " ".join(parsed.words)
    # No raw body, recipient, header value, URL, postal marker or address
    # is ever included in output; hash is for operator-side traceability.
    _, sender_address = parseaddr(str(message.get("From", "")))
    sender_name, _ = parseaddr(str(message.get("From", "")))
    subject_match = str(message["Subject"]).strip() == expected_subject.strip()
    unsubscribe_header = str(message.get("List-Unsubscribe", ""))
    header_urls = HTTP_UNSUB.findall(unsubscribe_header)
    header_link = any(_web_url(url) for url in header_urls)
    body_link = any(
        _web_url(href) and bool(re.search(r"\b(unsubscribe|opt[\s-]?out)\b", label, re.I))
        for href, label in parsed.anchors
    ) or any(_web_url(u) for u in PLAIN_UNSUB.findall(plain))
    one_click = (
        header_link
        and str(message.get("List-Unsubscribe-Post", "")).strip().lower()
        == "list-unsubscribe=one-click"
    )
    marker_present = (
        None if not postal_marker or not postal_marker.strip()
        else postal_marker.casefold().strip() in visible.casefold()
    )
    draft = bool(DRAFT_SENTINEL.search(visible))
    commercial_disclosure = bool(re.search(
        r"(may|might|could)\s+earn\s+(?:a\s+)?commission", visible, re.I
    ))
    # A received email is still not authenticated merely by importing an .eml.
    return {
        "schema": "fv-dispatch-native-mime-candidate-v1",
        "mime_sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "source": "OFFLINE_IMPORTED_CANDIDATE_NOT_AUTHENTICATED",
        "subject_exact_match": subject_match,
        "sender_display_match": sender_name.strip().casefold() == expected_sender.casefold(),
        "sender_address_exists": bool(sender_address),
        "has_plain_text": bool(plain.strip()),
        "has_html": bool(html.strip()),
        "has_header_unsubscribe_https": header_link,
        "has_body_unsubscribe_https": body_link,
        "has_rfc8058_one_click_declaration": one_click,
        "draft_or_inactive_placeholder_visible": draft,
        "founder_supplied_postal_marker_present": marker_present,
        "postal_address_legally_verified": False,
        "unsubscribe_endpoint_functionally_tested": False,
        "legitimate_delivery_proven": False,
        "consented_eligible_audience_verified": False,
        "affiliate_email_permission_verified": False,
        "commercial_disclosure_present": commercial_disclosure if commercial else None,
        "observations_are_not_attestations": True,
        "release": "HOLD_UNSENT",
        "merchant_release": "HOLD_MERCHANT" if commercial else "NOT_APPLICABLE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eml", type=Path, help="Founder-authorized received email (.eml)")
    parser.add_argument("--expected-subject", required=True)
    parser.add_argument("--expected-sender", default="Final Vestige")
    parser.add_argument("--commercial", action="store_true")
    parser.add_argument(
        "--postal-marker-file", type=Path,
        help="Local PRIVATE file with founder-verified postal text; never exported",
    )
    parser.add_argument(
        "--report", type=Path,
        help="Optional path for PII-free JSON report (no raw MIME or recipient)",
    )
    args = parser.parse_args()
    postal = None
    if args.postal_marker_file:
        postal = args.postal_marker_file.read_text(encoding="utf-8").strip()
    result = analyze_mime(
        args.eml.read_bytes(), expected_subject=args.expected_subject,
        expected_sender=args.expected_sender, commercial=args.commercial,
        postal_marker=postal,
    )
    serialized = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    # ALWAYS nonzero until a separate human approval system exists. Passing
    # structure checks never silently becomes send authorization.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
