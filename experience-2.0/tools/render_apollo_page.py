"""Render the Apollo 1 investigation page as ONE self-contained WordPress `core/html` block. No plugin.

Everything comes from `data/apollo1.json` (records, image identity, rights, crosswalk, chronology) and `atlas/data/atlas.json`
(documented-versus-interpretive classification, related investigations). Nothing is typed here that is not in those files except
interface wording. The block carries its own inline CSS and JS, namespaced `.fv-ex2*` / `--fvx-*` / `data-fvx-*`, and fails open:
the content is complete HTML, and the script only reveals optional controls.

The theme (Assembler) supplies the site header, footer, `main` and skip link, and no page title, so the block owns the single h1.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date

import fvx_lib as lib
from fvx_lib import esc, safe_https
from render_desk import render_desk
from render_flagship import _chapter, _provenance, render_chronology

SIGNOFFS = lib.EX2 / "page-blocks" / "image-signoffs.json"
DESK_INSTANCE = "apollo1"
DESK_ID = "research-desk"

REVIEW_TEXT = {"unreviewed": "Not yet reviewed", "approved": "Reviewed and approved"}
BASIS_TEXT = {"documented": "Documented", "interpretive": "Interpretive"}

PAGE_CSS = """
.fv-ex2-page .fv-ex2-hero { min-height: 0; align-items: start; }
.fv-ex2-page .fv-ex2-hero::after { content: none; }
.fv-ex2-page .fv-ex2-hero__inner > * { animation: none; }
.fv-ex2-page .fv-ex2-hero__inner { padding-block: clamp(3.5rem, 9vw, 7rem) clamp(2.5rem, 6vw, 4.5rem); }
.fv-ex2-page { max-width: none; margin-block: 0; overflow-x: clip; }
.fv-ex2-sec { padding-block: clamp(3rem, 7vw, 6rem); border-top: 1px solid var(--fvx-line); }
.fv-ex2-sec__head { display: grid; gap: var(--fvx-s-4); max-width: 46rem; margin-bottom: var(--fvx-s-6); }
.fv-ex2-sec__title { font-size: var(--fvx-fs-h2); line-height: 1.05; letter-spacing: -0.025em; }
.fv-ex2-sec__intro { color: var(--fvx-text-muted); font-size: var(--fvx-fs-lede); line-height: 1.5; }
.fv-ex2-legend { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--fvx-s-4); }
.fv-ex2-legend > div { display: grid; gap: var(--fvx-s-3); align-content: start; padding: var(--fvx-s-5); background: var(--fvx-raised); border: 1px solid var(--fvx-line); }
.fv-ex2-legend p { color: var(--fvx-text-muted); font-size: var(--fvx-fs-small); }
.fv-ex2-badge[data-status="documented"] { color: #8fd19e; }
.fv-ex2-badge[data-status="interpretive"] { color: var(--fvx-amber); }
.fv-ex2-legend .fv-ex2-badge { justify-self: start; }
.fv-ex2-plate__basis { flex-basis: 100%; display: grid; gap: var(--fvx-s-2); justify-items: start; padding-top: var(--fvx-s-2); }
.fv-ex2-plate .fv-ex2-plate__basis .fv-ex2-badge { color: var(--fvx-paper-ink); }
.fv-ex2-plate .fv-ex2-plate__basis .fv-ex2-caption { color: var(--fvx-paper-ink); }
.fv-ex2-classlist { display: grid; gap: var(--fvx-s-4); }
.fv-ex2-classlist li { display: grid; gap: var(--fvx-s-2); padding: var(--fvx-s-4) var(--fvx-s-5); background: var(--fvx-raised); border: 1px solid var(--fvx-line); }
.fv-ex2-classlist__head { display: flex; flex-wrap: wrap; gap: var(--fvx-s-3); align-items: baseline; }
.fv-ex2-classlist__title { font-weight: 600; }
.fv-ex2-classlist p { color: var(--fvx-text-muted); font-size: var(--fvx-fs-small); }
.fv-ex2-rights { display: grid; gap: var(--fvx-s-5); grid-template-columns: repeat(2, minmax(0, 1fr)); }
.fv-ex2-rights > li { min-width: 0; display: grid; gap: var(--fvx-s-3); align-content: start; padding: var(--fvx-s-5); background: var(--fvx-raised); border: 1px solid var(--fvx-line); }
.fv-ex2-rights h3 { font-size: var(--fvx-fs-h3); line-height: 1.15; }
.fv-ex2-rights .fv-ex2-provenance { font-size: var(--fvx-fs-small); }
.fv-ex2-policy { display: grid; gap: var(--fvx-s-3); margin-bottom: var(--fvx-s-6); padding: var(--fvx-s-5); border: 1px solid var(--fvx-gold-deep); max-width: 60rem; }
.fv-ex2-policy p { font-size: var(--fvx-fs-small); color: var(--fvx-text-muted); }
.fv-ex2-related { display: grid; gap: var(--fvx-s-4); grid-template-columns: repeat(2, minmax(0, 1fr)); }
.fv-ex2-related > li { min-width: 0; display: grid; gap: var(--fvx-s-2); align-content: start; padding: var(--fvx-s-5); background: var(--fvx-raised); border: 1px solid var(--fvx-line); }
.fv-ex2-related h3 { font-size: var(--fvx-fs-h3); line-height: 1.15; }
.fv-ex2-related h3 a { color: var(--fvx-text); text-decoration-color: var(--fvx-gold-deep); }
.fv-ex2-related p { color: var(--fvx-text-muted); font-size: var(--fvx-fs-small); }
.fv-ex2-page .fv-ex2-desk__head { padding-block: 0 var(--fvx-s-5); }
.fv-ex2-page .fv-ex2-desk__title { font-size: var(--fvx-fs-h2); line-height: 1.05; letter-spacing: -0.025em; }
.fv-ex2-pagefoot { padding-block: var(--fvx-s-6); border-top: 1px solid var(--fvx-line); display: grid; gap: var(--fvx-s-2); font-size: var(--fvx-fs-small); color: var(--fvx-text-muted); }
/* The Assembler theme sets `.wp-site-blocks main * { min-width: 0 }`, which would collapse the 44px chapter links. */
.fv-ex2-page .fv-ex2-chapterbar a { min-width: 2.75rem; }

/* Chromium confines a sticky grid item to the grid container, not its row, so the sticky plate slid over the chronology below it.
   Stretch the grid item to its row and make the plate inside it the sticky element. */
@media (min-width: 60rem) and (min-height: 40rem) {
  .fv-ex2-page .fv-ex2-chapter__plate { position: static; align-self: stretch; }
  .fv-ex2-page .fv-ex2-chapter__plate > .fv-ex2-plate { position: sticky; top: var(--fvx-sticky-top); }
}
@media (max-width: 48rem) { .fv-ex2-legend, .fv-ex2-rights, .fv-ex2-related { grid-template-columns: minmax(0, 1fr); } }
"""


def approved_images(data: dict, path=SIGNOFFS) -> set:
    """NASA ids an editor has signed off for this page. A photograph with no complete sign-off is not shown (founder rule)."""
    known = {r["image"]["nasa_id"] for r in data["records"]}
    ok = set()
    for item in json.loads(path.read_text(encoding="utf-8")).get("approved", []):
        if item.get("nasa_id") in known and all(str(item.get(k, "")).strip() for k in ("editor", "date", "contextual_use")):
            ok.add(item["nasa_id"])
    return ok


# Kept in its own block so the main style block (and its stored hash) did not change when text-only chapters were added.
TEXT_CHAPTER_CSS = """
.fv-ex2-page .fv-ex2-chapter__grid--text { grid-template-columns: minmax(0, 1fr); }
.fv-ex2-page .fv-ex2-chapter__grid--text .fv-ex2-chapter__text { grid-column: 1; grid-row: auto; justify-self: start; max-width: 46rem; }
"""


def _minify(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    return re.sub(r"\s*([{};,])\s*", r"\1", css).strip()


def _badge(basis: str) -> str:
    return f'<span class="fv-ex2-badge" data-status="{esc(basis)}">{esc(BASIS_TEXT[basis])}</span>'


def _classification(atlas: dict, inv_id: str, shown: set) -> list[dict]:
    """Relationships about this investigation's event, joined to their documents, in dataset order."""
    docs = {d["id"]: d for d in atlas["documents"]}
    event_ids = {e["id"] for e in atlas["events"] if e["investigation_id"] == inv_id}
    rows = []
    for rel in atlas["relationships"]:
        doc = docs[rel["subject"]]
        if rel["object"] in event_ids and (doc["document_type"] != "photograph" or doc["archive_id"] in shown):
            rows.append({"rel": rel, "doc": doc})
    return rows


def _intro(data: dict, shown: set, any_open: bool) -> str:
    documented = "The cited source states it directly, or the item is a record made of the event: the Review Board report" + (
        ", or a photograph taken of the spacecraft after the fire." if any(r["image"]["depicts_event"] and r["image"]["nasa_id"] in shown for r in data["records"]) else ".")
    interp = ("Final Vestige placed it here. " + ("Context photographs and the chronology axis are editorial choices; the archive does not say they belong to this event."
              if shown else "The chronology axis is an editorial arrangement of the Board's time marks; the archive does not present it that way."))
    labels = "the third marks what is still unresolved" if any_open else "every claim on this page is matched to a named source"
    open_card = ('<div style="grid-column:1/-1"><span class="fv-ex2-badge" data-status="partial">Open question</span><p>A claim our sources do not yet fully support. It is flagged '
                 'inside the chapter and in the Research Desk crosswalk as "article only", "partial" or "editorial note".</p></div>') if any_open else ""
    lead = ("Items carry one of these labels. The first two describe how an item relates to the Apollo 1 fire; " + labels + ". None is a verdict on whether something is true."
            if any_open else "Items carry one of two labels describing how they relate to the Apollo 1 fire; " + labels + ", and the Research Desk shows each match. Neither label is a verdict on whether something is true.")
    return f'''<section class="fv-ex2-sec" aria-labelledby="fvx-howto">
<div class="fv-ex2-wrap">
<div class="fv-ex2-sec__head"><p class="fv-ex2-label">How to read this page</p>
<h2 class="fv-ex2-sec__title" id="fvx-howto">What is documented, and what is our reading of it</h2>
<p class="fv-ex2-sec__intro">{esc(lead)}</p></div>
<div class="fv-ex2-legend">
<div>{_badge("documented")}<p>{esc(documented)}</p></div>
<div>{_badge("interpretive")}<p>{esc(interp)}</p></div>
{open_card}
</div></div></section>'''


def _basis_for_image(rows: list[dict], nasa_id: str) -> dict | None:
    for row in rows:
        if row["doc"].get("archive_id") == nasa_id:
            return row
    return None


def _classification_section(rows: list[dict], shown: set) -> str:
    items = []
    for row in rows:
        rel, doc = row["rel"], row["doc"]
        title = doc["title"] if doc["document_type"] != "photograph" else f'NASA photograph {doc["archive_id"]}'
        items.append(
            f'<li><div class="fv-ex2-classlist__head">{_badge(rel["basis"])}<span class="fv-ex2-classlist__title">{esc(title)}</span></div>'
            f'<p>{esc(rel["justification"])}</p>'
            f'<p>Atlas review status: {esc(REVIEW_TEXT.get(rel["review_status"], rel["review_status"]))}.</p></li>')
    intro = ("The Evidence Atlas records why every document is attached to this event. Only one photograph, S67-21294, is documented as showing the aftermath of the fire."
             if "S67-21294" in shown else "The Evidence Atlas records why each document is attached to this event. No photographs are shown in this release.")
    return f'''<section class="fv-ex2 fv-ex2-page alignfull fv-ex2-sec" id="classification" aria-labelledby="fvx-class">
<div class="fv-ex2-wrap">
<div class="fv-ex2-sec__head"><p class="fv-ex2-label">Evidence Atlas</p>
<h2 class="fv-ex2-sec__title" id="fvx-class">How each item is classified</h2>
<p class="fv-ex2-sec__intro">{esc(intro)}</p></div>
<ul class="fv-ex2-classlist">{"".join(items)}</ul></div></section>'''


OPEN_TEXT = {
    "article-only": "Stated in our published article; not yet matched to a primary source.",
    "partial": "Partly supported by the sources; the exact wording is not yet confirmed.",
    "editorial-note": "An editorial question is open. See the Research Desk.",
}


def _open_questions(rec: dict) -> str:
    """Claims whose crosswalk status is not `verified`, shown in the chapter itself so a reader cannot miss them."""
    rows = [r for r in rec["crosswalk"] if r["status"] in OPEN_TEXT]
    if not rows:
        return ""
    items = "".join(
        f'<li><span class="fv-ex2-badge" data-status="{esc(r["status"])}">{esc(r["status"].replace("-", " "))}</span> <strong>{esc(r["claim"])}</strong> '
        f'<span>{esc(OPEN_TEXT[r["status"]])}</span></li>' for r in rows)
    return (f'<div class="fv-ex2-callout"><span class="fv-ex2-label">Open question</span>'
            f'<ul class="fv-ex2-crosswalk">{items}</ul></div>' + NL)


def _limits(recs: list[dict]) -> str:
    limits = "".join(f'<li><span class="fv-ex2-label">{i + 1:02d} &middot; {esc(r["eyebrow"])}</span><p>{esc(r["caution"])}</p></li>' for i, r in enumerate(recs))
    return f'''<section class="fv-ex2-chapter" id="limits" aria-labelledby="limits-title"><div class="fv-ex2-wrap">
<div class="fv-ex2-chapter__text" style="max-width:60rem">
<p class="fv-ex2-chapter__index">Conclusion</p>
<h2 class="fv-ex2-chapter__title" id="limits-title">What the record can and cannot establish</h2>
<p class="fv-ex2-chapter__dek">Every chapter carries a limit. Read together, they are the shape of what is actually known.</p>
<ol class="fv-ex2-crosswalk" style="gap:var(--fvx-s-5)">{limits}</ol>
<div class="fv-ex2-hero__actions"><a class="fv-ex2-button fv-ex2-button--primary" href="#{DESK_ID}">Inspect every source in the Research Desk</a><a class="fv-ex2-button" href="#rights">Sources and rights</a></div>
</div></div></section>'''


def _rights(data: dict, shown: set) -> str:
    policy = data["rights_policy"]
    items, held = [], []
    for i, rec in enumerate(data["records"]):
        img = rec["image"]
        if img["nasa_id"] in shown:
            items.append(f'<li id="rights-{esc(rec["id"])}"><p class="fv-ex2-label">Image {i + 1:02d} &middot; {esc(img["role_label"])}</p>'
                         f'<h3>{esc(img["nasa_id"])}</h3><p class="fv-ex2-caption">{esc(img["caption"])}</p>'
                         f'{_provenance(rec, policy)}<p class="fv-ex2-caption">Identity check: {esc(img["identity_note"])}</p></li>')
        else:
            held.append(f'<li id="rights-{esc(rec["id"])}"><p class="fv-ex2-label">Not shown &middot; {esc(img["role_label"])}</p>'
                        f'<h3>{esc(img["nasa_id"])}</h3><p class="fv-ex2-caption">{esc(img["role_label"])}. {esc(img["date_text"])}.</p>'
                        f'<p class="fv-ex2-caption"><a href="{esc(safe_https(img["record_url"]))}" target="_blank" rel="noopener noreferrer">NASA image record'
                        f'<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a></p></li>')
    intro = (f"{len(items)} of {len(data['records'])} photographs are shown, all credited to NASA. Each links to its original archive record." if items
             else "This release shows no photographs. The six NASA photographs in the research record are listed below, with their archive records.")
    shown_html = f'<ul class="fv-ex2-rights">{"".join(items)}</ul>' if items else ""
    held_html = (f'<div class="fv-ex2-sec__head" style="margin-top:var(--fvx-s-7)"><h3 class="fv-ex2-sec__title" style="font-size:var(--fvx-fs-h3)">Photographs not shown in this release</h3>'
                 f'<p class="fv-ex2-sec__intro">Each is added only after a named editor has signed off its use on this page.</p></div>'
                 f'<ul class="fv-ex2-rights">{"".join(held)}</ul>') if held else ""
    title = "Where every image comes from" if items else "Sources and image rights"
    return f'''<section class="fv-ex2 fv-ex2-page alignfull fv-ex2-sec" id="rights" aria-labelledby="fvx-rights">
<div class="fv-ex2-wrap">
<div class="fv-ex2-sec__head"><p class="fv-ex2-label">Sources and rights</p>
<h2 class="fv-ex2-sec__title" id="fvx-rights">{title}</h2>
<p class="fv-ex2-sec__intro">{esc(intro)}</p></div>
<div class="fv-ex2-policy"><span class="fv-ex2-label">Rights basis &middot; retrieved {esc(policy["retrieved_on"])}</span>
<p>{esc(policy["summary"])}</p>
<p><strong>{esc(policy["restriction"])}</strong> Basis: <a href="{esc(safe_https(policy["basis_url"]))}" target="_blank" rel="noopener noreferrer">{esc(policy["basis_title"])}<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a></p></div>
{shown_html}{held_html}</div></section>'''


def _related(atlas: dict, inv: dict) -> str:
    events = {e["id"]: e for e in atlas["events"]}
    mine = set(inv["themes"])
    cards = []
    for other in sorted(atlas["investigations"], key=lambda i: i["published"]):
        if other["id"] == inv["id"]:
            continue
        shared = [lbl for slug, lbl in zip(other["themes"], other["theme_labels"]) if slug in mine]
        if not shared:
            continue
        ev = events[other["event_ids"][0]]
        cards.append(f'<li><p class="fv-ex2-label">Shared theme: {esc(", ".join(shared))}</p>'
                     f'<h3><a href="{esc(safe_https(other["url"]))}">{esc(other["title"])}</a></h3>'
                     f'<p>{esc(ev["label"])}.</p><p>Published {esc(other["published"])}.</p></li>')
    places = atlas["places"]
    from validate_atlas import map_eligible  # noqa: PLC0415  (path is set up by render_atlas)
    eligible = sum(1 for p in places if map_eligible(p))
    return f'''<section class="fv-ex2 fv-ex2-page alignfull fv-ex2-sec" id="related" aria-labelledby="fvx-related">
<div class="fv-ex2-wrap">
<div class="fv-ex2-sec__head"><p class="fv-ex2-label">Evidence Atlas &middot; related investigations</p>
<h2 class="fv-ex2-sec__title" id="fvx-related">More investigations on the record</h2>
<p class="fv-ex2-sec__intro">Related by theme tag only, which is an editorial grouping and not a claim of cause. The Atlas does not draw a map: {eligible} of {len(places)} places have a verified coordinate with a stated precision, so no pin is shown.</p></div>
<ul class="fv-ex2-related">{"".join(cards)}</ul></div></section>'''


def _hero(data: dict) -> str:
    """Text-only hero. The flagship's background photograph was measured as the mobile LCP element (2.8 s on the throttled method, over the
    2.5 s limit), so this page has none; the first evidence plate is the first photograph. No entrance animation either: an element that
    starts at opacity 0 is not painted, and so not counted as LCP, until the animation runs."""
    inv = data["investigation"]
    return f'''<section class="fv-ex2-hero" aria-labelledby="fvx-title">
<div class="fv-ex2-wrap fv-ex2-hero__inner">
<p class="fv-ex2-label">Evidence Atlas &middot; Apollo 204</p>
<h1 class="fv-ex2-hero__title" id="fvx-title">The Hatch Opened <em>Inward</em></h1>
<p class="fv-ex2-hero__dek">Six records from the Apollo 204 Review Board and NASA's archive, in the order the evidence unfolds: what the surviving record shows, and where it stops.</p>
<dl class="fv-ex2-hero__meta"><div><dt>Event</dt><dd>27 January 1967, Launch Complex 34</dd></div><div><dt>Primary source</dt><dd>Apollo 204 Review Board</dd></div><div><dt>Records</dt><dd>Six, each with its limits</dd></div></dl>
<div class="fv-ex2-hero__actions"><a class="fv-ex2-button fv-ex2-button--primary" href="#record-01">Begin the evidence</a><a class="fv-ex2-button" href="{esc(safe_https(inv["url"]))}">Read the full investigation</a></div>
</div></section>'''


# Blocks are stored separately so each can be written and verified on its own (WordPress reports a SHA-1 per block) and so a defect in
# one cannot hide in a single 100 KB string. Every root is a direct child of the post content, full width, with no gap between them.
NL = chr(10)
UNUSED_CSS = {"14-drawer.css", "16-atlas.css"}  # the source drawer and the Atlas catalogue grid are not on this page


def render_parts(data: dict, atlas: dict) -> list[tuple[str, str]]:
    inv = data["investigation"]
    recs = data["records"]
    total = len(recs)
    policy = data["rights_policy"]
    atlas_inv = next(i for i in atlas["investigations"] if i["wordpress_post_id"] == inv["wordpress_post_id"])
    shown = approved_images(data)
    rows = _classification(atlas, atlas_inv["id"], shown)
    any_open = any(r["status"] != "verified" for rec in recs for r in rec["crosswalk"])
    chapters = []
    for i, rec in enumerate(recs):
        nxt = recs[i + 1] if i + 1 < total else None
        chrono = render_chronology(data["chronology"]) if rec["id"] == "record-03" else ""
        row = _basis_for_image(rows, rec["image"]["nasa_id"])
        basis = (f'<p class="fv-ex2-plate__basis">{_badge(row["rel"]["basis"])}<span class="fv-ex2-caption">{esc(row["rel"]["justification"])}</span></p>'
                 if row else "")
        desk_link = f'<a class="fv-ex2-button" href="#fv-ex2-desk-{DESK_INSTANCE}-{esc(rec["id"])}">Source record in the Research Desk</a>'
        html = _chapter(rec, i, total, nxt, policy, chrono, actions_html=desk_link + basis)
        marker = '<div class="fv-ex2-transition">'
        if html.count(marker) != 1:
            raise ValueError("chapter markup changed: cannot place the callouts")
        extra = _open_questions(rec)
        if rec["image"]["nasa_id"] not in shown:
            # No signed-off photograph: drop the plate and let the text use the full measure.
            start, end = html.index('<div class="fv-ex2-chapter__plate">'), html.index('<div class="fv-ex2-chapter__text">')
            html = html[:start] + html[end:]
            html = html.replace('fv-ex2-chapter__grid"', 'fv-ex2-chapter__grid fv-ex2-chapter__grid--text"', 1)
            extra += f'<p>{desk_link}</p>' + NL
        html = html.replace(marker, extra + marker, 1)
        chapters.append(html)
    bar_links = "".join(
        f'<li><a href="#{esc(r["id"])}"><span aria-hidden="true">{i + 1:02d}</span>'
        f'<span class="fv-ex2-visually-hidden">Record {i + 1}: {esc(r["title"])}</span></a></li>' for i, r in enumerate(recs))
    desk = render_desk(data, DESK_INSTANCE, fragment=True, with_footer=False, show_images=shown)
    css = "".join(_minify(p.read_text(encoding="utf-8")) for p in sorted(lib.CSS_SRC.glob("*.css")) if p.name not in UNUSED_CSS) + _minify(PAGE_CSS)
    js = lib.bundle_js().strip()
    if "</script" in js.lower() or "<!--" in js:
        raise ValueError("Script contains a sequence that cannot be inlined safely")
    foot_images = (f'<p>Images: NASA, editorial use under the <a href="{esc(safe_https(policy["basis_url"]))}">NASA Media Usage Guidelines</a>. {esc(policy["restriction"])}</p>'
                   if shown else '<p>Primary source: the <a href="' + esc(safe_https(data["primary_report"]["url"])) + '">Apollo 204 Review Board report</a> on nasa.gov.</p>')
    page = f'class="fv-ex2 fv-ex2-page alignfull"'
    return [
        ("00-style", f"<style>{css}</style>"),
        ("00b-style-text", f"<style>{_minify(TEXT_CHAPTER_CSS)}</style>"),
        ("01-investigation", f'''<div {page} data-fvx="flagship" data-fvx-investigation="{int(inv["wordpress_post_id"])}">
{_hero(data)}
{_intro(data, shown, any_open)}
<nav class="fv-ex2-chapterbar" data-fvx-chapterbar aria-label="Apollo 1 records"><div class="fv-ex2-wrap fv-ex2-chapterbar__inner"><ol>{bar_links}</ol><span class="fv-ex2-chapterbar__title" data-fvx-chapter-title aria-hidden="true"></span></div></nav>
<div class="fv-ex2-chapters">
{"".join(chapters)}
</div>
{_limits(recs)}
</div>'''),
        ("02-classification", _classification_section(rows, shown)),
        ("03-research-desk", f'<div id="{DESK_ID}" class="fv-ex2 fv-ex2-page alignfull fv-ex2-sec">{desk}</div>'),
        ("04-rights", _rights(data, shown)),
        ("05-related", _related(atlas, atlas_inv)),
        ("06-footer", f'''<div {page}><div class="fv-ex2-wrap fv-ex2-pagefoot"><p>A companion to the published investigation <a href="{esc(safe_https(inv["url"]))}">{esc(inv["title"])}</a>. It does not replace the full article.</p>
{foot_images}</div></div>'''),
        ("07-script", "<script>" + NL + js + NL + "</script>"),
    ]


def render_blocks(data: dict | None = None, atlas: dict | None = None) -> list[tuple[str, str]]:
    """[(name, serialized block)], in page order. Each is exactly what is stored as one top-level `core/html` block."""
    data = lib.load_apollo1(data)
    if atlas is None:
        atlas = json.loads((lib.EX2 / "atlas" / "data" / "atlas.json").read_text(encoding="utf-8"))
    from validate_atlas import validate  # noqa: PLC0415
    errors = validate(atlas)
    if errors:
        raise ValueError("Atlas dataset invalid: " + "; ".join(errors[:5]))
    return [(name, "<!-- wp:html -->" + NL + body + NL + "<!-- /wp:html -->" + NL) for name, body in render_parts(data, atlas)]


def render_block(data: dict | None = None, atlas: dict | None = None) -> str:
    """The whole page content: every block, concatenated in order."""
    return NL.join(markup for _, markup in render_blocks(data, atlas))


def fingerprints(text: str) -> dict:
    raw = text.encode("utf-8")
    return {"bytes": len(raw), "sha1": hashlib.sha1(raw).hexdigest(), "sha256": hashlib.sha256(raw).hexdigest()}


def manifest(blocks: list[tuple[str, str]]) -> dict:
    atlas_path = lib.EX2 / "atlas" / "data" / "atlas.json"
    content = NL.join(m for _, m in blocks)
    return {
        "page": {"title": "Apollo 1: The Evidence Atlas", "slug": "apollo-1-evidence-atlas", "status_when_created": "draft"},
        "page_content": {**fingerprints(content), "join": "blocks concatenated in order, separated by one newline"},
        "blocks": [{"order": i, "file": f"apollo1-investigation/{name}.block.html", **fingerprints(markup)} for i, (name, markup) in enumerate(blocks)],
        "sources": {"apollo1_sha256": hashlib.sha256((lib.DATA / "apollo1.json").read_bytes()).hexdigest(),
                    "atlas_sha256": hashlib.sha256(atlas_path.read_bytes()).hexdigest(),
                    "image_signoffs_sha256": hashlib.sha256(SIGNOFFS.read_bytes()).hexdigest()},
        "note": "Plugin-free: top-level core/html blocks only. Store each block byte-for-byte; never wrap one inside another block.",
    }


if __name__ == "__main__":
    for name, markup in render_blocks():
        print(name, fingerprints(markup), date.today())
