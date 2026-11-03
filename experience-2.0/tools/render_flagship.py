"""Render the Apollo 1 "Evidence Unfolds" companion experience from data/apollo1.json."""
from __future__ import annotations

from fvx_lib import esc, safe_https


def _provenance(rec: dict, policy: dict) -> str:
    img = rec["image"]
    depicts = "Yes. Photographed after the event." if img["depicts_event"] else "No. Not taken during the events described."
    inst = "NASA (copy served from the Final Vestige media library)" if "finalvestige.com" in img["src"] else "NASA"
    rows = [
        ("Institution", inst),
        ("Archive ID", img["nasa_id"]),
        ("Record date", img["date_text"]),
        ("Credit", img["credit"]),
        ("Shows the event?", depicts),
        ("Rights basis", f"{policy['basis_title']}: {policy['status']}"),
    ]
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows)
    link = f'<dt>Original record</dt><dd><a href="{esc(safe_https(img["record_url"]))}" target="_blank" rel="noopener noreferrer">NASA image record<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a></dd>'
    return f'<dl class="fv-ex2-provenance">{dl}{link}</dl>'


def _img(rec: dict, *, lazy: bool, sizes: str) -> str:
    img = rec["image"]
    srcset = ""
    if img["variants"]:
        srcset = ' srcset="' + ", ".join(f'{esc(v["url"])} {int(v["w"])}w' for v in img["variants"]) + f'" sizes="{esc(sizes)}"'
    loading = 'loading="lazy" ' if lazy else ""
    return (f'<img src="{esc(img["src"])}"{srcset} width="{int(img["width"])}" height="{int(img["height"])}" '
            f'alt="{esc(img["alt"])}" {loading}decoding="async">')


def plate_frame(rec: dict, *, sizes: str) -> str:
    """Image inside a frame that reserves its aspect ratio (prevents layout shift while the file loads)."""
    img = rec["image"]
    return (f'<div class="fv-ex2-plate__frame" style="--fvx-w:{int(img["width"])};--fvx-h:{int(img["height"])}">'
            f'{_img(rec, lazy=True, sizes=sizes)}</div>')


def _crosswalk(rec: dict) -> str:
    def source(r: dict) -> str:
        link = (f' <a href="{esc(safe_https(r["url"]))}" target="_blank" rel="noopener noreferrer">NASA source<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a>'
                if r.get("url") else "")
        return f'<span>{esc(r["source"])}{link}</span>'

    items = "".join(
        f'<li><span><span class="fv-ex2-badge" data-status="{esc(r["status"])}">{esc(r["status"].replace("-", " "))}</span> '
        f'<strong>{esc(r["claim"])}</strong></span>{source(r)}</li>'
        for r in rec["crosswalk"]
    )
    return f'<ul class="fv-ex2-crosswalk">{items}</ul>'


def _drawer_template(rec: dict, idx: int, total: int, desk_url: str, article_url: str, policy: dict) -> str:
    img = rec["image"]
    desk_link = f'{desk_url}#fv-ex2-desk-apollo1-{rec["id"]}'
    return f'''<template data-fvx-source="{esc(rec["id"])}">
<p class="fv-ex2-label">Record {idx + 1:02d} of {total:02d} &middot; {esc(rec["kind"])}</p>
<h2 class="fv-ex2-drawer__title" data-fvx-drawer-title tabindex="-1">{esc(rec["title"])}</h2>
<figure class="fv-ex2-drawer__figure">{_img(rec, lazy=False, sizes="(min-width: 48rem) 46rem, 100vw")}
<figcaption class="fv-ex2-caption"><strong>{esc(img["role_label"])}.</strong> {esc(img["caption"])} Credit: {esc(img["credit"])}.</figcaption></figure>
{_provenance(rec, policy)}
<div class="fv-ex2-callout"><span class="fv-ex2-label">What this chapter says</span><p>{esc(rec["dek"])}</p></div>
<div class="fv-ex2-callout"><span class="fv-ex2-label">Evidence boundary</span><p>{esc(rec["caution"])}</p></div>
<div><h3 class="fv-ex2-label">Claim crosswalk</h3>{_crosswalk(rec)}</div>
<p class="fv-ex2-caption">Identity check: {esc(img["identity_note"])}</p>
<p class="fv-ex2-drawer__links"><a href="{esc(safe_https(img["record_url"]))}" target="_blank" rel="noopener noreferrer">NASA image record &#8599;</a>
<a href="{esc(safe_https(rec["report"]))}" target="_blank" rel="noopener noreferrer">Institutional source &#8599;</a>
<a href="{esc(desk_link)}">Open in the Research Desk</a>
<a href="{esc(safe_https(article_url))}">Read the full investigation</a></p>
</template>'''


