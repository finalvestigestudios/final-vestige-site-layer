#!/usr/bin/env python3
"""R96 PRIVATE HOLD: visible source, draft and safety-review shell custody.

R93 audits citation/source identity; R94 text; R95 authored DOM. R96 checks the
BUILDER-INSERTED shell outside the authored body and the formerly opaque
inserted citation supers, where retained text could be hidden or re-attributed.
Structural visibility checks are NOT a substitute for browser/CSS QA,
independent claim verification, qualified safety review, or QD approval.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r96-visible-source-review-shell-private-hold-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
VOID = frozenset(("area", "base", "br", "col", "embed", "hr", "img",
                  "input", "link", "meta", "param", "source", "track", "wbr"))
INVISIBLE_STYLE = re.compile(
    r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse)"
    r"|opacity\s*:\s*0(?:\.0+)?\s*(?:;|$)|content-visibility\s*:\s*hidden"
    r"|font-size\s*:\s*0(?:px|em|rem|%)?(?:;|$))", re.I)
FORBIDDEN_CONTENT = frozenset(("template", "iframe", "object", "embed", "script",
                               "style", "form", "input", "button", "svg", "canvas"))
SENSITIVE = frozenset(("pa-head", "pa-review", "pa-sources", "pa-cite"))


class Gate(ValueError):
    """Private transport/visibility integrity failed. Release remains HOLD."""


def need(condition, reason):
    if not condition:
        raise Gate(reason)


def seal(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def invisible(attrs):
    style = attrs.get("style") or ""
    return ("hidden" in attrs or "inert" in attrs or
            (attrs.get("aria-hidden") or "").lower().strip() == "true" or
            bool(INVISIBLE_STYLE.search(style)))


class Witness(HTMLParser):
    """Strict stack; local text custody, critical visibility and citation shape."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.article_count = 0
        self.article_slug = None
        self.counts = {k: 0 for k in ("pa-head", "pa-body", "pa-sources", "pa-review")}
        self.sections = {}
        self.cites = []
        self.rows = []
        self.source_anchors = 0

    def zone(self, name):
        return next((f for f in reversed(self.stack) if name in f["classes"]), None)

    def guarded(self):
        return any(f["classes"] & SENSITIVE for f in self.stack)

    def handle_starttag(self, tag, pairs):
        keys = [k for k, _ in pairs]
        need(len(keys) == len(set(keys)), "duplicate HTML attribute: " + tag)
        attrs = dict(pairs)
        classes = set((attrs.get("class") or "").split())
        parent = self.stack[-1] if self.stack else None
        in_article = self.zone("pa-article") is not None
        if "pa-article" in classes:
            need(not in_article and self.article_count == 0 and tag == "div",
                 "duplicate or nested article root")
            self.article_count += 1
            self.article_slug = attrs.get("data-slug")
            need(bool(self.article_slug), "missing rendered article slug")
            in_article = True
        if in_article:
            sensitive_here = bool(classes & SENSITIVE) or self.guarded()
            if invisible(attrs) and (sensitive_here or "pa-article" in classes
                                     or "pa-body" in classes):
                raise Gate("hidden, inert or aria-hidden critical evidence: " + tag)
            # The existing authoring template has one bounded Print button.
            # It is not a source link or claim and must never accept edits.
            print_button = (tag == "button" and parent is not None and
                            "pa-printbar" in parent["classes"] and attrs == {
                                "type": "button", "class": "pa-btn pa-btn--ghost",
                                "onclick": "window.print()"})
            if sensitive_here and tag in FORBIDDEN_CONTENT and not print_button:
                raise Gate("active/opaque element in critical evidence: " + tag)
            if sensitive_here and not print_button and any(
                    k.startswith("on") or k in ("ping", "download") for k in attrs):
                raise Gate("event handler or link side effect in critical evidence: " + tag)
            if sensitive_here and attrs.get("role") in ("presentation", "none"):
                raise Gate("critical evidence removed from accessibility tree: " + tag)
            region_tags = {"pa-head": "header", "pa-body": "div",
                           "pa-sources": "section", "pa-review": "section"}
            for name, expected_tag in region_tags.items():
                if name in classes:
                    need(tag == expected_tag,
                         "wrong element kind for critical shell region: " + name)
                    need(self.counts[name] == 0, "duplicate critical shell region: " + name)
                    self.counts[name] += 1
            if "pa-cite" in classes:
                need(tag == "sup" and self.zone("pa-body") is not None,
                     "citation marker outside article body or wrong element")
                need(self.zone("pa-cite") is None, "nested citation marker")
                need(set(attrs) == {"class"} and classes == {"pa-cite"},
                     "unexpected citation superstructure attributes")
            if self.zone("pa-cite"):
                need(parent is not None and
                     ((parent["tag"] == "sup" and tag == "a") or False),
                     "opaque or nested element in citation marker")
                need(set(attrs) == {"href", "aria-label"},
                     "unexpected citation anchor attributes")
            if self.zone("pa-sources") and tag == "a":
                need(parent is not None and parent["tag"] == "li",
                     "source link must be a direct source-row child")
                need(set(attrs) == {"href", "rel"} and attrs["rel"] == "noopener",
                     "unsafe or altered outbound source link attributes")
            if "pa-cite" in classes and self.zone("pa-sources"):
                raise Gate("citation marker inside source list")
        f = {"tag": tag, "attrs": attrs, "classes": classes, "text": "", "anchors": []}
        if in_article and tag == "a":
            marker = self.zone("pa-cite")
            if marker is not None:
                marker["anchors"].append(f)
            row = next((x for x in reversed(self.stack)
                        if x["tag"] == "li" and self.zone("pa-sources")), None)
            if row is not None:
                row["anchors"].append(f)
                self.source_anchors += 1
        if tag not in VOID:
            self.stack.append(f)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        for f in self.stack:
            f["text"] += data
        if self.zone("pa-cite") and self.stack[-1]["tag"] == "sup" and data.strip():
            raise Gate("unattributed text adjacent to citation anchor")

    def handle_comment(self, data):
        need(not self.guarded(), "comment in citation, source or review evidence")

    def handle_endtag(self, tag):
        need(bool(self.stack) and self.stack[-1]["tag"] == tag,
             "unbalanced or misnested HTML in private rendered shell: " + tag)
        f = self.stack.pop()
        if "pa-cite" in f["classes"]:
            need(len(f["anchors"]) == 1 and f["anchors"][0]["tag"] == "a",
                 "citation marker must contain exactly one direct anchor")
            anchor = f["anchors"][0]
            need(f["text"] == anchor["text"],
                 "extra invisible/unattributed citation text")
            self.cites.append(anchor)
        if f["tag"] == "li" and any("pa-sources" in x["classes"] for x in self.stack):
            need(bool(f["attrs"].get("id")), "source row has no footnote target")
            need(len(f["anchors"]) == 1, "source row needs exactly one outbound link")
            self.rows.append(f)
        for key in self.counts:
            if key in f["classes"]:
                self.sections[key] = f

    def finish(self):
        need(not self.stack, "truncated HTML document")
        need(self.article_count == 1, "rendered article root missing")
        need(all(v == 1 for v in self.counts.values()),
             "missing/duplicate critical shell regions: " + str(self.counts))
        return self


