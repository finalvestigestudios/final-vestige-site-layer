#!/usr/bin/env python3
"""R95 private fail-closed original HTML DOM and link-attribute custody.

R93 checked citation/source fidelity; R94 checked textual reading depth. This
independent gate catches structural/attribute changes that can preserve BOTH:
relocated anchor wrappers, swapped hrefs, hidden safety notes, event-handler
injection, form target changes, and invisible added HTML elements. This does
NOT verify that any source supports a claim or that the advice is safe.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r95-private-original-dom-attribute-custody-hold-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
LINK = re.compile(r"\{\{link:([a-z0-9-]+)\|([^}]+)\}\}")
INLINE = re.compile(r"\{\{inline-js:([a-z_]+\.js)\}\}")
VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img",
                  "input", "link", "meta", "param", "source", "track", "wbr"})


class Gate(ValueError):
    """Original unabridged markup or an attribute has lost its custody."""


def need(ok, explanation):
    if not ok:
        raise Gate(explanation)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def expand_author_body(original, root, routes):
    """Independently resolve ONLY approved literal macros; never call builder."""
    need(type(original) is str and bool(original.strip()), "missing original body")
    need(type(routes) is dict, "missing exact target-route inventory")

    def inline(match):
        name = match.group(1)
        file = root / "tools" / name
        need(file.is_file() and not file.is_symlink(),
             "untrusted local author script: " + name)
        return file.read_text(encoding="utf-8")

    def link(match):
        slug, label = match.groups()
        if slug not in routes:
            return label  # planned-only article cannot become a broken link
        url = routes[slug]
        need(type(url) is str and url.startswith("/preparedness/") and
             url.endswith("/") and not any(c in url for c in '"<>'),
             "invalid intended local destination: " + slug)
        return '<a href="' + url + '">' + label + '</a>'

    text = INLINE.sub(inline, original)
    text = CITE.sub("", text)
    text = LINK.sub(link, text)
    need("{{" not in text, "unresolved original editorial macro")
    return text


class DOMWitness(HTMLParser):
    """Exact ordered HTML event stream; skip only inserted inline cite supers."""

    def __init__(self, rendered=False):
        super().__init__(convert_charrefs=True)
        self.rendered = rendered
        self.active = not rendered
        self.depth = 0
        self.body_count = 0
        self.skip = []
        self.stack = []
        self.events = []
        self.anchors = 0
        self.suppressed_citations = 0

    def _record(self, kind, *parts):
        if kind == "text" and self.events and self.events[-1][0] == "text":
            self.events[-1] = ("text", self.events[-1][1] + parts[0])
        else:
            self.events.append((kind, *parts))

    def handle_starttag(self, tag, pairs):
        keys = [k for k, _ in pairs]
        need(len(set(keys)) == len(keys), "duplicate HTML attribute: " + tag)
        attrs = tuple(sorted(pairs))
        classes = set((dict(pairs).get("class") or "").split())
        if self.rendered and not self.active:
            if tag == "div" and "pa-body" in classes:
                self.body_count += 1
                self.active = True
                self.depth = 1
            return
        if not self.active:
            return
        if self.skip:
            if tag not in VOID:
                self.skip.append(tag)
            return
        if self.rendered and tag == "sup" and "pa-cite" in classes:
            self.suppressed_citations += 1
            self.skip.append(tag)
            return
        need(not (self.rendered and tag == "div" and "pa-body" in classes),
             "unexpected nested .pa-body")
        self._record("start", tag, attrs)
        if tag == "a":
            self.anchors += 1
        if tag not in VOID:
            self.stack.append(tag)
            if self.rendered:
                self.depth += 1

    def handle_startendtag(self, tag, pairs):
        self.handle_starttag(tag, pairs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if self.skip:
            need(self.skip[-1] == tag,
                 "malformed inserted citation superstructure: " + tag)
            self.skip.pop()
            return
        if self.rendered and self.depth == 1 and tag == "div":
            need(not self.stack, "unclosed rendered editorial elements")
            self.active = False
            self.depth = 0
            return
        need(bool(self.stack) and self.stack[-1] == tag,
             "unbalanced original/rendered HTML element: " + tag)
        self.stack.pop()
        self._record("end", tag)
        if self.rendered:
            self.depth -= 1
            need(self.depth >= 1, "rendered wrapper closed too early")

    def handle_data(self, data):
        if self.active and not self.skip:
            self._record("text", data)

    def handle_comment(self, data):
        if self.active and not self.skip:
            self._record("comment", data)

    def handle_decl(self, decl):
        if self.active and not self.skip:
            self._record("declaration", decl)

    def finish(self):
        need(not self.stack and not self.skip, "truncated or unbalanced editorial HTML")
        if self.rendered:
            need(self.body_count == 1 and not self.active and self.depth == 0,
                 "missing, duplicate or unterminated rendered .pa-body")
        need(bool(self.events), "original or rendered HTML has no editorial events")
        return self


def audit_markup(slug, original, rendered, root, routes):
    need(re.fullmatch(r"[a-z0-9-]+", slug) is not None, "unsafe document slug")
    need(type(rendered) is str and bool(rendered.strip()), "missing rendered body")
    expected = DOMWitness()
    expected.feed(expand_author_body(original, root, routes))
    expected.close()
    expected.finish()
    actual = DOMWitness(rendered=True)
    actual.feed(rendered)
    actual.close()
    actual.finish()
    need(expected.events == actual.events,
         slug + ": original DOM, link target, attribute, or claim attachment changed")
    return {
        "slug": slug,
        "original_dom_events": len(expected.events),
        "rendered_dom_events": len(actual.events),
        "authored_anchors_preserved": expected.anchors,
        "inserted_inline_citations_skipped_NOT_APPROVED": actual.suppressed_citations,
        "original_dom_sha256": digest(expected.events),
        "may_publish": False,
        "qualified_safety_review": "NOT_REVIEWED",
        "human_source_claim_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "release_state": "HOLD",
    }


def audit_library(lib, render, r93_document, r94_body):
    """Existing 35 articles plus REAL tool drafts only; no CMS or disk writes."""
    expected_articles = {x["slug"] for x in lib.taxonomy["slate"]}
    planned_tools = {x["slug"] for x in lib.taxonomy["tools"]}
    actual_articles = {slug for slug, m in lib.articles.items()
                       if m.get("kind") != "tool"}
    actual_tools = {slug for slug, m in lib.articles.items()
                    if m.get("kind") == "tool"}
    need(len(expected_articles) == 35 and actual_articles == expected_articles,
         "complete original 35-article slate has changed")
    need(len(planned_tools) == 6 and actual_tools <= planned_tools,
         "real versus planned tool inventory is ambiguous")
    routes = {}
    for slug, meta in lib.articles.items():
        route = (lib.taxonomy["base_path"] + meta["section"] + "/" + slug + "/")
        need(route.startswith("/preparedness/") and route.endswith("/"),
             "invalid original internal URL")
        need(route not in routes.values(), "duplicate WordPress draft URL: " + route)
        routes[slug] = route
    rows = []
    total_citations = 0
    total_blocks = 0
    for slug in sorted(lib.articles):
        meta = lib.articles[slug]
        need(meta["status"]["publish"] == "draft",
             slug + ": original unpublished state changed")
        page = render(lib, slug)
        need(page["meta"] is meta and page["slug"] == slug,
             slug + ": non-identical draft metadata returned")
        row = audit_markup(slug, meta["_body"], page["inner"], lib.root, routes)
        body = r94_body(slug, meta["_body"], page["inner"], lib.root)
        citations = r93_document(lib, meta, page["inner"])
        need(row["inserted_inline_citations_skipped_NOT_APPROVED"] == len(citations),
             slug + ": citation count differs from independently audited R93")
        total_citations += len(citations)
        total_blocks += body["original_reading_blocks"]
        rows.append(row)
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "human_source_claim_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "limitation": "Exact DOM transport custody only; NOT proof of factual or medical safety.",
        "slated_articles": len(expected_articles),
        "planned_tools": len(planned_tools),
        "real_article_drafts": len(actual_articles),
        "real_tool_drafts": len(actual_tools),
        "missing_tool_drafts_NOT_IMPORTABLE": sorted(planned_tools - actual_tools),
        "distinct_private_draft_urls": len(routes),
        "original_reading_blocks_rechecked_R94": total_blocks,
        "rendered_citation_occurrences_rechecked_R93": total_citations,
        "original_dom_events_preserved": sum(x["original_dom_events"] for x in rows),
        "authored_anchors_preserved": sum(x["authored_anchors_preserved"] for x in rows),
        "per_draft_dom_custody_NOT_APPROVED": rows,
    }
    report["sha256_seal"] = digest(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    for filename in ("build.py", "r93_rendered_citation_fidelity.py",
                     "r94_body_custody.py"):
        target = root / "tools" / filename
        need(target.is_file() and not target.is_symlink(),
             "trusted local read-only dependency missing: " + filename)
    sys.path.insert(0, str(root / "tools"))
    import build
    import r93_rendered_citation_fidelity as r93
    import r94_body_custody as r94
    report = audit_library(build.Library(), build.build_article,
                           r93.audit_document, r94.audit_body)
    if args.private_json_stdout:
        print(canonical(report))
    else:
        print(canonical({k: v for k, v in report.items()
                         if k != "per_draft_dom_custody_NOT_APPROVED"}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Gate, OSError, ValueError, KeyError) as exc:
        print("R95 PRIVATE ORIGINAL DOM CUSTODY HOLD: " + str(exc),
              file=sys.stderr)
        sys.exit(2)
