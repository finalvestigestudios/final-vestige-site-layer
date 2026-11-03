"""Render the Research Desk. `instance` is substituted into every id so several desks can share one page."""
from __future__ import annotations

from fvx_lib import BadRecord, INSTANCE_PLACEHOLDER, INSTANCE_RE, esc, safe_https
from render_flagship import _crosswalk


def render_desk(data: dict, instance: str = "apollo1", fragment: bool = False, with_footer: bool = True) -> str:
    """`fragment=True` renders for embedding in a WordPress post: the heading drops to h2 because the post owns the h1."""
    if instance != INSTANCE_PLACEHOLDER and not INSTANCE_RE.fullmatch(instance):
        raise BadRecord("Instance identifier must be a lowercase ASCII slug")
    h = "h2" if fragment else "h1"
    recs = data["records"]
    inv = data["investigation"]
    report = data["primary_report"]
    prefix = f"fv-ex2-desk-{instance}"
    cards = []
    for i, rec in enumerate(recs):
        img = rec["image"]
        needle = " ".join([rec["title"], img["nasa_id"], rec["kind"], rec["dek"], rec["detail"], rec["caution"], img["caption"],
                           " ".join(r["claim"] for r in rec["crosswalk"])])
        shows = (f'{img["role_label"]}, photographed after the event' if img["depicts_event"]
                 else f'{img["role_label"]}, not taken during the events described')
        sub = "h3" if fragment else "h2"
        cards.append(f'''<article class="fv-ex2-record" id="{prefix}-{esc(rec["id"])}" data-fvx-item data-fvx-text="{esc(needle)}">
<div class="fv-ex2-record__head"><span class="fv-ex2-label">Evidence {i + 1:02d} / {len(recs):02d}</span><span class="fv-ex2-label fv-ex2-record__kind">{esc(rec["kind"])}</span></div>
<div><{sub} class="fv-ex2-record__title">{esc(rec["title"])}</{sub}><p class="fv-ex2-record__id">{esc(img["nasa_id"])} &middot; {esc(img["credit"])} &middot; {esc(img["date_text"])}</p></div>
<p class="fv-ex2-record__summary">{esc(rec["dek"])}</p>
<p class="fv-ex2-caption"><strong>Image:</strong> {esc(shows)}.</p>
<div class="fv-ex2-callout"><span class="fv-ex2-label">Evidence limitation</span><p>{esc(rec["caution"])}</p></div>
<details><summary>Review the underlying finding</summary><p>{esc(rec["detail"])}</p></details>
<details><summary>Claim crosswalk ({len(rec["crosswalk"])})</summary>{_crosswalk(rec)}</details>
<p class="fv-ex2-record__links"><a href="{esc(safe_https(img["record_url"]))}" target="_blank" rel="noopener noreferrer">NASA archive record<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a>
<a href="{esc(safe_https(rec["report"]))}" target="_blank" rel="noopener noreferrer">Institutional research<span class="fv-ex2-visually-hidden"> (opens in a new tab)</span> &#8599;</a></p>
</article>''')
    footer = f'''<footer class="fv-ex2-footer"><div class="fv-ex2-footer__inner"><p>Source-backed integration candidate. Not published.</p>
<p><a href="{esc(safe_https(inv["url"]))}">Read the original investigation &#8599;</a> &middot; <a href="{esc(safe_https(report["url"]))}">NASA Review Board &#8599;</a></p></div></footer>''' if with_footer else ""
    open_main, close_main = ("", "") if fragment else ("<main>\n", "\n</main>")
    return open_main + f'''<section class="fv-ex2" data-fvx="desk" data-fvx-noun="evidence records" aria-labelledby="{prefix}-title">
<div class="fv-ex2-wrap">
<header class="fv-ex2-desk__head">
<p class="fv-ex2-label">Final Vestige Research Desk &middot; Apollo 1</p>
<{h} class="fv-ex2-desk__title" id="{prefix}-title">The proof <em>and the gaps.</em></{h}>
<p class="fv-ex2-desk__intro">Every claim has a history. These are the records behind our Apollo 1 investigation, and what the surviving evidence does not allow us to say.</p>
</header>
<div class="fv-ex2-desk__tools" data-fvx-tools hidden>
<div class="fv-ex2-field"><label class="fv-ex2-label" for="{prefix}-search">Search source records</label>
<input class="fv-ex2-field__input" id="{prefix}-search" type="search" data-fvx-search autocomplete="off" placeholder="Ignition, hatch, oxygen, pressure" aria-controls="{prefix}-grid"></div>
<p class="fv-ex2-status" data-fvx-status role="status" aria-live="polite"></p></div>
<div class="fv-ex2-desk__grid" id="{prefix}-grid">{"".join(cards)}</div>
<p class="fv-ex2-desk__empty" data-fvx-empty hidden>No matching evidence records. Try a different search.</p>
{footer}
</div></section>''' + close_main