def audit_shell(meta, rendered, source_rows):
    """Inspect the entire builder-inserted review/source shell, read only."""
    slug = meta["slug"]
    need(type(rendered) is str and rendered, slug + ": empty rendered body")
    need(meta.get("status", {}).get("publish") == "draft",
         slug + ": publish state is not draft")
    need(type(meta.get("_body")) is str, slug + ": missing original body")
    need(type(meta.get("source_use")) is dict, slug + ": missing author-scoped source-use")
    literals = CITE.findall(meta["_body"])
    ids = list(dict.fromkeys(literals))
    need(literals and len(ids) == len(source_rows), slug + ": source variant count changed")
    need(set(ids) == set(meta["source_use"]), slug + ": source-use keys changed")
    need(all(s["id"] == sid for s, sid in zip(source_rows, ids)),
         slug + ": source variant ordering/identity changed")

    p = Witness()
    p.feed(rendered)
    p.close()
    p.finish()
    need(p.article_slug == slug, slug + ": rendered article slug changed")
    need(len(p.rows) == len(ids), slug + ": source-footnote list incomplete")
    need(len(p.cites) == len(literals), slug + ": inserted citation count changed")
    head = p.sections["pa-head"]["text"]
    review = p.sections["pa-review"]["text"]
    sources = p.sections["pa-sources"]["text"]
    need("Draft: not public" in head, slug + ": visible draft warning missing")
    need("Editorial status" in review and "Safety review" in review
         and "Last source check" in review and "Recheck when" in review,
         slug + ": visible editorial/safety review record missing")
    need("Sources and verification" in sources
         and "machine-assisted source check" in sources
         and "not independent human link verification" in sources,
         slug + ": visible source-method limitation missing")
    state = meta.get("safety_review", {}).get("state")
    need(state in ("pending", "approved", "not-required"),
         slug + ": unknown human safety review state")
    if state == "pending":
        need("Safety review pending" in head and
             "A human safety review is required before this page can be published." in review,
             slug + ": visible pending safety review warning missing")
    elif state == "approved":
        need("Approved by " in review, slug + ": original metadata review label changed")
    else:
        need("Not required for this topic." in review,
             slug + ": original not-required label missing")
    order = {sid: n for n, sid in enumerate(ids, 1)}
    for n, (sid, src, li) in enumerate(zip(ids, source_rows, p.rows), 1):
        need(li["attrs"]["id"] == "src-" + str(n),
             slug + ": source footnote target changed")
        link = li["anchors"][0]
        need(link["attrs"]["href"] == src["url"] and src["url"].startswith("https://")
             and link["text"] == src["title"],
             slug + ": source URL, text or provenance changed")
        need(type(meta["source_use"][sid]) is str and
             bool(meta["source_use"][sid].strip()),
             slug + ": original source reading scope empty")
        need("Used for: " + meta["source_use"][sid] in li["text"],
             slug + ": authored source reading scope disappeared")
        marker = ("Human source-link check complete" if src.get("human_link_check") is True
                  else "Human source-link check pending")
        need(marker in li["text"],
             slug + ": human link-verification state hidden/misrepresented")
    for idx, (sid, marker) in enumerate(zip(literals, p.cites), 1):
        num = order[sid]
        a = marker["attrs"]
        need(a["href"] == "#src-" + str(num) and
             a["aria-label"] == "Source " + str(num) + ": " + source_rows[num - 1]["title"]
             and marker["text"] == "[" + str(num) + "]",
             slug + ": rendered citation anchor hidden/malformed at " + str(idx))
    return {
        "slug": slug, "rendered_citations": len(p.cites),
        "rendered_sources": len(p.rows), "source_link_anchors": p.source_anchors,
        "metadata_safety_state_NOT_REVIEWED": state,
        "visible_safety_review_record": True,
        "visible_draft_notice": True,
        "may_publish": False, "release_state": "HOLD",
        "human_source_claim_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
    }


