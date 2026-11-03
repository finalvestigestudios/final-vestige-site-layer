#!/usr/bin/env python3
"""Private, read-only end-to-end citation fidelity gate for Preparedness drafts.

Checks the ORIGINAL author-scoped source reading, literal body cite token,
rendered inline marker, rendered footnote number and visible source-list link.
This establishes transport fidelity, NOT support for the claim, link accuracy,
medical/emergency safety, QD approval or permission to publish.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r93-rendered-citation-fidelity-private-hold-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"


class Gate(ValueError):
    """A draft citation, source presentation or release safeguard changed."""


def need(ok, message):
    if not ok:
        raise Gate(message)


def seal(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class CitationHTML(HTMLParser):
    """Scoped HTML parser: unrelated anchors cannot satisfy source checks."""

    VOID = frozenset(("area", "base", "br", "col", "embed", "hr", "img",
                      "input", "link", "meta", "param", "source", "track", "wbr"))

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.citations = []
        self.sources = []
        self._cite_anchor = None
        self._source_li = None
        self._inside_cite = 0
        self._seen_cite_anchor = 0

    def contains_class(self, name):
        return any(name in frame[1] for frame in self.stack)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        classes = frozenset(attrs.get("class", "").split())
        in_body = self.contains_class("pa-body")
        in_sources = self.contains_class("pa-sources")
        if tag == "sup" and "pa-cite" in classes and in_body:
            need(self._inside_cite == 0, "nested citation marker")
            self._inside_cite = 1
            self._seen_cite_anchor = 0
        elif tag == "a" and self._inside_cite:
            need(self._cite_anchor is None, "multiple inline anchors")
            self._cite_anchor = {"href": attrs.get("href"),
                                 "aria_label": attrs.get("aria-label"),
                                 "text": ""}
            self._seen_cite_anchor += 1
        elif tag == "li" and in_sources:
            need(self._source_li is None, "nested source list row")
            self._source_li = {"id": attrs.get("id"), "href": None,
                               "link_text": "", "text": "", "links": 0}
        elif tag == "a" and self._source_li is not None:
            self._source_li["links"] += 1
            if self._source_li["links"] == 1:
                self._source_li["href"] = attrs.get("href")
        if tag not in self.VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self._cite_anchor is not None:
            self._cite_anchor["text"] += data
        if self._source_li is not None:
            self._source_li["text"] += data
            if (self._source_li["links"] == 1 and
                    self.stack and self.stack[-1][0] == "a"):
                self._source_li["link_text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._cite_anchor is not None:
            self.citations.append(self._cite_anchor)
            self._cite_anchor = None
        if tag == "li" and self._source_li is not None:
            self.sources.append(self._source_li)
            self._source_li = None
        if tag == "sup" and self._inside_cite:
            need(self._seen_cite_anchor == 1 and self._cite_anchor is None,
                 "citation marker has zero/multiple anchors")
            self._inside_cite = 0
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def finish(self):
        need(not self._cite_anchor and not self._source_li and
             not self._inside_cite, "truncated citation/source HTML")
        return self


def audit_document(lib, meta, rendered):
    """One literal original citation -> one rendered source-specific workorder."""
    slug = meta["slug"]
    need(type(meta.get("_body")) is str, slug + ": missing complete original body")
    need(meta.get("status", {}).get("publish") == "draft",
         slug + ": unpublished article state changed")
    need(type(rendered) is str and rendered, slug + ": missing final rendered HTML")
    need(rendered.count('data-slug="' + slug + '"') == 1,
         slug + ": wrong/duplicate rendered document identity")
    need("Draft: not public" in rendered, slug + ": absent visible draft warning")
    need('Human source-link check' in rendered, slug + ": missing source-check notice")
    safety_state = meta.get("safety_review", {}).get("state")
    if safety_state == "pending":
        need("Safety review pending" in rendered and
             "A human safety review is required before this page can be published." in rendered,
             slug + ": pending human safety notice is absent")
    need(safety_state in ("pending", "approved", "not-required"),
         slug + ": unexpected safety state; manual reconciliation required")

    literal = [m.group(1) for m in CITE.finditer(meta["_body"])]
    need(bool(literal), slug + ": zero literal citation occurrences")
    expected_order = list(dict.fromkeys(literal))
    need(type(meta.get("source_use")) is dict and
         set(meta["source_use"]) == set(expected_order),
         slug + ": author-scoped source-use evidence differs from cited IDs")
    parsed = CitationHTML()
    parsed.feed(rendered)
    parsed.close()
    parsed.finish()
    need(len(parsed.citations) == len(literal),
         slug + ": inline citation occurrence count lost or gained")
    need(len(parsed.sources) == len(expected_order),
         slug + ": rendered distinct source list count lost or gained")
    need(len(set(x["id"] for x in parsed.sources)) == len(parsed.sources),
         slug + ": duplicate source-footnote destinations")

    number = {sid: n for n, sid in enumerate(expected_order, 1)}
    snapshots = {}
    for n, sid in enumerate(expected_order, 1):
        src = lib.source_for(meta, sid)
        need(src.get("id") == sid and type(src.get("url")) is str and
             src["url"].startswith("https://") and src.get("_origin") is not None,
             slug + ": original contributor-scoped source identity lost: " + sid)
        need(type(meta["source_use"][sid]) is str and meta["source_use"][sid].strip(),
             slug + ": missing complete local source scope: " + sid)
        actual = parsed.sources[n - 1]
        need(actual["id"] == "src-" + str(n),
             slug + ": wrong footnote destination: " + sid)
        need(actual["links"] == 1 and actual["href"] == src["url"],
             slug + ": source URL changed, duplicated or retargeted: " + sid)
        need(actual["link_text"] == src["title"],
             slug + ": original source title altered: " + sid)
        need("Used for: " + meta["source_use"][sid] in actual["text"],
             slug + ": original author-specific source-use reading hidden: " + sid)
        expected_check = ("Human source-link check complete"
                          if src.get("human_link_check") is True
                          else "Human source-link check pending")
        need(expected_check in actual["text"],
             slug + ": source human-link status misrepresented: " + sid)
        pending = (lib.crosswalk_groups.get(src["url"]) or {}).get("review_status") != "resolved"
        if src["url"] in lib.crosswalk_groups and pending:
            need("Shared-source reading scope: independent review pending" in actual["text"],
                 slug + ": unresolved URL collision is hidden: " + sid)
        snapshots[sid] = src

    kind = "tool" if meta.get("kind") == "tool" else "article"
    review_rows = []
    for occurrence, (sid, anchor) in enumerate(zip(literal, parsed.citations), 1):
        n = number[sid]
        src = snapshots[sid]
        need(anchor == {"href": "#src-" + str(n),
                        "aria_label": "Source " + str(n) + ": " + src["title"],
                        "text": "[" + str(n) + "]"},
             slug + ": citation marker/text/label was silently retargeted at " +
             str(occurrence))
        review_rows.append({
            "kind": kind, "slug": slug, "citation_ordinal": occurrence,
            "literal_source_ID": sid, "rendered_footnote_number": n,
            "literal_source_URL": src["url"], "original_reading_origin": src["_origin"],
            "original_source_use_UNABRIDGED": meta["source_use"][sid],
            "human_link_check_metadata": src.get("human_link_check") is True,
            "claim_support_verified": False, "human_claim_review": REVIEW,
            "qualified_safety_review": REVIEW, "independent_QD_review": REVIEW,
            "may_publish": False, "release_state": HOLD,
        })
    return review_rows


def audit_library(lib, render_article, wp_wrap, preview_wrap):
    """Read only existing bodies; never create planned tools or write to WordPress."""
    slated = {x["slug"] for x in lib.taxonomy["slate"]}
    planned_tools = {x["slug"] for x in lib.taxonomy["tools"]}
    actual_articles = {s for s, m in lib.articles.items() if m.get("kind") != "tool"}
    actual_tools = {s for s, m in lib.articles.items() if m.get("kind") == "tool"}
    need(len(slated) == 35 and actual_articles == slated,
         "35-article slate or available draft bodies changed; review required")
    need(len(planned_tools) == 6 and actual_tools <= planned_tools,
         "planned tool inventory or existing draft tools changed")
    routes, review_rows, state_counter = set(), [], Counter()
    for slug in sorted(lib.articles):
        meta = lib.articles[slug]
        route = lib.url_path(slug)
        need(route.startswith("/preparedness/") and route.endswith("/") and
             route not in routes, "duplicate or non-Preparedness draft route: " + route)
        routes.add(route)
        state_counter[meta["safety_review"]["state"]] += 1
        page = render_article(lib, slug)
        need(page["slug"] == slug and page["meta"] is meta,
             "rendered article identity mismatch: " + slug)
        inner = page["inner"]
        need(page["sources"] == list(dict.fromkeys(
            m.group(1) for m in CITE.finditer(meta["_body"]))),
            "build returned a source sequence different from original body: " + slug)
        wp = wp_wrap(lib, inner)
        preview = preview_wrap(lib, inner, meta["title"], meta["description"])
        need(type(wp) is str and wp.startswith("<!-- wp:html -->") and
             wp.endswith("<!-- /wp:html -->\n") and wp.count(inner) == 1,
             "WordPress draft wrapper loses original rendered document: " + slug)
        need(type(preview) is str and 'name="robots" content="noindex,nofollow"' in preview
             and preview.count(inner) == 1,
             "private preview loses draft or noindex warning: " + slug)
        review_rows.extend(audit_document(lib, meta, inner))
    need(len({(x["kind"], x["slug"], x["citation_ordinal"]) for x in review_rows})
         == len(review_rows), "citation ordinal collision")
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": HOLD,
        "may_publish": False, "independent_QD_approval": REVIEW,
        "qualified_safety_approval": REVIEW,
        "disclaimer": "Rendering fidelity only; not proof of any claim or medical safety.",
        "full_slate_article_count": len(slated),
        "actual_article_drafts": len(actual_articles),
        "planned_tools": len(planned_tools),
        "actual_tool_drafts": len(actual_tools),
        "missing_tool_drafts_NOT_WORDPRESS_READY": sorted(planned_tools - actual_tools),
        "actual_distinct_draft_routes": len(routes),
        "metadata_safety_states_NOT_QUALIFIED_APPROVALS": dict(sorted(state_counter.items())),
        "literal_citation_occurrences_reconciled_to_rendered_html": len(review_rows),
        "unabridged_rendered_source_workorders_NOT_APPROVED": review_rows,
    }
    report["sha256_seal"] = seal(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-json-stdout", action="store_true",
                    help="full literal URL/scope workorders: private local use only")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    need(not root.is_symlink(), "untrusted preparedness working tree")
    # An -I process does not inherit cwd packages; the trusted sibling builder
    # is explicitly loaded after checking it is a regular non-symlink file.
    trusted = root / "tools" / "build.py"
    need(trusted.is_file() and not trusted.is_symlink(), "trusted builder absent")
    sys.path.insert(0, str(trusted.parent))
    import build
    report = audit_library(build.Library(), build.build_article, build.wp_wrap,
                           build.preview_wrap)
    if args.private_json_stdout:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False))
    else:
        print(json.dumps({k:v for k,v in report.items()
                         if k != "unabridged_rendered_source_workorders_NOT_APPROVED"},
                         sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Gate, OSError, KeyError, ValueError) as exc:
        print("R93 PRIVATE CITATION FIDELITY HOLD: " + str(exc), file=sys.stderr)
        sys.exit(2)
