# FV Media Recovery — Sunshine Skyway post 287 / source integrity and cold-weight methodology

**2026-11-10 — isolated draft #1703; no production edits.**
**Scope:** third-party article media, source fidelity, copyright and transferred-image measurement only. Homepage visual design belongs to interim lead. Site QA #154 owns the **existing** actual logged-out Chromium/CDP browser collector; DO NOT fork or duplicate it.

## Source results (read-only)

Live WordPress post **287**, *The Warning Was a Man Waving* (modified 2026-11-02T21:40:01), exposes **six inline image tags**. All **six literal stored src values match** the frozen October 30 inventory. Current ALT text was captured, but **historical ALT equality cannot be claimed** because source freeze lacks ALT fields. Image URLs 287:0–287:4 were rendered in independent web image retrieval; 287:5 (old St Pete Catalyst URL) yielded a **retriever 404**, while publisher's new media CDN renders a corresponding photograph. **None** of these observations establishes a logged-out visitor browser status or measured transfer bytes.

Five newly researched positions (287:0–287:4) are added to the cumulative 288-slot recovery register. The high-priority **287:5** was already researched: **not counted again**. Result **257/288 uniquely researched**, **31 pending**, **262 evidence entries**, with all **283 unrelated positions and previously researched 287:5 unchanged**.

**Two visually significant published ALT problems:**

* **287:4** currently describes the bridge **and the Summit Venture**, but the exact federal-court-hosted image visibly depicts a **salvage crane barge, small tug and damaged bridge**, not the freighter. Proposed ALT for editor: “Aerial view of the damaged Sunshine Skyway Bridge with a crane barge and tug working near the severed span.”
* **287:5** claims a later replacement bridge appears; the current publisher photo shows the **shattered original bridge and ship**, without the subsequent replacement. Proposed ALT for editor: “Damaged bow of Summit Venture beside the shattered supports of the original Sunshine Skyway Bridge after the 1980 collision.”

Image **287:2** is a newspaper-created **collision-sequence infographic with small annotations**; it is neither a federal archival photograph nor freely reusable merely because NTSB describes the disaster. Do not casually shrink below label legibility. Images **287:0**, **287:1** and **287:3** are syndicated news/video images with unresolved photographer and rights. Image **287:4** is hosted by a federal court but government hosting **does not establish federal photographic authorship**. Manatee County Public Library official digitized catalog candidates (records **29937** and **29902**) are different views, not exact binary replacements; rights must be checked with the institution.

**Evidence:** [six-image exact-source audit](../qa/media-recovery/skyway_287_six_live_retriever_rights_20261110.json) blob `63ae58b54c1b4def7a80e54e4cb84e0456bee838`; [257/288 reconciled register](../qa/media-recovery/coverage_257_exact_pr1703_20261110.json) blob `49d308444c58edb9022f104a2fb1eadd541843e6`; validator blob `21811efbc0fe5dfe4172d46bbd8c90904f626fd6`; 32-case isolated regression suite blob `4befc9735c2920403048a56d17e7f0c0ea7018be`. All rights, origin/guest statuses, decoded widths, transferred bytes, and native pixel dimensions remain NULL/false where not established. Native Node CI and genuine guest browser remain pending.

## P0 browser verification handoff

Keep original priority **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. For **287:5**, Site QA should compare guest `currentSrc`, HTTP response, `naturalWidth/Height`, console errors, transferred bytes and visual scene for legacy URL `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`. Candidate `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` **rendered in independent retriever only**. Before any source substitution, require rights/attribution review and same crop/scene editor approval. Do not hotlink-switch merely because the alternative URL opens.

## 42 purported failures and proposed 76% image-weight reduction

The **42 reported as broken** are a *historical audit assertion*, not 42 confirmed visitor failures. Failures from a text/image retriever, URL redirect wrapper or native shell DNS failure are **not visitor HTTP results**. The **76% transferred-weight reduction** remains *unmeasured*; no savings should be stated until a valid pairwise comparison.

A reproducible browser protocol, to be performed by existing Site QA collector **without duplicate tooling**, is:

