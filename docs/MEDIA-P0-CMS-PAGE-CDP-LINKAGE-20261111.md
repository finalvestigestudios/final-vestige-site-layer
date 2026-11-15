# P0 published page and CDP-request lineage — 2026-11-10 Pacific / 2026-11-11 UTC

## Verified WordPress source, not visitor-browser delivery

Authenticated read-only WordPress `posts.get(context=edit)` returned published **post permalink, last-modified date, and complete stored inline source** for articles **285 (6 images), 287 (6), 418 (6), and 407 (8)**. All six P0 image `src` strings at **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** matched the frozen recovery inventory exactly; this is evidence of stored source integrity, **not proof that visitors received or decoded the images**. Exact sources, source-only web-retriever wrapper observations and null guest statuses are in [the machine-readable audit](../qa/media-recovery/p0_cms_article_cdp_lineage_20261111.json).

## Reproduced and corrected evidence-attribution defect

Before this patch, `guestFinding` classified **the correct original source URL**, with a synthetic uncached 404 and zero pixels, as `CONFIRMED_GUEST_BROKEN` **even if that request was captured while viewing the wrong article**. This is a demonstrable *offline false attribution*, not a live Final Vestige image failure. The prior six-slot source check alone did not bind a network result to the expected article, page navigation or actual DOM image element.

The draft-only gate now requires the independently read-back **published article permalink**, successful HTTP 200 article navigation, complete page image census and lazy scroll, exact source-image ordinal, matching DOM `img.src`, nonempty capture run and CDP request ID, identical request/response/DOM-element request IDs, and a SHA-256 screenshot fingerprint. Incomplete or contradictory attribution returns `HOLD`. Redirected or transformed CDN `currentSrc` still needs separate manual source-lineage evidence; no implicit equivalence is introduced.

Regression: **84/84 isolated V8 test cases passed before commit** (70 existing, 14 new), including 13 synthetic wrong-page/slot/request/screenshot adversarial scenarios. Native Node CI and actual guest Chromium are **not established**. The Site QA #154 browser collector is not duplicated, changed or executed by this patch.

## Item-specific primary-source alternative (not a restoration)

**Florida Memory, State Archives of Florida, RC09236**, dated **May 9, 1980**, describes a car close to the collapsed Sunshine Skyway span (https://www.floridamemory.com/items/show/32082). This official catalog item depicts the disaster aftermath and is not verified as identical to published **287:5** (old wreckage and later replacement bridge scene). It is a **separate editorial archival candidate only**. Copyright/commercial reuse, attribution, native pixel dimensions, exact photo identity and license-free access all remain **HOLD**; do not copy, cache, or substitute the image.

## Image restoration and size limits

Maintain first priority **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1** for Site QA's already-owned guest/CDP collector. Only after real failures are verified may the team request separate editorial staging review: identify the same event/date/view, locate rights holder and item-level commercial-reuse grant, check credit/attribution, obtain allowed source binary and hash, confirm native dimensions, preserve full-frame crop (no unauthorized image restructuring), and prepare max-width **min(960,native_width)** proportional output with no enlargement. The **819×614 Three Mile Island Commons original** cannot be made 960px or silently recropped from its original ~4:3 frame to the SayMedia derivative's 16:9 request. Historic Coast Guard/NOAA 1946-versus-1964 scene dating remains subject to human historical verification. Make full-resolution viewing available where maps/engineering drawings' lettering would otherwise become illegible.

A WordPress media caching proposal must remain **staging-only** until individually authorized: documented rights and credit, safe derivatives, reversible source reference mapping, mobile/desktop screenshot parity, attachment provenance, and rollback. Zero third-party image binaries were retrieved or cached during this sprint; zero WordPress content was changed.

## Cold transferred-image weight: 76% still only a target

Historical baseline: **61 posts / 355 source inline images / 288 offsite research positions**. Expanded worklist (#183) baseline: **66 posts / 361 inline images**. Do not mix them. **15 WordPress stored originals >1,500,000 bytes total 47,096,779 bytes**, of which 11 inline-matched originals account for **38,480,915 bytes** across eight posts. Those are disk storage sizes, **not transferred visitor bytes**. The old assertion of 42 missing external images has not been proven by a complete guest-browser census.

For paired cold visitor tests, use the **same URL, viewport, DPR, scroll/lazy-image coverage, cache-disabled state, image source identity and CDP protocol** before and after, count distinct completed encoded image transfers (without double-counting redirects, cached images or repeated image slots), record Jetpack and responsive `currentSrc` decisions, require screenshots that preserve scene identity, and publish exact baseline and candidate byte totals. The high-value initial traffic measurements remain direct-original Malbone images and the five PNG posts lacking subsizes; the Vasa source already selects Jetpack transformations and should not be assumed to transfer full originals.

**No homepage design changes, duplicate Site QA collector, risky block rewrite, production image replacement, WordPress write, merge/deploy or subscription spending.**