def audit_library(lib, render, r95_audit, r93_document, r94_body):
    """Run R95->R94/R93 plus R96 over actual drafts; never write the CMS."""
    prior = r95_audit(lib, render, r93_document, r94_body)
    need(prior["release_state"] == "HOLD" and prior["may_publish"] is False,
         "upstream R95 evidence unexpectedly released")
    need(prior["real_article_drafts"] == 35 and prior["planned_tools"] == 6,
         "full article/tool inventory drifted")
    rows = []
    for slug in sorted(lib.articles):
        meta = lib.articles[slug]
        page = render(lib, slug)
        ids = list(dict.fromkeys(CITE.findall(meta["_body"])))
        sources = [lib.source_for(meta, sid) for sid in ids]
        rows.append(audit_shell(meta, page["inner"], sources))
    need(len(rows) == prior["distinct_private_draft_urls"],
         "real WordPress draft count drifted")
    need(sum(x["rendered_citations"] for x in rows) ==
         prior["rendered_citation_occurrences_rechecked_R93"],
         "citation counts drifted across independent R95/R96 parsers")
    need(sum(x["rendered_sources"] for x in rows) ==
         sum(x["source_link_anchors"] for x in rows),
         "source-list anchors not one-to-one")
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "qualified_safety_review": "NOT_REVIEWED",
        "human_source_claim_review": "NOT_REVIEWED", "independent_QD": "NOT_REVIEWED",
        "limitation": "Structural visibility and transport only: no browser/CSS, source support or medical safety verdict.",
        "full_slate_articles": prior["slated_articles"],
        "real_article_drafts": prior["real_article_drafts"],
        "real_tool_drafts": prior["real_tool_drafts"],
        "planned_tools": prior["planned_tools"],
        "unbuilt_tools_NOT_IMPORTABLE": prior["missing_tool_drafts_NOT_IMPORTABLE"],
        "private_drafts": len(rows),
        "rendered_citations_rechecked_R93_R95_R96": sum(x["rendered_citations"] for x in rows),
        "distinct_source_rows_with_visible_links": sum(x["rendered_sources"] for x in rows),
        "original_dom_events_rechecked_R95": prior["original_dom_events_preserved"],
        "per_document_NOT_APPROVED": rows,
    }
    report["sha256_seal"] = seal(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    for name in ("build.py", "r93_rendered_citation_fidelity.py", "r94_body_custody.py",
                 "r95_dom_attribute_custody.py"):
        p = root / "tools" / name
        need(p.is_file() and not p.is_symlink(),
             "trusted read-only gate missing: " + name)
    sys.path.insert(0, str(root / "tools"))
    import build
    import r93_rendered_citation_fidelity as r93
    import r94_body_custody as r94
    import r95_dom_attribute_custody as r95
    report = audit_library(build.Library(), build.build_article, r95.audit_library,
                           r93.audit_document, r94.audit_body)
    if args.private_json_stdout:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps({k: v for k, v in report.items()
                          if k != "per_document_NOT_APPROVED"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Gate, OSError, ValueError, KeyError) as e:
        print("R96 PRIVATE SHELL VISIBILITY HOLD: " + str(e), file=sys.stderr)
        sys.exit(2)
