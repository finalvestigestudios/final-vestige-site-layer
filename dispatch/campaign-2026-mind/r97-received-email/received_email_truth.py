"""Read-only RFC 5322 evidence inspector for Dispatch. Never sends, follows URLs, or writes raw mail.

This is a *diagnostic*, never a release authorization. All reported fields are
restricted to non-identifying booleans/enumerations. Feed a LOCAL .eml privately.
"""
from __future__ import annotations

import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

ALLOWED_ISSUES = {"01", "02", "03", "04", "05", "06"}
COMMERCIAL_ISSUES = {"03", "05"}
DISCLOSURE = re.compile(r"(?:may earn|may receive)\s+a\s+commission", re.I)
UNSUB = re.compile(r"unsubscribe|opt\s*out", re.I)


class HtmlText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.hrefs: list[str] = []
        self.skipped = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style"):
            self.skipped += 1
        if tag.lower() == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style"):
            self.skipped = max(0, self.skipped - 1)

    def handle_data(self, data):
        if not self.skipped:
            self.fragments.append(data)


def _safe_body(part):
    try:
        return part.get_content()
    except (UnicodeError, LookupError, ValueError, TypeError):
        return ""


def _body_parts(msg):
    found = {"plain": [], "html": []}
    hrefs = []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        body = _safe_body(part)
        if not isinstance(body, str):
            continue
        kind = part.get_content_type()
        if kind == "text/plain":
            found["plain"].append(body)
        elif kind == "text/html":
            parser = HtmlText()
            parser.feed(body)
            found["html"].append(" ".join(parser.fragments))
            hrefs.extend(parser.hrefs)
    return {k: "\n".join(v) for k, v in found.items()}, hrefs


def _safe_urls(headers):
    # Do not log URL destinations: unsubscribe URLs can contain subscriber tokens.
    raw = " ".join(headers)
    return bool(re.search(r"<https://[^>\s]+>|<mailto:[^>\s]+>", raw, re.I))


def _content_class(subject, body):
    s = subject.lower()
    t = body.lower()
    if "confirm" in s and "subscription" in s:
        return "CONFIRMATION_NOT_WELCOME"
    if "welcome" in s and ("focus fieldbook" in t or "seven day focus" in t):
        return "WELCOME_CANDIDATE_NOT_DELIVERY_PROOF"
    if "dispatch" in s or "the dispatch" in t:
        return "NEWSLETTER_CANDIDATE"
    return "OTHER_UNKNOWN"


def inspect_bytes(raw: bytes, issue: str | None = None, postal_phrase: str | None = None) -> dict:
    """Inspect a locally supplied message; result contains no addresses, subjects or links.

    postal_phrase is an optional privately held exact comparison string; the
    return value cannot assert the address is legally valid, so approval stays HOLD.
    """
    if issue is not None and issue not in ALLOWED_ISSUES:
        raise ValueError("issue must be one of 01..06")
    if len(raw) > 5_000_000:
        raise ValueError("MIME exceeds 5MB local review limit")
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    parts, hrefs = _body_parts(msg)
    presented = [k for k, v in parts.items() if v.strip()]
    combined = "\n".join(parts.values())
    subject = str(msg.get("Subject", ""))
    list_unsub = msg.get_all("List-Unsubscribe", [])
    list_unsub_post = msg.get_all("List-Unsubscribe-Post", [])
    commercial = issue in COMMERCIAL_ISSUES
    # Both representations must carry disclosure if present; any missing one fails.
    disclosures_all = bool(presented) and all(bool(DISCLOSURE.search(parts[k])) for k in presented)
    offer_mentions = {"03": ("zen12", "meditation"), "05": ("total focus", "hypnosis")}
    offer_terms = offer_mentions.get(issue or "", ())
    offer_in_all = bool(presented) and all(any(term in parts[k].lower() for term in offer_terms) for k in presented) if commercial else None
    # Explicit sent-from-publisher phrase must appear in the actual message, not an Automattic footer.
    postal_visible = (bool(postal_phrase) and all(postal_phrase.casefold() in parts[k].casefold() for k in presented)) if presented else False
    _ = hrefs  # Parsed, but not returned or followed: hrefs may contain personal tokens.
    classification = _content_class(subject, combined)
    return {
        "classification": classification,
        "message_mime_parseable": bool(msg.get("From") and msg.get("Date") and msg.get("Subject")),
        "representations_present": sorted(presented),
        "list_unsubscribe_header_present": bool(list_unsub),
        "list_unsubscribe_header_url_format": _safe_urls(list_unsub),
        "one_click_header_claim_present": any("List-Unsubscribe=One-Click" in str(x) for x in list_unsub_post),
        "visible_unsubscribe_wording_all_representations": bool(presented) and all(bool(UNSUB.search(parts[k])) for k in presented),
        "postal_phrase_visible_all_representations": bool(postal_visible),
        "postal_qualification_verified": False,
        "functional_unsubscribe_verified": False,
        "disclosure_all_representations": disclosures_all if commercial else None,
        "offer_identity_all_representations": offer_in_all,
        "commercial_issue": commercial,
        "campaign_delivery_verified": False,  # Cannot infer by existence of an .eml file alone.
        "launch_decision": "HOLD_UNSENT" if not commercial else "HOLD_UNSENT_HOLD_MERCHANT",
        "notes": "No recipient, sender, subject, URL, body, tracking parameter or address is output. Human source/consent/footer/link review and final founder approval remain required."
    }


def main():
    ap = argparse.ArgumentParser(description="PRIVATE offline .eml diagnostic (never sends or exports contacts)")
    ap.add_argument("eml", type=Path)
    ap.add_argument("--issue", choices=sorted(ALLOWED_ISSUES))
    args = ap.parse_args()
    print(json.dumps(inspect_bytes(args.eml.read_bytes(), args.issue), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
