# Commons `width=1280` cohort: 79 exact source requests, conditional `width=960` proposals
**Audit date:** November 5, 2026 Pacific. **Scope:** source-only; isolated engineering; production untouched.

## Executive finding
Six immutable November 5 WordPress source-census JSON blobs from draft PR #1138 cover 66 published articles, 361 stored inline image slots, 124 Commons `Special:Redirect/file` references, and 294 externally originated image references. This cohort includes **79 exact Wikimedia Commons image requests with `?width=1280` across 18 posts**. The [79-row machine-readable audit](../qa/media-recovery/commons_width_79_20261105.json) records every unchanged published URL, an *unverified request-only* candidate pointing to the same Commons file path but `?width=960`, post identity, ALT, prospective Commons file page, and all rights/browser/production HOLD flags. No image binaries were downloaded.

For **8 of the 79 descriptions**, a conservative word-based heuristic flags maps, diagrams, engravings, figures, or other text/detail-sensitive content for extra review. This is triage only; **all 79 items require visual QA**, and even a lower-risk photo may not be safely downsampled without its catalog intrinsic dimensions.

### Article distribution
- Post 253: 7 references
- Post 254: 7 references
- Post 256: 7 references
- Post 257: 7 references
- Post 367: 7 references
- Post 215: 6 references
- Post 217: 6 references
- Post 218: 6 references
- Post 219: 6 references
- Post 166: 5 references
- Post 425: 3 references
- Post 214: 2 references
- Post 216: 2 references
- Post 268: 2 references
- Post 1917: 2 references
- Post 1920: 2 references
- Post 220: 1 references
- Post 431: 1 references

### Detail-first queue
- 215:2: A Wall in the Dark
- 256:1: The Torch Never Reopened
- 257:4: The Numbers Came Back
- 268:0: They Painted Over Archimedes
- 268:6: They Painted Over Archimedes
- 367:1: They Found the Bomb Twice
- 1917:0: The Piri Reis Map: What the 1513 Chart Actually Shows
- 1917:1: The Piri Reis Map: What the 1513 Chart Actually Shows

## Guard against fake performance claims
A stored query parameter requesting 1,280 pixels is **not** proof of actual 1,280 decoded pixels, desktop image selection, full original bytes on the wire, or an opportunity for exactly 25% byte savings. A 960 request might be ignored, transformed, fail, or degrade a detailed historical chart. All actual guest-Chromium image HTTP status, `currentSrc`, `naturalWidth/naturalHeight`, origin bytes, encoded transfer and cache flags are **null**, not assumed. **76% is an unmeasured claim**, not a verified image-weight reduction; **42 broken is unverified**, not a confirmed visitor-facing count. Do not conflate 13 WordPress images totaling 43,522,829 *stored original bytes* with delivered transfer weight.

## Release sequence (not approved here)
1. Site QA #154 retains the existing **P0 confirmed-failure investigation order**: 285:5, 285:2, 287:5, 418:1/2 and 407:1. This cohort does not modify or duplicate the guest Chromium collector and must not displace real broken-image repairs.
2. Choose a **small low-detail photo pilot** and independently inspect its Commons file page and upstream archive (when relevant): actual pixel dimensions, specific author/credit/license, required attribution, version history, and suitability for commercial publication. If original pixel width <960, preserve the smaller original size; **no upscaling**.
3. Collect **paired cold guest-browser evidence**, first current source then conditional 960 same-file URL, across matching viewport/device, logged-out state, full scroll, no service-worker/HTTP cache. Capture actual request IDs, redirects/status/MIME, natural dimensions, encodedDataLength, decoded image, responsive behavior, before/after screenshot and visual legibility. Avoid changing fine-label maps, photographs with delicate artifacts, and figures on the strength of numeric width alone.
4. **Only after proved byte savings, attribution and exact-image visual parity** consider separately authorized, reversible staged WordPress media/HTML changes. For lawful local assets, use content-addressed filenames and original/candidate SHA-256, store per-file rights/credit, preserve alt/caption/crop, create `width`/`height`, `srcset`/`sizes`, and distinguish lazy offscreen images from LCP hero assets. Use a documented rollback of exact original URL and verify page 200, redirects and desktop/mobile screenshot parity. **No bulk Gutenberg block rewrite.**
5. If Commons permits request-width optimization without localization, preserve the exact same file identity, avoid altering attribution, and do not treat a file-page attribution statement as a universal rights grant. Consider using smaller first-party derivatives only where rights separately permit caching and publication.

## Evidence, tests, ownership
- Input Git blobs: `part 1: 05b01ce3876a62233b1bb497cdc4b1e842d487ee`; `part 2: fe4a33b8a0ca0d2c19d8a577d92281af0ce1e9e7`; `part 3: ccda35904b62ed1f2dbda09ab5001c39888b6faa`; `part 4: a4e0ad40652446761fdcc5f879127038255d8838`; `part 5: c3278c73bd6498debb541e9a52dc3df9b4fd3e61`; `part 6: aab2002740fcd59bb0a192d80a86a3b2e1514e26`.
- Audit: `qa/media-recovery/commons_width_79_20261105.json`.
- Offline fail-closed validator: `qa/media-recovery/validate_commons_width_79_20261105.cjs`.
- Native Node test suite (committed, runner pending): `qa/media-recovery/test_commons_width_79_20261105.cjs`.
- Isolated V8 test execution against the full audit **PASS**, all **25/25 negative mutations rejected**. Native repository Node CI and actual guest Chrome pending.
- Wikimedia's [reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) makes clear that file-specific licensing and attribution should be verified independently.
- Existing independent drafts #154 (Site QA), #183 (historical source/rights worklist) and #1138 (66-post census) are intentionally untouched; homepage visual work is separately owned.

**Safe outcome:** 79 conditional source-request candidates cataloged; **0 visitor failures established; 0 measured bytes saved; 0 images copied, modified or published; 0 WordPress production writes; 0 subscription spend**.
