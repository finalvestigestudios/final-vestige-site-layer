# The Link Is a Lead — source-trail witness and publication audit

**Owner:** Final Vestige Studios Library Resource Studio. **Last checked:** 2026-11-15 (Pacific).  
**Scope:** the ten currently published direct Library guide/dossier child pages listed below; not the 90-card Research Sources directory, homepage, Prepar­edness, Investigations, social accounts or shared design.  
**Release decision:** **No public WordPress edit.** Field-guide/workbook prepared; link-route testing is incomplete and live-theme QA remains unresolved.

## Reader problem: a link can work while the evidence does not

An archive homepage, a help article, an item-level record, an editable catalog transcription, and a rights statement can all be legitimate institution-controlled URLs. They do not prove the same thing. An editorial claim may fail if its original-record CTA leads to a usage FAQ, or if a catalog description is presented as a primary scan. A 403, 429, content-type error, JavaScript gate or timeout in an automated reader does not alone establish that a normal public browser cannot open it.

The accompanying original illustrated **four-page PDF field guide and printable Source-Trail Witness Card** is delivered as a conversation artifact. Its six-pass method is **capture → follow → compare → qualify → clear → recheck**. It contains an original FV evidence-flow diagram, a blank link-level provenance/rights worksheet, and the exact publication audit totals below; no archival scans or third-party images were copied.

The complete source-trail inventory, based on authenticated WordPress edit-context **raw markup**, is:

[**Published Library Source-Trail Ledger — 254 page+destination records (CSV)**](./published-library-source-trail-2026-11-15.csv)

The ledger preserves page ID/slug/title, site-local modified time, link class, source-label text, original destination URL, repetition count, access-check status, and a **link-only / reproduction rights NOT cleared** flag. It is deliberately not a comprehensive live-link-check result.

## In-scope inventory

| WordPress ID | Published guide | Raw `<a>` occurrences | Distinct destinations within page |
|---:|---|---:|---:|
| 2213 | The Quote That Crossed a Language | 26 | 15 |
| 2209 | The Page That Changed | 28 | 24 |
| 2204 | The List Without the Passenger | 45 | 30 |
| 2198 | The Year That Changed Twice | 40 | 32 |
| 2185 | The Machine in the Drawing | 30 | 27 |
| 2178 | The Box Behind the Citation | 50 | 39 |
| 2173 | The Boundary That Moved | 38 | 26 |
| 2165 | The Same Story Twice | 41 | 29 |
| 2152 | The Black Bar | 31 | 17 |
| 1377 | Puységur's Animal Magnetism Files | 18 | 15 |
| **Total** | **10 pages** | **347** | **254** |

**Definitions:** A link occurrence is an anchor in serialized raw Gutenberg content (including repeated citations and any HTML contained in raw blocks). A distinct destination is deduplicated **within each page**; the same URL in two different pages creates two ledger records. **93** of 347 occurrences were repeated page-local destinations. The counts are *not* equivalent to visible rendered links, third-party URLs, confirmed-good links, or unique websites across the whole corpus. An exact same-page fragment check found **zero missing targets** among fragment-only anchors in this raw inspection; this does not substitute for browser or accessible-name QA.

These ten guides were unchanged in WordPress and all were confirmed `status=publish` in authenticated reads. Their site-local last-modified dates range from November 5 to November 7, 2026.

## Sample institution/route checks (not exhaustive)

