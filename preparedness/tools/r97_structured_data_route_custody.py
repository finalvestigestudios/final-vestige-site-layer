#!/usr/bin/env python3
"""R97 PRIVATE HOLD: independently bind structured data and generated navigation.

R93-R96 conserve citations, authored DOM, source readings, and visible safety
review shell. They do not verify the JSON-LD payload or generator-created
breadcrumbs, table of contents, and related links. An altered JSON-LD Article
could misrepresent publication, review, identity, or canonical destination
without changing visible words or any source citation.

This read-only gate does NOT validate source claims, emergency/medical safety,
browser CSS, human review, independent QD, or permission to publish.
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r97-private-structured-data-route-custody-hold-v1"
SITE = "https://finalvestige.com"
VOID = frozenset(("area", "base", "br", "col", "embed", "hr", "img",
                  "input", "link", "meta", "param", "source", "track", "wbr"))
SAFE_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class Gate(ValueError):
    """The private route/metadata custody contract has failed closed."""


def need(value, reason):
    if not value:
        raise Gate(reason)


def seal(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON-LD object key: " + key)
        result[key] = value
    return result


def parse_jsonld(raw):
    need(type(raw) is str and bool(raw.strip()), "empty JSON-LD payload")
    need(len(raw.encode("utf-8")) <= 100_000, "oversized JSON-LD payload")
    try:
        return json.loads(raw, object_pairs_hook=no_duplicate_keys,
                          parse_constant=lambda name: (_ for _ in ()).throw(
                              Gate("nonfinite JSON-LD number: " + name)))
    except (ValueError, TypeError) as exc:
        raise Gate("malformed or duplicate-key JSON-LD payload") from exc


class Trace(HTMLParser):
    """Record exact subtree event streams and enforce outer shell order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []
        self.stack = []
        self.root_count = 0
        self.shell_count = 0
        self.root_attrs = None
        self.shell_children = []
        self.root_children = []
        self.regions = {}
        self.scripts = []
        self.h1 = []
        self.skip = []
        self.skip_text = []

    def zone(self, name):
        return any(name in f["classes"] for f in self.stack)

    def handle_starttag(self, tag, pairs):
        need(len(pairs) == len(set(k for k, _ in pairs)),
             "duplicate HTML attributes: " + tag)
        attrs = dict(pairs)
        classes = set((attrs.get("class") or "").split())
        parent = self.stack[-1] if self.stack else None
        if parent and "pa-article" in parent["classes"]:
            self.root_children.append((tag, tuple(sorted(classes))))
        if parent and "pa-shell" in parent["classes"]:
            self.shell_children.append((tag, tuple(sorted(classes))))
        if "pa-article" in classes:
            need(tag == "div" and parent is None and self.root_count == 0,
                 "unexpected or duplicate article root")
            self.root_count += 1
            self.root_attrs = attrs
        elif parent is None:
            raise Gate("content outside private article root")
        if "pa-shell" in classes:
            self.shell_count += 1
        if tag == "a" and "pa-skip" in classes:
            self.skip.append(attrs)
        if tag == "script" and not self.zone("pa-body"):
            self.scripts.append((attrs, None))
        self.events.append(("open", tag, tuple(sorted(pairs))))
        if tag not in VOID:
            self.stack.append({"tag": tag, "classes": classes, "attrs": attrs,
                               "start": len(self.events) - 1, "text": ""})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        need(self.stack or not data.strip(), "unattributed text outside article root")
        self.events.append(("text", data))
        for frame in self.stack:
            frame["text"] += data

    def handle_comment(self, data):
        self.events.append(("comment", data))

    def handle_decl(self, decl):
        raise Gate("unexpected HTML declaration in private fragment")

    def handle_endtag(self, tag):
        need(self.stack and self.stack[-1]["tag"] == tag,
             "truncated or misnested private HTML: " + tag)
        frame = self.stack.pop()
        self.events.append(("end", tag))
        if tag == "a" and "pa-skip" in frame["classes"]:
            self.skip_text.append(frame["text"])
        kind = next((k for k in ("pa-crumbs", "pa-toc", "pa-related")
                     if k in frame["classes"]), None)
        if kind is not None:
            need(kind not in self.regions, "duplicate generated route region: " + kind)
            self.regions[kind] = self.events[frame["start"]:]
        if tag == "script" and not self.zone("pa-body"):
            need(self.scripts and self.scripts[-1][1] is None,
                 "untracked JSON-LD payload")
            self.scripts[-1] = (frame["attrs"], frame["text"])
        if tag == "h1" and self.zone("pa-head"):
            self.h1.append(frame["text"])

    def finish(self):
        need(not self.stack and self.root_count == 1 and self.shell_count == 1,
             "private article root/shell incomplete")
        return self


