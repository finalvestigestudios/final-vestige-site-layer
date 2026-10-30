#!/usr/bin/env python3
"""Deterministic, static-first Experience 2.0 staging build; no third-party modules."""
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parent
REPORT = "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"

def e(value):
    return escape(str(value), quote=True)

def source_link(url, caption):
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(caption)} <span aria-hidden="true">↗</span></a>'

def validate(manifest):
    assert manifest["primary_report"] == REPORT
    records = manifest["records"]
    assert len(records) == 6 and [x["id"] for x in records] == ["01", "02", "03", "04", "05", "06"]
    assert [x["sort"] for x in records] == list(range(1, 7))
    assert len(manifest["atlas"]) == 6
    assert len({x["wp_id"] for x in manifest["atlas"]}) == 6
    for row in records:
        assert row["rights"].startswith("link_only_")
        assert re.fullmatch(r"[A-Za-z0-9 _.–-]{1,100}", row["source_id"])
        assert urlparse(row["image_url"]).netloc == "www.nasa.gov"
        assert urlparse(row["image_url"]).scheme == "https"
        for field in ("title", "summary", "finding", "limit", "image_description", "image_credit"):
            assert row[field]
    for item in manifest["atlas"]:
        assert item["geometry"] is None and item["location_review"] == "unverified"
        assert urlparse(item["url"]).netloc == "finalvestige.com"
        assert urlparse(item["url"]).scheme == "https"

def plate(row):
    id = e(row["id"])
    return f'''<figure class="ex2-plate" aria-labelledby="plate-caption-{id}">
       <div class="ex2-plate__visual" role="img" aria-label="Typographic record marker; not a historical photograph"><span class="ex2-plate__kicker">ARCHIVE INDEX / NO IMAGE REPRODUCED</span><strong aria-hidden="true">{id}<span> / 06</span></strong><span class="ex2-plate__type">SOURCE RECORD</span></div>
       <figcaption id="plate-caption-{id}"><b>{e(row['source_id'])}</b> <small>{e(row['source_date'])} · {e(row['image_credit'])}</small><p>{e(row['image_description'])}</p><p class="ex2-plate__rights">The NASA source page is verified. Its photograph is linked, not embedded, pending individual visual and rights clearance.</p></figcaption>
    </figure>'''

def stage(row):
    id=e(row["id"])
    return f'''<article id="stage-{id}" class="ex2-stage" data-ex2-stage tabindex="-1" aria-labelledby="stage-{id}-title">
    <div class="ex2-stage__body"><p class="ex2-index">{e(row['label'])} <span>· EVIDENCE {id} / 06</span></p>
      <h3 id="stage-{id}-title">{e(row['title'])}</h3><p class="ex2-stage__summary">{e(row['summary'])}</p>
      <div class="ex2-stage__boundary"><b>WHAT REMAINS UNPROVEN</b><p>{e(row['limit'])}</p></div>
      <details class="ex2-source" id="source-{id}"><summary>Open source drawer: record {id}</summary>
       <div class="ex2-source__body"><p class="ex2-source__scope"><b>What this source supports.</b> {e(row['finding'])}</p>
       <p><b>What the photograph actually depicts.</b> {e(row['image_description'])}</p>
       <p><b>Source and date.</b> {e(row['source_id'])}; {e(row['source_date'])}. Image credit: {e(row['image_credit'])}.</p>
       <p class="ex2-source__links">{source_link(row['image_url'], 'Inspect NASA photograph metadata')} {source_link(REPORT,'Read the NASA Review Board report')}</p>
       <p class="ex2-source__caution">An image's subject and the Review Board's finding are different evidence types. NASA does not endorse this independent presentation.</p></div></details>
     </div>{plate(row)}
   </article>'''

def gallery_card(row):
    """A factual record index, not a reproduced NASA photograph or an image of the fire."""
    rid=e(row["id"])
    return f'''<li class="ex2-gallery__item" data-ex2-gallery-item>
      <a class="ex2-gallery__stamp" href="#stage-{rid}" aria-label="Go to evidence stage {rid}, {e(row['source_id'])}"><span>NASA IMAGE RECORD</span><strong aria-hidden="true">{rid}</strong><small>OPEN DOCUMENTARY STAGE ↗</small></a>
      <div class="ex2-gallery__metadata"><p class="ex2-gallery__date">{e(row['source_date'])} · NASA IMAGE CATALOG</p>
      <h3>{e(row['source_id'])}</h3><p><b>What it depicts:</b> {e(row['image_description'])}</p>
      <details><summary>What it cannot establish</summary><p>{e(row['limit'])}</p></details>
      <p class="ex2-gallery__links">{source_link(row['image_url'], 'Inspect the original NASA record')} · <a href="#source-{rid}">Read our evidence limitation</a></p>
      </div></li>'''

