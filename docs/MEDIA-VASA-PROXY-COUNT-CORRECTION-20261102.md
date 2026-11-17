# November 2, 2026 — correct oversized-image inline exposure: Vasa Jetpack proxy blind spot

**Scope:** Media Recovery draft PR #183 only. No WordPress/media/CDN/homepage production write, image download, content block rewrite, licensing assumption or spend. Site QA PR #154 retains browser proof ownership.

## Finding: direct-URL-only November 2 count regressed an October 31 fix

The 2026-11-02 audit `qa/media-recovery/oversized_inline_exposure_20261102.json` reported **7 of 13** WordPress originals above 1.5 MiB inline (23,619,602 original-storage bytes) and **6 of 13** not referenced inline (19,903,227 bytes). That was a **direct-original-URL match count**, not a complete first-party source-equivalence count.

The earlier authenticated 2026-10-31 media metadata reconciliation had already established that Vasa post **299**, *Thirty Men Were Enough*, uses **three** of those oversized originals through `i0.wp.com/finalvestige.com/...` responsive-image URLs. The frozen October 30 census `parts/02.json` (blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`) independently contains all three exact post image slots and their ALTs.

| Original WordPress media | Source slot | Original stored size | Exact first-party proxy path |
|---|---|---:|---|
| #388 | **299:1** | **8,176,362 bytes** | `i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg` |
| #389 | **299:0** (also the recorded featured-image media) | **2,822,969 bytes** | `i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg` |
| #382 | **299:7** | **2,318,980 bytes** | `i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg` |

The exact full URLs, including the `fit` and `ssl` parameters and article destination, are in the machine ledger. These are **first-party-origin images using a WordPress proxy**, not three new third-party-photo dependencies. The proxy hostname alone is insufficient to classify them.

### Corrected 13-image source accounting

| Category | Media records | Original storage bytes |
|---|---:|---:|
| Direct first-party inline | 7 | 23,619,602 |
| First-party Jetpack proxy inline (Vasa) | 3 | 13,318,311 |
| **All source-equivalent inline** | **10** | **36,937,913** |
| **Not matched inline in frozen 61-post census** | **3** | **6,584,916** |
| **All >1.5 MiB WordPress originals** | **13** | **43,522,829** |

This supersedes the **7/6 complete-inline interpretation** of the November 2 direct-only report; preserve that older file as a documented, direct-only historical baseline. Do **not** retroactively describe the 13,318,311 bytes as new downloads, extra page load, or realized savings. The Vasa three have **registered responsive subsizes**. Their actual Chrome `currentSrc`, encoded wire bytes, decode results, viewport behavior, LCP/CLS effects and cache state are unmeasured.

The **five** oversized original PNGs at post slots **34:0–38:0**, total **13,267,538 storage bytes**, still lack registered 1024px subsizes and remain a *separate, conditional* performance cohort. The conditional Vasa no-upscale width/height proposals are **#388 960×639**, **#389 960×634**, **#382 960×640**; these are calculated from known original geometries, **not** inspected output files.

## Evidence, isolated code and verification

- [Corrected, complete 13-original machine-readable ledger](../qa/media-recovery/oversized_inline_proxy_corrected_20261102.json) — creation commit `96cced57213c58a1a05e5fca8331dddbc9701cbe`.
- [Fail-closed validator](../qa/media-recovery/validate_oversized_inline_proxy_corrected_20261102.cjs) — commit `6ec89da4c9bf9da5d0ba921f5a771816cd4520fa`.
- [25-case regression suite](../qa/media-recovery/test_oversized_inline_proxy_corrected_20261102.cjs) — commit `f81c0b468bc65e2bc09828118f433c450764ef72`.
- Source 2026-10-31 reconciliation blob `8388236ca03c283da3f72354bdc3f7ca9913e440`; source 2026-11-02 direct-only report blob `f8207544a0d11823b6e10cb500bc9f3abbc009ed`.
- **25/25 isolated V8 regression cases passed** against the exact committed validator code (one positive real-corpus crosswalk plus 24 adversarial mutations: proxy host spoof, altered source/ALT/slot, rights, upscaling, fabricated 404/76% savings, WordPress authorization and corrupted totals). Native Node execution/hosted CI **not run**.
- All original image rights/reproduction, visual fidelity, caching into WordPress, new media uploads and post rewrites remain **HOLD**.

## Site QA handoff and next priority

Site QA #154 should not modify its independent draft to adopt a blanket proxy assumption. It should simply recognize **three first-party-origin Vasa slots** `299:0, 299:1, 299:7` when prioritizing actual visitor transfer checks. Media Recovery owns the corrected audit and validator; Site QA owns logged-out Chrome guest `currentSrc`, request-ID, final status, natural dimensions, screenshot and transfer evidence. Higher-priority suspected missing images remain **285:5, 287:5, 407:1, 418:1–2**.

The site-wide denominator remains **61 published posts / 355 stored image references**. The **42 reported broken external-source images are not verified guest-browser failures**; the purported **76% page-image weight reduction has no compliant paired transfer measurement**; **production media repairs remain zero**.
