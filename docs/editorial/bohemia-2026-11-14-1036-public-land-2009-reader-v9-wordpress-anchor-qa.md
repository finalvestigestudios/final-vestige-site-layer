# Final Vestige Investigations: Bohemia reader v9, public-land distinction and WordPress draft QA
**Cycle:** November 14, 2026, approximately 10:36 a.m. Pacific  
**State:** RELEASE HOLD. No article published; no subscription or social delivery.  
**Scope:** WordPress **post #2488** only; no changes to post #2151, homepage or shared templates. Issue #1463 coordinates the investigation; QA issue #1589 governs authenticated visual proof.

## Primary record reverified
The **Louisiana First Circuit Court of Appeal, September 10, 2009**, *Plaquemines Parish Government v. Department of Natural Resources*, docket 2008 CA 2094, is available in a [seven-page judicial opinion PDF](https://cases.justia.com/louisiana/first-circuit-court-of-appeal/2008ca2094-1.pdf?ts=1462355169) and [searchable reproduction](https://law.justia.com/cases/louisiana/first-circuit-court-of-appeal/2009/2008ca2094-1.html). Original PDF **printed pages 6 and 7** (zero-based indices 5 and 6) were **visually inspected** this cycle. The court rejected the effort of Plaquemines Parish Government, acting for Grand Prairie Levee District, to obtain a return under Act 233 for land transferred between public districts under legislative acts. Dismissal for failure to state a cause of action was affirmed. The constitutional exception addresses property expropriated or purchased under threat of expropriation from private owners, not a legislative public-to-public conveyance. The opinion describes approximately 51% private-acquisition and 49% public-transfer categories; those figures are rounded and are NOT a complete ownership or payment inventory. This does not establish any private claimant's final title or payment.

**Source-provenance note:** this 2009 decision was **already captured in master dossier source [20]**, visually checked on November 12. This cycle reverified its central reasoning and **promoted it to the reader edition**, rather than claiming a new archive discovery or adding a duplicate master source [61]. The existing **60-source master dossier stays unchanged**.

## Production actions completed
1. [Reader edition v9](./bohemia-spillway-reader-edition-2026-11-14.md): added two evidence-bounded paragraphs distinguishing Grand Prairie's failed public-land claim from qualifying private-heir cases; added select reader source **[21]** with the original decision, dates, procedural limits and PDF link. Previous reader source count 20. Committed as `d3a571529e6b03f782180b7da14b4cec6a104e52`; independent GitHub readback: new blob `cee692fb74df8317b1eab5fbb3bd7e69a8f5ab21`.
2. WordPress **draft #2488**, slug `the-spillway-that-kept-its-names-bohemia`: inserted two Gutenberg paragraphs directly after the 3%/48%/49% acquisition breakdown. The new citation targets `#fv-source-21`.
3. Updated its Gutenberg source list to **21 actual bibliography IDs**. Found and corrected **two broken in-page references** `#fv-source-45` and `#fv-source-47`: those referred to the 60-source **internal** master dossier, not the 20-item **public** article list. The four direct year-specific official financial-report URLs in source [9] remain intact. The private GitHub master-dossier link was removed from the public bibliography introduction so readers aren't sent to inaccessible private working files. The source intro now states the 60-source dossier is separate internal working documentation.
4. Replaced a literal `<p>---</p>` with a real Gutenberg separator block. No change to existing images, figure, categories, permalink, other posts, template or subscriber settings.
5. WordPress section operations used `expected_modified`, content SHA-1 and target block SHA-1 optimistic checks, **not** a blind 55K-character overwrite.

## Independent readback
- WordPress **status: draft**, never published; 94 Gutenberg sections; **21 consecutive numbered source targets**, **58 in-page source links**, **zero missing in-page citation targets**.
- Two pre-existing NASA/USDA/USGS documentary image blocks are retained. Media #2484 and #2485 read back with the creator/attribution, source URL, dimensions and descriptive alt text. Original FV in-post FY2000 litigation figure remains present.
- **No public-facing GitHub private-repository link** remains in the WordPress article body.
- Category IDs **9369 and 232815** and featured media **2484** unchanged. `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`, `jetpack_seo_noindex=true`, `jetpack_post_was_ever_published=false`.
- Latest readback site-local modified time **2026-11-14 10:35:40**, Gutenberg SHA-1 **`ba2f7911a9f7f8b30c5ed196ffa01bb5681c3535`**. This is the **new** screenshot QA target; older v8 draft hashes are superseded.
- The public NASA original was reopened and provenance matched. Attempts to retrieve site-local JPEG bytes through the available unauthenticated web preview returned a non-diagnostic inaccessible result, while the site WordPress media API readback succeeded. **Do not claim independent public image-loading verification**.
- **NOT performed:** authenticated production-theme screenshot / interactive mobile CSS inspection at 390px and 1440px; visual acceptance of public full-resolution image bytes; full final legal claim review; beneficiary payment reconstruction.

## Release blockers & next work
Obtain and compare the original 1997 *Vogt* accounting schedules and fractional award, `Haspel & Davis` consent judgment and beneficiary receipts, evidence of executed 2015 escrow transfer and post-2021 administrative account statements. Inspect 2015 board-minutes original PDF page images in a capable viewer. The lack of claimant-level data does **not** itself preclude a clearly bounded historical article, but final copy must not suggest a definitive current unpaid balance.

QA owner should inspect **WordPress #2488, modified 2026-11-14 10:35:40, SHA ba2f7911…**, in the genuine current production theme at 390px and 1440px, including both local documentary images, the custom 26/73 litigation graphic, 21-item source list, separator, heading hierarchy, overlays, overflow and mobile accessibility. Do not reuse #2151 screenshots for this separate story.

**Decision:** hold as draft until proofed. No new paid services; no emails, social distribution, homepage or shared-template edits.
