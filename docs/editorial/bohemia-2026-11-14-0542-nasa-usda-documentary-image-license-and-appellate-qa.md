# Bohemia — documentary imagery, Fifth Circuit limitation, and release audit
**Editorial cycle:** 2026-11-14 05:42 Pacific. **Owner:** FV Investigations Publishing Studio. **Status:** research/reader revision saved, **PUBLICATION HELD**. No public post, newsletter, social media or homepage change.

## Collision and standards checks
- Public [Journal](https://finalvestige.com/blog/) retrieved; newest publicly listed investigations include the November 2, 2026 Crystal Skulls and Mesmerism articles. No Bohemia companion seen in recent list. An explicit authenticated WordPress search for “Bohemia” across publish/draft/pending found only the unrelated *Caernarvon 1927* draft #2151 (its content apparently references the term). No new Bohemia post was created or modified.
- [Editorial Standards](https://finalvestige.com/editorial-standards/) read through authenticated WordPress page #17. The standard requires firsthand-source scrutiny, provenance, evidence/inference boundaries and reconstruction labels.
- [GitHub issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and its ongoing comments reviewed. Separate QA issue #1589 remains open. WordPress draft #2151 remains status=draft with unchanged 2026-11-12T12:44:30 modified time; `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`.
- Public /investigations/ endpoint could not be retrieved; Journal and WordPress queue served as partial substitutes. Do not claim full public navigation visual audit.

## Primary documentary image provenance and permission basis
**2007 aerial view**
- Date/explanation: September 20, 2007 NAIP aerial view of the canal before Mardi Gras Pass formed, as [NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/mardi-gras-pass-150986/) describes in its **February 21, 2023** article.
- Data producer: USDA Farm Service Agency National Agriculture Imagery Program; NASA image presentation: Joshua Stevens; NASA article: Emily Cassidy.
- Rights review: [USDA GEO / Aerial Photography Field Office public data hub](https://apfo-usdaonline.opendata.arcgis.com/) says USDA-acquired aerial photography and digital orthophotography are in the public domain. [NASA's official image/media rules](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally permit factual/editorial reuse of NASA-produced images with source acknowledgment and no implied endorsement, warning that separately marked third-party copyrighted images are exceptions. NASA's caption names the public-agency datasets; no contrary copyright notice was found on this specific NASA page. No NASA logo is used.
- Original NASA source file: https://assets.science.nasa.gov/dynamicimage/assets/science/esd/eo/images/imagerecords/150000/150986/mardigras_nap_2007263_lrg.jpg
- **WordPress media ID #2485**: https://finalvestige.com/wp-content/uploads/2026/11/bohemia-prepass-naip-2007-usda-nasa.jpg — JPEG, 1125 × 1280; 440,401 bytes according to authenticated media readback. Media-library alt text and credit caption saved and independently fetched. Original is documentary 2007 aerial imagery, **not** a 1920s photo and **not** a reconstruction. Source/caption/alt are documented in the reader edition asset register.
**2023 satellite view**
- Date/explanation: Landsat 8 OLI acquisition of Mardi Gras Pass on February 13, 2023; NASA article dated February 21, 2023.
- Data source: USGS Landsat 8; NASA Earth Observatory image/presentation by Joshua Stevens; story by Emily Cassidy.
- Rights: [USGS confirms Landsat products and imagery are public domain](https://www.usgs.gov/media/images/landsat-product-citation-screenshot); NASA factual editorial reuse policy linked above, cite both agencies, no NASA endorsement.
- Original NASA source file: https://assets.science.nasa.gov/dynamicimage/assets/science/esd/eo/images/imagerecords/150000/150986/mardigras_oli_2023044_lrg.jpg
- **WordPress media ID #2484**: https://finalvestige.com/wp-content/uploads/2026/11/bohemia-mardi-gras-pass-landsat-2023-nasa-usgs.jpg — JPEG, 1280 × 1280; 302,285 bytes via independent media readback; credit caption and alt present. Not an image of land titles, payments or the actual moment the river breached.
- Both files were ingested by WordPress server-side HTTPS from NASA and stored on finalvestige.com (no third-party hotlink in intended article). These are NASA-hosted derived image files, not a claim that full-resolution source dataset was archived. WordPress screenshot service returned `status=ready`, `capture_shows=site` at 390px for 2023 media URL; **actual screenshot pixels and reader-page responsive rendering were not inspected**. This is a readback of media metadata, not final publication QA.

## New appellate footnote QA (no new case invented)
Directly reopened the official **July 23, 2007** Fifth Circuit 17-page opinion:
https://www.ca5.uscourts.gov/Opinions/pub/07/07-30086-CV0.wpd.pdf
Visual page images checked at PDF zero-based pages 2, 9, 10, **11** (printed pp.3, 10, 11, **12**). Printed p.3 verifies the immediate/conditional settlement sums. Printed pp.10–11 show release, conditional appropriations, annual benchmark and state-court-retained enforcement jurisdiction. The court's footnote 18 on **printed p.12 was visually confirmed**, and states it **did not decide** the anti-seizure statute question because the judgment being enforced was reversed. The reader edition now distinguishes vacated seizure orders from a merits determination on that independent defense. This opinion reports numerous partial payments but does not furnish a claimant-by-claimant final disbursement register. The separate Vogt case must not be added into Haspel totals.

## Reader revision and change control
Revised [The Spillway That Kept Its Names — Reader Edition](./bohemia-spillway-reader-edition-2026-11-14.md) to revision 4: two documentary images, dated captions and alt text, public-source rights ledger, and the narrow appellate limitation. Reader narrative, conditional funding, reserve distinctions, 1984/1996/2009 chronology and the existing 57-entry master dossier remain intact. Commit is separately recorded in repository history. No WordPress post is associated with either media file and neither media file is the site's public feature image.

## Release blockers / next exact documentary requests
1. Obtain full *Haspel & Davis* state-court Consent Judgment, original Settlement Agreement, appropriation history, receipts/satisfaction and payee allocation evidence. Federal appeal does **not** establish current debt.
2. Obtain *Vogt* May 1997 accounting exhibit, 1998 signed individualized allocation judgment and satisfaction records. Its $2,853,358.44 accounting is not a payment schedule.
3. Independently reopen original **March 19, 2015** flood-authority minutes as an actual PDF page image (previous attempt failed), plus final escrow bank transfer record; recover post-2021 DNR account 1107 ledger.
4. Finish article-wide legal/editorial line QA, resolve every consequential quoted/paraphrased allegation; explicitly separate unresolved third-party record access from proved nonpayment.
5. Create a separate Bohemia **draft** only after release assembly and inspect actual WordPress content/links, locally held images, image block alt and caption, and theme at 390 and 1440px. Confirm category, URL, no competing post, internal links and metadata. On *first publication*, set `_jetpack_dont_email_post_to_subs=true` in the publishing call; disable automatic Jetpack Social. Independently read back live URL/content and do not infer completion from API success.

**Costs:** $0 new paid services. **Changes:** exactly two WordPress media items, one GitHub reader file, this audit, and issue coordination after audit. No publication or distribution.