1. Freeze same published page list, consent state, viewport (at minimum mobile **390×844** and desktop **1365×768**), visitor logged-out session, route, and image slot identity. Disable cache in fresh contexts and capture at least three independent baseline runs at consistent network/CPU conditions. Record runtime `currentSrc/srcset` and Jetpack/proxy rewrites, not only stored editor URLs.
2. Preserve per-request final URL, all redirect response codes, **browser** HTTP status, MIME, decoded `naturalWidth/Height`, CSS dimensions, visibility/lazy-load intersection, and image load/error events. Record actual transferred bytes from network instrumented bodies or validated HAR/DevTools `encodedDataLength`; where not supported mark NULL, not zero. Cross-origin `performance.getEntriesByType("resource").transferSize` can be **zero/opaque due to TAO/CORS**: do not mistake zero for zero transfer. Request counts may include duplicates from redirects and different `srcset` choices; count actual wire requests only once.
3. Distinguish **cold transfer** (network), **cache-hit transfer**, **decoded size** (RAM), and **stored WordPress attachment bytes** (disk). Measure image-category wire bytes per page and aggregated across the same page cohort, using consistent request inclusion and viewport. On page changes, track article slot identity; do **not** substitute an unrelated scene with a smaller file and call it optimization.
4. After an independently authorized staging-only derivative, rerun identical protocol, verify expected exact image/crop/copyright and accessibility, compare initial vs replacement image wire bytes across the **same requested page slots**. Reduction `= (baseline_image_wire_bytes - optimized_image_wire_bytes) / baseline_image_wire_bytes * 100`; report coverage and missing data before any percent. An asserted 76% reduction needs real baseline and after numbers, no estimates based on originals.
5. Capture first-viewport LCP element candidate and CLS shift, especially dimensions missing from external tags; prioritize failed images and layout fidelity over speculative byte savings. Browser collector output should link every failure back to the exact stored source, `currentSrc`, HTTP, decoded dimensions and image-slot index.

## Oversized WordPress originals >1.5 decimal MB — **storage**, not guest transfer

Frozen source [cross-ledger](../qa/media-recovery/cross_ledger_43_source_15_oversize_20261109.json) blob `8526557c7a5138e1ca22a347e3f9839503d48b2c` reports **15 originals = 47,096,779 stored bytes**; **11** match expanded published inline posts = **38,480,915 stored bytes**. Five originals (`39–43`) are large PNGs used inline on posts 34–38 **with no generated subsizes** and merit responsive-image review first. Other originals frequently already have subsizes; no one can infer that a visitor loads the original.

| Media ID | Original MB (decimal) | Original px | Conditional max 960 target px | Subsized assets | Directly referenced post IDs |
|---|---:|---:|---:|---:|---|
| 388 | 8.18 | 4256×2832 | 960×639 | 7 | 299 |
| 1258 | 5.55 | 5667×3831 | 960×649 | 7 | 621 |
| 1257 | 4.80 | 4000×3000 | 960×720 | 7 | 621 |
| 39 | 2.89 | 1672×941 | 960×540 | 0 | 34 |
| 43 | 2.84 | 1672×941 | 960×540 | 0 | 38 |
| 389 | 2.82 | 2147×1417 | 960×634 | 7 | 299 |
| 40 | 2.55 | 1672×941 | 960×540 | 0 | 35 |
| 41 | 2.50 | 1672×941 | 960×540 | 0 | 36 |
| 42 | 2.49 | 1672×941 | 960×540 | 0 | 37 |
| 382 | 2.32 | 1800×1200 | 960×640 | 6 | 299 |
| 482 | 2.29 | 1672×941 | 960×540 | 6 | No direct inline match |
| 405 | 2.20 | 1122×1402 | 960×1200 | 5 | No direct inline match |
| 293 | 2.09 | 1122×1402 | 960×1200 | 5 | No direct inline match |
| 2148 | 2.03 | 1821×1190 | 960×627 | 6 | No direct inline match |
| 1714 | 1.54 | 1280×1280 | 960×960 | 5 | 269 |

Do not upload or generate derivatives from an image with unverified reproduction/derivative rights. Specifically, the apparent 8.18 MB Vasa original (**media #388**) already has seven subsizes; original stored bytes ≠ real visitor loading cost. The five 1672×941 PNGs with no subsizes are a candidate workflow investigation, not proof of slow pages.

## Proposed staging and WordPress media recovery sequence (NOT executed)

Rights gate: primary catalog and creator, specific source item and actual usage license, attribution, consent/endorsement restrictions, modification/derivative permissions. Visual gate: exact scene, date, crop, diagram labels, ALT and figure caption approved by editor. Sizing gate: original native pixels confirmed from a lawful, approved source; **width=min(960,source native width)**, preserve aspect ratio, no upscaling; exceptions to 960 for necessary legible diagrams only by explicit visual QA. File gate: create derivatives using local/transcoded JPEG/WebP/AVIF where allowed, with limited max file size, metadata and `srcset`/width/height; never remove source credit or add misleading edits. Stage-only WordPress Media Library upload after express permission; link each candidate to attachment ID and restore/rollback plan. Test the target post first, run Site QA browser decode/CLS/LCP and attribution checks, then request a separate deployment decision. **No production WordPress write, image download, cache, media upload, post block rewrite, deployment, homepage edit, or paid call is authorized by this audit.**

## Worklist status

Requested `docs/IMAGE-WEIGHT-WORKLIST.md` is **absent** from `main` and draft #1703 branch. The known cross-ledger above is a traceable, read-only fallback; do not invent a worklist. Site QA #154 receives the source evidence as a **handoff**, not a duplicate browser collector.
