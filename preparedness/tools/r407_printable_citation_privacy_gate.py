#!/usr/bin/env python3
"""R407 E399 printable privacy/citation custody; extra review ONLY, no QD/pass."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
from urllib.parse import parse_qsl, urlsplit

HOLD = "DRAFT_HARD_HOLD"
ARTICLE_SHA256 = "75ed08831c138ad3057220df060897e1efe518f1156ea68bb2400c06db898661"
PRINT_SHA256 = "240a20ea5cdb6a34a686eb605550766e8572bb9c37d3836e2abd85f2d84e7709"
LIMIT = 4 * 1024 * 1024
BLOCKS = frozenset("h1 h2 h3 h4 h5 h6 p li td th pre blockquote figcaption".split())
SAFE_TAGS = frozenset(("html head body main article section header footer div span "
    "h1 h2 h3 h4 h5 h6 p ul ol li dl dt dd table thead tbody tfoot tr td th caption "
    "blockquote em strong b i u small abbr time cite figure figcaption pre code "
    "hr br a style meta").split())
VOID = frozenset("br hr meta".split())
CSS_DANGER = re.compile(r"(?i)@import|@font-face|url\s*\(|image-set\s*\(|expression\s*\(|behavior\s*:|binding\s*:|\\")
TRACKING = frozenset("fbclid gclid msclkid dclid mc_eid mc_cid".split())
WORD = re.compile(r"(?u)\b\w+\b")

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def read_original(path: Path | None) -> bytes | None:
    """Do not read symlinks, hardlinks, devices or oversized files."""
    if path is None:
        return None
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= LIMIT:
            return None
        with os.fdopen(os.dup(fd), "rb") as handle:
            raw = handle.read(LIMIT + 1)
        after = os.fstat(fd)
        if (len(raw) != before.st_size or len(raw) > LIMIT or
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
            return None
        return raw
    except (OSError, ValueError):
        return None
    finally:
        if fd is not None:
            os.close(fd)

def clean_source(value: str) -> str | None:
    if not isinstance(value, str) or len(value) > 2048 or any(ord(c) < 32 for c in value):
        return None
    try:
        u = urlsplit(value)
        if u.scheme != "https" or not u.hostname or u.username or u.password or (
            u.port is not None and u.port != 443
        ):
            return None
        host = u.hostname.lower()
        if not (host.endswith(".gov") or host.endswith(".edu") or host == "foodsafety.gov"):
            return None
        if any(k.lower().startswith("utm_") or k.lower() in TRACKING
               for k, _ in parse_qsl(u.query, keep_blank_values=True)):
            return None
        return u._replace(fragment="").geturl()
    except ValueError:
        return None

def css_unsafe(text: str) -> bool:
    return bool(CSS_DANGER.search(re.sub(r"/\*.*?\*/", "", text, flags=re.S)))

class CheckPrint(HTMLParser):
    """Static no-network printable audit. CSS/browser visibility is NOT proved."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = []
        self.failures = set()
        self.elements = 0
        self.css_chars = 0
        self.ids = set()
        self.targets = set()
        self.links = []
        self.blocks = []
        self.link = None

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        self.elements += 1
        if self.elements > 20000 or len(self.frames) > 256:
            self.failures.add("html_size_or_depth_limit")
        if tag not in SAFE_TAGS:
            self.failures.add("unsafe_element")
        keys = [k.lower() for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.failures.add("duplicate_attribute")
        if any(v is None for _, v in attrs):
            self.failures.add("bare_attribute")
        a = dict(attrs)
        for k, v in attrs:
            if k.lower().startswith("on") or k.lower() in (
                "src", "srcset", "formaction", "action", "poster", "background",
                "hrefdoc", "http-equiv", "data", "xlink:href"
            ):
                self.failures.add("active_or_remote_attribute")
            if k.lower() == "style" and css_unsafe(v or ""):
                self.failures.add("remote_or_executable_css")
        if tag == "meta" and set(keys) - {"charset", "name", "content"}:
            self.failures.add("unapproved_meta")
        identifier = a.get("id")
        if identifier:
            if identifier in self.ids:
                self.failures.add("duplicate_id")
            self.ids.add(identifier)
        if tag == "a":
            if self.link:
                self.failures.add("nested_link")
            href = a.get("href") or ""
            local = href.startswith("#") and len(href) > 1
            if local:
                self.targets.add(href[1:])
            canon = None if local else clean_source(href)
            if not local and not canon:
                self.failures.add("unsafe_tracking_or_commercial_link")
            self.link = {"url": canon, "text": [], "local": local}
        if tag not in VOID:
            self.frames.append({"tag": tag, "text": [], "child": False})
            if tag in BLOCKS:
                for older in reversed(self.frames[:-1]):
                    if older["tag"] in BLOCKS:
                        older["child"] = True
                        break

    def handle_data(self, data):
        if any(f["tag"] == "style" for f in self.frames):
            self.css_chars += len(data)
            if self.css_chars > 250000:
                self.failures.add("css_size_limit")
            if css_unsafe(data):
                self.failures.add("remote_or_executable_css")
            if re.search(r"(?i)(?:^|[{;])\s*content\s*:", data):
                self.failures.add("css_generated_text_unverified")
            return
        if any(f["tag"] == "head" for f in self.frames):
            return
        if self.link:
            self.link["text"].append(data)
        for f in self.frames:
            if f["tag"] in BLOCKS:
                f["text"].append(data)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.frames or self.frames[-1]["tag"] != tag:
            self.failures.add("misnested_markup")
            return
        frame = self.frames.pop()
        if tag == "a" and self.link is not None:
            link = self.link
            self.link = None
            if not "".join(link["text"]).strip():
                self.failures.add("unlabeled_link")
            self.links.append(link["url"])
        if tag in BLOCKS and not frame["child"]:
            raw = " ".join("".join(frame["text"]).split())
            if raw:
                self.blocks.append({"tag": tag, "text_sha256": sha(raw.encode()),
                                    "words": len(WORD.findall(raw))})

    def finish(self):
        if self.frames or self.link:
            self.failures.add("unclosed_markup")
        if self.targets - self.ids:
            self.failures.add("broken_local_link")
        if not self.blocks:
            self.failures.add("no_visible_reading_blocks")
        return self

def audit(article: object, printable: object, approved_article_urls: object,
          *, article_pin: str = ARTICLE_SHA256, print_pin: str = PRINT_SHA256) -> dict:
    """Pin overrides ONLY for isolated unit fixtures; CLI always uses constants."""
    errors = set()
    if not isinstance(article, bytes) or not 0 < len(article) <= LIMIT:
        errors.add("missing_or_oversized_article")
    if not isinstance(printable, bytes) or not 0 < len(printable) <= LIMIT:
        errors.add("missing_or_oversized_print")
    if not isinstance(article, bytes) or sha(article) != article_pin:
        errors.add("article_original_hash_mismatch")
    if not isinstance(printable, bytes) or sha(printable) != print_pin:
        errors.add("print_original_hash_mismatch")
    if not isinstance(approved_article_urls, (set, frozenset)) or any(
            not isinstance(u, str) or clean_source(u) != u for u in approved_article_urls):
        errors.add("untrusted_article_source_inventory")
        approved_article_urls = set()
    scanner = None
    if isinstance(printable, bytes) and 0 < len(printable) <= LIMIT:
        try:
            scanner = CheckPrint()
            scanner.feed(printable.decode("utf-8", "strict"))
            scanner.close()
            scanner.finish()
        except (UnicodeDecodeError, ValueError, AssertionError, OverflowError):
            errors.add("unparseable_print")
            scanner = None
    links = {v for v in (scanner.links if scanner else ()) if v}
    if scanner:
        errors.update("print:" + s for s in scanner.failures)
    if links - set(approved_article_urls):
        errors.add("printed_link_without_visible_article_citation")
    return {"schema": "r407.printable_privacy.v1",
            "integrity": "FAIL" if errors else "PASS",
            "release": HOLD, "eligible": False,
            "publication_approved": False, "qualified_food_safety": "NOT_GRANTED",
            "qualified_child_privacy": "NOT_GRANTED", "source_authenticity_proven": False,
            "selected_variant": None, "article_hash_match": "article_original_hash_mismatch" not in errors,
            "print_hash_match": "print_original_hash_mismatch" not in errors,
            "printed_source_urls": sorted(links),
            "unreviewed_print_blocks": len(scanner.blocks) if scanner else 0,
            "print_word_count": sum(b["words"] for b in scanner.blocks) if scanner else 0,
            "failures": sorted(errors)}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e399-html", type=Path)
    parser.add_argument("--e399-print", type=Path)
    args = parser.parse_args(argv)
    article, printable = read_original(args.e399_html), read_original(args.e399_print)
    sources = set()
    if article is not None:
        try:
            here = Path(__file__).parent
            spec = importlib.util.spec_from_file_location("r406_prior", here / "r406_visible_claim_citation_lineage.py")
            upstream = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(upstream)
            r = upstream.capture(article, set())
            if r.get("integrity") == "PASS":
                sources = {u for u in r.get("claim_bound_source_urls", []) if clean_source(u) == u}
        except (OSError, ValueError, AttributeError, RuntimeError):
            pass
    report = audit(article, printable, sources)
    report["r405_r406_original_custody_still_required"] = True
    print(json.dumps(report, sort_keys=True))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
