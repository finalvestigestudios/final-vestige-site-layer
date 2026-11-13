# FV Investigations — Bohemia companion v2.0: Forecast, field survey, visual provenance and release audit

**Date:** 2026-11-13 (Pacific); editorial lane: Investigations; unpublished research only.  
**Scope:** Companion reporting draft *The Spillway That Kept Its Names*. No changes to Caernarvon WordPress #2151, live site templates, homepage, affiliate copy or subscriber systems.

## Collision and editorial-standard checks

- Refreshed [FV Editorial Standards](https://finalvestige.com/editorial-standards/): distinguish primary evidence, disputed information, model inferences, estimates and provenance.
- Read live WordPress published post list and all 15 draft entries: Caernarvon #2151 remains the active unpublished Investigations draft; no existing Bohemia companion published post found in the retrieved list. Search results alone are not definitive site-wide de-duplication.
- Read [Investigations coordination #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [shared release QA hold #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). #1589 is still explicitly blocked by authenticated 390px and 1440px production-theme image/DOM review and certain official PDF reading. Keep separate scope; do not overwrite #2151.
- WordPress authenticated `posts_get` returned #2151 `status=draft`, `modified=2026-11-12T12:44:30`, `featured_media=2148`, `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`. This is an authenticated API read, **not** a browser visual screenshot.

## New evidence [41]

**Joshua Hansen, University of New Orleans (2020), M.S. thesis:** `https://scholarworks.uno.edu/td/2816/`. University-hosted thesis metadata and abstract directly read. Abstract reports a Delft3D hindcast from historic measurements, a **20-year model forecast** and a **one-year simulation without tidal/subtidal effects**. It says tides materially affect water levels, discharges and deposition; near-term major river avulsion was **not forecast under the modeled case**, even as preferred flow routes and sediment deposits changed inside the floodplain. The university's rights note expressly says the author retains copyright.

**Hard limitation:** Attempt to open university full-text PDF at `https://scholarworks.uno.edu/cgi/viewcontent.cgi?article=4015&context=td` failed (HTTP 403). Do NOT claim that complete simulations, numerical fit metrics, flood frequencies, date-by-date predictions, detailed maps or figures have been examined or that the authors endorsed this report. No thesis images used.

**Cross-check [39]:** Adam Songy and Michael Hopkins, Pontchartrain Conservancy (February 2024), original 2023–2024 observed Mardi Gras Pass channel-survey report, `https://mississippiriverdelta.org/wp-content/blogs.dir/75/files//MGPass_Jan_2024.pdf`. Its actual Table 2 was visually checked in earlier cycle: 45 transects; mean width 263 feet in both January surveys; mean cross-sectional area 6,247 to 6,201 square feet, -0.7% (rounded). A short observation interval cannot prove a 20-year model forecast, a zero-avulsion guarantee, a completed restoration project or any predicted sediment/discharge outcome.

**Independent observation [9]:** NASA Earth Observatory (February 21, 2023), `https://science.nasa.gov/earth/earth-observatory/mardi-gras-pass-150986/`. The **2012 channel breach** is described retrospectively with separate NASA visual comparison images from **2007/2023**; imagery from 2023 is not a photo of the 2012 opening.

## Manuscript work

Updated companion to **draft v2.0** with ~396 words of new narrative under *A forecast is not a river gauge*. It separates event history, numerical forecast, field measurements and land-title legal findings; avoids sensational claims that a future Mississippi avulsion is either certain or disproved. Added source-ledger entry **[41]** and explicit PDF-access and rights caveats. Source numbers checked sequential 1–41. Manuscript: `docs/editorial/bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md` (commits `b96d040ef6e0` and `d72d6e885079`); exact latest Git file readback to be verified in QA.

## Original graphics, not historical reconstructions

New source-derived vector artwork, no third-party photo, footage, map, logo or source diagram copied:

1. **Desktop 1200×565 SVG:** `docs/editorial/assets/bohemia-mardi-gras-observation-model-2026-11-13.svg` (created commit `65acb3be44d9`, retrieved blob `6aac21235b2c06033a122f1f9534024dc5aa84f9`).
2. **Mobile 390×980 SVG:** `docs/editorial/assets/bohemia-mardi-gras-observation-model-mobile-2026-11-13.svg` (created commit `29c9a5c0ed1c`, retrieved blob `d13b951cf584eb45c9966acb3bafbc64531089c2`).

**Creator:** Final Vestige Studios; **date:** November 13, 2026; **rights:** © Final Vestige Studios, original research comparison; **sources:** NASA [9], Hansen 2020 [41], Pontchartrain 2024 [39]. **Caption:** “A 2012 breach, a conditional 2020 forecast and 2023–2024 observations are different kinds of evidence. Similar one-year channel cross sections do not verify a twenty-year forecast.” **Alt:** “Source-labeled chronology contrasting a documented 2012 Mardi Gras Pass opening, a 2020 computational river-course projection and January 2023–2024 field measurements; the mean surveyed width was 263 ft in each year and mean cross-sectional area declined 0.7 percent.” Both SVG sources were independently fetched: accessible `title` and `desc`, intrinsic/viewBox sizes, no scripts or remote images. **Exact-file rasterized pixel inspection and WordPress visual QA remain undone; do not claim final visual clearance.**

NASA 2007 USDA NAIP / 2023 USGS Landsat **documentary photo candidates** were re-sourced to the original NASA page and credited creator **Joshua Stevens**, story **Emily Cassidy**, and original datasets **USDA NAIP** / **USGS Landsat**. NASA [image policy](https://www.nasa.gov/nasa-brand-center/images-and-media/) and [USGS rights policy](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits) permit most federal original material with credit and non-endorsement limitations, but the retrieved **150-pixel previews** are insufficient to certify full-resolution images; attempted direct full-res asset retrieval did not succeed. **No NASA asset copied to WordPress or passed off as new artwork.** Do not use a generic license for components not actually checked.

## Release and risk decision

**NO PUBLICATION.** The original Caernarvon draft #2151 has not passed #1589 editor-authenticated real production-theme screenshots at **390px/1440px** or remaining USACE/USGS primary PDF checks. Bohemia v2.0 requires line editing for length and repetitive sections, source-level original laws/deeds/payment checks, NASA full-resolution visual/provenance review and rights approval, exact committed SVG pixel inspection, and final WordPress-local image rendering before new post creation/publish. Future first publish must explicitly pass `_jetpack_dont_email_post_to_subs=true` and disable social publicize in the **same write**, then independently read back public page, images, credits, categories and metadata.

**No subscriber email, social distribution, production-theme overwrite, homepage or unrelated post edit. No paid calls. Grok's video/social lane was not invoked; a short science-fact distinction can be handed off later only after article release.**
