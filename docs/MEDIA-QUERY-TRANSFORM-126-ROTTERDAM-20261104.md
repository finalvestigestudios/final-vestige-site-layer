# Media Recovery: 126 query-bearing photo URLs and crop-safe browser identity — 2026-11-04

**Scope:** independent draft PR #183, separate from homepage visual design and Site QA's draft PR #154. **Production changes: zero.** The frozen Oct 30 repository inventory is **61 posts / 355 image slots**; **126 slots** carry a URL query string. Neither the alleged **42 visitor-broken images** nor a **76% visitor-transfer reduction** has been demonstrated in a logged-out browser. This batch did not make network-origin response measurements, download media, or edit WordPress.

## Concrete engineering defects fixed

1. The source-identity classifier treated every static `?fit=` as size-only. WordPress documents numeric `fit=W,H` on its own image service as proportional, but **imgix** documents `fit=crop`, `fit=smart-crop` and `fit=facearea` as potentially cropping photograph content. This matters for preserving historical photograph identity: the wrong crop must **not** be counted as a successful rendering or failure of the original. The revised classifier strips only documented numeric `fit=W,H` for Jetpack proxies or first-party WordPress upload paths, otherwise preserves `fit` and both geometry axes.
2. Static `?w=`, `?h=`, `?width=` and `?height=` previously vanished even if the values were **not pixel numbers**. The site has a concrete example: **post 292, slot 1**, an external Stadsarchief Rotterdam image with `?h=3e6ca723&itok=wjXwUo3w`. That `h` is **not a numeric height**; its exact upstream semantics have not been established. The new classifier preserves nonnumeric selectors. Drupal documents `itok` as an image derivative protection token; it must also remain present.

