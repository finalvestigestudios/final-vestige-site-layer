#!/usr/bin/env python3
"""R412: fail-closed semantic and accessible citation custody overlay; ALWAYS HARD HOLD.

Scope: unselected 35-article WordPress-ready / private-preview drafts only.
Not a browser, accessibility certification, citation fact-check, safety sign-off or release.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location("r411_visible_evidence_gate", Path(__file__).with_name("r411_visible_evidence_gate.py"))
_r411 = module_from_spec(_spec)
_spec.loader.exec_module(_r411)

BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote",
          "figcaption", "caption", "dt", "dd", "td", "th", "summary", "pre"}
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,127}\Z")
WORD = _r411.WORD
MAX_DEPTH = 96
MAX_ELEMENTS = 30000
MAX_ATTRS = 64


class SemanticCitationHTML(_r411.VisibleEvidenceHTML):
    """Conservative static parser to compare *where* words and citations appear."""

    def __init__(self):
        super().__init__()
        self.frames = []
        self.semantic_events = []
        self.accessible_cites = []
        self.identifiers = set()
        self.nodes = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        # Always retain R411 concealed markup / balancing detection.
        super().handle_starttag(tag, attrs)
        self.nodes += 1
        if self.nodes > MAX_ELEMENTS:
            self.errors.append("HTML element limit exceeded")
        if len(attrs) > MAX_ATTRS:
            self.errors.append("HTML attribute limit exceeded")
        if len(self.frames) >= MAX_DEPTH:
            self.errors.append("HTML nesting depth exceeded")
        a = dict(attrs)
        for key, value in attrs:
            if value is not None and any(ch in _r411.FORMAT_CONTROLS or
                                         (ord(ch) < 32 and ch not in "\t\n\r") for ch in value):
                self.errors.append("Unicode/control character in attribute: " + key)
        ident = a.get("id")
        if ident is not None:
            if not isinstance(ident, str) or not ID.fullmatch(ident):
                self.errors.append("unsafe/ambiguous HTML identifier")
            elif ident in self.identifiers:
                self.errors.append("duplicate HTML identifier: " + ident)
            else:
                self.identifiers.add(ident)
        if tag in BLOCKS and (a.get("role") or "").lower() in {"none", "presentation", "img", "button"}:
            self.errors.append("semantic block role suppressed or changed")
        if tag == "a" and ("data-source-id" in a or "href" in a):
            role = (a.get("role") or "link").lower()
            if role != "link":
                self.errors.append("citation link role overridden")
            if a.get("tabindex") is not None and a.get("tabindex") != "0":
                self.errors.append("citation link keyboard tab order overridden")
            if "aria-labelledby" in a or "aria-describedby" in a:
                self.errors.append("citation refers to unverified accessible description")
        if tag not in _r411.VOID:
            self.frames.append({"tag": tag, "words": [], "href": a.get("href"),
                                "source_id": a.get("data-source-id"), "aria_label": a.get("aria-label"),
                                "is_block": tag in BLOCKS, "is_link": tag == "a"})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _r411.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        # The parent checks visible text and bidi formatting controls.
        super().handle_data(data)
        if not self._is_hidden():
            words = WORD.findall(data)
            for frame in self.frames:
                if frame["is_block"] or frame["is_link"]:
                    frame["words"].extend(words)

    def handle_endtag(self, tag):
        tag = tag.lower()
        super().handle_endtag(tag)
        if tag in _r411.VOID:
            return
        if not self.frames or self.frames[-1]["tag"] != tag:
            self.errors.append("ambiguous semantic nesting at " + tag)
            # R411 already fails on misnesting; no attempt to recover semantics.
            return
        frame = self.frames.pop()
        words = tuple(frame["words"])
        if frame["is_block"]:
            self.semantic_events.append(("block", tag, words))
        if frame["is_link"]:
            label = " ".join(words).strip()
            sid, href = frame["source_id"], frame["href"]
            if not words:
                self.errors.append("citation has no reader-visible accessible text")
            aria = frame["aria_label"]
            if aria is not None and tuple(WORD.findall(aria)) != words:
                self.errors.append("citation aria-label changes visible link meaning")
            context = tuple(x["tag"] for x in self.frames if x["is_block"])
            record = ("citation", sid, href, words, context)
            self.semantic_events.append(record)
            self.accessible_cites.append((sid, href, label, aria))

    def finish(self):
        super().finish()
        if self.frames:
            self.errors.append("unterminated semantic element")
        return self


def check(original, manifest, exports, *, raw_original=None, test_only=False):
    """Always held: structural results cannot imply safe advice or publication approval."""
    base = _r411.check(original, manifest, exports, raw_original=raw_original, test_only=test_only)
    errors = list(base.get("errors", []))
    records = []
    if not isinstance(exports, dict):
        errors.append("invalid semantic export map")
    else:
        for slug in sorted(exports, key=str):
            pair = exports[slug]
            if not isinstance(slug, str) or not isinstance(pair, (list, tuple)) or len(pair) != 2:
                errors.append("invalid semantic export entry")
                continue
            parsed = []
            for side, raw in zip(("wordpress", "preview"), pair):
                if isinstance(raw, bytes):
                    try:
                        raw = raw.decode("utf-8", "strict")
                    except UnicodeError:
                        errors.append("invalid semantic UTF-8: " + slug)
                        continue
                if not isinstance(raw, str) or not 10 <= len(raw.encode("utf-8")) <= 1_000_000:
                    errors.append("invalid semantic HTML length/type: " + slug)
                    continue
                try:
                    parser = SemanticCitationHTML()
                    parser.feed(raw)
                    parser.finish()
                except (ValueError, TypeError, OverflowError, RecursionError) as exc:
                    errors.append("semantic HTML parser failure " + slug + ": " + str(exc))
                    continue
                errors.extend(slug + " [" + side + "]: " + error for error in parser.errors)
                parsed.append(parser)
            if len(parsed) != 2:
                errors.append("missing semantic HTML pair: " + slug)
                continue
            if parsed[0].semantic_events != parsed[1].semantic_events:
                errors.append("paragraph/heading/link semantic placement differs between exports: " + slug)
            if parsed[0].accessible_cites != parsed[1].accessible_cites:
                errors.append("citation accessible label parity differs between exports: " + slug)
            records.append({"slug": slug, "wordpress_semantic_events": len(parsed[0].semantic_events),
                            "preview_semantic_events": len(parsed[1].semantic_events),
                            "wordpress_citations": len(parsed[0].accessible_cites)})
    return {"release_state": "DRAFT_HARD_HOLD", "eligible": False,
            "publication_approved": False, "integrity_ok": bool(base.get("integrity_ok")) and not errors,
            "errors": sorted(set(errors)), "articles_inspected": len(records), "details": records,
            "warnings": list(base.get("warnings", [])) + [
                "Semantic equivalence of export pairs is not original-manuscript reading-depth preservation",
                "Static parsing cannot establish computed CSS accessibility, source-to-claim support or safety/QD clearance",
                "No manuscript variant/source dispute resolution and no paid offer or publication authorization"]}


def main():
    p = argparse.ArgumentParser(description="R412 semantic citation custody: always DRAFT_HARD_HOLD")
    p.add_argument("original", type=Path)
    p.add_argument("manifest", type=Path)
    p.add_argument("export_root", type=Path)
    args = p.parse_args()
    try:
        raw = _r411._r410.read_original(args.original)
        original = json.loads(raw.decode("utf-8"), object_pairs_hook=_r411._r410.unique_pairs)
        manifest = json.loads(_r411._r410.read_original(args.manifest).decode("utf-8"),
                              object_pairs_hook=_r411._r410.unique_pairs)
        exports = {}
        for entry in manifest["articles"]:
            slug = entry["slug"]
            if not isinstance(slug, str) or not _r411._r410.SLUG.fullmatch(slug) or slug in exports:
                raise ValueError("unsafe/duplicate article slug")
            exports[slug] = (_r411._r410.read_original(args.export_root / "wordpress" / (slug + ".html")),
                             _r411._r410.read_original(args.export_root / "preview" / (slug + ".html")))
        result = check(original, manifest, exports, raw_original=raw)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, OverflowError, AttributeError) as exc:
        result = {"release_state": "DRAFT_HARD_HOLD", "eligible": False,
                  "publication_approved": False, "integrity_ok": False, "errors": [str(exc)]}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
