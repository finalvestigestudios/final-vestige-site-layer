#!/usr/bin/env python3
"""R94 read-only Preparedness original-reading-depth to WordPress-body custody gate.

Compares the ordered literal editorial blocks in original source bodies with the
WordPress-rendered `.pa-body`, independently of the builder's rendered-text
output. Citation anchor fidelity is separately enforced by R93. Neither gate
verifies medical safety, source validity, fact accuracy or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r94-original-editorial-body-custody-private-hold-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
LINK = re.compile(r"\{\{link:([a-z0-9-]+)\|([^}]+)\}\}")
INLINE = re.compile(r"\{\{inline-js:([a-z_]+\.js)\}\}")
BLOCKS = frozenset({"p", "li", "h1", "h2", "h3", "h4", "h5", "h6",
                    "th", "td", "caption", "blockquote", "dt", "dd",
                    "pre", "summary", "strong", "em"})
VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img",
                  "input", "link", "meta", "param", "source", "track", "wbr"})


class CustodyGate(ValueError):
    """Literal original editorial material was missing, moved or changed."""


def require(ok, why):
    if not ok:
        raise CustodyGate(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def whitespace(s):
    return " ".join(s.split())


def expand_original(body, root):
    """Independent token normalization, not a call to build.resolve_tokens()."""
    require(isinstance(body, str) and body.strip(), "original HTML body absent")

    def inline(match):
        p = root / "tools" / match.group(1)
        require(p.is_file() and not p.is_symlink(), "untrusted inline script")
        return p.read_text(encoding="utf-8")

    expanded = INLINE.sub(inline, body)
    expanded = CITE.sub("", expanded)
    expanded = LINK.sub(lambda m: m.group(2), expanded)
    require("{{" not in expanded, "unrecognized unresolved original body token")
    return expanded


class EditorialWitness(HTMLParser):
    """Ordered nested block text plus exact script hashes; no source-list leakage."""

    def __init__(self, rendered=False):
        super().__init__(convert_charrefs=True)
        self.rendered = rendered
        self.active = not rendered
        self.depth = 0
        self.body_count = 0
        self.frames = []
        self.blocks = []
        self.skip_depth = 0
        self.skip_kind = None
        self.skip_chunks = []
        self.scripts = []

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        classes = set((attrs.get("class") or "").split())
        if self.rendered and not self.active:
            if tag == "div" and "pa-body" in classes:
                self.active = True
                self.depth = 1
                self.body_count += 1
            return
        if not self.active:
            return
        if self.rendered and tag not in VOID:
            self.depth += 1
        if self.skip_depth:
            if tag not in VOID:
                self.skip_depth += 1
            return
        if tag in {"script", "style"}:
            self.skip_depth = 1
            self.skip_kind = tag
            self.skip_chunks = []
            return
        if tag == "sup" and "pa-cite" in classes:
            require(self.rendered, "unexpected embedded citation in original body")
            self.skip_depth = 1
            self.skip_kind = "citation"
            return
        if tag in BLOCKS:
            self.frames.append([tag, []])

    def handle_startendtag(self, tag, pairs):
        self.handle_starttag(tag, pairs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.active:
            return
        if self.skip_depth:
            if self.skip_kind == "script":
                self.skip_chunks.append(data)
            return
        for _, fragments in self.frames:
            fragments.append(data)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if self.skip_depth:
            self.skip_depth -= 1
            if self.skip_depth == 0:
                if self.skip_kind == "script":
                    self.scripts.append(hashlib.sha256(
                        "".join(self.skip_chunks).encode("utf-8")).hexdigest())
                self.skip_kind = None
                self.skip_chunks = []
        elif tag in BLOCKS:
            require(self.frames and self.frames[-1][0] == tag,
                    "malformed editorial block stack: " + tag)
            name, fragments = self.frames.pop()
            self.blocks.append([name, whitespace("".join(fragments))])
        if self.rendered:
            self.depth -= 1
            require(self.depth >= 0, "rendered body depth underflow")
            if self.depth == 0:
                require(not self.frames, "unclosed rendered editorial blocks")
                self.active = False

    def finish(self):
        require(not self.frames and not self.skip_depth, "unclosed original/rendered editorial markup")
        if self.rendered:
            require(self.body_count == 1 and not self.active and self.depth == 0,
                    "missing, duplicate or unterminated .pa-body")
        require(bool(self.blocks), "zero editorial reading blocks")
        return self


def witness(markup, rendered=False):
    parser = EditorialWitness(rendered=rendered)
    parser.feed(markup)
    parser.close()
    return parser.finish()


def audit_body(slug, original, rendered_html, root):
    """Fail closed on loss, reordering, replacement or emphasis of literal text."""
    require(re.fullmatch(r"[a-z0-9-]+", slug) is not None, "invalid draft slug")
    before = witness(expand_original(original, root), rendered=False)
    after = witness(rendered_html, rendered=True)
    require(before.blocks == after.blocks,
            slug + ": original unabridged editorial block sequence changed")
    require(before.scripts == after.scripts,
            slug + ": literal original executable script lost or altered")
    return {"slug": slug, "original_reading_blocks": len(before.blocks),
            "literal_script_blocks": len(before.scripts),
            "body_block_sha256": digest(before.blocks),
            "script_hashes": before.scripts, "may_publish": False,
            "editorial_reading_review": "NOT_REVIEWED", "release_state": "HOLD"}


def audit_library(lib, build_article, r93_audit_document):
    """Audit only the real article/tool draft pairs, never planned placeholders."""
    articles = set(x["slug"] for x in lib.taxonomy["slate"])
    tools = set(x["slug"] for x in lib.taxonomy["tools"])
    drafts = set(lib.articles)
    require(len(articles) == 35 and drafts & articles == articles,
            "35 original article draft pairs not present")
    require(len(tools) == 6 and (drafts - articles) <= tools,
            "unexpected existing tool or incomplete six-tool planning slate")
    rows = []
    citations = 0
    for slug in sorted(drafts):
        m = lib.articles[slug]
        require(m["status"]["publish"] == "draft", slug + ": release-state drift")
        page = build_article(lib, slug)
        require(page["slug"] == slug and page["meta"] is m,
                slug + ": non-identical original metadata returned from builder")
        row = audit_body(slug, m["_body"], page["inner"], lib.root)
        citations += len(r93_audit_document(lib, m, page["inner"]))
        rows.append(row)
    report = {"schema": SCHEMA, "issue": 136, "release_state": "HOLD",
              "may_publish": False, "qualified_safety_review": "NOT_REVIEWED",
              "source_claim_review": "NOT_REVIEWED", "independent_QD": "NOT_REVIEWED",
              "notes": "Literal body/render custody only; not factual, medical or source approval.",
              "article_draft_pairs": len(articles), "planned_tools": len(tools),
              "actual_tool_draft_pairs": len(drafts - articles),
              "missing_tool_draft_pairs_NOT_IMPORTABLE": sorted(tools - drafts),
              "real_drafts_read": len(rows),
              "literal_body_blocks_preserved": sum(r["original_reading_blocks"] for r in rows),
              "literal_script_blocks_preserved": sum(r["literal_script_blocks"] for r in rows),
              "citations_independently_rechecked_through_R93": citations,
              "private_editorial_body_witnesses_NOT_APPROVED": rows}
    report["sha256_seal"] = digest(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    for name in ("build.py", "r93_rendered_citation_fidelity.py"):
        p = root / "tools" / name
        require(p.is_file() and not p.is_symlink(), "trusted local dependency absent")
    sys.path.insert(0, str(root / "tools"))
    import build
    import r93_rendered_citation_fidelity as r93
    report = audit_library(build.Library(), build.build_article, r93.audit_document)
    if args.private_json_stdout:
        print(canonical(report))
    else:
        print(canonical({k: v for k, v in report.items()
                         if k != "private_editorial_body_witnesses_NOT_APPROVED"}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (CustodyGate, OSError, KeyError, ValueError) as exc:
        print("R94 READ-ONLY ORIGINAL BODY CUSTODY HOLD: " + str(exc), file=sys.stderr)
        sys.exit(2)