def atlas_card(row):
    key = e(row["wp_id"])
    searchable = " ".join((row["title"], row["theme"], row["summary"]))
    return f'''<article class="ex2-atlas__item" data-ex2-atlas-item data-ex2-theme="{e(row['theme'].lower())}" data-ex2-search="{e(searchable.lower())}"><div><span class="ex2-atlas__tag">{e(row['theme'])}</span><span class="ex2-atlas__id">WP {key}</span></div><h3>{e(row['title'])}</h3><p>{e(row['summary'])}</p><p class="ex2-atlas__geonote">No mapped location: archival precision unreviewed.</p>{source_link(row['url'], 'Read published investigation')}</article>'''

def render(manifest):
    records=manifest["records"]
    rail="\n".join(f'<li><a href="#stage-{e(row["id"])}" data-ex2-rail-link><span>{e(row["id"])}</span><span>{e(row["time"])}</span></a></li>' for row in records)
    article="\n".join(stage(row) for row in records)
    gallery="\n".join(gallery_card(row) for row in records)
    atlas="\n".join(atlas_card(row) for row in manifest["atlas"])
    css=(ROOT/'assets/app.css').read_text(encoding='utf-8')
    js=(ROOT/'assets/app.js').read_text(encoding='utf-8')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Apollo 1 | The Evidence Unfolds — Final Vestige Experience 2.0 (staging)</title>
