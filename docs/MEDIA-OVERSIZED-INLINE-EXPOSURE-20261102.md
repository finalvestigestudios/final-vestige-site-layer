# Media Recovery — exact oversized-original inline exposure (2026-11-02)

**Scope:** read-only classification of the previously captured **61 published posts / 355 stored image slots** against the **13 WordPress Media Library originals greater than 1.5 MiB**. This is not a live site fetch. Guest HTTP status, actual transferred image bytes, decoded pixels, source licenses, and before/after savings **remain unknown**. No media conversion, rights assertion, CMS write, post block rewrite, or homepage design change occurred.

## Important new finding

The 13 large WordPress **originals total 43,522,829 bytes of stored files**, but only **7** appear as inline image source URLs in the frozen 61-post article snapshot. Those seven represent **23,619,602 stored-original bytes**, not a browser-waterfall total. The remaining **6** originals total **19,903,227 bytes** and have *no stored inline source reference in these 61 posts*. They may still occur as featured imagery, home-page modules, downloads, or other website surfaces; **do not call them unused assets**.

**Highest-value distinct optimization queue:** **five** 1672×941 PNG files total **13,267,538 original bytes** and **lack a recorded 1024px/Jetpack variant in the original Media Library inventory**. This absence of a recorded variant is not evidence that a current browser downloads the full PNG: dynamic HTML, CDN transforms, lazy loading, and other page contexts still require verification.

| Slot | Post / original | Original bytes | Recorded 1024px variant | Conditional no-upscale limit |
|---|---|---:|---|---|
| **34:0** | [The Morning San Francisco Lost Its Water](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) / [original PNG](https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png) | 2,892,087 | No | 960×540 |
| **38:0** | [The Cisterns Beneath San Francisco](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) / [original PNG](https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png) | 2,836,245 | No | 960×540 |
| **35:0** | [The Boat That Refused to Die](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) / [original PNG](https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png) | 2,552,136 | No | 960×540 |
| **36:0** | [The City That Went Underground](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) / [original PNG](https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png) | 2,498,247 | No | 960×540 |
| **37:0** | [How Petra Made Water Flow Through Stone](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) / [original PNG](https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png) | 2,488,823 | No | 960×540 |

The **two remaining inline large originals** are post **621:1** (1903 BRT map, 5,553,669 bytes; conditional **960×649**) and **621:0** (Malbone tunnel photograph, 4,798,395 bytes; **960×720**). They already have *recorded* 1024px Jetpack/WordPress variants; verify the *actual* `currentSrc` and transfer size before optimization. Also assess legibility of historical maps and overlays at target resolution.

## Site QA handoff: verify the five PNGs without duplicating PR #154

Use Site QA's existing browser evidence workflow for **34, 35, 36, 37, 38** when possible, prioritizing an actual visible missing image before a merely oversized stored original. On desktop and mobile, gather (a) rendered `src/currentSrc/srcset`, lazy-loaded completion and `naturalWidth/naturalHeight`; (b) CDP final request URL, redirect chain, MIME, status, content length **and measured encoded transfer bytes**; (c) cache/service-worker provenance and screenshots to confirm correct subject, crop, captions, LCP and CLS. Keep both successful and failed loads in the evidence batch. A missing image is **not** a 100% weight reduction.

The prior site's source-census discrepancy **286 vs 288 external references** remains independent of this first-party oversized-original classification. The previously reported **42 broken images** are unverified, and a claimed **76% wire-byte reduction** is unmeasured. First confirm genuine broken off-site images **285:5 / 287:5 / 407:1 / 418:1–2** before attempting an optimization-only CMS release.

## Rights, cache, and WordPress plan — all conditional, no production action

1. **Identify the exact rights holder and original photograph/illustration.** An asset already hosted by WordPress does not demonstrate derivative/rehosting permission. Never replace a historical photograph with a similar scene. Preserve original source captions, credit, historical dates and visual crop.
2. **Measure the page first**, and confirm the browser is actually transferring the original bytes, not an existing Jetpack/CDN responsive variant. Hold if measured transferred size is already small.
3. **Only after rights and visual review**, locally generate a 960px-wide (never upscaled) candidate; use an appropriate quality format (e.g., WebP/AVIF or optimized PNG when transparency/detail demands it). Test image sharpness, map labels, factual scene fidelity, accessibility alt and visually equivalent crops at mobile and desktop sizes. Don't assume a particular compression saving.
4. **Only with separate CMS deployment approval**, use a new WordPress Media Library asset, retain original permalink/source credit/ALT semantics, verify `srcset/sizes`, cache/CDN behavior and rollback ability. Avoid fragile bulk Gutenberg rewrites or hotlink circumvention.
5. **Measure paired complete page loads** (same page, device, network profile and cache policy; count each distinct transferred request once). Include failed/missing media explicitly and retain LCP/CLS. Calculate reduction only from confirmed comparable successful loads. Report storage savings separately from wire savings.

## Reproducibility

Machine-readable exact-source crosswalk: `qa/media-recovery/oversized_inline_exposure_20261102.json`. Validator: `qa/media-recovery/validate_oversized_inline_exposure_20261102.cjs`. Native Node test definitions: `qa/media-recovery/test_oversized_inline_exposure_20261102.cjs`. Inputs are pinned by recorded source Git blob SHAs (one oversized-original JSON, eight 61-post source inventory parts). In a checked-out PR branch:

```sh
node qa/media-recovery/validate_oversized_inline_exposure_20261102.cjs
node --test qa/media-recovery/test_oversized_inline_exposure_20261102.cjs
```

The ledger and validator passed an isolated V8 source replay, including **13/13 rejected unsafe ledger mutations**. **The committed 24-case native Node suite and browser QA remain unexecuted in this runner.** The runner cannot resolve FinalVestige.com for a trustworthy visitor-browser waterfall.

**Release gate: CLOSED.** Media rights: HOLD. Visitor-byte and HTTP proof: UNKNOWN. WordPress write authorization: FALSE. No unlicensed scraping, image downloads, new subscriptions, site-design edits, or production changes.
