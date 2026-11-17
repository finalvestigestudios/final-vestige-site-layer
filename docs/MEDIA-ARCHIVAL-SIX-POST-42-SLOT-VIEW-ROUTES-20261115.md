# Media Recovery — 42-image EDIT/VIEW source-route crosswalk (Nov 15, 2026 Pacific)

**Scope:** six published articles (268, 257, 217, 432, 280, 288), distinct from the four P0 articles already covered in `wp_view_proxy_26_20261115.json`. **Read-only authenticated WordPress `posts_get` in both `edit` and `view` contexts. No image GET and no logged-out browser.** No homepage edits, production WordPress writes, file copies, cache uploads, subscriptions, merges or deployments.

## New actionable finding

The six articles have **42 stored `<img>` slots, and 42 matching WordPress view-context image slots**, with matching post modified timestamps and ALT text. All 42 stored-origin host/path pairs match their view-context target when Jetpack's URL wrapper is decoded. The view routes are:

- **22 external-origin photos through Jetpack** `i0.wp.com`. Seven of these are the Florida Memory article's entire image set; 12 slots occur in the two Navy articles and the remaining three in the other selected stories.
- **19 direct Wikimedia Commons `Special:Redirect/file` images** remain direct URLs in the WordPress view markup, with no Jetpack transformation.
- **1 direct other external URL.** No first-party routes in this *selected batch*.
- **42/42 view image tags lack explicit width/height pairs, `srcset` and `sizes`.** This flags potential responsive-image inefficiency and layout instability, not proven bytes, decode failure, CLS or a production theme defect. Browser HTML, CSS, width constraints and real `currentSrc` may differ from REST view markup.

**These 42 audited image slots are not the separately alleged “42 broken images.”** Zero real-browser failures were verified in this batch. Source preservation alone cannot establish visual correctness. [Machine-readable 42-row ledger](../qa/media-recovery/wp_view_six_archival_posts_42_slots_20261115.json) records full stored and view URLs, ALT, route class, archive leads, null HTTP/decoded/bytes observations and explicit rights/publication holds.

## Primary-source candidate custody and historical accuracy

- **Florida Memory, post 432:** 7 exact item-ID leads PR04493, RC17068, RC10673, N031889, RC04344, RC07668, MSF-PB11548-001. Their individual archival catalog links appear in the JSON. **432:3** is 1928 State Board of Health headquarters, not catalog proof of *post-disaster* headquarters. **432:6** is a photograph taken **in 2001** of a historic mass-burial site, not a 1928 event photograph. Preserve these distinctions in any ALT/caption review. See [previous item-by-item verification](MEDIA-FLORIDA-MEMORY-432-ARCHIVAL-SOURCES-20261104.md).
- **Navy posts 280 / 288:** 6 official accession leads, including USS Pueblo 428-GX-USN-1129207, NH 75559, NH 75561, K-64683 and K-64728, and Honda Point NH 69586. Two further Navy-hosted exact-image catalog matches remain unresolved. **NH 69586** is a donated Naval Historical Foundation / Admiral Pratt collection image; Navy hosting is not independent proof of government authorship. See [Navy accessions and retrieval limitations](MEDIA-NAVY-EIGHT-PUEBLO-HONDA-20261108.md).
- **Commons photographic originals, sample no-upscale review geometry:** 268:0 is **665×448 → 665×448**; 268:6 is **8160×10880 → 960×1280** (manuscript microtext preservation review); 257:6 is **800×800 → 800×800**. All remain release-HOLD. No new pixel data were fabricated. See [Commons item-specific review](MEDIA-COMMONS-EIGHT-FINE-DETAIL-20261108.md).

The [Florida Memory disclaimer](https://floridamemory.com/learn/about/disclaimer.php) describes the archive's access and possible donation conditions; its [selection policy](https://floridamemory.com/learn/about/selections.php) provides added rights context. The [NHHC Photo Archives policy](https://www.history.navy.mil/our-collections/photography.html) explains that most, but not all, items are public domain. Rights review remains **item-specific** for copying or republishing. No replacement image was assumed or selected just because another archive picture depicts the same event.

## Isolated engineering evidence

- [Exact 42-slot JSON audit](../qa/media-recovery/wp_view_six_archival_posts_42_slots_20261115.json)
- [Fail-closed offline validator](../qa/media-recovery/validate_wp_view_six_archival_20261115.cjs) checks post/image slot identity, original source versus rendered proxy host/path, route taxonomy, null guest evidence, 13 official catalog leads, rights/WordPress release holds, and proportional no-upscale geometry.
- [Native Node test definitions](../qa/media-recovery/test_wp_view_six_archival_20261115.cjs): one positive + 20 adversarial cases.
- **Execution:** The exact committed JSON and validator passed a read-back in isolated V8 using a Node-compatible module harness, and **14/14 targeted adversarial copies were correctly rejected**. Native Node tests, CI and logged-out Chrome were not executed for this sprint.

## Recovery and performance plan — no production changes

1. Site QA #154 retains its six P0 cold guest-browser captures. Capture real browser `currentSrc`, image CDP response and cache flags, `naturalWidth`/`decode()`, screenshot and unmodified transfer bytes for 285:5, 285:2, 287:5, 418:1/2 and 407:1 **before** any restoration.
2. Use this *different* cohort to extend Site QA's next batch with **one direct Commons image, one Florida Memory Jetpack-proxied image and one Navy Jetpack-proxied image**, demonstrating that source HTTP/redirect and visitor CDN status are distinct. Target 268:0, 432:6 and 288:0 for visually meaningful rights/date tests. Do not modify Site QA's collector, drafts or existing P0 queue.
3. If and only if a photo actually fails, secure the **exact same item and historical scene**, per-item license and credit, authorized original file identity and SHA-256. Determine intrinsic pixels before producing optional derivative `w=min(960, native_w)`; `h=round(native_h*w/native_w)`. Preserve legibility of maps, diagrams and manuscript text. Stage a non-production WordPress Media candidate separately, without automatic Gutenberg rewrites.
4. After editorial review, a future separately authorized change may localize an image with a reversible URL/media-ID manifest, fallback format and appropriate `srcset`/`sizes`/dimensions. Compare unchanged URL identity or explicitly approved photo replacement against equal-viewport cold-browser request-ID/network bytes. Record layout/screenshot and LCP/CLS. **Do not claim 76% network reduction** until a matched full-census before/after transfer audit supports it.

**Context stays separate:** Historical 61 posts/355 stored images/288 external-origin dependencies are not a broken count. The reported 42 broken are still guest-unconfirmed; proposed 76% image network savings are unmeasured. The last independent WordPress inventory remains 132 images, **20** originals >1,500,000 stored bytes totaling **64,385,752** stored bytes, not visitor transfer.

**Release:** HOLD — no copying, caching, rehosting, upload, post rewrite, homepage work, merge, deployment or subscription spend.