def _chapter(rec: dict, idx: int, total: int, nxt: dict | None, policy: dict, chrono_html: str, actions_html: str | None = None) -> str:
    img = rec["image"]
    rid = rec["id"]
    if actions_html is None:
        actions_html = f'<button type="button" class="fv-ex2-button" data-fvx-open-source="{esc(rid)}" hidden>Inspect source</button>'
    transition = ""
    if nxt:
        transition = (f'<div class="fv-ex2-transition"><a class="fv-ex2-transition__next" href="#{esc(nxt["id"])}">'
                      f'<span class="fv-ex2-label">Next record &middot; {idx + 2:02d}</span>'
                      f'<span class="fv-ex2-transition__title">{esc(nxt["title"])}</span></a></div>')
    else:
        transition = '<div class="fv-ex2-transition"><a class="fv-ex2-transition__next" href="#limits"><span class="fv-ex2-label">Conclusion</span><span class="fv-ex2-transition__title">What the record can and cannot establish</span></a></div>'
    return f'''<section class="fv-ex2-chapter" id="{esc(rid)}" data-fvx-chapter data-fvx-chapter-name="{esc(rec["title"])}" aria-labelledby="{esc(rid)}-title">
<div class="fv-ex2-wrap fv-ex2-chapter__grid">
<div class="fv-ex2-chapter__plate"><div class="fv-ex2-plate">
<figure>{plate_frame(rec, sizes="(min-width: 60rem) 50vw, 100vw")}
<figcaption class="fv-ex2-plate__label"><span class="fv-ex2-plate__role">{esc(img["role_label"])}</span>
<span class="fv-ex2-plate__caption">{esc(img["caption"])}</span>
<span class="fv-ex2-plate__id">NASA {esc(img["nasa_id"])} &middot; {esc(img["credit"])}</span></figcaption></figure>
<details><summary>Source record and rights</summary>{_provenance(rec, policy)}</details>
<div class="fv-ex2-plate__actions">{actions_html}</div>
</div></div>
<div class="fv-ex2-chapter__text">
<p class="fv-ex2-chapter__index">Record {idx + 1:02d} / {total:02d} &middot; {esc(rec["eyebrow"])}</p>
<h2 class="fv-ex2-chapter__title" id="{esc(rid)}-title">{esc(rec["title"])}</h2>
<p class="fv-ex2-chapter__when">{esc(rec["when"])} &middot; {esc(rec["kind"].title())}</p>
<p class="fv-ex2-chapter__dek">{esc(rec["dek"])}</p>
<p class="fv-ex2-chapter__detail">{esc(rec["detail"])}</p>
<div class="fv-ex2-callout"><span class="fv-ex2-label">Evidence boundary</span><p>{esc(rec["caution"])}</p></div>
{transition}
</div>
{chrono_html}
</div>
</section>'''


