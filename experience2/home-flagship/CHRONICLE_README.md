# Experience 2.0 — Franklin document chronicle (unpublished)

This is a stacked homepage feature draft on [PR #177](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/177), independently tracking [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150). The frozen production release [PR #49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) and Apollo Research Desk [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) are unchanged. There is **no WordPress production write, release, merge, new plugin or subscription**.

## Major lift in one readable artifact

The monumental hero now leads into an original two-era typographic evidence composition before the three-case exhibit. The Franklin Victory Point note's **1847 "All well"** contrasts with the **April 1848 message** reporting abandonment. Both halves are actually readable HTML, not animation frames or an invented document image. The presentation explicitly says **"not a document facsimile"**. A native details disclosure distinguishes the officers' observations from the unknown individual later fates. Direct museum source links are retained without hidden modal logic.

The chapter rail adds five ordinary anchor links with genuine IDs. A skip-to-evidence link becomes visible on focus. An intentional small responsive CSS override fixes a tangible PR #177 weakness: below 920px the previous masthead nav was hidden without a direct replacement; now the existing nav stays accessible on a second line and can scroll horizontally *within itself*, not the page. No JS, frameworks, remote fonts, or fresh hero imagery.

## Source custody and rights

- Royal Museums Greenwich [Victory Point note original object HSR/C/9/1](https://www.rmg.co.uk/collections/objects/rmgc-object-504898).
- Canadian Museum of History [Victory Point transcription and context](https://www.historymuseum.ca/blog/a-very-special-piece-of-paper).
- Existing [Final Vestige Franklin investigation](https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/).

Text transcription opens 1848 addition with "25th April 1848"; RMG catalogue calls it an addition on 26 April. The new display says **APRIL 1848**, and disclosed source metadata retains this discrepancy rather than inventing a resolution. The two quotations are short historic primary-source fragments, not lifted from contemporary marketing/editorial copy. **Zero new archival images, zero new external media license dependencies, zero new scripts**. This does NOT clear NASA / NYPL media from the underlying flagship prototype; those retain their prior publishing holds. Original CSS paper composition cannot be confused with a source scan because it is labelled.

## Tests, measured evidence, and limitations

- Local Python test file (eight tests): **8/8 PASS** on the authored feature/fixture in the developer runtime, 2026-10-30. Run against GitHub exact head again before independent QD and release. `python -m unittest discover -s experience2/home-flagship/tests -v`
- Actual local **Chromium** browser was used with `page.set_content()` on a representative offline fixture containing the exact CSS/chronicle/rail. Recorded six widths 360,390,768,1024,1440,1920: no root overflow; native details works; five chapter anchors exist; mobile masthead links visible; JavaScript not needed. CSS 200% zoom at 390 viewport did not create root overflow. Measurements are stored in `qa/CHRONICLE_BROWSER_RESULTS.json`. Locally captured screenshots: chronicle-390.png and chronicle-1440.png, with 200%-zoom extra screenshot. This is **NOT** WordPress/site rendering, loaded network image, screen-reader, Lighthouse or p75 CWV verification.
- Three previous PR #177 source-case records and Focus/Puységur links remain; new section contains no Inspire3 recommendations or unverified benefit claims.

## Before/after statement

Before: visual-direction study directly entered a three-case evidence chamber from a monumental opening, with the primary navigation display:none on narrow screens. After: native five-chapter wayfinding, a full museum-sourced Franklin text contrast as meaningful intermediate story chapter, explicit evidence limits and fully visible mobile navigation. Real CSS-rendered offline 390/1440 captures exist; main/production has **not** changed.

## Release gates OPEN

Full actual PR head tests/browser across the existing three visual directions and three loaded source images; live WordPress Assembler/staging integration preserving 72 Margins and Jetpack /focus/; NYPL image rights; axe and NVDA/VoiceOver; WCAG 2.2 AA focus/contrast and touch; 200% browser zoom on the entire integrated page; Lighthouse/CWV measured; founder art-direction selection; QD exact-SHA and hosted CI green; explicit merge/deploy approval. No route/WordPress production change is authorized by this draft.