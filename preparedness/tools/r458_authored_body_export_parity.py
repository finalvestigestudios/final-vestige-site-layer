#!/usr/bin/env python3
"""R458 — fail-closed authored-body-to-draft-export custody, WITHOUT release approval.

R457 attests source identity/citation bibliography and authored metadata; this
independent oracle proves the *entire authored body* (headings, notes, warnings,
figures, lists, tables and long-form analysis) survives BOTH output surfaces,
not merely citation counts. It never alters files or contacts a CMS/network.

Native invocation (after local native validate/build):
  python -I preparedness/tools/r458_authored_body_export_parity.py --root preparedness
A structural HOLD result is not a clinical, emergency, food, privacy or QD PASS.
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

HOLD = "DRAFT_HARD_HOLD"
MAX_INPUT = 5_000_000
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
LINK = re.compile(r"\{\{link:([a-z0-9-]+)\|([^}]+)\}\}")
INLINE = re.compile(r"\{\{inline-js:([a-z_]+\.js)\}\}")


class BodyHold(ValueError):
    """Integrity failure, never a human-qualified safety decision."""


class _BodyBoundary(HTMLParser):
    """Locate actual pa-body element boundaries, respecting nested divs/script."""

    def __init__(self, document: str):
        super().__init__(convert_charrefs=False)
        self.document = document
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", document)]
        self.start = None
        self.end = None
        self.depth = 0
        self.found = 0
        self.fault = None

    def absolute_offset(self) -> int:
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        is_body = tag == "div" and attrs.get("id") == "pa-main" and "pa-body" in (attrs.get("class") or "").split()
        if is_body:
            self.found += 1
            if self.found > 1 or self.depth:
                self.fault = "duplicate or nested article-body element"
                return
            self.start = self.absolute_offset() + len(self.get_starttag_text())
            self.depth = 1
        elif self.depth and tag == "div":
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        # Void/self-closing tags must not increase div nesting depth.
        if tag == "div" and dict(attrs).get("id") == "pa-main":
            self.fault = "self-closing article body"

    def handle_endtag(self, tag):
        if self.depth and tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.end = self.absolute_offset()


def extract_authored_region(document: str) -> str:
    if not isinstance(document, str) or not document or len(document.encode("utf-8")) > MAX_INPUT:
        raise BodyHold("missing/oversized rendered export")
    parser = _BodyBoundary(document)
    try:
        parser.feed(document)
        parser.close()
    except (ValueError, IndexError) as exc:
        raise BodyHold(f"unparseable rendered HTML: {exc}") from exc
    if parser.fault or parser.found != 1 or parser.depth != 0 or parser.start is None or parser.end is None:
        raise BodyHold(f"ambiguous/incomplete rendered body: {parser.fault or parser.found}")
    if parser.end <= parser.start:
        raise BodyHold("empty rendered article body")
    return document[parser.start:parser.end]


def checked_inline_js(root: Path, name: str) -> str:
    if not root.is_dir() or root.is_symlink():
        raise BodyHold("native Preparedness checkout root is absent or linked")
    path = root / "tools" / name
    if not path.is_file() or path.is_symlink() or (root / "tools").is_symlink():
        raise BodyHold(f"inline-JS original missing/linked: {name}")
    if not (0 < path.stat().st_size <= MAX_INPUT):
        raise BodyHold(f"invalid inline-JS original length: {name}")
    return path.read_text(encoding="utf-8", errors="strict")


def independently_resolve_body(root: Path, library, meta: dict, original: str) -> tuple[str, list[str]]:
    """Independent reproduction of documented build.py cite/link/inline contract."""
    if not isinstance(original, str) or not original.strip() or len(original.encode("utf-8")) > MAX_INPUT:
        raise BodyHold("missing/oversized original authored body")
    order = []

    def cite(match):
        sid = match.group(1)
        if sid not in library.register:
            raise BodyHold(f"authored citation {sid} absent from register")
        source = library.source_for(meta, sid)
        if not isinstance(source, dict) or source.get("id") != sid or not isinstance(source.get("title"), str):
            raise BodyHold(f"authored citation {sid} has wrong source identity")
        if sid not in order:
            order.append(sid)
        n = order.index(sid) + 1
        return (f'<sup class="pa-cite"><a href="#src-{n}" '
                f'aria-label="Source {n}: {escape(source["title"], quote=True)}">[{n}]</a></sup>')

    def link(match):
        slug, label = match.groups()
        if slug in library.articles:
            return f'<a href="{library.url_path(slug)}">{label}</a>'
        return label  # matches native builder's absent-target fallback

    body = INLINE.sub(lambda m: checked_inline_js(root, m.group(1)), original)
    body = CITE.sub(cite, body)
    body = LINK.sub(link, body)
    if "{{" in body:
        raise BodyHold("unresolved/unsupported authored macro")
    return body, order


def audit_pair(root: Path, library, meta: dict, wp: str, preview: str) -> dict:
    if not isinstance(meta, dict) or not isinstance(meta.get("_body"), str):
        raise BodyHold("missing original body metadata")
    slug = meta.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise BodyHold("invalid article identity")
    expected, source_ids = independently_resolve_body(root, library, meta, meta["_body"])
    for surface, document in (("wordpress", wp), ("private_preview", preview)):
        region = extract_authored_region(document)
        if region != expected:
            # Strict byte-for-byte equality means nested tables, action steps,
            # word order, caveats, editorial labels and headings cannot vanish.
            pos = next((i for i, (a, b) in enumerate(zip(region, expected)) if a != b), min(len(region), len(expected)))
            raise BodyHold(f"{slug}: {surface} authored body altered at character {pos}; "
                           f"expected {len(expected)} chars, found {len(region)}")
    return {"slug": slug, "source_ids": source_ids,
            "authored_bytes": len(meta["_body"].encode("utf-8")),
            "resolved_body_sha256": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
            "wordpress_body_sha256": hashlib.sha256(extract_authored_region(wp).encode("utf-8")).hexdigest(),
            "preview_body_sha256": hashlib.sha256(extract_authored_region(preview).encode("utf-8")).hexdigest()}


def _module(path: Path, name: str):
    if not path.is_file() or path.is_symlink():
        raise BodyHold(f"missing/linked trusted native module: {name}")
    spec = importlib.util.spec_from_file_location("r458_" + name, path)
    if not spec or not spec.loader:
        raise BodyHold(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_native(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise BodyHold("native Preparedness checkout absent/linked")
    build = _module(root / "tools" / "build.py", "build")
    parity = _module(root / "tools" / "r455_rendered_citation_parity.py", "citation_parity")
    custody = _module(root / "tools" / "r457_native_authority_export.py", "native_custody")
    lib = build.Library(root)
    # The full original source/metadata/35-slate/build-report/dual-export
    # safety HOLD is mandatory, not optional, before this independent oracle.
    previous = custody.verify_native(root, lib, parity)
    rows = previous.get("entries")
    if previous.get("qualified_qd_pass") is not False or not isinstance(rows, list) or len(rows) < 35:
        raise BodyHold("parent custody gate missing or claims QD approval")
    receipts = []
    seen = set()
    for row in rows:
        slug = row["slug"]
        if slug in seen or slug not in lib.articles:
            raise BodyHold("duplicated/unrecognized original article identity")
        seen.add(slug)
        meta = lib.articles[slug]
        folder = "tools" if meta.get("kind") == "tool" else "articles"
        body_bytes = custody.read_bytes_checked(root, root / "content" / folder / f"{slug}.body.html", label="original body")
        if meta.get("_body") != body_bytes.decode("utf-8", "strict"):
            raise BodyHold(f"{slug}: original authored-body mutated in memory")
        wp = custody.read_bytes_checked(root, root / "build" / "wp" / f"{slug}.html", label="actual WP export").decode("utf-8", "strict")
        preview = custody.read_bytes_checked(root, root / "build" / "preview" / f"{slug}.html", label="actual private preview").decode("utf-8", "strict")
        receipts.append(audit_pair(root, lib, meta, wp, preview))
    if set(lib.articles) != seen:
        raise BodyHold("source and export inventory diverged")
    return {"release_state": HOLD, "qualified_qd_pass": False,
            "source_claim_support_verified": False, "wordpress_published": False,
            "human_safety_review": "NOT_APPROVED", "native_build": "NOT_ATTESTED_BY_THIS_GATE",
            "article_and_tool_bodies_checked": len(receipts),
            "complete_body_surfaces_checked": 2 * len(receipts), "entries": receipts}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        print(json.dumps(verify_native(args.root.absolute()), sort_keys=True, indent=2))
        return 0
    except (BodyHold, OSError, UnicodeError, ValueError, KeyError, AttributeError, TypeError) as exc:
        print(json.dumps({"release_state": HOLD, "qualified_qd_pass": False,
                          "wordpress_published": False, "integrity": "HOLD", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
