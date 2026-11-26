# Fresh 12-post / 51-image WordPress VIEW recovery batch — 2026-11-18 07:22 PST

**Draft QA only — HOLD, no production writes.** Scope is article image reliability and transfer performance; homepage layout, brand visuals, and design remain with interim lead. This is a current WordPress.com **`posts_get(context=view)` content-source snapshot**, NOT a logged-out browser run, network waterfall, or rendered-image validation. The historic [IMAGE-WEIGHT-WORKLIST](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/9cdf7af84175883775aaebf55ffa5ca77b33e423/docs/IMAGE-WEIGHT-WORKLIST.md) is absent from main/current draft and was read through its historical Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`.

## Actual source evidence and coverage

The machine ledger [`wp_view_51_actual_source_batch_20261118_0722.json`](../qa/media-recovery/wp_view_51_actual_source_batch_20261118_0722.json) contains **51 exact current stored VIEW src URLs in 12 published articles**, including the exact upstream image origin for each Jetpack URL, stable WordPress post ID/last-modified timestamp, authored srcset/dimension attributes and explicit unknown visitor HTTP/raster/wire fields. These 12 posts are a *targeted subset*, not a new sitewide census. P0 posts 274 (7 images), 285 (6), 287 (6), 407 (8), 418 (6), 432 (7); five first-party oversized PNG posts 34–38 (1 each); and Malbone post 621 (6): **51** images total. P0 queue has **7 exact archival candidate records**, still `HOLD` with image/raster identity, credit, rights and rehosting unapproved.

The fresh upstream source probes (independent public retriever, **not Jetpack or guest Chromium**) returned **HTTP 404** for:

- **274:6** — `https://www.warhistoryonline.com/wp-content/uploads/sites/64/2016/04/uss_tang_ss-306_rescues_airmen_off_truk_in_1944-640x432.jpg` (USS Tang; Navy accession candidate **80-G-227989**, not an approved identical replacement)
- **287:5** — `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` (Sunshine Skyway; authoritative exact-image candidate not cleared)

All other 49 image origins in this 51-slot batch were **not probed in this sprint**. WordPress stored URLs and upstream 404s do **not** establish that those images are broken through the Jetpack path in a logged-out browser. A further Florida Memory origin `www` → apex redirect produced a public retriever wrapper error; it is **not** a confirmed origin HTTP 500.

### Five stored-large, non-srcset PNGs unchanged

WordPress VIEW continues to show `has_srcset=false` and authored 1024×576 attributes for slots **34:0, 35:0, 36:0, 37:0, 38:0**. The independently reconciled WordPress library original-file sizes total **13,267,538 bytes** (stored originals only). We have not measured Jetpack response compression, actual unique cold image requests or bytes, or whether a 960px derivative improves LCP. **No claim of 13.27MB visitor savings.**

## QA, release and media integrity

- [`fv_wp_view_51_20261118.cjs`](../qa/media-recovery/fv_wp_view_51_20261118.cjs) is a **read-only**, offline source ledger validator. Rejects missing/duplicated post slots, URL/path substitutions, unsupported source HTTP claims, any fabricated guest HTTP/decoded/transfer metrics, rights clearance, unreviewed candidates, invented derivatives, upscale/rehosting/production write flags, and false 42/76% claims.
- [`test_fv_wp_view_51_20261118.cjs`](../qa/media-recovery/test_fv_wp_view_51_20261118.cjs) contains **39 adversarial assertions**; the exact committed code and ledger were also exercised together in isolated V8. Native Node synthetic-equivalent 39-case test suite passed against byte-matched validator. This is not a native Node repository CI result or independent authenticated visitor trace.
- Source code and exact ledger Git blob SHAs belong in the review evidence log. If the stored post revision or URL changes, a new read is required; a stale snapshot cannot authorize release.
- Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains exclusive ownership of the **existing** guest desktop/mobile Chromium collector. P0 first: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1, then Tang 274:6. The five no-srcset PNGs and Malbone 621:0–5 follow for true performance measurement. Capture final request URL/status, redirects, MIME, actual decoded raster dimensions, binary SHA-256, screenshot/ALT/credit parity, cold deduplicated transfer sizes, and LCP/CLS in paired identical-viewport tests.
- For each *identical* archival master with item-specific written reuse approval, record authoritative catalog/accession and caption credit. Create proportionate derivative only in approved staging with **width `min(960,native_width)`**, no upscaling, inspect crop and legibility, retain master and rollback. Use a separately approved WordPress Media Library staged attachment/reference update, **never** a mass Gutenberg block rewrite; no origin hotlink circumvention.
- Historical **61 posts / 355 images** and latest known **66 posts / 361 images** must not be mixed in before/after denominators. The reported **42 missing visitor images** and **76% wire reduction** remain unverified; the 20 originals above decimal 1.5 MB total **64,385,752 stored bytes**, not visitor transfers.

**No image downloads, unlicensed scraping, rehosting, production WordPress edits, Gutenberg rewrites, homepage work, merges, deployments or subscription spending.**