class Fragment(HTMLParser):
    """Independent structural signature for expected, safely escaped routes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        need(len(attrs) == len(set(k for k, _ in attrs)),
             "duplicate attribute in expected route")
        self.events.append(("open", tag, tuple(sorted(attrs))))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        self.events.append(("text", data))

    def handle_comment(self, data):
        self.events.append(("comment", data))

    def handle_endtag(self, tag):
        need(self.stack and self.stack[-1] == tag, "bad expected route markup")
        self.stack.pop()
        self.events.append(("end", tag))


def signature(markup):
    parser = Fragment()
    parser.feed(markup)
    parser.close()
    need(not parser.stack, "unclosed expected route markup")
    return parser.events


def e(text):
    return escape(text, quote=True)


def expected_routes(meta, lib):
    """Build route expectations from source metadata, not generated page HTML."""
    need(type(meta) is dict and type(lib.taxonomy) is dict, "invalid article inventory")
    slug = meta["slug"]
    section = meta["section"]
    track = meta["track"]
    base = lib.taxonomy["base_path"]
    need(base == "/preparedness/", "unexpected Preparedness base path")
    need(type(slug) is str and SAFE_SLUG.fullmatch(slug),
         "invalid article or tool URL slug")
    need(type(section) is str and SAFE_SLUG.fullmatch(section)
         and section in lib.sections, "invalid or unknown section route")
    need(track in lib.taxonomy["tracks"], "unknown source editorial track")
    need(meta["status"]["publish"] == "draft",
         "non-draft article cannot pass private release gate")
    path = base + section + "/" + slug + "/"
    canonical = SITE + path
    section_label = lib.sections[section]["label"]
    crumbs = [
        ("Final Vestige", "/"),
        ("The Preparedness Archive", base),
        (section_label, base + section + "/"),
        (meta["title"], None),
    ]
    links = []
    ld = []
    for pos, (label, href) in enumerate(crumbs, 1):
        if href is not None:
            links.append('<li><a href="' + e(href) + '">' + e(label) + '</a></li>')
            ld.append({"@type": "ListItem", "position": pos, "name": label,
                       "item": SITE + href})
        else:
            links.append('<li><span aria-current="page">' + e(label) + '</span></li>')
            ld.append({"@type": "ListItem", "position": pos, "name": label})
    crumb_nav = ('<nav class="pa-crumbs" aria-label="Breadcrumb"><ol>'
                 + "".join(links) + '</ol></nav>')
    # This is based on the original authored headings, not altered generated nav.
    headings = re.findall(r'<h2 id="([a-z0-9\-]+)"[^>]*>(.*?)</h2>',
                          meta["_body"], flags=re.S)
    headings = [(ident, re.sub(r"<[^>]+>", "", title).strip())
                for ident, title in headings if not ident.endswith("-h")]
    if len(headings) < 3:
        toc = None
    else:
        li = ''.join('<li><a href="#' + e(ident) + '">' + e(unescape(label))
                     + '</a></li>' for ident, label in headings)
        # The source builder already escapes heading HTML in the TOC. Parsing
        # character references lets this independent expectation compare
        # decoded text while retaining the original authored label meaning.
        toc = ('<nav class="pa-toc" aria-label="On this page"><h2>On this page</h2>'
               + '<ol>' + li + '</ol></nav>')
    related = []
    seen = set()
    for dest in meta.get("related", []):
        need(type(dest) is str and SAFE_SLUG.fullmatch(dest),
             "unsafe related article slug")
        need(dest not in seen, "repeated generated related-article link")
        seen.add(dest)
        if dest in lib.articles:
            target = lib.articles[dest]
            target_path = base + target["section"] + "/" + dest + "/"
            related.append('<li><a href="' + e(target_path) + '">' +
                           e(target["title"]) + '</a></li>')
    related_html = None
    if related:
        related_html = ('<aside class="pa-related" aria-labelledby="rel-h">'
                        '<h2 id="rel-h">Keep reading</h2><ul>' +
                        "".join(related) + '</ul></aside>')
    article = {
        "@type": "Article", "@id": canonical + "#article",
        "headline": meta["h1"], "description": meta["description"],
        "mainEntityOfPage": canonical, "dateModified": meta["updated"],
        "inLanguage": "en-US",
        "author": {"@type": "Organization", "name": "Final Vestige Studios"},
        "publisher": {"@type": "Organization", "name": "Final Vestige Studios",
                      "url": SITE + "/"},
        "isAccessibleForFree": True,
    }
    return {
        "canonical": canonical, "slug": slug,
        "root_attrs": {"class": "pa pa-article", "data-slug": slug,
                       "data-track": track, "data-section": section},
        "breadcrumbs": crumb_nav, "toc": toc, "related": related_html,
        "jsonld": {"@context": "https://schema.org",
                   "@graph": [article, {"@type": "BreadcrumbList",
                                        "itemListElement": ld}]},
    }


def audit_page(meta, page, lib):
    """Reconcile one private WordPress-ready page's non-editorial route shell."""
    expectations = expected_routes(meta, lib)
    slug = expectations["slug"]
    need(type(page) is dict and type(page.get("inner")) is str,
         slug + ": missing rendered draft")
    need(page.get("slug") == slug and page.get("canonical") ==
         expectations["canonical"], slug + ": page identity or canonical drift")
    p = Trace()
    p.feed(page["inner"])
    p.close()
    p.finish()
    need(p.root_attrs == expectations["root_attrs"],
         slug + ": root track, section or slug attributes changed")
    need(p.skip == [{"class": "pa-skip", "href": "#pa-main"}]
         and p.skip_text == ["Skip to the guide"],
         slug + ": skip-to-guide destination or label changed")
    need(p.h1 == [meta["h1"]], slug + ": visible article headline changed")
    for key, expected in (("pa-crumbs", expectations["breadcrumbs"]),
                          ("pa-toc", expectations["toc"]),
                          ("pa-related", expectations["related"])):
        found = p.regions.get(key)
        need((expected is None and found is None) or
             (expected is not None and found == signature(expected)),
             slug + ": generated " + key + " route or text changed")
    want_root = [("a", ("pa-skip",)), ("nav", ("pa-crumbs",)),
                 ("header", ("pa-head",)), ("div", ("pa-shell",)),
                 ("section", ("pa-sources",)), ("section", ("pa-review",))]
    if expectations["related"] is not None:
        want_root.append(("aside", ("pa-related",)))
    want_root.append(("script", ()))
    need(p.root_children == want_root,
         slug + ": unexpected/missing/reordered generated root content")
    want_shell = [("div", ("pa-body",))]
    if expectations["toc"] is not None:
        want_shell.insert(0, ("nav", ("pa-toc",)))
    need(p.shell_children == want_shell,
         slug + ": unexpected/missing/reordered generated body shell")
    need(len(p.scripts) == 1 and p.scripts[0][0] ==
         {"type": "application/ld+json"},
         slug + ": missing/duplicate/modified JSON-LD script")
    ld = parse_jsonld(p.scripts[0][1])
    need(ld == expectations["jsonld"],
         slug + ": changed structured metadata, unpublished state, or breadcrumb identity")
    return {
        "slug": slug, "canonical": expectations["canonical"],
        "authored_h1_preserved": True,
        "breadcrumb_items": 4,
        "generated_toc_present": expectations["toc"] is not None,
        "related_route_count": len(meta.get("related", [])),
        "structured_data_sha256": seal(ld),
        "release_state": "HOLD", "may_publish": False,
        "human_source_claim_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED", "independent_QD": "NOT_REVIEWED",
    }