Primary technical references: [WordPress image transformations](https://wp.cloud/docs/performance/image-optimization/image-transformation/); [imgix fit modes](https://docs.imgix.com/en-US/apis/rendering/size/resize-fit-mode); [imgix aspect-ratio and crop](https://docs.imgix.com/en-US/apis/rendering/size/aspect-ratio); [Drupal image-style token](https://api.drupal.org/api/drupal/core%21modules%21image%21src%21Entity%21ImageStyle.php/function/ImageStyle%3A%3AgetPathToken/11.x).

## Verified site-wide query audit (frozen CMS snapshot, not real-time probe)

Machine ledger: [query_transform_126_slot_census_20261104.json](../qa/media-recovery/query_transform_126_slot_census_20261104.json). The audit pins the eight exact GitHub `parts/01..08.json` blobs and preserves every query-bearing original image URL, post ID, source type, transformation category, null browser status, unknown actual image pixels/bytes, copyright HOLD and prohibition on caching or upload.

| Family | Image slots | Key operational consideration |
|---|---:|---|
| Wikimedia Commons width redirects | 92 | Existing Commons identity mapping; renderer bytes/redirects not verified |
| Other dynamic/query selectors | 12 | No global assumption that a parameter is size-only |
| WordPress Jetpack numeric `fit` | 7 | Documented proportional transform; actual 299:0–5,299:7 |
| Navy archival `image=` IDs | 6 | Preserve `image` while ignoring rendition-only formatting |
| Drupal style tokens | 3 | `itok` must remain part of original source URL |
| S3 `VersionId` | 3 | Version pin selects historical original; preserve |
| Drupal nonnumeric `h` + `itok` | 1 | **292:1**, previously conflated; now preserved |
| Cropping `resize=` query | 1 | **283:3**, earlier crop-safety fix retained |
| Cropping instructions in URL path | 1 | **291:3**, retain exact path |
| **Total** | **126** | **Zero confirmed visitor breakages in this batch** |

This review is in addition to—and does not replace—the 355-slot source census, existing 13 originals >1.5 MiB (~43,522,829 stored bytes), P0 restoration packet, or browser/CDP byte-claim gate. Counting masters in storage cannot validate a site download improvement.

## New historical-integrity issue: Prinsendam 292:1

**Published source URL** (frozen inventory; exact guest browser GET not tested):

`https://stadsarchief.rotterdam.nl/sites/default/files/styles/gallery_large/public/2025-04/hal-prinsendam-nl-rtsa_4121_24162-1-14.jpg?h=3e6ca723&itok=wjXwUo3w`

**Published ALT:** “Prinsendam at Rotterdam's Wilhelminakade in 1973, seven years before the Gulf of Alaska fire.”

**Primary archival record:** [Stadsarchief Rotterdam, Holland Amerika Lijn](https://stadsarchief.rotterdam.nl/holland-amerika-lijn) identifies its linked photograph (same named file, different derivative) as **MS Prinsendam passing Koningsbruggen, April 8, 1973**, credited to **Ary Groeneveld**, collection **4121**. An [archive-published alternate rendition](https://stadsarchief.rotterdam.nl/sites/default/files/styles/original_scaled_large/public/2025-04/hal-prinsendam-nl-rtsa_4121_24162-1-14.jpg?itok=Tm3Q-0CM) visually shows the vessel alongside a bridge. This is a strong subject match, **not a proved identical binary/crop or verified 200 on the original published derivative**. The published ALT's location claim conflicts with the archive caption; do not silently overwrite.

**Proposed editorial ALT (HOLD, not applied):** “MS Prinsendam passing Rotterdam's Koningsbruggen on April 8, 1973. Photograph by Ary Groeneveld.” Obtain editorial/photo identity review first. Location accuracy matters to historical credibility.

**Rights:** Ary Groeneveld is a named photographer; archive display does **not** constitute reuse permission. The item-level license, attribution, permitted crop and commercial redistribution terms are **unverified**. No image copied, cached or rehosted. **960px maximum** is only a future derivative upper bound—never upscale. Intrinsic master geometry and computed target height remain **NULL until binary inspection is permitted**.

## Acceptance gate and safe WordPress cache plan

1. Site QA #154 retains logged-out desktop/mobile Chrome/CDP ownership and priority sequence **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**. Add **292:1** as P1 visual-caption/source-transform check after P0: full DOM `src/currentSrc`, final Image request, redirects, status/MIME, decoding/natural dimensions, screenshot and bytes. **Do not alter its draft or duplicate its browser scripts.**
2. If a specific original truly fails: verify archival image identity and exact rights with a catalog/rights contact before considering a local copy. A similarly named file or government archive credit does not by itself establish a valid reuse grant.
3. If permission is granted, obtain legitimate master from publisher/archival source; retain source URL, accession, creator, permission and checksum; compare to live original crop; produce proportional derivative at **min(960px, intrinsic width)** and appropriate height, and a smaller mobile variant only if needed. Do not upscale, strip credits, change historical subject, or overwrite the published source blindly.
4. Upload to **staging WordPress only after separately authorized**; preserve original post-block snapshot, check published design and responsive `srcset`/dimensions/ALT, test CLS and network bytes, compare before/after screenshots, document rollback URL/media ID. **Production WordPress writes are not authorized.**
5. Only claim a 76% optimization after an uncached, complete **61-page/355-image**, same-profile desktop/mobile CDP comparison with approved source-change attribution; do not infer savings from storage or synthetic fixtures.

## Exact file provenance, tests and release state

- Source identity implementation: `qa/media-recovery/browser_probe_core.cjs` — crop `fit` patch **9b9e5456607864b33a88104acdf41febd5702abc**, nonnumeric selector patch **ea0e26b03065483bda9759e8d0d2277f0bcb2c07**.
- New 25-case synthetic identity suite: `qa/media-recovery/test_fit_crop_mode_identity_20261104.cjs` (initial commit `1da754c5`, extra `292:1` tests `45abc6ff`); existing Iroquois regression adapted `1c675de0`.
- 126-row exact-source machine audit: `qa/media-recovery/query_transform_126_slot_census_20261104.json` commit **420003f6b78c64ab574956cae40861fcfe2e60fc**.
- Audit validator: `qa/media-recovery/validate_query_transform_20261104.cjs` commit **e588b7c2a75c2e46200327ff70273c66f1ce16bc**; 14 mutation regressions `qa/media-recovery/test_query_transform_20261104.cjs` commit **e63260908a00dda2b1c16ae49ae40f80fb1fdfcf**.
- **80/80 synthetic checks passed** on exact GitHub-committed source files using isolated V8, a URL/Node-test/fs compatibility shim, including previous identity suites and 14 census tests. **Not native Node CI. No live guest Chrome, actual HTTP status, transferred bytes or CLS measured.** All copyright, binary, WordPress, production and spend gates remain closed.

There were **no production repairs** in this batch. The benefit is improved **correctness of every future image failure/performance determination**, with a real article-level miscaption surfaced for editorial review while P0 browser verification remains the highest repair priority.
