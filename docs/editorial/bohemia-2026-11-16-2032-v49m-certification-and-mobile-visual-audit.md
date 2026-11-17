# Bohemia Investigations | Reader v49m | 2026-11-16 20:32 Pacific | source, design and release audit

**RELEASE HOLD — not published.** Working candidate: [The Spillway That Kept Its Names, reader v49m](./bohemia-spillway-reader-cut-v49-2026-11-16.md). Continues the same Bohemia workstream and does not modify the canonical v48 dossier, separate Caernarvon #2151, homepage, shared templates or live WordPress posts.

## Newly checked primary-source findings

The *enrolled* Louisiana [Act 130 of 2005, SB210, printed **page 2**, PDF page index 1](https://www.legis.la.gov/Legis/ViewDocument.aspx?d=317802) has now been checked as an original **page image**. The official [legislative digest, printed **page 1**, PDF page index 0](https://www.legis.la.gov/Legis/ViewDocument.aspx?d=315214) was also checked as a separate original page image, corroborating enactment changes. The digest is explanatory, not the legally operative instrument.

1. The prior law **required DNR certification to include an owner/successor notwithstanding inability to pay prior certification costs charged before August 15, 1997, and prohibited further certification costs after that date**. The entire former provision is visibly struck through on enrolled page 2. The digest explicitly says the 2005 law removed it. This is evidence of deletion **only**, not evidence of later individual fees, rejected applications, land loss or unpaid royalties. For possible remaining cost authority, compare La. R.S. 30:21.2 (existing [source #45](https://legis.la.gov/legis/Law.aspx?d=87164)) and 2002 Administrative Code rules ([source #44](https://www.dnr.louisiana.gov/assets/docs/coastal/cup/regs.pdf)); neither establishes any claim-specific outcome.
2. The prior law directed the board to publish certified owner names at least **three times** in the official journals of **Jefferson, Orleans, Plaquemines and St. Bernard** parishes, include instructions for getting land returned, and make other reasonable efforts to locate former owners/heirs. These instructions are visibly struck through on enrolled page 2. A retrospective statutory statement about quitclaim deeds replaces them. No inference is made that every heir was actually contacted, no notice duty remained elsewhere, or all deeds were recorded.
3. The same new law expressly added property **purchased January 1, 1924–December 31, 1932** to its acquisition-category description and contemplated rescinding/reissuing a prior quitclaim deed when a DNR recertification changed an owner's fractional interest. Broader or corrected title categories existed alongside removal of the former notice and cost clauses; this is *not* proof of any person's title or receipt.

**Narrative:** Added `## The missing notice, the missing fee protection` (three source-limited paragraphs) immediately after the Act 130 introduction, before the older interest-rate discussion. Updated bibliography existing entries #29 and #66 to cite page 2 / digest page 1; retained their previously checked page-4 / digest-page-2 evidence. No new source numbers added to imply novelty of an already listed document. The distinction between statutory wording, other legal authorities, case judgments and actual payments is explicit.

## Original visual: a measurable mobile readability defect fixed in the GitHub candidate

Previous original [Act 130 v49l evidence SVG](./assets/bohemia-act130-three-deleted-clauses-v49l.svg), verified blob `0727d92e12c3114540e7bf2dbe834386a53964c4`, was reconstructed byte-identically from the fetched GitHub source for local raster testing. CairoSVG rendered **900 x 1440** and **390 x 624** PNGs; both visually inspected. **Finding:** wide-format source artwork was unclipped at desktop size, but explanatory copy and source/footer lines became uncomfortably small at 390px. This is an *asset-level mobile readability fail*, not a browser-theme test.

Created replacement first-party [v49m mobile-readable evidence SVG](./assets/bohemia-act130-readable-evidence-v49m.svg), checked Git blob SHA `6f183d17a3c1ef67931b396bc498a178f64955e8`. A byte-identical source copy was rasterized through CairoSVG at **540px natural width** and **390px rendered width (390 x 989)**; both outputs generated and the 390px result **visually inspected**. Three panels, headings, dates, large body copy, provenance footnote and warning visibly fit without clipping or sideways overflow. Larger type improves reading at mobile viewport size. This is **isolated image QA PASS at 390px**, not a real WordPress 390px theme pass, and not a substitute for a screen-reader test.

* **Creator/date:** Final Vestige Studios editorial research (AI-assisted vector design), November 16, 2026.
* **Rights:** Original first-party vector and text, © 2026 Final Vestige Studios, all rights reserved; no external image, font file, scripts or hotlinks.
* **Sources:** Louisiana Legislature, Act 130 (2005), printed p. 4 (above); official SB210 legislative digest, printed pp. 1–2 (above).
* **Alt text:** Three large readable panels describing the removed July 2009 structured-settlement deadline, annual March 1 reports and disputed-revenue escrow rule.
* **Caption:** Three statutory provisions deleted by Act 130. Deletion does not prove a judgment canceled, escrow released, or claimant paid.
* **Representation:** Original editorial *diagram*, neither an archival facsimile nor a purported historical photograph. It is not a historical reconstruction.
* **Storage:** Source-controlled SVG with original metadata, SVG <title>/<desc>, plain text/vector paths; inserted into the GitHub reader by relative path, **not** yet into WordPress.

## Independent checks

GitHub readback after manuscript + bibliography + visual changes found:

* Manuscript content SHA `2c4df065dbb4512285a9c632777045f496f60437`; reader v49m, **66 bibliography items**, **170 narrative bracketed citation references**, **54 distinct numbered sources used**, **zero dangling source numbers**. Citation reference integrity does not prove each assertion independently true; release line-review still required.
* New SVG content SHA `6f183d17a3c1ef67931b396bc498a178f64955e8` and successful isolated raster inspection as above.
* Authenticated WordPress post **#2488** remains **DRAFT**, modified `2026-11-16T02:44:46` site-local, categories 9369/232815, featured media #2484. `jetpack_seo_noindex=true`, `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`. **No WP mutation or first publish.**
* WordPress media **#2484** (NASA/USGS Landsat Feb 13, 2023) and **#2485** (NAIP/USDA Sept 20, 2007, NASA processing) retain explicit credits/captions/alt. **Anonymous direct JPEG-byte retrieval failed or could not be established in this runtime**; media metadata is not visitor-load proof.
* The public [Editorial Standards](https://finalvestige.com/editorial-standards/) and current published Journal listing were checked; no same-topic competing public post was identified, and coordination is maintained on existing issues.

## Release gates and next evidence

1. **Independent legal/editorial line-check** for the 2005 statute's reach, earlier notice/cost protections and surviving obligations; this analysis is not legal advice. Obtain source material showing claim-specific application of the cost clauses and actual notice/publication records if possible.
2. Original 2000/2005 agreements, 1998 and 2007 claimant Exhibits A, Bourgeois Bennett workpapers, audit/interest correspondence, original Aug 2005 financing instruments, execution and discharge records. Do not infer a final distribution or unpaid balance solely from an audit reserve, registry deposit, law, court opinion or minutes.
3. **Authenticated current-theme browser screenshots** at 390px and 1440px of the *exact staged reader revision*, including both public-domain/official documentary photos, the new image's placement, Source section, section headings and mobile keyboard/accessibility; the new SVG's isolated 390px image pass is only a partial production check.
4. **Anonymous working image-byte retrieval**, verified captions, source links, image credits, no overflow, and an editorial approval before any `status=publish` change. Subscriber-email suppression must be explicit on **first** publish; social remains disabled. Do not publish a partial or outdated WordPress copy.

**Grok coordination:** Potential angle after approval is the 2005 two-directional change: expanded purchase-category eligibility alongside deleted former certification-fee and heir-notice provisions. NO social actions performed. Additional external spending: **$0**.

**Coordination destinations:** [Investigations issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [production QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). No other agent's content overwritten.
