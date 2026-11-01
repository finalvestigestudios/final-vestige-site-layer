"""Render the Evidence Atlas catalogue from atlas/data/atlas.json. No map: pins are gated on `map_eligible`."""
from __future__ import annotations

import json
import sys

from fvx_lib import EX2, INSTANCE_PLACEHOLDER, esc, safe_https

sys.path.insert(0, str(EX2 / "atlas" / "tools"))
from validate_atlas import map_eligible, validate  # noqa: E402

DATASET = EX2 / "atlas" / "data" / "atlas.json"
STATUS_TEXT = {
    "verified_coordinate": "Verified coordinate",
    "approximate_region": "Approximate region",
    "unverified_reference": "Location under review",
}


def _date_text(ev: dict) -> str:
    if ev["date_precision"] == "unknown" or not ev["date_from"]:
        return "Date not yet established"
    span = ev["date_from"] if ev["date_from"] == ev["date_to"] else f'{ev["date_from"]} to {ev["date_to"]}'
    return f'{span} ({ev["date_precision"]}, {ev["date_status"]})'


def render_atlas(dataset_path=DATASET, fragment: bool = False) -> tuple[str, dict]:
    """`fragment=True` renders for embedding in a WordPress post: no masthead, heading levels shifted below the post h1."""
    ds = json.loads(dataset_path.read_text(encoding="utf-8"))
    errors = validate(ds)
    if errors:
        raise ValueError("Atlas dataset invalid: " + "; ".join(errors[:5]))
    events = {e["id"]: e for e in ds["events"]}
    places = {p["id"]: p for p in ds["places"]}
    themes: dict[str, str] = {}
    for inv in ds["investigations"]:
        themes.update(zip(inv["themes"], inv["theme_labels"]))
    chips = '<button type="button" class="fv-ex2-chip" data-fvx-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" class="fv-ex2-chip" data-fvx-filter="{esc(slug)}" aria-pressed="false">{esc(label)}</button>'
        for slug, label in sorted(themes.items(), key=lambda kv: kv[1])
    )
    cards = []
    for inv in sorted(ds["investigations"], key=lambda i: i["published"]):
        ev = events[inv["event_ids"][0]]
        place = places[ev["place_id"]]
        needle = " ".join([inv["title"], ev["label"], place["display_name"], *inv["theme_labels"]])
        status = place["location_status"]
        sub = "h3" if fragment else "h2"
        cards.append(f'''<article class="fv-ex2-atlascard" data-fvx-item data-fvx-text="{esc(needle)}" data-fvx-theme="{esc(" ".join(inv["themes"]))}">
<p class="fv-ex2-label">{esc(" / ".join(inv["theme_labels"]))}</p>
<{sub} class="fv-ex2-atlascard__title"><a href="{esc(safe_https(inv["url"]))}">{esc(inv["title"])}</a></{sub}>
<div class="fv-ex2-atlascard__meta"><span><strong>Event:</strong> {esc(ev["label"])}</span><span><strong>Date:</strong> {esc(_date_text(ev))}</span><span><strong>Published:</strong> {esc(inv["published"])}</span><span><strong>Cited outside sources:</strong> {inv["outbound_source_count"]}</span></div>
<p class="fv-ex2-atlascard__place" data-location-status="{esc(status)}"><span class="fv-ex2-badge">{esc(STATUS_TEXT[status])}</span><span>{esc(place["display_name"])}. Not mapped.</span></p>
</article>''')
    eligible = [p["id"] for p in ds["places"] if map_eligible(p)]
    report = {"investigations": len(ds["investigations"]), "map_eligible_places": len(eligible), "relationships_total": len(ds["relationships"]),
              "relationships_approved": sum(1 for r in ds["relationships"] if r["review_status"] == "approved")}
    h = "h2" if fragment else "h1"
    mast = "" if fragment else '''<header class="fv-ex2-masthead"><div class="fv-ex2-wrap fv-ex2-masthead__inner"><a class="fv-ex2-masthead__brand" href="https://finalvestige.com/">Final Vestige Studios</a>
<nav class="fv-ex2-nav" aria-label="Experience navigation"><a href="../apollo-1/index.html">Evidence Unfolds</a><a href="../research-desk/index.html">Research Desk</a><a href="index.html" aria-current="page">Evidence Atlas</a></nav></div></header>
'''
    main_open, main_close = ("<div>", "</div>") if fragment else ("<main>", "</main>")
    body = f'''<div class="fv-ex2" data-fvx="atlas" data-fvx-noun="investigations">
{mast}{main_open}<div class="fv-ex2-wrap">
<header class="fv-ex2-desk__head"><p class="fv-ex2-label">Evidence Atlas &middot; catalogue</p>
<{h} class="fv-ex2-desk__title">Every investigation, <em>on the record.</em></{h}>
<p class="fv-ex2-desk__intro">Published investigations, filtered by theme. A map pin appears only after a place has a verified coordinate, a stated precision and a reviewed source. {len(eligible)} of {len(ds["places"])} places qualify today, so nothing is plotted.</p></header>
<div class="fv-ex2-atlas__controls" data-fvx-tools hidden>
<div class="fv-ex2-field"><label class="fv-ex2-label" for="atlas-search">Search investigations</label><input class="fv-ex2-field__input" id="atlas-search" type="search" data-fvx-search autocomplete="off" placeholder="Fire, water, expedition" aria-controls="atlas-grid"></div>
<div class="fv-ex2-atlas__chips" role="group" aria-label="Filter by theme">{chips}</div>
<p class="fv-ex2-status" data-fvx-status role="status" aria-live="polite"></p></div>
<div class="fv-ex2-atlas__grid" id="atlas-grid">{"".join(cards)}</div>
<p class="fv-ex2-desk__empty" data-fvx-empty hidden>No investigations match. Try a different search or theme.</p>
</div>{main_close}
<footer class="fv-ex2-footer"><div class="fv-ex2-wrap fv-ex2-footer__inner"><p>Catalogue generated from published WordPress posts (snapshot {esc(ds["generated_from"]["snapshot_retrieved_at"][:10])}). Integration candidate: not published.</p></div></footer>
</div>'''
    pid = "fv-ex2-atlas-" + (INSTANCE_PLACEHOLDER if fragment else "main")
    body = body.replace("atlas-search", f"{pid}-search").replace("atlas-grid", f"{pid}-grid")
    return body, report
