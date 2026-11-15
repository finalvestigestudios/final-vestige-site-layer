# Bohemia Spillway · Reader Edition v30 · Source, visual, WordPress and release audit

**Date:** November 15, 2026, ~06:45 Pacific. **Owner:** FV Investigations Publishing Studio. **Decision:** DRAFT/HOLD, do not publish. No paid services.

## Collision avoidance and editorial scope
Reviewed live [Editorial Standards](https://finalvestige.com/editorial-standards/) (last reviewed August 23, 2026), currently published WordPress entries and the pending Investigations/QA GitHub coordination [#1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Direct anonymous Journal/Investigations endpoint access was unavailable; the WordPress published-post API was available. This is a continuation of *The Spillway That Kept Its Names*, not a new duplicate. The separate Caernarvon draft #2151, homepage, shared templates, newsletter, and Grok distribution lane were not modified.

## New primary source, evidence #71 / reader source #39
**Southeast Louisiana Flood Protection Authority–East / Silva Gurtner & Abney**, [*Combined Financial Statements as of June 30, 2015*](https://app.lla.state.la.us/PublicReports.nsf/FD28474B7D2636D686257EEA006F1A21/%24FILE/0000AE49.pdf), official Louisiana Legislative Auditor-hosted source, examined November 15, 2026. Exact indexed-text locations:

| Observation | Original document support | Interpretation and limit |
| --- | --- | --- |
| June 30, 2014 governmental judgments **$200,000**; FY2015 additions **$325,000**, retirements **$0**, June 30, 2015 balance **$525,000** | Note K, printed p. 50, *Changes in Long-Term Obligations* | Exact math verified; **Authority-wide**, not case-specific. FY2015 zero in this *judgments retirement line* does not prove zero payments or full litigation inactivity. |
| June 30, 2013 governmental judgments **$21,182,620** | [FY2013 independent audit](https://www.lla.state.la.us/PublicReports.nsf/0587D41B7EEF34E086257C06004E70CD/%24FILE/00035B16.pdf), Note K printed p. 42, source [70]/reader [38] | This is a substantially different earlier combined balance. **FY2014 detail is missing**. The arithmetical change to the FY2014 comparative must not be described as Bohemia payout, forgiveness, loss or diversion. |
| FY2014 had a settlement-reduction *gain* mentioned in a roughly **$11 million** general-revenue comparison | FY2015 MD&A printed p. 9, under OLD budget-to-actual discussion | Management does **not name** the settlement in this passage. Accounting gain may not be disbursement, and may not be Bohemia. Original FY2014 journal/notes and case ID are needed. |
| Restricted assets **$6,747,694**, enumerated for state debt, OPEB and Corps escrow | FY2015 Note F printed pp. 34–35 | No separately identified Bohemia escrow in that disclosure; absence of a label is **not proof of the executed March 2015 escrow transfer** or any claimant payment. |

**Original document verification:** Official PDF indexed text was read directly, with exact sections and numbers. Original page-image screenshot **attempted** on page 57 but web service rejected **16,613,162-byte PDF** (400 content-size limit). It is **text-verified, original-page visual NOT verified**. The FY2013 PDF page-image likewise remains blocked by its 15.2 MB size. No firsthand archive visit, witness statement, legal review or independent bank-ledger access claimed.

## Editorial and illustration
- [Reader Edition v30](./bohemia-spillway-reader-edition-2026-11-14.md) gained substantial section *A fiscal year the summary does not explain*, 4 analytical paragraphs, source [39], and corrected stale bibliography intro to **39** sources / **71** master entries.
- [Master dossier](./bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md) gained evidence [71], with a source classification and documentary retrieval checklist.
- [Original studio SVG](./assets/bohemia-2013-2015-rollforward-uncertain-v30.svg) was committed and independently read back. Creator: **Final Vestige Studios**; date: **2026-11-15**; license/ownership: original studio-authored source-derived vector, no embedded third-party assets; alt: “Three authority-wide judgments balances for June 2013 ($21,182,620), June 2014 ($200,000) and June 2015 ($525,000), separated by unverified FY2014 reconciliation; no Bohemia payment demonstrated.” Caption: **Three balances, one missing bridge.** Not archival photography and not AI-generated historical reconstruction.
- Original local SVG was rendered to 390px PNG and visually inspected for clipping, numerical labels and caveat legibility. Its Git content blob matched the local SVG bytes **excluding the local trailing newline**. This standalone raster is **not** an authenticated WordPress current-theme screenshot. A separately authored responsive HTML evidence figure was staged in WordPress.

## WordPress guarded staging and independent readback
**Site:** finalvestige.com; **post ID:** 2488; slug `the-spillway-that-kept-its-names-bohemia`; **status:** `draft`. Guarded single-block insertions added one H3, three source-anchored paragraphs, one responsive original HTML figure. The existing bibliography core/list block was replaced under content-hash/block-hash locking to add **source #39**, and the bibliography explanatory paragraph updated to 39/71. No full-post replacement was performed; unrelated blocks, categories and media were preserved.

Independent authenticated readback on November 15:
- Last site-local modification: `2026-11-15T06:44:59`.
- Serialized content hash: `29a0ead27333d9279d64b792797db7849e495beb`.
- **187** Gutenberg top-level blocks; **39** unique numbered source-anchor targets, **152** internal source links, **zero missing targets**, **zero duplicate targets**.
- Categories **9369, 232815**; featured media **#2484** unchanged.
- Registered flags: `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`, `jetpack_seo_noindex=true`, `jetpack_post_was_ever_published=false`.
- Both documentary local WordPress image IDs **2484** (NASA/USGS Landsat 8, 2023) and **2485** (USDA/NAIP, 2007) retain title/alt/caption/creator/source metadata, but public image URL requests were **inaccessible/indeterminate**; this is not independently successful byte-loading QA.

## Hard release gates / next record
1. Retrieve and independently check the **FY2014 audited statement/Note K**, the case-specific settlement-reduction journal and the referenced gain; do not equate a fall in liability with money received.
2. Retrieve the 2015 **executed** escrow closure/transfer entry (not only board authorization), original Haspel/Vogt court judgment and payee-level distribution or registry records, and qualify any 2026 financial-currentness assertion.
3. Actual **editor-authenticated WordPress current-theme screenshots/DOM QA at 390px and 1440px** for this exact draft SHA: hero, original HTML figure, documentary images, caption and source list, navigation and page overflow. An unauthenticated screenshot URL reported `ready` but **does not render the private draft for editor-level verification**.
4. Independently verify public image bytes and complete final legal/editorial review. Original FY2015 PDF-page image QA also remains open.
5. Re-read draft hash and publish-safety meta just before any eventual release. On first publish explicitly preserve newsletter-suppression and disabled auto-social, then independently check live HTML, canonical link, source targets, images, mobile display and metadata. Do not publish this run.

**Distribution note for Grok:** A future *after-publication* story angle is “a $21.18m line in 2013 and $200k in the FY2015 audit's 2014 comparison are not a payment register.” No social post was authorized or sent.

**Current outcome:** Primary source discovery, substantial manuscript advance, original verified vector graphic, guarded WordPress draft staging, independent content integrity checks. **Published: none; subscriber mail: none; social: none; extra cost: $0.**
