# FV Image Performance — complete 13-original census and final three risk disposition (2026-11-05)
 
**Scope:** Read-only WordPress media inventory + targeted published/draft page content. Does not touch homepage visual design, Site QA collector, WordPress production, external binaries, or billing. This branch is an isolated review and **not** a repair/deploy.

## New material result
A fresh WordPress media.list(image) scan returned **115 image records** in two complete pages (100+15). **Exactly 13 original images exceed 1.5 MiB (1,572,864 bytes)**, totaling **43,522,829 stored bytes**. This reconciles the previously reported total and, importantly, closes the remaining three previously unmapped assets.

| Cohort | IDs | Count | Source-original bytes | Disposition |
| --- | --- | ---: | ---: | --- |
| AI-assisted historic PNG hero reconstructions | 39–43 | 5 | 13,267,538 | Existing #1145 isolated offline staging; inspect actual visitor src/bytes first |
| Malbone photographic originals | 1257–1258 | 2 | 10,352,064 | Existing #1153 rights/virtual-size gate, historic map legibility exception |
| Vasa press photos | 382,388,389 | 3 | 13,318,311 | Already documented Jetpack-served 1024px variants in post 299; **do not** assume full master transferred |
| **Three newly dispositioned** | **293,405,482** | **3** | **6,584,916** | Preserved; distinct use/rights risks detailed below |
| **Total** | | **13** | **43,522,829** | No visitor-wire claim |

### Previously unresolved assets: new evidence, not deletion candidates
- **#293** `https://finalvestige.com/wp-content/uploads/2026/08/ne.png`, **2,090,327 bytes**, **1122×1402**. Published /about/bryan-rhodes/ page **234** has an exact `ne.png` reference in author **JSON-LD image**, so deleting or blindly swapping could break entity/profile structured data. Conditional 960×1199 derivative; verify source rights and metadata/identity before any changes. Priority **protect published schema**.
- **#405** `https://finalvestige.com/wp-content/uploads/2026/08/The20Water20Resilience20Field20Manual.png`, **2,201,573 bytes**, **1122×1402**. Page **85** is **draft**, and its cover image uses the Jetpack transformed URL `?fit=819%2C1024&ssl=1`. A draft media request is **not** a verified public-visitor transfer; retain existing cover while offer status is unresolved. Conditional 960×1199 derivative only after provenance and visual review.
- **#482** `https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png`, **2,293,016 bytes**, **1672×941**, no alt/caption and no attached post ID. No exact reference was found in the **six specifically sampled pages** (85/234/6/1/77/191). This does **not** prove nonuse elsewhere, in theme assets, post metadata, or CDN cache. Retain; unknown creator/rights and possible use. Conditional 960×540 derivative; **do not delete**.

## Strict safety and performance gates
1. **First priority remains broken visitor images** in Site QA #154 queue: 285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1. This branch does not modify or copy the browser collector; guest HTTP, currentSrc, decoded pixels, and CDP bytes remain **NULL**. Reported **42** broken still unverified.
2. Original storage is not image transfer. The alleged **76%** image-transfer reduction is **unmeasured**; no browser before/after exists here. Confirm real mobile and desktop logged-out source, Jetpack/Photon transformations, request IDs and cold transfer bytes before changing assets.
3. **Jetpack official documentation:** `virtual:true` thumbnails are URL transformation candidates, not independently tested copies or verified browser delivery. The Site Accelerator may resize images automatically, and its image CDN has no ordinary cache invalidation; refresh by assigning a **new filename** after a separately authorized staging, with staged visual check and rollback. See https://jetpack.com/support/site-accelerator/ and https://wordpress.com/support/site-accelerator-cdn/ . No blanket third-party rehosting.
4. For each potential derivative: rights/creator attribution and exact original binary SHA-256 verified first; width ≤960px and no enlargement; preserve map text, authored diagram details and author portrait; store a **new, versioned media file** with rollback mapping, preserve SEO/schema and alt/captions; obtain editor approval separately before any CMS write. The 960px geometry is a **conditional preview**, never a validated final rendition.
5. Additional rights cautions: Vasa imagery has press/editorial-use terms and source attribution; Malbone tunnel CC BY-SA requires license/credit; historic NYPL map needs exact capture rights. **No item-level rights has been cleared by this PR**. Source-only metadata is not publication permission.

## Reproducibility and ownership
`qa/media-recovery/oversize13_remaining3_20261105.json`: all 13 exact URLs, dimensions, stored bytes, WordPress virtual-size descriptors, rights and browser NULLs, and six targeted page checks.
`qa/media-recovery/validate_oversize13_remaining3_20261105.cjs` and `test_...`: all exact identities, totals and no-upscale, rights, caching/WordPress write and fabricated HTTP assertions enforced. Run: `node --test qa/media-recovery/test_oversize13_remaining3_20261105.cjs`.
**No image binaries were fetched, transformed, cached or republished. WordPress was read-only.**

### Independent 66-post cross-check (source only)
For additional confidence, fetched all six pinned JSON batches from the separate **#1138** published-post inventory (Git blobs named in the machine-readable manifest) and scanned **all 66 posts / 361 inline `img src` slots** for the three remaining filenames. Result: **0/361** exact filename matches for **#293, #405, #482**. This finding does *not* establish nonuse: #293 is linked in live page 234 JSON-LD, #405 is on draft page 85, and #482 could be referenced in theme/CSS/custom fields/other pages. No assets were deleted. Keep #482 status **UNKNOWN**, not `verified_orphan`.
