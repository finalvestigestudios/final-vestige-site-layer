#!/usr/bin/env python3
"""R148: fail-closed rendered Preparedness citation and reading-depth custody.

Offline/draft-only. A structural check is NEVER source/medical review, QD, merchant
verification, an approval to publish, or a substitute for real browser QA.
"""
from __future__ import annotations
import argparse
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")
LINK = re.compile(r"\{\{link:([a-z0-9-]+)\|([^}]+)\}\}")
INLINE = re.compile(r"\{\{inline-js:[a-z_]+\.js\}\}")
WS = re.compile(r"\s+")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class Hold(ValueError):
    pass


def require(ok, why):
    if not ok:
        raise Hold(why)


def norm(s):
    return WS.sub(" ", unescape(s)).strip()


def read(p):
    require(p.is_file() and not p.is_symlink(), f"missing or linked evidence: {p}")
    return p.read_text(encoding="utf-8", errors="strict")


def json_read(p):
    result = json.loads(read(p))
    require(isinstance(result, dict), f"invalid JSON object: {p}")
    return result


class EvidenceHTML(HTMLParser):
    """Read only the article body and sources, detecting hidden source evidence."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.body_count = 0
        self.sources_count = 0
        self.body_text = []
        self.cites = []
        self.sources = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("class", "id", "href", "hidden", "style", "aria-hidden", "inert"):
            require(sum(x == k for x, _ in attrs) <= 1, f"duplicate HTML attribute: {k}")
        classes = set(a.get("class", "").split())
        parent = self.stack[-1] if self.stack else {"region": None, "hidden": False, "suppress": False, "li": None}
        hidden = (parent["hidden"] or "hidden" in a or "inert" in a
                  or a.get("aria-hidden", "").lower() == "true"
                  or bool(re.search(r"(?:display\s*:\s*none|visibility\s*:\s*hidden)", a.get("style", ""), re.I)))
        region = parent["region"]
        if "pa-body" in classes:
            self.body_count += 1
            region = "body"
            require(not hidden, "article evidence body is hidden")
        if "pa-sources" in classes:
            self.sources_count += 1
            region = "sources"
            require(not hidden, "sources section is hidden")
        if region == "body" and tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "section", "div", "li", "blockquote", "br"):
            self.body_text.append(" ")
        suppress = parent["suppress"] or tag in ("script", "style", "template") or (tag == "sup" and "pa-cite" in classes)
        li = parent["li"] if region == "sources" else None
        if region == "sources" and tag == "li":
            require(not hidden, "hidden source entry")
            li = {"id": a.get("id"), "urls": []}
            self.sources.append(li)
        if region == "sources" and tag == "a" and li is not None:
            require(not hidden, "hidden source hyperlink")
            li["urls"].append(a.get("href"))
        if region == "body" and tag == "a" and parent["suppress"] and parent["region"] == "body":
            # Only a source-number link within a sup.pa-cite is evidence.
            if any(f["tag"] == "sup" and f["cite"] for f in self.stack):
                require(not hidden, "hidden citation marker")
                self.cites.append(a.get("href"))
        self.stack.append({"tag": tag, "region": region, "hidden": hidden,
                           "suppress": suppress, "li": li,
                           "cite": tag == "sup" and "pa-cite" in classes})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        require(self.stack, f"unexpected closing tag {tag}")
        # Ignore browser-tolerated malformed HTML tag nesting, but reject
        # evidence source nodes losing scope due to early closings.
        if self.stack[-1]["tag"] == tag:
            self.stack.pop()
        else:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i]["tag"] == tag:
                    del self.stack[i:]
                    break

    def handle_data(self, data):
        if self.stack:
            f = self.stack[-1]
            if f["region"] == "body" and not f["hidden"] and not f["suppress"]:
                self.body_text.append(data)


def evidence_parse(markup):
    parser = EvidenceHTML()
    parser.feed(markup)
    parser.close()
    return parser


def expected_text(body):
    require(body.count("{{cite:") == len(CITE.findall(body)), "malformed citation token")
    raw = CITE.sub("", body)
    raw = LINK.sub(lambda m: m.group(2), raw)
    raw = INLINE.sub("", raw)
    require("{{" not in raw, "unresolved source-body token")
    # Use the same independent HTML text extractor for raw body, without
    # needing to trust the WordPress builder's word-count implementation.
    parser = evidence_parse('<div class="pa-body">' + raw + '</div>')
    require(parser.body_count == 1, "invalid source-body evidence section")
    return norm("".join(parser.body_text))


def verify_document(body, meta, wp, preview, source_by_id):
    """Return a draft-only structural result. Source URLs must be author-scoped."""
    require(meta.get("status", {}).get("publish") == "draft", "publication state not draft")
    slug = meta.get("slug")
    require(isinstance(slug, str) and SLUG.fullmatch(slug), "invalid document slug")
    ids = CITE.findall(body)
    require(body.count("{{cite:") == len(ids), "malformed citation token")
    use = meta.get("source_use")
    require(isinstance(use, dict) and set(use) == set(ids), "source_use/citation mismatch")
    require(all(isinstance(v, str) and v.strip() for v in use.values()), "missing author reading scope")
    ordered = list(dict.fromkeys(ids))
    require(all(x in source_by_id for x in ordered), "missing author-specific source")
    for sid in ordered:
        u = source_by_id[sid]
        require(isinstance(u, str) and urlsplit(u).scheme == "https" and bool(urlsplit(u).hostname),
                "untrusted source URL")
    number = {sid: i for i, sid in enumerate(ordered, 1)}
    expected_links = [f"#src-{number[sid]}" for sid in ids]
    expected_sources = [(f"src-{i}", source_by_id[sid]) for i, sid in enumerate(ordered, 1)]
    source_text = expected_text(body)
    require(len(source_text) >= 10, "empty article evidence")
    outputs = {}
    for label, html_text in (("wp", wp), ("preview", preview)):
        doc = evidence_parse(html_text)
        require(doc.body_count == doc.sources_count == 1,
                f"{label}: missing or duplicated evidence region")
        require(norm("".join(doc.body_text)) == source_text,
                f"{label}: body reading text truncated or rewritten")
        require(doc.cites == expected_links,
                f"{label}: missing, reordered or forged citation markers")
        actual = [(s["id"], s["urls"]) for s in doc.sources]
        require(len(actual) == len(expected_sources), f"{label}: source entry count drift")
        for (source_id, urls), (wanted_id, wanted_url) in zip(actual, expected_sources):
            require(source_id == wanted_id and urls.count(wanted_url) == 1 and len(urls) == 1,
                    f"{label}: missing, reordered or changed author-specific source URL")
        outputs[label] = {"body_characters": len(source_text),
                          "citation_occurrences": len(ids), "unique_sources": len(ordered)}
    return {"slug": slug, "status": "DRAFT_RENDER_EVIDENCE_CHECKED_RELEASE_HOLD",
            "outputs": outputs, "publication_allowed": False,
            "independent_qd": "NOT_APPROVED", "medical_safety_verified": False}


def source_index(root, origins):
    variants = {}
    all_files = [("base", root / "sources/register.json")]
    all_files += [(p.stem, p) for p in sorted((root / "sources/fragments").glob("*.json"))]
    for origin, file in all_files:
        records = json_read(file).get("sources")
        require(isinstance(records, list), f"source register invalid: {file}")
        for record in records:
            sid, url = record.get("id"), record.get("url")
            require(isinstance(sid, str) and isinstance(url, str), "malformed source identity")
            key = (origin, sid)
            require(key not in variants, f"duplicate source origin/id: {key}")
            variants[key] = url
    def scoped(slug, ids):
        origin = origins.get(slug, "base")
        out = {}
        for sid in ids:
            key = (origin, sid) if (origin, sid) in variants else ("base", sid)
            require(key in variants, f"{slug}: missing author-scoped source {sid}")
            out[sid] = variants[key]
        return out
    return scoped


def inspect(root, *, expected_articles=35, expected_tools=6, expected_citations=2000):
    root = Path(root).resolve(strict=True)
    crosswalk = json_read(root / "sources/crosswalk.json")
    origins = crosswalk.get("article_origins", {})
    require(isinstance(origins, dict), "missing article origin crosswalk")
    find_source = source_index(root, origins)
    counts, documents, citations = {}, [], 0
    for kind, expected in (("articles", expected_articles), ("tools", expected_tools)):
        path = root / "content" / kind
        metas = {p.name.removesuffix(".meta.json"): p for p in path.glob("*.meta.json")}
        bodies = {p.name.removesuffix(".body.html"): p for p in path.glob("*.body.html")}
        require(len(metas) == expected and set(metas) == set(bodies),
                f"{kind}: missing/duplicate article body/metadata")
        counts[kind] = expected
        for slug in sorted(metas):
            meta, body = json_read(metas[slug]), read(bodies[slug])
            require(meta.get("slug") == slug, "body/metadata slug mismatch")
            sources = find_source(slug, CITE.findall(body))
            wp = read(root / "build/wp" / f"{slug}.html")
            preview = read(root / "build/preview" / f"{slug}.html")
            doc = verify_document(body, meta, wp, preview, sources)
            citations += doc["outputs"]["wp"]["citation_occurrences"] if kind == "articles" else 0
            documents.append(doc)
    require(citations == expected_citations, f"citation baseline changed: {citations}")
    return {"schema": "FV-PREP-R148-RENDER-CUSTODY-1",
            "state": "DRAFT_RENDER_STRUCTURAL_CHECK_PASSED_RELEASE_HOLD",
            "counts": counts, "article_citations": citations, "documents": documents,
            "publication_allowed": False, "independent_qd": "NOT_APPROVED",
            "medical_safety_verified": False, "merchant_offer_verified": False,
            "live_website_verified": False}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--preparedness", type=Path, default=Path("preparedness"))
    opt = a.parse_args(argv)
    outcome = {"schema": "FV-PREP-R148-RENDER-CUSTODY-1", "state": "HOLD",
               "publication_allowed": False, "independent_qd": "NOT_APPROVED",
               "medical_safety_verified": False, "live_website_verified": False}
    try:
        outcome.update(inspect(opt.preparedness))
        code = 0
    except (Hold, ValueError, TypeError, OSError, UnicodeError) as exc:
        outcome["error"], code = str(exc), 2
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
