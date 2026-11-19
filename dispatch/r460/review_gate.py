"""Offline-only review guard. Reads files from local checkout; never sends or contacts anyone."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
PDF = "https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"
SOURCE_URLS = (
    "https://wellcomecollection.org/works/uqa27qrt",
    "https://www.ph.ucla.edu/epi/snow/socscimed50_923_935_2000.pdf",
    "https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.1740-9713.2011.00493.x",
    "https://academic.oup.com/ije/article/42/6/1553/740477",
)

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.headings = []
        self.banned = []
        self._anchor = False
        self._anchor_text = ""
    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if tag in {"script", "img", "form", "iframe", "input"}:
            self.banned.append(tag)
        if tag == "a":
            self.links.append(at.get("href", ""))
            self._anchor = True
            self._anchor_text = ""
        if tag == "h1":
            self.headings.append(tag)
    def handle_data(self, data):
        if self._anchor:
            self._anchor_text += data
    def handle_endtag(self, tag):
        if tag == "a":
            if not self._anchor_text.strip():
                self.banned.append("empty-anchor")
            self._anchor = False

def inspect(md: str, txt: str, html: str, ledger: dict) -> list[str]:
    errors = []
    parser = LinkParser()
    parser.feed(html)
    def need(condition, message):
        if not condition: errors.append(message)
    need(md.startswith("# THE DISPATCH"), "manuscript missing")
    need("Not approved to replace PR #175" in md, "original substitution risk")
    need(txt.startswith("Subject: The map was not the whole argument"), "subject mismatch")
    need("Preheader (review intent only; native Jetpack transport not verified): John Snow's 1854 investigation, and the limits of a seven-day log." in txt, "preheader mismatch")
    need(html.count("<h1 ") == 1 and parser.headings == ["h1"], "h1 hierarchy")
    need('<html lang="en">' in html and 'role="presentation"' in html, "email table accessibility")
    need(not parser.banned, "unsafe tag or empty anchor")
    need(parser.links.count(PDF) == 1, "exactly one first-party PDF CTA")
    need(set(parser.links) == set(SOURCE_URLS) | {PDF}, "unreviewed destination")
    need(all(u in txt and u in md for u in SOURCE_URLS), "source parity")
    need(PDF in txt and PDF in md, "CTA parity")
    for mark in ("[[VALID_POSTAL_ADDRESS_REQUIRED]]", "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"):
        need(all(mark in s for s in (md,txt,html)), "missing hard legal hold " + mark)
    need("HOLD UNSENT" in html and "HOLD UNSENT" in txt, "release status")
    need(not re.search(r"(?i)utm_source|utm_campaign|refersion|href=\"[^\"]*zen12|href=\"[^\"]*hypnosislive",html), "unapproved commercial URL / tracking")
    need(ledger.get("status") == "HOLD_UNSENT", "ledger release status")
    claims = ledger.get("claims",[])
    need(len(claims) >= 6 and all(not c.get("commercial_rights_verified", False) for c in claims), "affiliate permission unverified")
    need(not ledger.get("paid_orders", False), "unverified paid orders")
    return errors

def main():
    errors = inspect((ROOT / "ISSUE06_SNOW_OPTION.md").read_text(),
                     (ROOT / "ISSUE06_OFFLINE_REVIEW.txt").read_text(),
                     (ROOT / "ISSUE06_OFFLINE_REVIEW.html").read_text(),
                     json.loads((ROOT / "MERCHANT_AND_PDF_SOURCE_LEDGER.json").read_text()))
    if errors:
        print("FAIL: " + "; ".join(errors))
        return 1
    print("PASS: offline source and HOLD-only gate; NOT a Jetpack preview or send authorization")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