def render_chronology(chrono: dict) -> str:
    lo, hi = chrono["range"]
    span = float(hi - lo)
    dots = "".join(
        f'<span class="fv-ex2-chronology__dot" data-fvx-dot style="--fvx-p:{(m["t"] - lo) / span * 100:.2f}">{i + 1}</span>'
        for i, m in enumerate(chrono["markers"])
    )
    items = "".join(
        f'<li class="fv-ex2-chronology__item" data-fvx-marker data-t="{m["t"]}" data-label="{esc(m["label"])}" data-clock="{esc(m["clock"])}">'
        f'<span class="fv-ex2-chronology__time">+{m["t"]:g} s &middot; {esc(m["clock"])}{" (approximate)" if m["precision"] == "approximate" else ""}</span>'
        f'<span class="fv-ex2-chronology__label">{esc(m["label"])}</span>'
        f'<span class="fv-ex2-chronology__note">{esc(m["note"])}</span></li>'
        for m in chrono["markers"]
    )
    cid = esc(chrono["id"])
    return f'''<div class="fv-ex2-chapter__extra"><section class="fv-ex2-chronology" data-fvx-chronology aria-labelledby="{cid}-title">
<h3 class="fv-ex2-chronology__title" id="{cid}-title">{esc(chrono["title"])}</h3>
<p class="fv-ex2-chronology__notice">{esc(chrono["notice"])} Times are {esc(chrono["unit"])}; origin: {esc(chrono["origin_label"])}. <a href="{esc(safe_https(chrono["source_url"]))}" target="_blank" rel="noopener noreferrer">Source: Apollo 204 Review Board report &#8599;</a></p>
<div class="fv-ex2-chronology__axis" aria-hidden="true"><span class="fv-ex2-chronology__line"></span>{dots}<span class="fv-ex2-chronology__cursor" data-fvx-cursor style="--fvx-p:0"></span></div>
<div class="fv-ex2-chronology__tool" data-fvx-chrono-tool hidden>
<label for="{cid}-range">Move through the recorded seconds ({esc(chrono["unit"])})</label>
<input class="fv-ex2-chronology__range" id="{cid}-range" type="range" min="{lo}" max="{hi}" step="0.1" value="0">
<p class="fv-ex2-chronology__readout" data-fvx-chrono-readout role="status" aria-live="polite"></p></div>
<ol class="fv-ex2-chronology__list">{items}</ol></section></div>'''


