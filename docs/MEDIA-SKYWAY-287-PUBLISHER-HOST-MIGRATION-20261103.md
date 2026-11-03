# Sunshine Skyway 287 P0 — published publisher URL fails in independent viewer; same-publisher media host works
Observed **2026-11-03**. Media Recovery lane only, independent of homepage design and Site QA #154. **No production edits.**

## Fresh observations and exact evidence
Authenticated **read-only** WordPress `posts.get(id=287, context=edit)` reports **published**, modified `2026-11-02T21:40:01`, with **six exact image sources + six ALT attributes** still identical to frozen `qa/media-recovery/parts/03.json`, Git blob **`49183f66f880f7c4dfd363acca906876877f2e5e`**. Page: https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/.

Independent web image retriever **displayed 287:0 through 287:4**. The *exact published URL* for **P0 287:5** returned a retriever **404**:
`https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`.

A link on the publisher's *April 10, 2020* article points instead to **a displayed image** at:
`https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`.
Publisher page: https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/.

**Important distinction:** these are **independent retriever outcomes**, **not Chrome visitor Image GETs or actual guest HTTP statuses**. Browser `currentSrc`, final MIME/HTTP, image decoding, wire bytes, redirects, cache and visible failure remain **unknown**. We therefore have a credible *publisher URL migration* hypothesis, **not** a confirmed live broken photograph. Do not count it toward the founder's 42 reported failures until logged-out browser confirmation.

The publisher **credits the photograph to University Press of Florida**. Publisher hosting and equal filename do not grant Final Vestige permission to republish or copy, nor establish binary identity. **No image downloaded, media attachment created, WordPress image URL edited, or licence approved.**

## Visual-integrity correction — separate editorial action, not applied
Current ALT claims “The old Sunshine Skyway wreckage **and the later bridge replacement** in Tampa Bay.” The candidate image depicts **Summit Venture, shattered old bridge piers and remaining old steel truss**; there is **no 1987 cable-stayed replacement span visible**. St Pete Catalyst's own historical caption dates this scene to the May **1980** collision, not the replacement era. Suggested ALT (requires human editorial approval): “Damaged Summit Venture beside the wrecked Sunshine Skyway piers and surviving old steel truss after the May 1980 collision.” Do not turn that caption into a 1987 photo.

## Authoritative archival alternatives, **different scenes**
Florida Memory [DGM0234](https://floridamemory.com/items/show/267898) — Don Marks, **February 1982**, bridge before the February 1987 replacement. Florida Memory [DGM0237](https://floridamemory.com/items/show/267896) — Don Marks, **May 1969**, bridge before the accident. Both are valuable chronology references, **neither is an exact replacement** for 287:5. Item-level usage/reproduction terms unresolved; rights, image scans, intrinsic pixel sizes, and 960px derivative heights **not verified**. Do not substitute them without editorial scene approval and independently established rights.

Image 287:4 is served by the Middle District of Florida US courts and displayed in the independent viewer, but government hosting alone does not confirm the underlying photographer's copyright status. Image 287:2 carries **St Petersburg Times** graphics: avoid treating it as government-produced. Preserve tiny diagram labels if any future derivative is authorized.

## Safe restoration sequence (no current permission)
1. Site QA #154 logs a **logged-out desktop and mobile** visit, scrolls slot 287:5 into view, records `src/currentSrc`, `img.decode()`, `naturalWidth/Height`, final CDP **Image-type** requestId/HTTP/status/MIME/redirect/cache, encoded transfer bytes, console errors, and screenshot. Explicitly test whether Jetpack rewrites the stored URL.
2. Test the migrated publisher URL in a **separate read-only browser tab**, record whether it displays. Compare scene/crop to originally intended photo; matching basename is not proof of identical bits.
3. Seek the **item-specific reproduction license** from rights owner/authorized agent (publisher credits University Press of Florida), or obtain a genuinely rights-cleared same-scene replacement. Preserve exact photo credit, no false 1987 caption, no unlicensed downloads.
4. **Only after separate staging permission**: verify true intrinsic dimensions and visual crop, create an aspect-preserving `min(960, source_width)` derivative (no upscaling; height unknown until checked). Record binary SHA256 and rights proof; register in staging WordPress Media Library; configure responsive `srcset` and image width/height to minimize CLS. No Gutenberg bulk replacement.
5. Compare staging desktop/mobile image visibility, credits, LCP/CLS, uncached CDP image transfer against the identical baseline protocol. Record rollback to original post revision/media ID; secure explicit release authorization before any production change.

## Metrics and tests
Archived scope: **61 posts / 355 stored refs / 288 external source refs** (Site QA #154 previously counted 286; difference unresolved) / **13 WordPress originals >1.5 MiB**. These originals are **not** visitor transfer bytes. **42 alleged broken images unverified, 76% wire-weight reduction unmeasured, 0 production repairs**.
Machine ledger: [skyway_287_p0_migration_20261103.json](../qa/media-recovery/skyway_287_p0_migration_20261103.json). Offline gate: [validate_skyway_287_p0_20261103.cjs](../qa/media-recovery/validate_skyway_287_p0_20261103.cjs). Adversarial suite: [test_skyway_287_p0_20261103.cjs](../qa/media-recovery/test_skyway_287_p0_20261103.cjs). **36/36 exact-committed-source isolated V8 tests passed**, gate also checked against exact **GitHub archived 6/6**. Native Node in CI and actual logged-out Chrome were **not** executed. Zero subscription spend, site QA draft edits, homepage changes, image downloads, WordPress writes or rights assumptions.