<meta name="description" content="Source-custody-first Apollo 1 archival evidence staging prototype. Six findings and limitations, NASA links, a documentary chronology, and a curated atlas without invented map pins.">
<style>{css}</style></head><body>
<a class="ex2-skip" href="#main">Skip to documentary</a>
<header class="ex2-top" aria-label="Site preview header"><a href="https://finalvestige.com/" class="ex2-brand">FINAL VESTIGE<span>STUDIOS</span></a><span>EXPERIENCE 2.0 / STAGING ONLY</span><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Original investigation <span aria-hidden="true">↗</span></a></header>
<main id="main">
<section class="ex2-hero" aria-labelledby="case-title"><div class="ex2-hero__light" aria-hidden="true"></div><div class="ex2-hero__inner">
<p class="ex2-hero__overline">ARCHIVE / 27 JANUARY 1967 / SIX DOCUMENTED RECORDS</p>
<h1 id="case-title">The evidence <em>unfolds.</em></h1>
<p class="ex2-hero__lede">The fire aboard Apollo 1 did not begin with a single proven spark. What survived instead is a documentary trail: test conditions, a crew's last transmissions, instrument readings, a hatch that could not open—and an investigation that refused to claim certainty it did not possess.</p>
<div class="ex2-hero__actions"><a class="ex2-button" href="#chronology">Follow the chronology <span aria-hidden="true">↓</span></a><a class="ex2-textlink" href="#research-desk">Inspect the source custody</a><a class="ex2-textlink" href="#source-gallery">Browse NASA source records</a></div>
<div class="ex2-hero__annotation"><strong>OUR METHOD</strong><p>Every plate distinguishes what a NASA photograph actually depicts from what the Apollo 204 Review Board concluded. No recreated accident photographs, simulated pressure curve, or invented location pins.</p></div>
</div><div class="ex2-hero__folio" aria-hidden="true">APOLLO<br><span>01</span></div></section>
<section class="ex2-section ex2-case" id="chronology" aria-labelledby="chron-title"><div class="ex2-section__intro"><p class="ex2-eyebrow">I / SIX RECORDS · A LIMITED CHRONOLOGY</p><h2 id="chron-title">Follow what <em>the record</em> can bear.</h2><p>This is a sequence of documented conditions, events and later decisions—not a continuous sensor replay. Time markers have different meanings and are explicitly labeled.</p></div>
<div class="ex2-case__layout"><nav class="ex2-rail" aria-label="Six evidence stages"><span>CHRONOLOGY RAIL</span><ol>{rail}</ol><p>Choose a stage to jump to its evidence. Without JavaScript, all six remain in the document.</p></nav>
<div class="ex2-stages">{article}</div></div></section>
<section id="research-desk" class="ex2-section ex2-custody" aria-labelledby="custody-title"><div class="ex2-section__intro"><p class="ex2-eyebrow">II / THE RESEARCH DESK</p><h2 id="custody-title">The source is <em>not</em> the interpretation.</h2><p>Six NASA photograph records have been matched to their actual published descriptions. Some were previously associated with a historical claim they cannot visually establish. Those distinctions are now explicit in every drawer above.</p></div><div class="ex2-custody__grid"><div class="ex2-custody__claim"><h3>Primary finding</h3><p>The Apollo 204 Review Board is the primary source for pressure, timing, cause investigation and egress limitations. It reports that no single ignition source was conclusively identified.</p>{source_link(REPORT,'Read the full Board report')}</div><div class="ex2-custody__claim"><h3>Image custody</h3><p>NASA's six linked photographs depict crew training, spacecraft preparation, post-fire damage or a 2017 memorial exhibit. They do <strong>not</strong> depict a real-time pressure graph, fire ignition or 1967 hatch operation.</p><p>Image reproduction is disabled in this prototype while actual asset transport, third-party credits and promotional-use constraints are audited.</p></div><div class="ex2-custody__claim"><h3>Media policy</h3><p>NASA generally permits informational reproduction of its released imagery subject to restrictions: retain source credit, do not use insignia as branding, do not imply NASA endorsement, and review third-party and identifiable-person rights.</p>{source_link(manifest['rights_policy'],'Read NASA brand and media guidelines')}</div></div><p class="ex2-custody__status">RESEARCH STATUS · 6 NASA description pages verified · image bytes not included · 0 speculative map points</p></section>
<section id="source-gallery" class="ex2-section ex2-gallery" aria-labelledby="gallery-title"><div class="ex2-section__intro"><p class="ex2-eyebrow">III / THE SOURCE GALLERY</p><h2 id="gallery-title">Six records. <em>Six different meanings.</em></h2><p>A dated index of the six NASA photograph records used in this research. The archive plates below are typographic representations—not reproduced accident photographs. Read what each real image depicts, what it cannot prove, and where NASA holds the source metadata.</p></div>
<ol class="ex2-gallery__grid">{gallery}</ol><p class="ex2-gallery__notice">Source-only gallery · no image bytes loaded · NASA credits preserved in linked records · this independent exhibition is not affiliated with or endorsed by NASA.</p></section>
<section id="atlas" class="ex2-section ex2-atlas" aria-labelledby="atlas-title"><div class="ex2-section__intro"><p class="ex2-eyebrow">IV / EVIDENCE ATLAS</p><h2 id="atlas-title">A map begins with <em>a verifiable place.</em></h2><p>Browse six published Final Vestige investigations. We have verified the published entries, not precise coordinates. Until primary evidence and location precision are reviewed, this atlas is an accessible catalog—with no false pins, lines or map edges.</p></div>
<div class="ex2-atlas__tools" data-ex2-atlas-tools hidden><label for="atlas-filter">Filter archive</label><select id="atlas-filter" data-ex2-atlas-filter><option value="all">All themes</option><option value="engineering">Engineering</option><option value="disasters">Disasters</option><option value="expeditions">Expeditions</option></select><label for="atlas-search">Search titles & topics</label><input type="search" id="atlas-search" data-ex2-atlas-search placeholder="Find an investigation" autocomplete="off"><output data-ex2-atlas-status aria-live="polite" role="status"></output></div>
<div class="ex2-atlas__grid" data-ex2-atlas-grid>{atlas}</div><p class="ex2-atlas__empty" data-ex2-atlas-empty hidden>No matching investigations. Try another search.</p></section>
<footer class="ex2-footer"><span>FINAL VESTIGE STUDIOS · INDEPENDENT STAGING STUDY · NOT DEPLOYED</span><span><a href="https://finalvestige.com/">Return to live Final Vestige</a> · <a href="#main">Back to top ↑</a></span></footer>
</main><script>{js}</script></body></html>'''

if __name__ == '__main__':
    manifest=json.loads((ROOT/'records.json').read_text(encoding='utf-8'))
    validate(manifest)
    rendered=render(manifest)
    dest=ROOT/'index.html'
    dest.write_text(rendered,encoding='utf-8',newline='\n')
    print(f'Generated {dest.name}: {len(rendered.encode("utf-8"))} bytes')
