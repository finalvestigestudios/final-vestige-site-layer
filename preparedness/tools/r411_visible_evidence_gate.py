#!/usr/bin/env python3
"""R411: conservative visible-evidence custody overlay for R410; ALWAYS DRAFT/HARD HOLD.

This static HTML inspector is NOT a browser visibility test, source-claim adjudication,
quality review, safety approval, or publication authorization. It never writes inputs.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location("r410_full_slate_export_gate", Path(__file__).with_name("r410_full_slate_export_gate.py"))
_r410 = module_from_spec(_spec)
_spec.loader.exec_module(_r410)

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
INERT = {"template", "noscript", "dialog"}
HIDDEN_CLASSES = {"hidden", "is-hidden", "u-hidden", "d-none", "display-none", "invisible", "sr-only", "visually-hidden", "screen-reader-text", "opacity-0"}
# These Unicode formatting controls can visually reorder or conceal text/links.
FORMAT_CONTROLS = {chr(n) for n in list(range(0x202a, 0x202f)) + list(range(0x2066, 0x206a)) + list(range(0x200b, 0x2010)) + [0xfeff, 0x061c]}
WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)

class VisibleEvidenceHTML(HTMLParser):
    """Fail on invisible evidence, ambiguous HTML nesting and text presentation controls."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors, self.visible_words, self.visible_cites, self.visible_headings = [], [], [], []

    def _is_hidden(self):
        return any(hidden for _tag, hidden in self.stack)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        keys = [k.lower() for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.errors.append("duplicate case-insensitive attributes")
        attr = {k.lower(): v for k, v in attrs}
        classes = set((attr.get("class") or "").lower().split())
        concealed = (tag in INERT or "hidden" in attr or "inert" in attr or "popover" in attr
                     or ("aria-hidden" in attr and (attr["aria-hidden"] or "").lower() != "false")
                     or bool(classes & HIDDEN_CLASSES)
                     or (tag == "details" and "open" not in attr)
                     or ("aria-expanded" in attr and (attr["aria-expanded"] or "").lower() == "false"))
        if concealed:
            self.errors.append("concealed, collapsible or inert content: " + tag)
        if tag == "a" and any(t == "a" for t, _ in self.stack):
            self.errors.append("nested citation/link anchors")
        hidden = concealed or self._is_hidden()
        if tag.startswith("h") and len(tag) == 2 and tag[1] in "123456":
            if not hidden:
                self.visible_headings.append(tag)
        if tag == "a" and ("data-source-id" in attr or "href" in attr):
            if hidden:
                self.errors.append("citation or link hidden from reader")
            else:
                self.visible_cites.append((attr.get("data-source-id"), attr.get("href")))
        if tag not in VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            self.errors.append("closing void HTML tag: " + tag)
        elif not self.stack or self.stack[-1][0] != tag:
            self.errors.append("missing/misnested close tag: " + tag)
            # Continue conservatively, never silently repair ambiguous evidence.
            if tag in [t for t, _ in self.stack]:
                while self.stack and self.stack[-1][0] != tag:
                    self.stack.pop()
                self.stack.pop()
        else:
            self.stack.pop()

    def handle_data(self, data):
        if any(ch in FORMAT_CONTROLS or (ord(ch) < 32 and ch not in "\r\n\t") for ch in data):
            self.errors.append("invisible/bidirectional text control")
        if not self._is_hidden():
            self.visible_words.extend(WORD.findall(data))

    def finish(self):
        self.close()
        if self.stack:
            self.errors.append("unclosed HTML element(s)")
        if not self.visible_headings:
            self.errors.append("no reader-visible heading")
        if len(self.visible_words) < 50:
            self.errors.append("fewer than 50 reader-visible words")
        if not self.visible_cites:
            self.errors.append("no reader-visible source link")
        return self


def check(original, manifest, exports, *, raw_original=None, test_only=False):
    """Return hold-only overlay; never alter or approve R410's source/citation outcome."""
    base = _r410.check(original, manifest, exports, raw_original=raw_original, test_only=test_only)
    errors, details = list(base.get("errors", [])), []
    if not isinstance(exports, dict):
        errors.append("invalid export mapping")
    else:
        for slug in sorted(exports, key=str):
            pair = exports[slug]
            if not isinstance(slug, str) or not isinstance(pair, (list, tuple)) or len(pair) != 2:
                errors.append("invalid export item"); continue
            parsed = []
            for i, body in enumerate(pair):
                if isinstance(body, bytes):
                    try: body = body.decode("utf-8", "strict")
                    except UnicodeError: errors.append("invalid HTML encoding: " + slug); continue
                if not isinstance(body, str) or not 10 <= len(body.encode("utf-8")) <= 1_000_000:
                    errors.append("invalid HTML size or type: " + slug); continue
                try:
                    p = VisibleEvidenceHTML()
                    p.feed(body)
                    p.finish()
                except (TypeError, ValueError, OverflowError) as exc:
                    errors.append("visible evidence parsing failed: " + slug + ": " + str(exc)); continue
                errors.extend(slug + " [" + ("wordpress" if i == 0 else "preview") + "]: " + e for e in p.errors)
                parsed.append(p)
            if len(parsed) == 2:
                if parsed[0].visible_words != parsed[1].visible_words:
                    errors.append("reader-visible text parity lost: " + slug)
                if parsed[0].visible_cites != parsed[1].visible_cites:
                    errors.append("reader-visible citation sequence changed: " + slug)
                if parsed[0].visible_headings != parsed[1].visible_headings:
                    errors.append("reader-visible heading structure changed: " + slug)
                details.append({"slug": slug, "wp_visible_words": len(parsed[0].visible_words),
                                "preview_visible_words": len(parsed[1].visible_words),
                                "visible_source_links": len(parsed[0].visible_cites)})
    return {"release_state": "DRAFT_HARD_HOLD", "eligible": False, "publication_approved": False,
            "integrity_ok": bool(base.get("integrity_ok")) and not errors,
            "errors": sorted(set(errors)), "articles_inspected": len(details), "details": details,
            "warnings": list(base.get("warnings", [])) + [
                "Static HTML cannot detect site CSS, browser rendering, factual citation support or baseline manuscript depth",
                "All five source disputes, nine Shelter forks and qualified safety/QD approvals remain unselected/HARD HOLD"]}


def main():
    parser = argparse.ArgumentParser(description="R411 read-only visible citation custody - ALWAYS HARD HOLD")
    parser.add_argument("original", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("export_root", type=Path)
    a = parser.parse_args()
    try:
        raw = _r410.read_original(a.original)
        original = json.loads(raw.decode("utf-8"), object_pairs_hook=_r410.unique_pairs)
        manifest = json.loads(_r410.read_original(a.manifest).decode("utf-8"), object_pairs_hook=_r410.unique_pairs)
        exports = {}
        for entry in manifest["articles"]:
            slug = entry["slug"]
            if not isinstance(slug, str) or not _r410.SLUG.fullmatch(slug):
                raise ValueError("invalid original slug")
            exports[slug] = (_r410.read_original(a.export_root / "wordpress" / (slug + ".html")),
                             _r410.read_original(a.export_root / "preview" / (slug + ".html")))
        result = check(original, manifest, exports, raw_original=raw)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, OverflowError) as exc:
        result = {"release_state": "DRAFT_HARD_HOLD", "eligible": False,
                  "publication_approved": False, "integrity_ok": False, "errors": [str(exc)]}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
