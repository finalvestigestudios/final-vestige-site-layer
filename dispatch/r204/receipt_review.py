"""Offline, privacy-minimizing Jetpack newsletter MIME inspector. NEVER sends mail.

Usage: python -I receipt_review.py sample.eml
Output contains booleans only; no addresses, message bodies or link tokens.
An .eml is evidence of *a message file*, not of receipt, consent or a working opt-out.
"""
from __future__ import annotations
import json
import re
import sys
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.block = 0
        self.fragments = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self.block += 1
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
    def handle_endtag(self, tag):
        if tag in ("script", "style", "head") and self.block:
            self.block -= 1
    def handle_data(self, data):
        if not self.block:
            self.fragments.append(data)

def audit_mime(raw: bytes) -> dict:
    """Analyze a private local message, returning only aggregate booleans."""
    if len(raw) > 3_000_000:
        raise ValueError("Too large; inspect manually")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html = [], []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() not in ("text/plain", "text/html"):
            continue
        try:
            body = part.get_content()
            if isinstance(body, str):
                (html if part.get_content_type() == "text/html" else plain).append(body)
        except (LookupError, UnicodeError, ValueError):
            continue
    view = VisibleText()
    joined_html = "\n".join(html)
    if joined_html:
        view.feed(joined_html)
    visible = " ".join(plain + view.fragments)
    low = re.sub(r"\s+", " ", visible).lower()
    # Header presence is only a diagnostic hint, never functional opt-out proof.
    unsub_header = bool(message.get("List-Unsubscribe"))
    unsub_body = bool(re.search(r"\bunsubscribe\b", low))
    has_disclosure = bool(re.search(r"(may|might|could) (earn|receive) (a )?commission", low))
    has_blockers = "[[" in visible or "APPROVED_" in visible
    return {
        "mime_parse_ok": bool(message.get("From") and message.get("Subject")),
        "has_plaintext_part": bool(plain),
        "has_html_part": bool(html),
        "visible_text_nonempty": bool(low.strip()),
        "unsub_header_present_not_functional_proof": unsub_header,
        "unsub_body_text_present_not_functional_proof": unsub_body,
        "prospective_commission_disclosure_present": has_disclosure,
        "hard_stop_placeholder_present": has_blockers,
        "requires_human_postal_validation": True,
        "requires_real_received_message_provenance": True,
        "requires_optout_operation_verification": True,
        "ready_to_send": False,
    }

def main(argv):
    if len(argv) != 2 or not Path(argv[1]).is_file():
        print("Usage: receipt_review.py received-message.eml", file=sys.stderr)
        return 2
    try:
        result = audit_mime(Path(argv[1]).read_bytes())
    except (ValueError, OSError) as exc:
        print(type(exc).__name__, file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
