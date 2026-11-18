#!/usr/bin/env python3
"""R471: authenticated, read-only WordPress and noindex preview export custody.

Independently recompute all local draft exports from their original authored input.
A prebuilt file is never a publication, source-truth, accessibility, or QD approval.
This command never builds, writes, publishes, visits WordPress, or changes a route.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HOLD = "DRAFT_HARD_HOLD"
PARENT_BLOB = "9a34357c68463b1ab4cc60f1024711455bf23043"
BUILDER_BLOB = "349173d1e1d735eade218d95c7a0a2649c8cccd9"

class ExportHold(ValueError):
    pass

def demand(ok, msg):
    if not ok:
        raise ExportHold(msg)

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def read(root, rel):
    root = root.resolve()
    path = root / rel
    demand(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root),
           "missing, linked or escaped export/input: " + rel)
    return path.read_bytes()

def strict_json(raw):
    def unique(pairs):
        d = {}
        for key, value in pairs:
            demand(key not in d, "duplicate JSON property: " + key)
            d[key] = value
        return d
    return json.loads(raw, object_pairs_hook=unique)

def audit_exports(expected, actual, report, expected_articles):
    """Pure, side-effect-free gate for an exact deterministic draft export inventory."""
    demand(len(expected_articles) == 35 and len(set(expected_articles)) == 35,
           "35 original article identities were not preserved")
    demand(set(actual) == set(expected), "missing/extra WP or private-preview export")
    demand(all(k.startswith(("wp/", "preview/")) and k.endswith(".html")
               and ".." not in k and "\\" not in k for k in expected), "unsafe export path")
    demand(all(isinstance(data, bytes) and data for data in expected.values()),
           "incomplete authoritative rendering")
    for rel, want in sorted(expected.items()):
        demand(actual[rel] == want, "rendered WordPress/preview byte drift: " + rel)
    wp = {x.removeprefix("wp/").removesuffix(".html") for x in actual if x.startswith("wp/")}
    preview = {x.removeprefix("preview/").removesuffix(".html") for x in actual if x.startswith("preview/")}
    demand(wp == preview and set(expected_articles).issubset(wp),
           "missing/duplicated original article output or WP/preview mismatch")
    rows = report.get("articles")
    demand(isinstance(rows, list), "missing build report article list")
    slugs = [r.get("slug") for r in rows]
    demand(len(slugs) == len(set(slugs)) and set(expected_articles).issubset(slugs),
           "build report lost or duplicated original article")
    canonicals = [r.get("canonical") for r in rows]
    demand(all(isinstance(x, str) and x.startswith("https://finalvestige.com/preparedness/")
               for x in canonicals) and len(canonicals) == len(set(canonicals)),
           "duplicate or external canonical destination")
    safety = report.get("release_evidence") or {}
    demand(safety.get("state") == "HOLD"
           and safety.get("independent_qa_verified") is False
           and safety.get("wordpress_publication_performed") is False,
           "false QD/publication or premature release state")
    for s in expected_articles:
        document = expected["wp/" + s + ".html"].decode("utf-8")
        demand("Draft: not public" in document
               and "Independent safety/source and QD verification pending" in document
               and "pa-src-use" in document and "pa-review" in document
               and "{{cite:" not in document,
               "article safety/source/citation disclosure missing: " + s)
    return {
        "state": "GENERATED_DRAFT_EXPORT_BYTES_MATCH_AUTHORED_INPUT",
        "release_state": HOLD, "articles_checked": len(expected_articles),
        "export_files_checked": len(actual), "qualified_qd_pass": False,
        "source_claims_human_verified": False, "browser_accessibility_verified": False,
        "may_publish": False, "wordpress_writes": False,
    }

def load_module(root, rel, sha, name):
    raw = read(root, rel)
    demand(blob(raw) == sha, "inherited trusted Python Git blob mismatch: " + rel)
    spec = importlib.util.spec_from_file_location(name, root / rel)
    demand(spec is not None and spec.loader is not None, "cannot load source: " + rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def native(root):
    root = root.resolve()
    parent = load_module(root, "tools/r470_css_citation_exposure.py",
                         PARENT_BLOB, "r471_r470_parent")
    previous = parent.native(root)
    demand(previous.get("articles") == 35 and previous.get("citation_occurrences") == 2000,
           "inherited original citation/source/CSS verification missing")
    builder = load_module(root, "tools/build.py", BUILDER_BLOB, "r471_pinned_builder")
    lib = builder.Library(root)
    originals = {s: m for s, m in lib.articles.items() if m.get("kind") != "tool"}
    demand(len(originals) == 35 and all(m.get("status", {}).get("publish") == "draft"
                                      for m in originals.values()),
           "35 original draft manuscripts not intact")
    render = {}
    rows = []
    for slug in lib.articles:
        article = builder.build_article(lib, slug)
        meta = article["meta"]
        inner = article["inner"]
        render["wp/" + slug + ".html"] = builder.wp_wrap(lib, inner).encode("utf-8")
        render["preview/" + slug + ".html"] = builder.preview_wrap(
            lib, inner, meta["h1"] + " | The Preparedness Archive",
            meta["description"]).encode("utf-8")
        rows.append({key: article[key] for key in
                     ("slug", "words", "minutes", "sources", "canonical")})
    hubs = []
    for sec in lib.taxonomy["sections"]:
        hub = builder.build_hub(lib, sec["slug"], include_drafts=True)
        if hub:
            key = hub["slug"] + ".html"
            render["wp/" + key] = builder.wp_wrap(lib, hub["inner"]).encode("utf-8")
            render["preview/" + key] = builder.preview_wrap(
                lib, hub["inner"], hub["title"], hub["description"]).encode("utf-8")
            hubs.append({"section": sec["slug"], "guides": hub["count"]})
    landing = builder.build_landing(lib, include_drafts=True)
    desc = ("Evidence-based household preparedness and a historical record of how "
            "earlier generations managed without modern infrastructure.")
    render["wp/landing.html"] = builder.wp_wrap(lib, landing["inner"]).encode("utf-8")
    render["preview/landing.html"] = builder.preview_wrap(
        lib, landing["inner"], "The Preparedness Archive | Final Vestige", desc).encode("utf-8")
    report = strict_json(read(root, "build/build-report.json").decode("utf-8"))
    demand(report.get("articles") == rows and report.get("hubs") == hubs
           and report.get("landing") == {key: landing[key] for key in
                                             ("populated_sections", "article_cards")},
           "native build report disagrees with original-authored input")
    actual = {}
    for kind in ("wp", "preview"):
        folder = root / "build" / kind
        demand(folder.is_dir() and not folder.is_symlink(), "missing/linked generated directory")
        for file in folder.iterdir():
            demand(file.is_file() and not file.is_symlink() and file.suffix == ".html",
                   "unexpected generated output or symlink")
            rel = kind + "/" + file.name
            demand(rel in render, "unexpected generated article/URL: " + rel)
            actual[rel] = read(root, "build/" + rel)
    return audit_exports(render, actual, report, sorted(originals))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        result = native(args.root)
    except (ExportHold, ValueError, KeyError, TypeError, OSError, UnicodeError,
            ImportError, AssertionError) as err:
        result = {"state": "WORDPRESS_EXPORT_CUSTODY_FAILURE_HARD_HOLD",
                  "release_state": HOLD, "qualified_qd_pass": False,
                  "may_publish": False, "wordpress_writes": False, "error": str(err)}
    print(json.dumps(result, sort_keys=True))
    return 2  # Exact draft rendering is NOT permission to publish.

if __name__ == "__main__":
    sys.exit(main())
