# The ninety-source directory: staged progressive-enhancement repair

**Final Vestige Studios · Library only · checked 2026-11-17 (Pacific)**  
**Disposition: WORDPRESS DRAFT REVISED / PUBLIC RELEASE HELD**

## Reader problem

The [Research Sources](https://finalvestige.com/free-resources/research-sources/) directory has **90 distinct destination records**, split in WordPress into 60 initial cards and 30 separately readable fallback cards. Its two scripts both attached listeners to the same search/filter controls. Without scripting, the records were still present but readers received no notice that the search and filter buttons would not work. The filter region had an accessible-name attribute but no explicit grouping role.

These are interface issues, not missing archives or evidence that any institutional URL is broken. Rights stay with the contributing institutions and individual items; this repair reuses **no outside images or documents**.

## Exact change made to WordPress staging

After checking the live [Library](https://finalvestige.com/free-resources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), [coordination issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788), [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816) and authenticated pages, applied **one** revision/hash-locked `wpcom-page-sections-replace` to **top-level block 0** of existing unpublished WordPress **page #2354**. The write returned **no content warnings**.

- Removed only the obsolete first 60-card filter/search script; the later 90-card controller and its 30-card regrouping are preserved and are now the sole input/click handler.
- Changed the existing filter container to `role="group" aria-label="Filter research sources"`.
- Added a `<noscript>` note: search/filter buttons are inactive without scripting, but all 90 source links remain in their original sixty plus separate thirty-record section; use browser Find.
- Retained all other source content, existing NARA qualification, card markup, references, external-link attributes, Gutenberg structure, and staging **draft/noindex** status. No published page was edited.

**Independent authenticated readback (2026-11-17 01:33:53 site-local):** staging #2354 remains draft, child of Library #77, noindex=true, 90 cards / **90 unique outbound URLs** in the **exact same source URL order as published page #1338**, category totals **12 / 24 / 21 / 25 / 8**, and precisely **one** controller and **one** search input handler. The labeled filter group and the no-script note are present. Published #1338 remains modified `2026-11-03T22:12:43`, unchanged with stale static “60”; parent Library #77 remains modified `2026-11-07T19:39:01`, unchanged.

## Repeatable QA, with precise evidence level

The [read-only Gutenberg structure checker](../../../scripts/editorial/check-research-sources-runtime-surface.mjs) now supports optional `--require-progressive-enhancement`; that switch fails closed when the no-script note, single controller or explicitly labeled group is missing. It is offline/read-only and must be run against a newly exported authenticated WordPress content file. It does **not** certify real browser accessibility.

An original offline **Python Playwright / Chromium synthetic fixture** was also executed locally with the exact *remaining* 90-card controller, the observed 60+30 cardinality, illustrative (not documentary) records, and simplified representative styles. **8/8 configurations passed** at 320/390/768/1440px, scripts enabled/disabled. Checks covered card regrouping, category filters 12/24/21/25/8, a unique supplemental record search (1/90), one pressed button, visual focus outline, no horizontal overflow, no JavaScript exceptions, no-script notice and fallback links. The local files/screenshots are in the session's attached QA ZIP; they are **not WordPress-theme screenshots**. No real-world source link was tested by the fixture.

The directory's separate `display:none` rule for numeric filter spans is **unchanged**, so its screen-reader and visual behavior must still be assessed. A synthetic fixture does not validate production theme, real browser downloads, assistive technology or delivery suppression.

## Release gate — HOLD

1. Inspect actual **WordPress-theme** screenshots at 320, 390, 768, 1440 with JavaScript on/off, plus real keyboard order, live-region announcement, screen reader group semantics, no overflow/duplication and supplemental-title search.
2. Verify enforceable suppression of subscriber **email and social syndication** for an existing-page update. A general disabled-new-post-email preference is not adequate proof.
3. Before any live write, refresh and compare current published #1338 and parent #77 revision plus block hashes; reconcile the existing **15-anchor editorial correction** with the staged accessible controller. Do not merge PR or publish #2354 as a substitute for guarded edits to the published pages.
4. After gated release, independently recheck signed-out public page, metadata/robots/canonical, 90 card integrity, grouped labels and sampled outbound links. No subscriber blast, Grok-account action, third-party media mirroring, or spend.

## Source and rights ledger

- [Live directory](https://finalvestige.com/free-resources/research-sources/), [Library](https://finalvestige.com/free-resources/), and [Editorial Standards](https://finalvestige.com/editorial-standards/) directly rechecked **2026-11-17**.
- [90-item provenance/access/rights ledger](research-sources-90-inventory-2026-11-16.json): all 90 destination attempts documented 2026-11-16; institutional URL retrieval does not confer item reuse permission.
- [Prior progressive-enhancement source audit](research-sources-progressive-enhancement-audit-2026-11-17.md); [release gate](research-sources-90-release-gate-2026-11-16.md).

**Optional Grok lane concept only, no account changes:** “The missing thirty archives were never missing. The interface was telling a shorter story than the records.” Keep promotion behind the verified public release.
