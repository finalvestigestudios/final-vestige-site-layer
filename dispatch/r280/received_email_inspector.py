"""Offline read-only MIME structure inspector. NEVER authorizes release, prints PII or sends mail.
This tool is for founder-authorized FUTURE privately received .eml only. Synthetic tests are not actual Jetpack proof.
"""
import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path

HOLD = "HOLD_REAL_JETPACK_DELIVERY_POSTAL_CONSENT_FOUNDER_APPROVAL"
PLACEHOLDER = re.compile(r"\[\[|NOT_VERIFIED|UNVERIFIED|REQUIRED", re.I)
POSTAL = re.compile(r"\b(?:P\.?\s*O\.?\s*Box\s*\d{1,8}|\d{1,8}\s+[\w .'-]{3,60}\s+(?:St\.?|Street|Ave\.?|Avenue|Rd\.?|Road|Blvd\.?|Boulevard|Lane|Ln\.?|Drive|Dr\.?|Way))\b", re.I)
OPT_OUT = re.compile(r"\bunsubscribe\b|\bopt[ -]?out\b|\bstop receiving\b", re.I)

class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words, self.links, self.unsafe, self.skip = [], [], False, 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "iframe", "form"):
            self.unsafe = True
            self.skip += 1
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href" and v)
    def handle_endtag(self, tag):
        if tag in ("script", "iframe", "form"):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, s):
        if not self.skip:
            self.words.append(s)

def inspect_bytes(raw):
    """Fixed Boolean-only output; not a legal decision or evidence of real delivery."""
    if not isinstance(raw, bytes) or len(raw) > 2_000_000:
        raise ValueError("Expected <=2 MB of EML bytes")
    email = BytesParser(policy=policy.default).parsebytes(raw)
    plain, html, attachments = [], [], 0
    for part in email.walk():
        if part.is_multipart():
            continue
        if part.get_content_disposition() == "attachment":
            attachments += 1
            continue
        typ = part.get_content_type()
        if typ not in ("text/plain", "text/html"):
            attachments += 1
            continue
        try:
            body = part.get_content()
            if not isinstance(body, str):
                body = ""
        except (LookupError, UnicodeError, ValueError):
            body = ""
        (plain if typ == "text/plain" else html).append(body)
    extracted = VisibleHTML()
    for part in html:
        extracted.feed(part)
    all_text = "\n".join(plain + extracted.words)
    # A URL containing "unsubscribe" by itself is not an accessible opt-out instruction.
    visible_without_urls = re.sub(r"https?://\S+", "", all_text)
    candidate_unsub = any(u.startswith("https://") and
                          ("unsub" in u.lower() or "optout" in u.lower()) and
                          not PLACEHOLDER.search(u) for u in extracted.links)
    from_addr = parseaddr(str(email.get("From", "")))[1]
    checks = {
        "subject_present": bool(str(email.get("Subject", "")).strip()) and not bool(PLACEHOLDER.search(str(email.get("Subject", "")))),
        "from_syntax_present": "@" in from_addr,
        "date_present": bool(email.get("Date")),
        "message_id_present": bool(email.get("Message-ID")),
        "multipart_plain_present": bool("".join(plain).strip()),
        "multipart_html_present": bool("".join(html).strip()),
        "postal_candidate_in_visible_body": bool(POSTAL.search(all_text)) and not bool(PLACEHOLDER.search(all_text)),
        "visible_optout_instruction": bool(OPT_OUT.search(visible_without_urls)),
        "https_optout_link_candidate": candidate_unsub,
        "no_html_script_iframe_form": not extracted.unsafe,
        "no_attachment": attachments == 0,
        "no_release_placeholders": not bool(PLACEHOLDER.search(all_text)),
        "list_unsubscribe_header_present": bool(email.get("List-Unsubscribe")),
    }
    required = tuple(k for k in checks if k != "list_unsubscribe_header_present")
    return {
        "scope": "STRUCTURAL_ONLY_UNAUTHENTICATED",
        "checks": {k: bool(v) for k, v in checks.items()},
        "structural_checks_pass": all(checks[k] for k in required),
        "actual_jetpack_receipt_verified": False,
        "publisher_postal_ownership_verified": False,
        "unsubscribe_operational_verified": False,
        "subscriber_consent_verified": False,
        "founder_send_approval": False,
        "release_state": HOLD,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("eml", type=Path)
    a = p.parse_args()
    print(json.dumps(inspect_bytes(a.eml.read_bytes()), indent=2))