def audit_library(lib, render, r96_audit, r95_audit, r93_document, r94_body):
    prior = r96_audit(lib, render, r95_audit, r93_document, r94_body)
    need(prior["release_state"] == "HOLD" and prior["may_publish"] is False,
         "upstream R96 custody is not fail-closed")
    need(prior["private_drafts"] == 36 and prior["real_article_drafts"] == 35
         and prior["real_tool_drafts"] == 1,
         "actual article/tool draft inventory changed")
    rows = []
    urls = set()
    for slug in sorted(lib.articles):
        meta = lib.articles[slug]
        row = audit_page(meta, render(lib, slug), lib)
        need(row["canonical"] not in urls,
             slug + ": duplicate private WordPress destination")
        urls.add(row["canonical"])
        rows.append(row)
    need(len(rows) == prior["private_drafts"], "rendered page inventory lost")
    report = {
        "schema": SCHEMA, "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "human_source_claim_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "limitations": "Generated navigation and JSON-LD integrity only; no human claims, safety, link, or browser verification.",
        "private_draft_pages": len(rows),
        "article_drafts": prior["real_article_drafts"],
        "tool_drafts": prior["real_tool_drafts"],
        "unbuilt_tools_NOT_IMPORTABLE": prior["unbuilt_tools_NOT_IMPORTABLE"],
        "prior_rendered_citations_conserved_R96": prior[
            "rendered_citations_rechecked_R93_R95_R96"],
        "unique_canonical_draft_routes": len(urls),
        "pages_with_structured_data": len(rows),
        "generated_breadcrumb_items": sum(r["breadcrumb_items"] for r in rows),
        "generated_tocs": sum(r["generated_toc_present"] for r in rows),
        "per_document_NOT_APPROVED": rows,
    }
    report["sha256_seal"] = seal(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    for name in ("build.py", "r93_rendered_citation_fidelity.py",
                 "r94_body_custody.py", "r95_dom_attribute_custody.py",
                 "r96_visible_source_safety_shell.py"):
        file = root / "tools" / name
        need(file.is_file() and not file.is_symlink(),
             "missing trusted upstream gate: " + name)
    sys.path.insert(0, str(root / "tools"))
    import build
    import r93_rendered_citation_fidelity as r93
    import r94_body_custody as r94
    import r95_dom_attribute_custody as r95
    import r96_visible_source_safety_shell as r96
    report = audit_library(build.Library(), build.build_article,
                           r96.audit_library, r95.audit_library,
                           r93.audit_document, r94.audit_body)
    if args.private_json_stdout:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps({key: value for key, value in report.items()
                          if key not in ("per_document_NOT_APPROVED",)},
                         sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Gate, ValueError) as exc:
        print(json.dumps({"release_state": "HOLD", "may_publish": False,
                          "gate": "R97_FAILED", "reason": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
