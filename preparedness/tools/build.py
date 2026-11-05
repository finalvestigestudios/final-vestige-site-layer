#!/usr/bin/env python3
"""Build the Preparedness Archive into WordPress-ready block markup and local preview pages.

Inputs  (preparedness/):  taxonomy.json, sources/register.json, assets/preparedness.css,
                          content/articles/<slug>.meta.json + <slug>.body.html, content/pages/landing.*
Outputs (preparedness/build/): wp/<slug>.html   (one wp:html block, ready for a DRAFT page)
                               preview/<slug>.html (standalone page for local QA)
                               build-report.json

Body tokens:  {{cite:source-id}}  numbered footnote, resolved against sources/register.json
              {{link:article-slug}} internal link, rendered only if that article is built
Nothing here publishes anything. Output is for review and for creating WordPress drafts.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from urllib.parse import urlsplit, urlunsplit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://finalvestige.com"
WORDS_PER_MINUTE = 220


def review_alias_key(url: str) -> str:
    """Only conservative terminal-slash equivalence for a review worklist.

    This is never an authority for merging source claims or URL redirects.
    Keep the original, literal source URL in WordPress citations.
    """
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc,
                       (parsed.path or '/').rstrip('/') or '/',
                       parsed.query, parsed.fragment))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(s: str) -> str:
    return html.escape(s, quote=True)


class Library:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.taxonomy = load_json(root / "taxonomy.json")
        crosswalk_file = root / "sources" / "crosswalk.json"
        self.crosswalk = load_json(crosswalk_file) if crosswalk_file.exists() else {}
        self.crosswalk_groups = {g["url"]: g for g in self.crosswalk.get("groups", [])}
        # Match a shared-source warning to the actual contributor + source ID
        # + literal URL, not an unrelated author who cited the same web page.
        self.crosswalk_member_groups = {}
        for group in self.crosswalk.get("groups", []):
            for variant in group["variants"]:
                source = variant["source"]
                key = (variant["origin"], source["id"], source["url"])
                if key in self.crosswalk_member_groups:
                    raise ValueError(f"duplicate crosswalk source identity: {key}")
                self.crosswalk_member_groups[key] = group
        self.article_origins = self.crosswalk.get("article_origins", {})
        self.source_variants: dict[str, list[dict]] = {}

        def add_source(source: dict, origin: str) -> None:
            # Preserve every original source record. One URL may have been read at
            # different depths by independent contributors. Never merge its claims.
            row = {**source, "_origin": origin}
            self.source_variants.setdefault(source["id"], []).append(row)

        for source in load_json(root / "sources" / "register.json")["sources"]:
            add_source(source, "base")
        for fragment in sorted((root / "sources" / "fragments").glob("*.json")):
            for source in load_json(fragment)["sources"]:
                add_source(source, fragment.stem)

        self.register = {}
        for sid, variants in self.source_variants.items():
            urls = {v["url"] for v in variants}
            if len(urls) != 1:
                raise ValueError(f"duplicate source id '{sid}' has conflicting URLs")
            url = next(iter(urls))
            verified = [v for v in variants if v.get("verified_on")]
            # A verified source must never be redefined without an explicit,
            # exhaustively documented crosswalk. A placeholder may be upgraded
            # once by a fragment with exactly the same URL.
            if len(verified) > 1 or (verified and variants[0].get("verified_on") and len(variants) > 1):
                group = self.crosswalk_groups.get(url)
                declared = {(v["origin"], v["source"]["id"]) for v in group["variants"]
                            if v["source"]["id"] == sid} if group else set()
                observed = {(v["_origin"], v["id"]) for v in variants}
                if declared != observed:
                    raise ValueError(f"duplicate source id '{sid}' is not documented in source crosswalk")
            # This global index is retained for existing tests and known-id checks.
            # Source claims shown to readers are ALWAYS selected by article origin.
            self.register[sid] = verified[0] if verified else variants[0]

        self.css = (root / "assets" / "preparedness.css").read_text(encoding="utf-8")
        self.sections = {s["slug"]: s for s in self.taxonomy["sections"]}
        self.slate = {a["slug"]: a for a in self.taxonomy["slate"]}
        self.articles: dict[str, dict] = {}
        for meta_path in sorted((root / "content" / "articles").glob("*.meta.json")):
            meta = load_json(meta_path)
            if meta["slug"] != meta_path.name.removesuffix(".meta.json"):
                raise ValueError(f"article slug mismatch: {meta_path.name} vs {meta['slug']}")
            if meta["slug"] in self.articles:
                raise ValueError(f"duplicate article slug '{meta['slug']}'")
            body = meta_path.with_name(meta_path.name.replace(".meta.json", ".body.html")).read_text(encoding="utf-8")
            meta["_body"] = body
            self.articles[meta["slug"]] = meta
        for meta_path in sorted((root / "content" / "tools").glob("*.meta.json")):
            meta = load_json(meta_path)
            if meta["slug"] in self.articles:
                raise ValueError(f"duplicate article/tool slug '{meta['slug']}'")
            meta["kind"] = "tool"
            meta["_body"] = meta_path.with_name(meta_path.name.replace(".meta.json", ".body.html")).read_text(encoding="utf-8")
            self.articles[meta["slug"]] = meta

    def source_for(self, meta: dict, sid: str) -> dict:
        """Find the source AS READ for this particular article, not a global merger.

        Reusing a source ID does not make the reading scope of another cluster
        apply to this article. A verified source from an unrelated fragment is
        never allowed to silently approve a base unverified placeholder.
        """
        if sid not in self.source_variants:
            # Preserve compatibility with isolated synthetic in-memory fixtures.
            if sid in self.register:
                return self.register[sid]
            raise KeyError(f"{meta['slug']}: unknown source id '{sid}'")
        versions = self.source_variants[sid]
        origin = self.article_origins.get(meta["slug"], "base")
        own = next((v for v in versions if v["_origin"] == origin), None)
        if own is not None:
            return own
        base = next((v for v in versions if v["_origin"] == "base"), None)
        if base is not None:
            return base
        raise KeyError(f"{meta['slug']}: source '{sid}' was not checked by its own cluster or the base archive")

    def url_path(self, slug: str) -> str:
        a = self.articles.get(slug) or self.slate[slug]
        return f"{self.taxonomy['base_path']}{a['section']}/{slug}/"

    def section_path(self, section: str) -> str:
        return f"{self.taxonomy['base_path']}{section}/"


def slate_status(lib: "Library", slug: str) -> str:
    """Derived from the article itself; the taxonomy 'status' field is not authoritative."""
    meta = lib.articles.get(slug)
    if not meta:
        return "not-started"
    if meta["status"]["publish"] == "published":
        return "published"
    return "safety-approved-draft" if meta["safety_review"]["state"] == "approved" else "drafted-pending-safety-review"


def write_lf(path: Path, text: str) -> None:
    """Write UTF-8 bytes with LF newlines on every platform.

    Path.write_text() translates LF to CRLF on Windows, which made generated WordPress and preview
    outputs differ byte-for-byte between operating systems and broke the export-custody byte checks."""
    path.write_bytes(text.encode("utf-8"))


def fmt_date(iso: str | None) -> str:
    if not iso:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
        y, m, d = iso.split("-")
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        return f"{months[int(m) - 1]} {int(d)}, {y}"
    return iso


def word_count(body_html: str) -> int:
    text = re.sub(r"<(style|script)[\s\S]*?</\1>", " ", body_html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


def resolve_tokens(lib: Library, meta: dict) -> tuple[str, list[str]]:
    """Replace cite/link tokens. Returns (body_html, ordered list of cited source ids)."""
    order: list[str] = []

    def cite(m: re.Match) -> str:
        sid = m.group(1)
        if sid not in lib.register:
            raise KeyError(f"{meta['slug']}: unknown source id '{sid}'")
        if sid not in order:
            order.append(sid)
        n = order.index(sid) + 1
        return f'<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}: {esc(lib.source_for(meta, sid)["title"])}">[{n}]</a></sup>'

    def link(m: re.Match) -> str:
        slug, label = m.group(1), m.group(2)
        if slug in lib.articles:
            return f'<a href="{lib.url_path(slug)}">{label}</a>'
        return label  # target not built yet: plain text, never a dead link

    inlined = re.sub(r"\{\{inline-js:([a-z_]+\.js)\}\}", lambda m: (lib.root / "tools" / m.group(1)).read_text(encoding="utf-8"), meta["_body"])
    body = re.sub(r"\{\{cite:([a-z0-9\-]+)\}\}", cite, inlined)
    body = re.sub(r"\{\{link:([a-z0-9\-]+)\|([^}]+)\}\}", link, body)
    if "{{" in body:
        raise ValueError(f"{meta['slug']}: unresolved token near {body[body.index('{{'):][:60]!r}")
    return body, order


def build_toc(body: str) -> str:
    items = re.findall(r'<h2 id="([a-z0-9\-]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
    items = [(i, re.sub(r"<[^>]+>", "", t).strip()) for i, t in items if not i.endswith("-h")]
    if len(items) < 3:
        return ""
    lis = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in items)
    return f'<nav class="pa-toc" aria-label="On this page"><h2>On this page</h2><ol>{lis}</ol></nav>'


def breadcrumbs(lib: Library, meta: dict) -> tuple[str, list[dict]]:
    base = lib.taxonomy["base_path"]
    sec = lib.sections[meta["section"]]
    trail = [("Final Vestige", "/"), ("The Preparedness Archive", base), (sec["label"], lib.section_path(meta["section"])), (meta["title"], None)]
    lis = []
    ld = []
    for pos, (label, href) in enumerate(trail, 1):
        if href:
            lis.append(f'<li><a href="{href}">{esc(label)}</a></li>')
            ld.append({"@type": "ListItem", "position": pos, "name": label, "item": SITE + href})
        else:
            lis.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
            ld.append({"@type": "ListItem", "position": pos, "name": label})
    return f'<nav class="pa-crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>', ld


def sources_block(lib: Library, order: list[str], meta: dict) -> str:
    use = meta.get("source_use", {})
    lis = []
    for n, sid in enumerate(order, 1):
        s = lib.source_for(meta, sid)
        bits = []
        if s.get("published"):
            bits.append(f"Published {fmt_date(s['published'])}")
        if s.get("updated"):
            bits.append(f"Updated {fmt_date(s['updated'])}")
        if s.get("reviewed"):
            bits.append(f"Reviewed {fmt_date(s['reviewed'])}")
        bits.append(f"Machine-checked {fmt_date(s['verified_on'])}")
        note = use.get(sid) or s.get("supports", "")
        scope = s.get("notes") or ""
        scope_html = (
            f'<span class="pa-src-use">Reading scope / limitations: {esc(scope)}</span>'
            if scope else ""
        )
        human_link = (
            "Human source-link check complete"
            if s.get("human_link_check") is True
            else "Human source-link check pending"
        )
        shared = lib.crosswalk_member_groups.get((s.get("_origin"), sid, s["url"]))
        shared_html = (
            '<span class="pa-src-use">Shared-source reading scope: independent review pending</span>'
            if shared and shared.get("review_status") != "resolved"
            else ""
        )
        lis.append(
            f'<li id="src-{n}"><a href="{esc(s["url"])}" rel="noopener">{esc(s["title"])}</a>. {esc(s["publisher"])}.'
            f'<span class="pa-src-meta">{esc(" · ".join(bits))} · {human_link}</span>'
            f'<span class="pa-src-use">Used for: {esc(note)}</span>{scope_html}{shared_html}</li>'
        )
    return (
        '<section class="pa-sources" aria-labelledby="sources-h"><h2 id="sources-h">Sources and verification</h2>'
        "<p>The date below records a researcher's machine-assisted source check. "
        "Source reading may have covered a full page, a specific passage or only a catalogue record; "
        "each available scope limitation is retained below. A machine check is not independent "
        "human link verification. The source publisher's own published or updated date is distinct.</p>"
        f'<ol>{"".join(lis)}</ol></section>'
    )


def review_block(meta: dict) -> str:
    st = meta["status"]
    safety = meta.get("safety_review", {"state": "not-required"})
    if safety["state"] == "approved":
        s_txt = f"Approved by {esc(safety['reviewer'])} on {fmt_date(safety['date'])}"
    elif safety["state"] == "pending":
        s_txt = "Pending. A human safety review is required before this page can be published."
    else:
        s_txt = "Not required for this topic."
    rows = [
        ("Editorial status", {"drafted": "Drafted; editor read-through pending", "reviewed": "Reviewed"}.get(st["editorial"], st["editorial"])),
        ("Safety review", s_txt),
        ("Last source check", fmt_date(meta["last_checked"])),
        ("Recheck when", meta.get("recheck", "Any source above changes, or at the latest 12 months after the last check.")),
    ]
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{v if k == 'Safety review' else esc(v)}</dd>" for k, v in rows)
    return f'<section class="pa-review" aria-labelledby="review-h"><h2 id="review-h">Review record</h2><dl>{dl}</dl></section>'


def related_block(lib: Library, meta: dict) -> str:
    items = []
    for slug in meta.get("related", []):
        if slug in lib.articles:
            items.append(f'<li><a href="{lib.url_path(slug)}">{esc(lib.articles[slug]["title"])}</a></li>')
    if not items:
        return ""
    return f'<aside class="pa-related" aria-labelledby="rel-h"><h2 id="rel-h">Keep reading</h2><ul>{"".join(items)}</ul></aside>'


def build_article(lib: Library, slug: str) -> dict:
    meta = lib.articles[slug]
    body, order = resolve_tokens(lib, meta)
    words = word_count(body)
    minutes = meta.get("read_minutes") or max(1, round(words / WORDS_PER_MINUTE))
    sec = lib.sections[meta["section"]]
    track = lib.taxonomy["tracks"][meta["track"]]
    crumbs_html, crumbs_ld = breadcrumbs(lib, meta)
    canonical = SITE + lib.url_path(slug)

    chips = [f'<li class="pa-chip pa-chip--gold">{esc(track["label"])}</li>', f'<li class="pa-chip">{esc(sec["label"])}</li>']
    if meta["status"]["publish"] != "published":
        chips.append('<li class="pa-chip pa-chip--warn">Draft: not public</li>')
    if meta.get("safety_review", {}).get("state") == "pending":
        chips.append('<li class="pa-chip pa-chip--warn">Safety review pending</li>')
    for t in meta.get("tags", []):
        chips.append(f'<li class="pa-chip">{esc(t)}</li>')

    head = (
        f'<header class="pa-head"><p class="pa-kicker">{esc(sec["label"])} · {esc(track["label"])}</p>'
        f'<h1>{esc(meta["h1"])}</h1><p class="pa-dek">{esc(meta["dek"])}</p>'
        f'<ul class="pa-meta"><li><b>{minutes} min read</b></li><li>Updated <b>{fmt_date(meta["updated"])}</b></li>'
        f'<li>Sources last checked <b>{fmt_date(meta["last_checked"])}</b></li></ul>'
        f'<ul class="pa-chips" aria-label="Article status and topics">{"".join(chips)}</ul>'
        f'<div class="pa-printbar"><button type="button" class="pa-btn pa-btn--ghost" onclick="window.print()">Print this guide</button></div></header>'
    )
    toc = build_toc(body)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": canonical + "#article",
                "headline": meta["h1"],
                "description": meta["description"],
                "mainEntityOfPage": canonical,
                "dateModified": meta["updated"],
                "inLanguage": "en-US",
                "author": {"@type": "Organization", "name": "Final Vestige Studios"},
                "publisher": {"@type": "Organization", "name": "Final Vestige Studios", "url": SITE + "/"},
                "isAccessibleForFree": True,
            },
            {"@type": "BreadcrumbList", "itemListElement": crumbs_ld},
        ],
    }
    if meta["status"]["publish"] == "published" and meta.get("published"):
        ld["@graph"][0]["datePublished"] = meta["published"]
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    inner = (
        f'<div class="pa pa-article" data-slug="{slug}" data-track="{meta["track"]}" data-section="{meta["section"]}">'
        f'<a class="pa-skip" href="#pa-main">Skip to the guide</a>{crumbs_html}{head}'
        f'<div class="pa-shell">{toc}<div class="pa-body" id="pa-main">{body}</div></div>'
        f'{sources_block(lib, order, meta)}{review_block(meta)}{related_block(lib, meta)}{ld_tag}</div>'
    )
    return {"slug": slug, "inner": inner, "words": words, "minutes": minutes, "sources": order, "canonical": canonical, "meta": meta}


def render_card(lib: Library, meta: dict) -> str:
    track = lib.taxonomy["tracks"][meta["track"]]
    draft = ' · <span>Draft</span>' if meta["status"]["publish"] != "published" else ""
    mins = meta.get("read_minutes") or max(1, round(word_count(meta["_body"]) / WORDS_PER_MINUTE))
    hay = " ".join([meta["title"], meta["dek"], " ".join(meta.get("tags", []))]).lower()
    verify = "reviewed" if meta.get("safety_review", {}).get("state") in ("approved", "not-required") and meta["status"]["editorial"] == "reviewed" else "pending"
    return (
        f'<li class="pa-card" data-section="{meta["section"]}" data-track="{meta["track"]}" data-verify="{verify}" data-text="{esc(hay)}">'
        f'<p class="pa-card-track">{esc(track["label"])}</p><h3><a href="{lib.url_path(meta["slug"])}">{esc(meta["title"])}</a></h3>'
        f'<p>{esc(meta["dek"])}</p><p class="pa-card-meta"><span>{mins} min read</span>'
        f'<span>Checked {fmt_date(meta["last_checked"])}</span>{draft}</p></li>'
    )


def build_landing(lib: Library, include_drafts: bool = True) -> dict:
    base = lib.taxonomy["base_path"]
    cards_by_section: dict[str, list[dict]] = {}
    for slug, meta in lib.articles.items():
        if meta["status"]["publish"] == "published" or include_drafts:
            cards_by_section.setdefault(meta["section"], []).append(meta)

    sections_html = []
    populated = []
    for sec in lib.taxonomy["sections"]:
        arts = cards_by_section.get(sec["slug"], [])
        if not arts:
            continue  # never render an empty section as if it were a place
        populated.append(sec["slug"])
        sections_html.append(
            f'<section class="pa-section" id="{sec["slug"]}" aria-labelledby="h-{sec["slug"]}"><h2 id="h-{sec["slug"]}">{esc(sec["label"])}</h2>'
            f'<p class="pa-lede">{esc(sec["blurb"])}</p><ul class="pa-cards">{"".join(render_card(lib, m) for m in arts)}</ul><p><a href="{lib.section_path(sec["slug"])}">All {esc(sec["label"])} guides</a></p></section>'
        )

    opts = "".join(f'<option value="{s}">{esc(lib.sections[s]["label"])}</option>' for s in populated)
    script = """<script>(function(){var r=document.currentScript.closest('.pa');if(!r)return;var q=r.querySelector('#pa-q'),s=r.querySelector('#pa-sec'),t=r.querySelector('#pa-trk'),o=r.querySelector('#pa-count'),e=r.querySelector('#pa-none'),c=[].slice.call(r.querySelectorAll('.pa-card'));function f(){var x=(q.value||'').toLowerCase().trim(),n=0;c.forEach(function(k){var ok=(!x||k.getAttribute('data-text').indexOf(x)>-1)&&(!s.value||k.dataset.section===s.value)&&(!t.value||k.dataset.track===t.value);k.hidden=!ok;if(ok)n++});o.textContent=n+(n===1?' guide shown':' guides shown');e.hidden=n>0}[q,s,t].forEach(function(el){el.addEventListener('input',f);el.addEventListener('change',f)});f()})();</script>"""

    hero = (
        '<header class="pa-hero"><p class="pa-kicker">Final Vestige Studios</p>'
        "<h1>The Preparedness Archive</h1>"
        '<p class="pa-dek">What people knew. What still works. What keeps a household ready.</p>'
        '<ul class="pa-promise"><li><b>Preparedness without panic.</b> Plain steps, dated sources, no fear selling.</li>'
        "<li><b>History without mythology.</b> Old methods are reported as they were practiced, then judged by today's safety standards.</li>"
        "<li><b>Free, always.</b> Nothing here sits behind a signup or a purchase.</li></ul></header>"
    )
    urgent = (
        '<aside class="pa-now-strip" aria-label="In an emergency"><h2>In an emergency right now</h2>'
        "<p>If someone is hurt, trapped, or in immediate danger, call your local emergency number first. "
        "This archive is for preparing and for slower decisions. It does not replace emergency services, your health department, or a clinician.</p></aside>"
    )
    tracks = (
        '<section class="pa-section" aria-labelledby="h-tracks"><h2 id="h-tracks">Two tracks, kept apart on purpose</h2>'
        '<div class="pa-two"><div class="pa-track pa-track--modern"><h3>Act now</h3>'
        "<p>Current guidance from regulators and public-health bodies, with the source and the date beside every instruction. If you only have ten minutes, this is the track.</p></div>"
        '<div class="pa-track pa-track--lost"><h3>The Lost Ways</h3>'
        "<p>How sailors, pioneers and householders actually managed, drawn from contracts, journals and museum records. Every history piece ends with a modern safety verdict, because a method that worked for a crew in 1813 is not thereby safe in your kitchen.</p></div></div></section>"
    )
    filt = (
        '<section class="pa-section" aria-labelledby="h-lib"><h2 id="h-lib">The library</h2>'
        '<p class="pa-lede">Filter by topic, track or keyword. Every guide shows when its sources were last checked.</p>'
        '<form class="pa-filter" role="search" aria-label="Filter guides" onsubmit="return false">'
        '<div><label for="pa-q">Search guides</label><input id="pa-q" type="search" autocomplete="off" placeholder="water, salt, botulism"></div>'
        f'<div><label for="pa-sec">Topic</label><select id="pa-sec"><option value="">All topics</option>{opts}</select></div>'
        '<div><label for="pa-trk">Track</label><select id="pa-trk"><option value="">Both tracks</option><option value="modern">Act now</option><option value="lost-ways">The Lost Ways</option></select></div>'
        '<output id="pa-count" aria-live="polite"></output></form>'
        '<p id="pa-none" class="pa-empty" hidden>No guide matches that filter yet. Clear a filter to see them all.</p></section>'
    )
    standards = (
        '<section class="pa-section" aria-labelledby="h-std"><h2 id="h-std">How we hold ourselves to account</h2><ul class="pa-standards">'
        "<li><b>Sources you can open.</b> Each guide lists the pages it relied on, with publication, update and check dates.</li>"
        "<li><b>Three kinds of statement.</b> Demonstrated fact, documented history, and uncertain conclusion are labeled differently.</li>"
        "<li><b>Safety review before publication.</b> Guides involving water treatment, food preservation, combustion or medicine need a named human review.</li>"
        '<li><b>No invented numbers.</b> We reproduce current official figures in context, or we send you to the source. We do not make up recipes, doses or times.</li></ul>'
        '<p>Read the full <a href="/editorial-standards/">Editorial Standards</a>. Spot a mistake? Use <a href="/contact/#corrections">Corrections &amp; Contact</a>.</p></section>'
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "The Preparedness Archive",
        "description": "Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure.",
        "url": SITE + base,
        "isAccessibleForFree": True,
        "publisher": {"@type": "Organization", "name": "Final Vestige Studios", "url": SITE + "/"},
    }
    crumbs = (
        '<nav class="pa-crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Final Vestige</a></li>'
        '<li><span aria-current="page">The Preparedness Archive</span></li></ol></nav>'
    )
    inner = (
        '<div class="pa pa-landing"><a class="pa-skip" href="#pa-library">Skip to the library</a>'
        f"{crumbs}{hero}{urgent}{tracks}<div id=\"pa-library\">{filt}{''.join(sections_html)}</div>{standards}"
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>{script}</div>'
    )
    return {"slug": "landing", "inner": inner, "populated_sections": populated, "article_cards": sum(len(v) for v in cards_by_section.values())}


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    return css.strip()


def build_hub(lib: Library, section: str, include_drafts: bool = True) -> dict | None:
    sec = lib.sections[section]
    arts = [m for m in lib.articles.values() if m["section"] == section and (include_drafts or m["status"]["publish"] == "published")]
    if not arts:
        return None  # an empty section is not a place; no hub page exists for it
    arts.sort(key=lambda m: m["n"])
    base = lib.taxonomy["base_path"]
    canonical = SITE + lib.section_path(section)
    crumbs = (
        '<nav class="pa-crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Final Vestige</a></li>'
        f'<li><a href="{base}">The Preparedness Archive</a></li><li><span aria-current="page">{esc(sec["label"])}</span></li></ol></nav>'
    )
    tracks_present = sorted({m["track"] for m in arts})
    chips = "".join(f'<li class="pa-chip pa-chip--gold">{esc(lib.taxonomy["tracks"][k]["label"])}</li>' for k in tracks_present)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": canonical + "#page", "name": f'{sec["label"]} | The Preparedness Archive',
             "description": sec["blurb"], "url": canonical, "isAccessibleForFree": True,
             "publisher": {"@type": "Organization", "name": "Final Vestige Studios", "url": SITE + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Final Vestige", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "The Preparedness Archive", "item": SITE + base},
                {"@type": "ListItem", "position": 3, "name": sec["label"]}]},
        ],
    }
    inner = (
        f'<div class="pa pa-hub" data-section="{section}"><a class="pa-skip" href="#pa-guides">Skip to the guides</a>{crumbs}'
        f'<header class="pa-head"><p class="pa-kicker">The Preparedness Archive</p><h1>{esc(sec["label"])}</h1>'
        f'<p class="pa-dek">{esc(sec["blurb"])}</p><ul class="pa-chips" aria-label="Tracks in this section">{chips}</ul></header>'
        f'<section class="pa-section" id="pa-guides" aria-labelledby="h-guides"><h2 id="h-guides">{len(arts)} {"guide" if len(arts) == 1 else "guides"}</h2>'
        f'<ul class="pa-cards">{"".join(render_card(lib, m) for m in arts)}</ul></section>'
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></div>'
    )
    return {"slug": f"hub-{section}", "inner": inner, "count": len(arts), "title": f'{sec["label"]} | The Preparedness Archive', "description": sec["blurb"]}


def wp_wrap(lib: Library, inner: str) -> str:
    return f"<!-- wp:html -->\n<style>{minify_css(lib.css)}</style>\n{inner}\n<!-- /wp:html -->\n"


def preview_wrap(lib: Library, inner: str, title: str, description: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}</title><meta name=\"description\" content=\"{esc(description)}\">"
        '<meta name="robots" content="noindex,nofollow">'
        f"<style>html{{background:#0C0D0D}}body{{margin:0}}{lib.css}</style></head><body><main>{inner}</main></body></html>"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", action="store_true", help="landing lists only published articles")
    args = ap.parse_args(argv)
    lib = Library()
    # Prevent even a local 'public' artifact from containing an article whose
    # editorial/safety/source release checks fail. Drafts may build with
    # documented unresolved-source warnings; publishing remains blocked.
    # The R18 private preflight invokes this script with Python -I, which
    # intentionally omits the script's directory from sys.path. Pin imports
    # to this checked-out Preparedness tools directory, never cwd/site paths.
    tools_directory = Path(__file__).resolve(strict=True).parent
    validator_file = tools_directory / "validate.py"
    if not validator_file.is_file() or validator_file.is_symlink():
        print("PREPAREDNESS BUILD HOLD: trusted validator file missing or linked.",
              file=sys.stderr)
        return 2
    if str(tools_directory) not in sys.path:
        sys.path.insert(0, str(tools_directory))
    import validate as approval_gates  # noqa: WPS433 (local checkout only)
    errors, _warnings = approval_gates.validate(lib)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"PREPAREDNESS BUILD HOLD: {len(errors)} validation error(s); no output written.", file=sys.stderr)
        return 2
    out = ROOT / "build"
    (out / "wp").mkdir(parents=True, exist_ok=True)
    (out / "preview").mkdir(parents=True, exist_ok=True)
    # These are files for drafts only, never an authorization to publish.
    # Expose collision status explicitly so a generated HTML file cannot be
    # mistaken for a source-checked/publication-ready finished guide.
    source_rows = [s for versions in lib.source_variants.values() for s in versions]
    unresolved_groups = sum(
        g.get("review_status") != "resolved"
        for g in lib.crosswalk_groups.values()
    )
    report = {
        "articles": [], "landing": None,
        "release_evidence": {
            "state": "HOLD" if unresolved_groups or any(
                m["status"]["publish"] != "published" for m in lib.articles.values()
            ) else "REQUIRES_INDEPENDENT_QA",
            "note": "A build artifact is not permission to publish or proof of medical/food/water safety.",
            "article_drafts": sum(m["status"]["publish"] == "draft" for m in lib.articles.values()),
            "article_published": sum(m["status"]["publish"] == "published" for m in lib.articles.values()),
            "raw_source_rows": len(source_rows),
            "human_link_checked_rows": sum(s.get("human_link_check") is True for s in source_rows),
            "source_collision_groups": len(lib.crosswalk_groups),
            "unresolved_collisions": unresolved_groups,
            "independent_qa_verified": False,
            "wordpress_publication_performed": False,
        },
    }
    for slug in lib.articles:
        built = build_article(lib, slug)
        meta = built["meta"]
        write_lf(out / "wp" / f"{slug}.html", wp_wrap(lib, built["inner"]))
        write_lf(out / "preview" / f"{slug}.html", preview_wrap(lib, built["inner"], f'{meta["h1"]} | The Preparedness Archive', meta["description"]))
        report["articles"].append({k: built[k] for k in ("slug", "words", "minutes", "sources", "canonical")})
    from collections import Counter
    report["slate_status"] = dict(Counter(slate_status(lib, a["slug"]) for a in lib.taxonomy["slate"]))
    report["hubs"] = []
    for sec in lib.taxonomy["sections"]:
        h = build_hub(lib, sec["slug"], include_drafts=not args.public)
        if h:
            write_lf(out / "wp" / f"{h['slug']}.html", wp_wrap(lib, h["inner"]))
            write_lf(out / "preview" / f"{h['slug']}.html", preview_wrap(lib, h["inner"], h["title"], h["description"]))
            report["hubs"].append({"section": sec["slug"], "guides": h["count"]})
    land = build_landing(lib, include_drafts=not args.public)
    desc = "Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure."
    write_lf(out / "wp" / "landing.html", wp_wrap(lib, land["inner"]))
    write_lf(out / "preview" / "landing.html", preview_wrap(lib, land["inner"], "The Preparedness Archive | Final Vestige", desc))
    report["landing"] = {k: land[k] for k in ("populated_sections", "article_cards")}
    write_lf(out / "build-report.json", json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
