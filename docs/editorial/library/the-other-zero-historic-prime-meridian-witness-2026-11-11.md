# The Other Zero — historic prime-meridian field guide and Meridian Witness Card

**FV Library Studio | 2026-11-11 Pacific | Status: HOLD — not published to WordPress**

## Why it matters

A nineteenth-century map can print a perfectly legible longitude from a prime meridian other than Greenwich. The map number is not necessarily wrong; its zero is different. This *does not* duplicate Library's existing The Coordinate That Moved (datum provenance), The Scale in the Copy (map reproduction scaling), The North in the Margin (magnetic declination), The Lost Landscape (place reconstruction) or The Moving Noon (historical clocks). First verified public Library and Editorial Standards and searched GitHub coordination issues. No similarly scoped issue was found.

## Original deliverables, finished locally

- 29 KB standalone accessible `The_Other_Zero.html`: original SVG meridian ruler with text alternative, seven-step method, worked example, source ledger and browser-local 12-field Meridian Witness Card; approximately rounded degrees/minutes calculator supports Ferro/Paris/Pulkovo/Greenwich and reverse conversions; local JSON export/print; no calls to remote scripts, APIs, or user-data services.
- 3-page original vector `Meridian_Witness_Field_Cards.pdf`, rendered and visually inspected.
- 11-entry `Source_Provenance_Rights.csv`: authors/owning institutions, dates/last-check, originals, source roles, access status and individual rights considerations.
- Reproducible build, browser QA script, QA results, SHA-256 manifest, ZIP package.
- All artifacts are attached to the corresponding Library Studio run, **not publicly hosted**. No third-party map scans or copyrighted photos copied.

## Scientific and historical guardrails

Library of Congress rounding: Ferro **−17°40′**, Paris **+2°20′**, Pulkovo **+30°20′** relative to Greenwich. For an east-positive historical longitude, approximate Greenwich longitude = historical longitude + historical zero's Greenwich offset (then normalize across ±180°). Example from the LOC method: **39°57′ E of Ferro ≈ 22°17′ E of Greenwich**. This is *only* historical reading of longitude labels, **not** a map projection, datum, survey-control, legal-boundary, navigation, or site-location transformation. Never print spurious second-level precision based on these rounded offsets. 1884 conference proceedings do not prove every post-1884 sheet used Greenwich. London and Washington meridians are not equated to single precise offsets because archival usage can vary.

## Sources & access ledger (checked 2026-11-11)

1. [Library of Congress — Latitude and Longitude](https://guides.loc.gov/maps-genealogy-eastern-europe/coordinates/latitude-longitude) — official historical-meridian methodology and rounded offsets; retrieved.
2. [NYPL — Using Latitude and Longitude](https://libguides.nypl.org/findingplaces/latandlong) — historic maps and coordinate caution; retrieved.
3. [1884 International Meridian Conference proceedings](https://www.gutenberg.org/cache/epub/17759/pg17759-images.html) — contemporary official primary proceedings in public-domain transcription; retrieved.
4. [LOC John Wallis 1783 map](https://www.loc.gov/item/gm71005486/) — LOC search metadata shows London meridian; direct automated open 403; ordinary-browser check **OPEN**. Link only, item rights pending.
5. [LOC Maria Hubbard 1809 map](https://www.loc.gov/item/2015591086/) — LOC search metadata shows Washington meridian; direct automated open 403; ordinary-browser check **OPEN**. Link only, item rights pending.
6. [NOAA NGS NCAT](https://beta.ngs.noaa.gov/NCAT/index.xhtml) — authoritative separate datum/coordinate transformation tool; retrieved.
7. [NOAA NGS historical geodetic diagrams](https://www.ngs.noaa.gov/data/survey_maps/) — official warning against using historic diagrams as present survey control; retrieved.
8. [FV The Lost Landscape](https://finalvestige.com/the-lost-landscape/) — live, related guide.
9. [FV The Moving Noon](https://finalvestige.com/the-moving-noon/) — live, related historical time work.
10. [FV Editorial Standards](https://finalvestige.com/editorial-standards/) — live FV source/rights policy.
11. [FV The Piri Reis Map investigation](https://finalvestige.com/2026/11/02/piri-reis-map/) — authenticated published investigation link, for source-specific historic chart interpretation; no prime-meridian offset is inferred for that chart.

Rights: all diagrams and worksheets are original FV creations; no archival imagery rehosted. External source links do not imply permission to republish external images; item-level rights still apply.

## Local QA

**38/38 standalone Chromium tests PASS**, on 320, 390, 768, 1440 px with JS enabled/disabled: no horizontal overflow or uncaught JS error; SVG and heading rendered, approximate arithmetic in both directions validated, invalid DMS rejected, reset worked, JSON export locally with inert HTML-shaped text, non-HTTP URL rejected, keyboard focus and worksheet clear tested. PDF 3-page raster review PASS; ZIP integrity PASS. Local browser cannot navigate production WordPress or read mshots pixels because container network/DNS blocks access; local fixture tests **are not production-theme validation**.

## Publication gate

**HOLD.** Both LOC catalog records need ordinary-browser checks, production-theme screenshots at 320/390/768/1440 must be inspectable and tested for keyboard, text wrapping and media, and per-first-publication notification/social-sharing suppression must be enforceable. Publishing to WordPress would otherwise violate Library's stated gate. Do not modify #1338 Research Sources, #2354 staging, #77 Library index or any shared templates until QA and scoped coordinated release. In particular, #1788's 90-card directory repair remains higher priority. No content, pages, settings, mailing lists, social accounts, or live URLs changed.

Potential Grok lane (NOT sent or published): visual short starting with a map labeled 39°57′ and a modern pin in the wrong place; show two zero meridians, then invite viewers to the free witness card *after* live release. Avoid suggesting the approximation is suitable for field navigation.
