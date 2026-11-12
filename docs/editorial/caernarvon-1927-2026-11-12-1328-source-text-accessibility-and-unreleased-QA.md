# Caernarvon 1927 — direct-source text-access verification and unreleased production QA

**Investigation:** Existing WordPress draft #2151, *The Levee They Blew on Purpose*. **Run:** 2026-11-12 13:28–13:xx PST. **Disposition: DRAFT / DO NOT PUBLISH.** This is a fresh verification pass; **no manuscript, homepage, theme, public page, subscription, or social distribution changes** were made.

## Coordination / identity

- Read live [Journal](https://finalvestige.com/blog/) (66 published investigations as surfaced November 12) and [Editorial Standards](https://finalvestige.com/editorial-standards/); inspected the active [Investigations #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and independent [Site QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589), plus previous 12:44 source-controlled [Dantoni audit](./caernarvon-1927-2026-11-12-1244-dantoni-1955-tax-afterlife-integration.md). No duplicate topic was opened.
- Fresh authenticated WordPress read of the **current** #2151: **draft**, site-local modified **2026-11-12T12:44:30**, Gutenberg sections SHA-1 **`6449c7fc2963f58f3f96aa1ea19e97f370ee3af1`**, **82 top-level blocks**, **43 source-list entries**, **11 H2 headings**, featured NOAA photograph #2148; newsletter suppression `_jetpack_dont_email_post_to_subs=true`, Jetpack auto-social `jetpack_publicize_feature_enabled=false`, and `jetpack_post_was_ever_published=false`. This is the **only** current release identity, subject to fresh re-read before any future write. No source text or preview hash changed this cycle.

## Claim-bearing technical documents — important improvement, not a graphic-browser PASS

### USGS, Appendix A (2008), **printed pp. 231–232**: source text now independently accessible

- **Exact current article source link:** https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_AppendixA.pdf (USGS, *Selected Extraordinary Floods in the United States and Implications for Future Advancement of Flood Science*, Appendix A, Arkansas City review; no unofficial mirror).
- An official indexed/extracted PDF-text result was **opened and read this cycle** via web retrieval; the Arkansas City discussion appears at the end (search text around lines 2578–2617). It directly differentiates Peak-Flow File **2,470,000 ft³/s** from the **2,472,000 ft³/s** value appearing in other publications and the NWIS station description. It calls these estimates of hypothetical levee-confined flow, says the calculation and peak-date records could not be recovered, reports an April 20, 1927 prior current-meter reading of **1,712,000 ft³/s** at Chicot, and recommends **approximately 2.47 million or 2.5 million ft³/s**. The article's existing paragraph #28 accurately preserves these distinctions.
- **Caution:** The document text was inspectable **through the web index/extractor**. An actual screenshot request on this PDF's near-end claim page returned **HTTP 403**, so this is **TEXTUAL CLAIM-CHECK IMPROVED / READER PIXELS NOT VERIFIED**. Neither indexed text nor a search snippet proves that an ordinary human browser can render the PDF pages. Do not mark source visual PASS.
- Independent freely available scholarly corroboration: [Smith & Baeck, *Water Resources Research* 51 (2015), 9964–9994](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2015WR017927), **free full-text HTML read and verified**. Its Introduction discusses the absence of measurement records, the 2,472,000 estimate, publication discrepancies, the hypothetical confined-levee interpretation, and historical 1,712,000 ft³/s current-meter figure. This HTML helps a reader understand the claim even if the USGS PDF is blocked. It is a **secondary peer-reviewed synthesis**, not another direct measurement nor a 1927 record. The manuscript **already links** the DOI in paragraph #28; avoid duplicate editorial churn.

### USACE Bonnet Carré Spillway booklet (December 2018)

- **Exact current article source:** https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf .
- The official USACE document's web-index text **this cycle** reproduced the caption containing both `With MRC approval` and `saved the city` as language in **one retrospective caption**. Cross-checks current paragraph #15 and #32. The official PDF again returned HTTP 403 through direct browser-like retrieval. An unofficial AnyFlip rendering carries similar words, but its 2016 provenance and independence are not verified and **it must not supplant the official edition**.
- This is **SOURCE-TEXT/CAPTION CORROBORATION**, **not** evidence of formal Corps authorization, an independently modeled no-breach flood, or an authenticated reader-browser PDF display. The post already qualifies the latter two; no correction warranted this cycle.

### Other technical source caveats

- Official *Situation Desperate* USACE historical PDF (large government-hosted download) hit a web-fetch size ceiling at roughly 60 MB in the direct retriever. The exact underlying April 1927 Jadwin/Davis correspondence was never independently opened; the manuscript explicitly attributes this to the secondary Corps history.
- Official USGS 1994 collection remains supplementary on Caernarvon flow comparisons. The original reported 1994 conference paper should not be represented as an independent current-meter measurement.

## Systematic current-draft structure & rights checks (non-visual)

Read the full 104,347-character Gutenberg markup from WordPress through the edit-context connector for automated, read-only structural checks:
- **151** hyperlink occurrences, **59** distinct href strings; no plain-`http:` hrefs, no repeated HTML IDs observed; four `<img>` tags, **all with nonempty alt text**; no `target=_blank` links lacking a `rel` attribute in the scanned markup.
- Two original evidence infographic `core/html` blocks remain; one 10-row `core/table` uses a 720px minimum-width table inside a labelled scrollable region with horizontal overflow rules. **Static markup assessment does not demonstrate visual overflow/legibility PASS.**
- Authenticated media library reads individually reconfirmed all four locally hosted historical photo IDs, dates, dimensions, credits, source links, alt texts and rights notes: #2148 NOAA (1821×1190); #2255 LOC Poydras (1024×822); #2202 Lou Block/LOC Emile Riche (506×640); #2149 National Photo Company/LOC (1024×805). Neither the image metadata nor rights-note completeness proves a live browser can render the post.

## Production screenshots and release gate: STILL BLOCKED

- The WordPress screenshot service generated **ready/public-site** screenshot URLs for `/blog/` at **390px and 1440px**. These are the **published Journal**, **not** the unpublished investigation, and do not satisfy authenticated draft preview QA. Do not label them article PASS or share private preview nonces.
- There is **no authenticated, inspectable production-theme draft #2151 screenshot** or DOM pass in this run at either **390px or 1440px**, and no ordinary-reader pixel review of the disputed official PDFs. Site QA issue #1589 remains the appropriate owner for these gates. Avoid claiming complete release based on accessible indexed text, script syntax, screenshot URL readiness or WP API response.
- Once the actual draft visual tests pass, re-read WordPress post and sections for a fresh content hash, source and rights references, category and metadata; **only then** use one first-publish request with `status=publish`, `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`; independently inspect resulting public URL, links, images, alt/credits and viewport behavior. No Grok social handoff before a verified live release.

**Outcome:** Two claim-specific government document texts and free full-text research corroboration rechecked, systematic full-manuscript static and image-metadata audit performed. **Source textual confidence strengthened; visual release blockers unchanged.** No paid services or site edits.