def render_flagship(data: dict, *, desk_url: str, atlas_url: str) -> str:
    inv = data["investigation"]
    recs = data["records"]
    total = len(recs)
    policy = data["rights_policy"]
    hero_rec = recs[1]  # Spacecraft 012 processing photograph: relevant hardware, no people, decorative here.
    hero_img = hero_rec["image"]
    hero_srcset = ", ".join(f'{esc(v["url"])} {int(v["w"])}w' for v in hero_img["variants"])
    chapters = []
    for i, rec in enumerate(recs):
        nxt = recs[i + 1] if i + 1 < total else None
        chrono = render_chronology(data["chronology"]) if rec["id"] == "record-03" else ""
        chapters.append(_chapter(rec, i, total, nxt, policy, chrono))
    bar_links = "".join(
        f'<li><a href="#{esc(r["id"])}"><span aria-hidden="true">{i + 1:02d}</span>'
        f'<span class="fv-ex2-visually-hidden">Record {i + 1}: {esc(r["title"])}</span></a></li>'
        for i, r in enumerate(recs)
    )
    templates = "\n".join(_drawer_template(r, i, total, desk_url, inv["url"], policy) for i, r in enumerate(recs))
    limits = "".join(f'<li><span class="fv-ex2-label">{i + 1:02d} &middot; {esc(r["eyebrow"])}</span><p>{esc(r["caution"])}</p></li>' for i, r in enumerate(recs))
    return f'''<div class="fv-ex2" data-fvx="flagship" data-fvx-investigation="{int(inv["wordpress_post_id"])}">
<a class="fv-ex2-skip" href="#fvx-main">Skip to the investigation</a>
<header class="fv-ex2-masthead"><div class="fv-ex2-wrap fv-ex2-masthead__inner">
<a class="fv-ex2-masthead__brand" href="https://finalvestige.com/">Final Vestige Studios</a>
<nav class="fv-ex2-nav" aria-label="Experience navigation"><a href="{esc(safe_https(inv["url"]))}">Full investigation</a><a href="{esc(desk_url)}">Research Desk</a><a href="{esc(atlas_url)}">Evidence Atlas</a></nav>
</div></header>
<main id="fvx-main">
<section class="fv-ex2-hero" aria-labelledby="fvx-title">
<div class="fv-ex2-hero__media"><img src="{esc(hero_img["variants"][1]["url"])}" srcset="{hero_srcset}" sizes="100vw" width="{int(hero_img["width"])}" height="{int(hero_img["height"])}" alt="" fetchpriority="high" decoding="async"></div>
<div class="fv-ex2-wrap fv-ex2-hero__inner">
<p class="fv-ex2-label">The Evidence Unfolds &middot; Apollo 204</p>
<h1 class="fv-ex2-hero__title" id="fvx-title">The Hatch Opened <em>Inward</em></h1>
<p class="fv-ex2-hero__dek">Six records from the Apollo 204 Review Board and NASA's archive, in the order the evidence unfolds: what the surviving record shows, and where it stops.</p>
<dl class="fv-ex2-hero__meta"><div><dt>Event</dt><dd>27 January 1967, Launch Complex 34</dd></div><div><dt>Primary source</dt><dd>Apollo 204 Review Board</dd></div><div><dt>Records</dt><dd>Six, each with its limits</dd></div></dl>
<div class="fv-ex2-hero__actions"><a class="fv-ex2-button fv-ex2-button--primary" href="#record-01">Begin the evidence</a><a class="fv-ex2-button" href="{esc(safe_https(inv["url"]))}">Read the full investigation</a></div>
<p class="fv-ex2-hero__credit">Background: NASA {esc(hero_img["nasa_id"])}, {esc(hero_img["date_text"])}. Spacecraft 012 during preparations; a processing photograph, not an image of the fire. Credit: {esc(hero_img["credit"])}.</p>
</div></section>
<nav class="fv-ex2-chapterbar" data-fvx-chapterbar aria-label="Records"><div class="fv-ex2-wrap fv-ex2-chapterbar__inner"><ol>{bar_links}</ol><span class="fv-ex2-chapterbar__title" data-fvx-chapter-title aria-hidden="true"></span></div></nav>
<div class="fv-ex2-chapters">
{"".join(chapters)}
</div>
<section class="fv-ex2-chapter" id="limits" aria-labelledby="limits-title"><div class="fv-ex2-wrap">
<div class="fv-ex2-chapter__text" style="max-width:60rem">
<p class="fv-ex2-chapter__index">Conclusion</p>
<h2 class="fv-ex2-chapter__title" id="limits-title">What the record can and cannot establish</h2>
<p class="fv-ex2-chapter__dek">Every chapter carries a limit. Read together, they are the shape of what is actually known.</p>
<ol class="fv-ex2-crosswalk" style="gap:var(--fvx-s-5)">{limits}</ol>
<div class="fv-ex2-hero__actions"><a class="fv-ex2-button fv-ex2-button--primary" href="{esc(desk_url)}">Inspect every source in the Research Desk</a><a class="fv-ex2-button" href="{esc(safe_https(inv["url"]))}">Read the full investigation</a></div>
</div></div></section>
</main>
<footer class="fv-ex2-footer"><div class="fv-ex2-wrap fv-ex2-footer__inner">
<p>A companion experience to the published investigation. It does not replace the full article. Integration candidate: not published.</p>
<p>Images: NASA, editorial use under the <a href="{esc(safe_https(policy["basis_url"]))}">NASA Media Usage Guidelines</a>. {esc(policy["restriction"])}</p></div></footer>
<dialog class="fv-ex2-drawer" data-fvx-drawer>
<div class="fv-ex2-drawer__bar"><span class="fv-ex2-label">Source inspector</span><button type="button" class="fv-ex2-button" data-fvx-drawer-close>Close</button></div>
<div class="fv-ex2-drawer__body" data-fvx-drawer-body></div>
<div class="fv-ex2-drawer__body fv-ex2-drawer__pager"><button type="button" class="fv-ex2-button" data-fvx-drawer-prev>Previous record</button><button type="button" class="fv-ex2-button" data-fvx-drawer-next>Next record</button></div>
</dialog>
{templates}
</div>'''
