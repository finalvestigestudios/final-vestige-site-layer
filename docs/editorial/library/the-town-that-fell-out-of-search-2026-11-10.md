# The Town That Fell Out of Search
**Final Vestige Studios — Library research and publication candidate**  
**Last checked:** November 10, 2026  
**State:** RESEARCH READY / PUBLICATION HOLD. No live WordPress change.

## The problem
The town is on an old map. A postal document uses its name. You type the name into a modern government database and get nothing.

That empty result does not answer the historical question. It describes what a particular index returned, using its present-day rules. Places can change names, move, lose an administrative function, fall outside a dataset's coverage, or be recorded under another county. A *name*, a *feature*, a *boundary*, and an *index entry* are not interchangeable evidence.

The guide and its original **Place Witness Card** teach readers to retain all four.

## What the sources establish
1. **The GNIS distinction.** The U.S. Geological Survey's Domestic Names system identifies official geographic names, feature IDs, variant names and selected geographic feature classes. A historical variant can belong to a feature still present. A GNIS feature marked “historical” has a specific status; do not read it as merely “the place is old.” [USGS Domestic Names](https://www.usgs.gov/us-board-on-geographic-names/domestic-names) · [GNIS definitions](https://www.usgs.gov/us-board-on-geographic-names/what-geographic-names-information-system-gnis).
2. **The missing-category trap.** USGS says many manmade/administrative classes—including post offices, schools, bridges and cemeteries—were removed from GNIS in 2021. Failure to find a former post office there cannot establish that it never existed. [USGS](https://www.usgs.gov/faqs/does-geographic-names-information-system-gnis-include-manmade-and-administrative-features-such).
3. **The alternate-name trail.** GNIS All Names downloads include official and variant forms; record the unique feature identifier before merging search hits. Retain the extract's date. [GNIS download guide](https://www.usgs.gov/us-board-on-geographic-names/download-gnis-data).
4. **The map edition.** topoView opens historical USGS topographic editions. Record the sheet name, scale, edition/publication or revision date, and exact label. Different editions may disagree. A printed label is evidence of cartographic representation, not necessarily the settlement's founding date or a complete list of local structures. [USGS topoView](https://www.usgs.gov/tools/topoview).
5. **The postmaster's sketch.** National Archives M1126 site-location reports can include local landmark distances and annotated sketches, generally not exact coordinates. Reports can appear under newer office names or changing counties. [NARA, Post Office Reports of Site Locations, 1837–1950](https://www.archives.gov/research/post-offices/locations-1837-1950.html).
6. **The census-vintage problem.** Census Gazetteer files are snapshots of defined geographic areas and identifiers, not a universal place-name history. Census cautions against assuming one-to-one correspondence of entities and codes across vintages because geographic names and boundaries change. [2020 Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html).
7. **Foreign names are a separate system.** NGA's Geographic Names Server is for names outside the U.S.; it specifically directs researchers to GNIS for U.S. features. Naming and coordinates can require political and technical qualifications. [NGA Geographic Names Server](https://geonames.nga.mil/geonames/GNSHome/index.html).

## Seven-pass field procedure
1. Copy the historic name exactly, including spelling and punctuation. Capture the page, frame, folio, or archival item identifier.
2. Establish the *claimed* time, then record historic jurisdiction, waterways, roads, county, and neighboring places without silently substituting modern versions.
3. Search GNIS official and variant names. Save Feature ID, feature class, source date, and negative-search limitations.
4. Compare at least two dated maps covering the same area, noting map scale, sheet edition, labeling and uncertainties.
5. For postal settlements, investigate NARA M1126 reports and alternate filing names. A site sketch supports relative location, not survey precision.
6. Use an appropriate Census vintage to distinguish named geographic entities; do not infer a timeless crosswalk or confuse a representative coordinate with the full boundary.
7. Write a provisional finding with links and contradictory observations. Distinguish “same-name candidate” from “supported same-place identity.”

## The Place Witness Card
The standalone HTML tool (delivered in the Library automation run) contains the original four-source schematic and a local-only, no-account research worksheet. Fields: verbatim name; suspected jurisdiction; target period; feature type; GNIS evidence; topo map editions; postal source; Census vintage; counter-evidence; confidence; last review date; provisional finding. It exports a JSON research record. No historical documents, maps, seal or photographs are embedded. A four-page PDF field card includes eight clickable primary-source links and a printable witness worksheet.

**The example in the field card is hypothetical, not an asserted historical site.** Use the actual archival records before making a factual claim about a real settlement.

## Provenance, rights and access ledger
All source landing pages were reviewed through official-institution web results November 10, 2026. Catalog access and web retrieval do **not** establish permission to reproduce an item, or prove that every downloadable image/media object works. Original graphics only; no third-party scan or map copied.

| Institution / collection | Primary link | What it proves or limits | Rights / access qualification |
| --- | --- | --- | --- |
| USGS / Domestic Names | https://www.usgs.gov/us-board-on-geographic-names/domestic-names | U.S. names, variants, Feature IDs, coverage rules | Government text/data linked, not reproduced |
| USGS / GNIS FAQ | https://www.usgs.gov/us-board-on-geographic-names/what-geographic-names-information-system-gnis | Historical-status versus variant-name distinction | Official explanatory page, link only |
| USGS / GNIS downloads | https://www.usgs.gov/us-board-on-geographic-names/download-gnis-data | All Names extracts and data provenance | Keep file vintage and metadata |
| USGS / topoView | https://www.usgs.gov/tools/topoview | Dated topo map editions | Maps generally public domain, but no maps copied here |
| Census Bureau / 2020 Gazetteer | https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html | Vintage-specific entities and codes | Do not conflate with historical communities |
| National Archives / M1126 | https://www.archives.gov/research/post-offices/locations-1837-1950.html | Surviving postal site reports and sketches | Records can contain privately created material; check object-level rights |
| Library of Congress / Cities and Towns | https://www.loc.gov/collections/cities-and-towns/about-this-collection/rights-and-access/ | Map-finding path and rights advisory | Institutional rights advisories must be checked per map |
| NGA / GNS | https://geonames.nga.mil/geonames/GNSHome/index.html | Non-U.S. name system | Data-use caveats; protected institutional names and seal |

## Internal navigation (upon publication)
Link from [The Library](https://finalvestige.com/free-resources/), next to *The Lost Landscape*; crosslink [Research Sources](https://finalvestige.com/free-resources/research-sources/) and [Editorial Standards](https://finalvestige.com/editorial-standards/). Do not alter homepage, Preparedness, Investigations, or the already-staged Research Sources corrections.

## Release QA and HOLD
- Static HTML QA: 16 checks pass, including source/ledger reconciliation, accessible SVG title and description, labels, no external scripts/media, print-card links and four PDF pages.
- Interactive witness tool: Node mock-DOM functional checks for JSON export, reset, print, and treating HTML-like text as inert data pass.
- PDF: rendered with PyMuPDF and inspected page-by-page. Initial overlapping content on pages 2–4 was corrected and second render verified.
- **Browser QA not passed.** Playwright launched but browser navigation to `file://` and localhost returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Cannot claim 320/390/768/1440 actual browser PASS or production-theme PASS.
- Anonymous public resource and downloadable-media checks unavailable, as there is no live WordPress resource yet.
- WordPress page-writing connector does not expose the required first-publish notification and auto-social suppression keys. **Do not publish or put a public link in Library cards until release blockers in #1589 pass.**
- Existing public Research Sources page #1338 and its unpublished staging page #2354 are unchanged by this candidate.

**Grok angle only after release:** “The town is on the old map. Why can't you find it in a modern federal database?” No posting or account actions authorized here.
