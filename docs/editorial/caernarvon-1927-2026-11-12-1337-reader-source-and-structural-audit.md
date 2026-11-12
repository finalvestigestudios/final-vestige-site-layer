# Caernarvon #2151 — source-access and draft-structure verification
**Verification window:** 2026-11-12 ~13:37–14:00 America/Los_Angeles  
**Owner:** FV Investigations Publishing Studio  
**State:** RELEASE HOLD; this note neither authorizes publication nor certifies a browser-rendered preview.

## Scope and conflict isolation
Rechecked live [Editorial Standards](https://finalvestige.com/editorial-standards/), [Journal](https://finalvestige.com/blog/) and homepage investigation listings. The Journal still shows 66 published entries and no published Caernarvon duplicate. Reviewed editorial issue [#1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463), site QA issue [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589), and recent discussion updates. Continue existing draft #2151, not a fresh story. No homepage, template, journal, media, or unrelated post modifications.

## Authenticated WordPress baseline
Read post #2151 in edit context plus its block-section manifest, **without writing**. It remains **draft**, never published, modified `2026-11-12T12:44:30` site-local, serialized Gutenberg **SHA-1 `6449c7fc2963f58f3f96aa1ea19e97f370ee3af1`**, **82 top-level blocks**, **43 source-list entries**, 11 H2 headings. Featured media #2148. `_jetpack_dont_email_post_to_subs=true`; `jetpack_publicize_feature_enabled=false`; `jetpack_post_was_ever_published=false`. The previously integrated 1955 Dantoni limitation, 2018 USACE caption provenance, and USGS Arkansas City distinctions remain. This is a new readback, not a change.

A read-only structure audit of 104,347 raw Gutenberg characters found **151 anchor links, 59 unique link destinations, zero empty/`#`/insecure-http anchors, four local documentary `img` tags each with nonempty alt text, 11 H2 headings, no duplicate HTML IDs, no iframe/script tags**. Two explicit large CSS widths (`1120px`, `720px`) were identified in the raw body; this does **not** establish browser overflow and is a focal point for 390px responsive inspection. A structural PASS is not a production-theme render PASS.

Four media records were separately read back (not pixel-rendered):
- #2148 NOAA Historic NWS collection wea00739, 1821×1190; original 1927 photographer not established; NOAA credits Steve Nicklas for archival photography; Wikimedia crop by Wisekwai; caption and alt present. [NOAA](https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg).
- #2255 LOC Poydras crevasse, April 30 1927, 1024×822; unknown photographer; no known publication restrictions, caption/alt present. [LOC catalog](https://www.loc.gov/pictures/item/2002709263/).
- #2202 Lou Block / LOC Emile Riche protest barn, **1939** not 1927, 506×640; no known restrictions, caption/alt present. [LOC catalog](https://www.loc.gov/item/2011645339/). Image does not prove claim resolution.
- #2149 National Photo Company / LOC, **April 29 1927**, 1024×805; precise location NOT identified in the catalog; no known publication restrictions, caption/alt present. [LOC catalog](https://www.loc.gov/item/2016843131/).

## Source verification advance: readable official USGS appendix text
The ordinary direct PDF URL `https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_MississippiRiver.pdf` returned 403 in the automated fetch. A separate **official full Appendix A PDF** was accessible to the text extraction service:
https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_AppendixA.pdf

The extracted printed pp. **231–232** (the end of the appendix) contain the specific Arkansas City table and discussion:
- USGS Peak-Flow File: **2,470,000 ft³/s** labeled an **estimate** for a hypothetical confined-by-levees peak, not a recovered measured crest.
- A distinct historical publication: **2,472,000 ft³/s**, cited from Chow's 1964 `Handbook of Applied Hydrology`, Dalrymple's section. Do not call two separately sourced figures independent USGS peak measurements.
- Earlier current-meter value: **1,712,000 ft³/s on April 20, 1927** at the Chicot reach, recorded before the Mounds Landing crevasse; underlying historical measurement sheets were not found by the USGS reviewers.
- The reviewers could not find a direct or indirect measurement of the May 1927 peak or a recoverable calculation demonstrating the hypothetical estimate. Exact day of the hypothetical peak likewise unknown.

The full-text [2015 Smith/Baeck peer-reviewed article](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2015WR017927) provides an independent scholarly **discussion** of those limitations, but itself cites the USGS review; it is **not an independent direct measurement**. The existing WordPress paragraph #28 already links the official Appendix A PDF and the journal DOI; bibliography already links the [USGS publication landing page](https://pubs.usgs.gov/publication/sir20085164). No text edit is needed.

**Critical limitation:** Web screenshot attempts for printed pages 231–232 of the official Appendix A PDF also returned automated **403**; this is **source-text verification only**, not a visual browser/rendered-page PASS. Container-based browsers also lack external DNS/network, so they cannot independently check reader-access or current-theme WordPress preview. Do not classify 403 as a broken public reader link.

The 2018 USACE Bonnet Carré booklet (https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf) remains visually unverified to an anonymous reader; previous caption text verification documented both `With MRC approval` and `saved the city` as **one caption**, not independent evidence. Do not infer formal authorization or inevitable city rescue from it.

## Outstanding release gates
1. **Actual editor-authenticated production-theme draft #2151 browser pixels and DOM measurements** at 390px and 1440px, keyed to SHA above, including title/hero, four historical images, original graphs, scrollable table, bibliography and footer, no overlay or horizontal overflow. Current screenshot service does not expose authenticated draft pixels. Script marker checks do not substitute for this.
2. **Ordinary-reader visual source checks** for claim-bearing USACE and USGS pages, or defensible claim-equivalent replacements with explicit editorial sign-off. We now have direct official USGS source-text corroboration, not rendered-page verification.
3. Once both PASS, inspect current modified/SHA tokens again before any publish; ensure email suppression true and publicize false on first publication. After publishing, independently fetch live URL and check responsive output, hyperlinks and image credits/alt. Grok handoff only after verified publication.

**Work performed:** research/readback, source-text cross-verification, structure and image metadata audits, coordination record. **Published:** no. **WordPress/media changes:** none. **New assets/paid calls/social distribution:** none / $0.
