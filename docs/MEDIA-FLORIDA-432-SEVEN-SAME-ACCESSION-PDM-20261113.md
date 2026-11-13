# Seven verified Florida Memory catalog aliases — post 432 (November 13, 2026)

**Scope:** draft-only Final Vestige media recovery, not homepage design; no WordPress writes, image download/rehost, licensing assumptions, merge, deployment or subscription spend. This is a **new indexed official-item evidence pass**, not new guest-browser failure evidence.

## High-value result

All **seven** published `www.floridamemory.com/fpc/...` source **paths** in the 1928 Okeechobee article, post 432, match the `Image URL` recorded under the **same accession** in the corresponding Florida Memory item catalog. The seven indexed official pages are:
- `432:0` **PR04493**: [Funeral, West Palm Beach, 1928](https://floridamemory.com/items/show/4144)
- `432:1` **RC17068**: [Flooded Avenue A, Belle Glade, September 1928](https://floridamemory.com/items/show/38362)
- `432:2` **RC10673**: [Destroyed auto garage, 1928](https://floridamemory.com/items/show/33289)
- `432:3` **N031889**: [State Board of Health staff, Pahokee, 1928](https://floridamemory.com/items/show/141398) — archive does **not** establish that this was a post-hurricane response photograph
- `432:4` **RC04344**: [Coffins at canal, Belle Glade, 1928](https://floridamemory.com/items/show/27848)
- `432:5` **RC07668**: [Burial in West Palm Beach, 1928](https://floridamemory.com/items/show/30741)
- `432:6` **MSF-PB11548-001**: [Historic mass-grave site photographed in **2001**](https://floridamemory.com/items/show/340182) — **not** a 1928 event image.

These are **same archive accession and URL-path mappings**, not verified equal image files/crops. The current `www` published sources and `apex` catalog paths differ in hostname; a host alias is not proved to fix rendering. The prior direct `www` requests produced web-retriever 500 wrappers on **November 9**, while direct catalog opens produced web-retriever 403 wrappers on **November 13**; neither is actual origin or browser HTTP. All 7 guest statuses and transfer bytes remain null.

## Reuse rights, visuals and performance

The official [Florida Memory FAQ](https://floridamemory.com/share/order-info/faq.php), Q9, declares PDM 1.0 for its images and asks for **State Archives credit under Florida Statutes §257.35(6)**. PDM is a mark of no known restrictions, not a license or representation that third-party publisher art can be copied. Verify item donor restrictions, credits, and any non-copyright limitations before rehosting. The seven exact accessions with credit strings are recorded in the [machine audit](../qa/media-recovery/florida_432_seven_catalog_same_accession_pdm_20261113.json).

Native dimensions, image bytes, SHA256, actual decoded pixels and `currentSrc` remain **unknown**; hence conditional **960 physical px maximum, no upscale**, derivative dimensions **unknown**, and caching/WordPress release **HOLD**. The only safe next step is a cold logged-out guest browser run through Site QA #154's *existing* collector after runtime Jetpack rewrites, followed by rights-verified source-master capture and visual/ALT/caption review. If subsequently authorized: snapshot original Gutenberg markup and media metadata; stage a credited first-party WordPress derivative with explicit dimensions and responsive choices; compare before/after on matching viewports/DPR, total **unique actual transferred bytes**, image decoding, LCP/CLS and screen captures; rollback without rewriting unrelated blocks.

The historical **42 broken** count remains browser-unverified. The separate frozen cohort remains 61 posts/355 inline images, while the newer census is 66/361. Fifteen >1.5 decimal MB originals total **47,096,779 stored bytes**, which cannot prove a **76% network reduction**.

## Reproducibility

Source index: frozen original [seven-source prior register](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/9cbadf738720d1b0bd9e1630a6fbb7af574b68d2/qa/media-recovery/florida_432_seven_web_redirect_20261109.json), blob `c0ec93d75ff6c7d1b655ea1ea1b42bc9c429106f`. The cross-draft worklist lives in PR #183, blob `2acd06a4ca4317646006eb6591face3fe76fedec`. This batch is separate from the **five different-photo Skyway alternatives** logged on November 13.

```bash
node qa/media-recovery/validate_florida_432_catalog_contract_20261113.cjs qa/media-recovery/florida_432_seven_catalog_same_accession_pdm_20261113.json
node --test qa/media-recovery/test_florida_432_catalog_contract_20261113.cjs
```

The audit is machine-readable, fail-closed and source-locked. **No production repairs were performed.**
