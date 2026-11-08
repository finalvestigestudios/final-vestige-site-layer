# Media weight: complete post cohorts, zero-image posts, and an honest 76% denominator
**Audit 2026-11-07 PT · isolated read-only engineering, no production deployment**

## New high-impact correctness finding
The current 66-published-post WordPress census records **361 inline image source references**. Post **1922 (Change Blindness)** has **zero** stored inline images; four other new posts provide six references. The older 2026-10-30 census is a **different** 61-post/355-reference cohort.

The existing cold CDP comparison helper (`qa/media-recovery/compare_cold_image_wire_v1.cjs` in the Media Recovery draft PR #183) had required `positive(p.stored_image_count)` and `positive(sum)` for **every** article. A complete 66-post run would incorrectly become HOLD because a legitimate image-free post has zero bytes. Simply dropping post 1922 to make the comparator pass would create an **unreported 65/66 sample** and could mislead any sitewide weight-reduction claim.

A narrow **QA-only comparator fix** is now committed on PR #183: allow an explicit zero-image page, but **only when its matched article-image request count and article-image wire bytes are both exactly zero** and the normal page/full-scroll/image-census and CDP evidence gates are satisfied. Require positive total bytes for the overall paired cohort to prevent divide-by-zero. Preserve the image-free page in paired results with an empty source list. Nine additional exact-committed-code regressions passed in an isolated Node-compatible V8 runner; native Node CI and actual browser replay remain pending.

## Immutable/cohort manifest for later actual measurement
- [Source-slot manifest](../qa/media-recovery/sitewide_wire_cohort_manifest_20261107.json): all **66 distinct post IDs and 361 image keys**; the original 61/355 records retain their October 30 date and nine Git source blob references identify the eight frozen inventory parts plus November 7 new-post audit.
- [Fail-closed offline validator](../qa/media-recovery/validate_sitewide_cohort_20261107.cjs) and [15-case suite](../qa/media-recovery/test_sitewide_cohort_20261107.cjs): enforce exact post and slot counts, the five-ID/six-image delta, original P0 source strings, the zero-image article, host/slot identity, provenance SHA format, unmeasured claims and no publication authorization.
- **15/15** checks passed against the exact committed blobs in isolated V8. Native Node CI and complete guest Chrome testing are not available from the current connector runner.

**Critical provenance caveat:** This is a mixed-date *source union*, **not** proof that every original October 30 URL was unchanged on November 7. Refresh source URLs for each of the 66 posts with a read-only WP capture before treating it as an up-to-the-minute baseline. Reject any mismatch rather than patching the manifest opportunistically.

## Acceptance criterion for genuine 76% image-transfer reduction
1. **Do not compare 61-post totals to 66-post totals**. Choose one versioned, exactly matched before/after cohort. Before/after must contain all expected post IDs **including 1922**, every expected stored inline image slot, and same site/runtime, device, viewport, browser version, guest permissions and run conditions.
2. Reuse **Site QA #154 / evidence-intake #1395 existing Chrome/CDP collector**, not a new collector. Run full-scroll, lazy-load-complete, **uncached** guest captures at `390x844` and `1440x900`, with service worker bypass, decoded pixels, real HTTP image responses, redirect identity, request IDs, encodedDataLength, MIME, currentSrc, and visual screenshots. Any mismatch, timeout, cache ambiguity or missing page/slot **HOLD**.
3. Use the existing `compare_cold_image_wire_v1.cjs` to validate each matched cold before/after pair. Image byte reduction per viewport is **100 × (sum of exact unique CDP Image encoded bytes before − sum after) / sum before**. Do not add a repeated DOM image request twice, add stored Media Library original bytes, or pool differently sized audience cohorts. Report results **separately by viewport**; neither is a verified sitewide field result.
4. Even if a laboratory pair measures ≥76%, no 76% public/sitewide or production-success claim follows until full-cohort evidence, source/photographic identity, historical caption/crop fidelity, readability, alt/attribution, rights and any CDN caching/rehost rights are separately cleared. LCP/CLS and actual visitor traffic require additional evidence.

## Operational priorities, kept separate
- **P0 broken-image diagnosis remains first:** Site QA queue `285:5, 285:2, 287:5, 418:1, 418:2, 407:1`. Existing PR #1423 already identifies a plausible same-filename publisher CDN migration for **287:5**; do not duplicate it. The old publisher path's retrieval failure is not a verified visitor-browser failure. The publisher credits **University Press of Florida**, so rehosting rights and ALT/scene integrity remain on HOLD.
- **P1 measured weight:** five no-subsize PNGs, posts **34–38**, original storage **13,267,538 bytes**; then two original Malbone JPEGs post **621**. All derivative maxima conditional ≤960px, aspect-preserving, never upscale. Vasa #299 is already served via a proxied URL in stored article HTML, so large library originals alone cannot measure real transfer savings.
- WordPress's **14** >1.5 MiB originals total **45,553,777 stored bytes** across the newer library inventory, not guest browser bytes.
- The asserted **42 broken images are not established by a logged-out browser**. The asserted **76% weight reduction has not been measured**. Production image repairs: **zero**.

**No third-party binaries fetched or mirrored, no subscription spend, no rehost permission assumed, no WordPress uploads or post rewrites, no homepage-design changes.** Stage any future rights-cleared derivatives separately with exact-scene comparison, rollback and explicit approval.
