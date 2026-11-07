"""Read-only, privacy-minimizing review of an already-received .eml file.

No network operations, writes, mail sends, subscriber changes or approvals.
This *cannot* prove delivery, valid opt-out behavior, publisher ownership,
actual permission to email, or authenticity from raw MIME alone.

Usage: python receipt_gate.py /path/to/authorized-received.eml
Only boolean/length-based findings are printed. NEVER print the MIME headers or body.
"""
import json
import re
import sys
from email import policy
from email.parser import BytesParser
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = attrs.get("style", "").replace(" ", "").lower()
        if self.hidden_depth or tag in {"script", "style", "template"} or "display:none" in style or attrs.get("hidden") is not None or attrs.get("aria-hidden") == "true":
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        # This heuristic intentionally cannot certify visibility in complex email clients.
        if self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


def _decoded(part):
    value = part.get_content()
    return value if isinstance(value, str) else ""


def analyze(raw: bytes, commercial: bool = False) -> dict:
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    text = []
    html = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() == "text/plain":
            text.append(_decoded(part))
        elif part.get_content_type() == "text/html":
            html.append(_decoded(part))
    plain = "\n".join(text)
    markup = "\n".join(html)
    v = VisibleHTML()
    v.feed(markup)
    visible = unescape(" ".join(v.parts))
    # Strings below may be present in a malicious message. Findings are never positive release approvals.
    unsub = bool(msg.get("List-Unsubscribe")) or bool(re.search(r"\bunsubscribe\b", visible, re.I))
    commercial_near = bool(re.search(r"(?:may earn (?:a )?commission|affiliate link|paid partnership)", visible, re.I))
    placeholders = bool(re.search(r"\[\[|VALID_POSTAL|UNSUBSCRIBE_LINK_MUST|APPROVED_.*URL_REQUIRED", plain + markup, re.I))
    # A postal address MUST be separately attested as belonging to Final Vestige;
    # a generic address in a received email is not publisher proof.
    has_postal_appearance = bool(re.search(r"\b(?:P\.?O\.?\s*Box|\d{1,6}\s+[^\n,]{4,60}(?:Street|St\.|Road|Rd\.|Ave\.|Avenue|Drive|Dr\.|Boulevard|Blvd))\b", visible, re.I))
    return {
        "has_subject_header": bool(msg.get("Subject")),
        "has_from_header": bool(msg.get("From")),
        "has_plaintext": bool(plain.strip()),
        "has_html": bool(markup.strip()),
        "plaintext_nonempty": bool(plain.strip()),
        "has_unsubscribe_indicator_not_function_test": unsub,
        "has_postal_appearance_not_publisher_proof": has_postal_appearance,
        "contains_unresolved_placeholders": placeholders,
        "commercial_disclosure_indicator_not_adjacency_proof": commercial_near if commercial else None,
        "native_jetpack_rendering_verified": False,
        "unsubscribe_functionally_verified": False,
        "publisher_postal_address_attested": False,
        "provider_confirmed_subscriber_and_consent": False,
        "fieldbook_welcome_received_verified": False,
        "merchant_named_email_permission_verified": False,
        "founder_campaign_send_approval": False,
        "release_decision": "HOLD_UNSENT",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2 or Path(sys.argv[1]).suffix.lower() != ".eml":
        raise SystemExit("usage: python receipt_gate.py path/to/authorized.eml")
    # Intentionally no From/To/Subject/body echo, even on failure.
    print(json.dumps(analyze(Path(sys.argv[1]).read_bytes()), indent=2, sort_keys=True))