| Route / example | Observation on 2026-11-15 | Qualification |
|---|---|---|
| [NARA — Contribution: Transcription](https://www.archives.gov/research/catalog/lcdrg/contribution/transcription) | Institutional page retrieved | Catalog transcription data has contributor provenance and is not a facsimile of the original item |
| [NARA — Container List](https://www.archives.gov/research/catalog/lcdrg/elements/container-list) | Institutional page retrieved | A container range does not identify every individual page or folder |
| [LOC — Curious Cases / selected articles](https://guides.loc.gov/chronicling-america-curious-cases/selected-articles) | LOC guide retrieved | A guide or index must be distinguished from the issue/page image it links |
| [USPTO — Lost X-patents](https://www.uspto.gov/blog/the-search-for-lost-x) | USPTO page retrieved | Finding-aid commentary, not a substitute for an individual patent |
| [NARA — Declassified Records](https://www.archives.gov/research/declassification.html) | NARA page retrieved | Overview, not proof that a specific withholding has been lifted |
| [NARA — Copyright and Permissions](https://www.archives.gov/research/still-pictures/permissions) | NARA page retrieved | Item rights remain un-cleared; custody does not establish public-domain status |
| [FV — The Lost Itinerary](https://finalvestige.com/the-lost-itinerary/) | Public page retrieved | Cross-link route only |
| [FV — The Moving Noon](https://finalvestige.com/the-moving-noon/) | Public page retrieved | Cross-link route only |
| [UK legislation historical section link ending `/section/1.`](https://www.legislation.gov.uk/apgb/Geo2/24/23/section/1.) | Automated retrieval returned unsupported XHTML | **Inconclusive; do not remove or rewrite without ordinary-browser check** |
| [FV `/archive-shelf/`](https://finalvestige.com/archive-shelf/) | Automated reader returned HTTP 429 | **Inconclusive; do not call the link broken** |

A later, separate verification must test the actual cited page/edition for each key claim, not only an institution's index.

## Six-pass practical field method

1. **Capture:** keep the precise original URL, visible link text, WP source page, date checked, cited claim and expected content type.
2. **Follow:** distinguish item/download, catalog description, search portal, methodology, institution homepage, and rights-only page. Do not exchange them silently.
3. **Compare:** evaluate what the destination actually substantiates. Record IDs, issue/page/volume, authorship, timestamps and edition.
4. **Qualify:** use separate statuses for retrieved, redirects, declared 404, 403/429, JS-required, timeout, PDF-content not visually inspected, and content mismatch. Do not infer failures from access denial.
5. **Clear:** before copying media, record creator, owning institution, creation date, item URL, rights/license or documented restriction, required credit, and privacy/publicity/donor restrictions. A page being freely readable is **not** reuse permission.
6. **Recheck:** re-open source links using a normal unauthenticated browser before an editorial release, preserve exact older URLs, then verify the published source route.

### Permissions and provenance

- *Authored material:* original FV field guide text, vector diagram, blank worksheet and this audit register, produced 2026-11-15. No AI-generated or reconstructed historical document imagery; none is presented as evidence.
- *Source data:* 254 destination references/title metadata extracted from user-owned published Final Vestige WordPress content by authenticated read; site content was not rewritten.
- *Third-party rights:* **no assets cleared for republication.** Institutional pages are linked, not copied. NARA [Copyright and Permissions](https://www.archives.gov/research/still-pictures/permissions) explicitly warns that some of its archival holdings retain copyright, deed or donor restrictions. LOC [Free to Use and Reuse](https://www.loc.gov/free-to-use/) offers selected materials but does not convert every LOC holding to an unrestricted work. Site-wide FV [Editorial Standards](https://finalvestige.com/editorial-standards/) control the work.
- *Media audit:* no new photo/video/scan embeds. Original diagram is solely editorial process visualization, with its meaning described in adjacent text. No Grok distribution, email send, media upload or spending.

## QA and release gate

**Passed in this run:** inventory from current authenticated WordPress edit-context; all ten pages published, 347 raw links, 254 page-deduplicated routes; ten-page CSV written to GitHub; original 4-page PDF rendered and visually inspected; sample institutional route checks; rights/access ledger distinguished from licensing. Current links in the public [Library](https://finalvestige.com/free-resources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), and [Research Sources](https://finalvestige.com/free-resources/research-sources/) were inspected for context.

**Not passed / not represented as passed:** 254/254 ordinary-browser link retrieval; historical legislation XHTML route; `/archive-shelf/` after rate limit; WordPress production-theme 320/390/768/1440 screenshots, keyboard and no-JS inspection, full external archive PDF visual comparison; item-level rights clearance; anonymous media delivery; any live-page release. GitHub CSV presence proves an inventory, not source availability. Do **not** publish companion into WordPress, auto-email subscribers, create a nav card or change the live source directory on this evidence.

**Coordination:** count-label mismatch and 90-card Research Sources staging remain [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788), production screenshot workflow [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). These are independent; do not promote 90-card staging or change a public Library page as part of this guide audit.

**Potential Grok promotion after release only:** “The URL works. But does it lead to the original record?” Use only the original FV process diagram; no Grok account access or promotion was attempted.
