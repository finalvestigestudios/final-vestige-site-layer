#!/usr/bin/env python3
"""Offline Apollo landing delivery audit. Source gate only, NOT browser/security/rights acceptance."""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

HOSTS = frozenset({"www.nasa.gov", "sma.nasa.gov", "finalvestige.com"})
BANNED_TAGS = frozenset({"base", "iframe", "frame", "frameset", "form", "input",
                         "textarea", "select", "img", "picture", "source", "video",
                         "audio", "object", "embed", "canvas", "svg", "applet", "portal"})
BANNED_JS = re.compile(r"(?i)(?:\bfetch\s*\(|\bxmlhttprequest\b|\bsendbeacon\b|"
                       r"\bwebsocket\b|\beventsource\b|\blocalstorage\b|"
                       r"\bsessionstorage\b|\bdocument\s*\.\s*cookie\b|"
                       r"\bwindow\s*\.\s*open\b|\bpostmessage\b|\bimport\s*\(|"
                       r"\beval\s*\(|(?-i:Function)\s*\(|\binnerHTML\b|"
                       r"\binsertAdjacentHTML\b|\bdocument\s*\.\s*write\s*\(|"
                       r"\b(?:location|navigator)\s*\.|\b(?:Image|Worker|SharedWorker)\s*\()")
BANNED_CSS = re.compile(r"(?i)(?:@import\b|\burl\s*\(|\bexpression\s*\(|-moz-binding\b)")

class DeliveryBoundaryError(ValueError):
    pass

def safe_url(href: str) -> bool:
    if not href or href != href.strip() or any(ord(c) < 32 for c in href):
        return False
    if href.startswith("#"):
        return bool(re.fullmatch(r"#[A-Za-z][A-Za-z0-9_-]*", href))
    try:
        u = urlsplit(href)
    except ValueError:
        return False
    return (u.scheme == "https" and u.hostname in HOSTS and u.netloc == u.hostname
            and bool(u.path.startswith("/")) and not u.query and not u.fragment
            and not u.username and not u.password)

class BoundaryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.links = []
        self.scripts = []
        self.styles = []
        self._capture = None
        self._buffer = []
        self.ctas = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in BANNED_TAGS:
            self.errors.append("BANNED_TAG:" + tag)
        a = dict(attrs)
        if len(a) != len(attrs):
            self.errors.append("DUPLICATE_ATTRIBUTE:" + tag)
        for k, v in attrs:
            k = k.lower()
            if k.startswith("on") or k in ("srcdoc", "formaction", "ping", "srcset"):
                self.errors.append("DANGEROUS_ATTRIBUTE:" + k)
            if k == "style" and BANNED_CSS.search(v or ""):
                self.errors.append("CSS_NETWORK_OR_BINDING")
            if k in ("href", "src", "action", "poster"):
                if tag != "a" or k != "href" or not safe_url(v or ""):
                    self.errors.append("URL_NOT_ALLOWLISTED:" + tag + ":" + k)
        if tag == "a":
            link = a.get("href", "")
            self.links.append(link)
            if "data-fv-primary-cta" in a:
                self.ctas.append(link)
        if tag == "meta" and a.get("http-equiv", "").lower() in ("refresh", "set-cookie"):
            self.errors.append("ACTIVE_META")
        if tag == "link":
            self.errors.append("LINK_TAG_REVIEW_REQUIRED")
        if tag == "script":
            if self._capture is not None:
                self.errors.append("NESTED_INLINE")
            if a:
                self.errors.append("SCRIPT_ATTRIBUTES_REVIEW_REQUIRED")
            self._capture = "script"
            self._buffer = []
        elif tag == "style":
            if self._capture is not None:
                self.errors.append("NESTED_INLINE")
            if a:
                self.errors.append("STYLE_ATTRIBUTES_REVIEW_REQUIRED")
            self._capture = "style"
            self._buffer = []

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == self._capture:
            data = "".join(self._buffer)
            (self.scripts if tag == "script" else self.styles).append(data)
            self._capture = None
            self._buffer = []

def validate(html: str) -> dict:
    p = BoundaryParser()
    p.feed(html)
    if p._capture:
        p.errors.append("UNCLOSED_INLINE_BLOCK")
    if len(p.scripts) != 1 or len(p.styles) != 1:
        p.errors.append("EXPECTED_ONE_INLINE_SCRIPT_AND_STYLE")
    for css in p.styles:
        if BANNED_CSS.search(css):
            p.errors.append("CSS_NETWORK_OR_BINDING")
    for js in p.scripts:
        if BANNED_JS.search(js):
            p.errors.append("SCRIPT_NETWORK_STORAGE_OR_INJECTION")
        if "data-fv-lens" not in js or "data-fv-claim" not in js:
            p.errors.append("UNKNOWN_SCRIPT_BEHAVIOR")
    if p.ctas != ["#classroom-preview"]:
        p.errors.append("UNAPPROVED_PRIMARY_CTA")
    if len(p.links) < 8 or not any("www.nasa.gov/image-detail/" in x for x in p.links):
        p.errors.append("NASA_EVIDENCE_LINKS_MISSING")
    if "S67-19766 (provisional)" not in html or "0/6" not in html:
        p.errors.append("RIGHTS_OR_CATALOG_UNCERTAINTY_MISSING")
    if p.errors:
        raise DeliveryBoundaryError(";".join(sorted(set(p.errors))))
    return {
        "classification": "SOURCE_ONLY_NOT_BROWSER_OR_RIGHTS_ACCEPTANCE",
        "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "allowlisted_external_hosts": sorted(HOSTS),
        "primary_actions": 1, "scripts_inline": 1, "styles_inline": 1,
        "external_scripts_images_forms": 0,
        "rights_review": "0/6 PHOTO_SPECIFIC_CLEARANCES",
        "merchant_conversions": "UNVERIFIED",
        "release": "STAGING_HOLD"
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path, default=Path(__file__).with_name("landing-preview.html"))
    args = ap.parse_args()
    print(json.dumps(validate(args.html.read_text(encoding="utf-8")), sort_keys=True, indent=2))
