# Cold-CDP source-cohort binding gate — 2026-11-07 Pacific / 2026-11-08 UTC

## Operational result

Added an **offline, read-only source-manifest binder** to the existing image-performance draft PR #1402. This is **not** another browser collector; Site QA PR #154 retains Chromium/CDP capture, and Media Recovery PR #183 retains its existing six-source P0 guest adjudicator and cold-CDP comparator.

**Risk addressed:** A legitimate **one-post** cold-browser baseline of 1,000 transferred image bytes and a candidate of 240 bytes calculates **76% for that one paired test**. The existing comparator correctly labels that `LAB_PAIR_MEASURED`, rather than sitewide proof. If one were to assemble or publish the result as a "61-post" or "66-post" figure without checking the frozen source manifest, missing articles, omitted original image slots, or mirrored reductions in both input captures could silently shrink the denominator. The new binder fails closed unless EVERY expected post and original stored image URL appears in BOTH inputs.

## Immutable cohorts and actual findings

- October 30 baseline: **61 published articles, 355 stored inline URLs**; 42 reported broken images **unverified** in guest Chromium. Different third-party URL count definitions (286 vs 288) are not browser failure counts.
- Historical mixed-date extension: **66 posts, 361 stored inline URLs** (61/355 from Oct 30 + five posts/six URLs on Nov 7). **Post 1922 has zero original inline images and must remain in the 66-post cohort**, with exactly zero article-attributed image bytes. This is not a fresh same-day recrawl of all 66 posts.
- Full-source manifest Git blob SHA **`1b83b72040a45374e614cc31b82216b3b06e89d7`**. The CLI validates the complete raw file against this immutable SHA before considering a trace.
- New code requires guest full-scroll/whole-census evidence for precisely 61 or 66 posted article IDs, same original post paths when known, exact original source URL by slot key (both baseline and candidate), same browser/device/cache settings, no confirmed broken images, and explicit 0-byte accounting for image-free pages. It then delegates wire math and CDP request-ID validation to the EXISTING `compare_cold_image_wire_v1.cjs`, without modifying that program.
- On a valid, fully proven pair, the result is only `BOUND_LAB_PAIR_ONLY`; **sitewide 76% permission remains false**. A claim of real impact requires fresh guest-browser captures, visual parity, independent repeatability and properly scoped analytics.

## How to run against genuine browser exports

```bash
node --test qa/media-recovery/test_cdp_cohort_binding_20261108.cjs
node qa/media-recovery/validate_cdp_cohort_binding_20261108.cjs \
  qa/media-recovery/sitewide_wire_cohort_manifest_20261107.json \
  path/to/guest-before.json path/to/guest-after.json expanded
# 'legacy' is available for the fixed 61-post cohort.
```

**Before and after** must contain the raw evidence from the existing Site QA browser capture; do not synthesize transferred bytes or bypass unverified pages. Published `stored_url` changes (e.g. a newly substituted photograph) deliberately fail this optimization-only gate; those require separate image-specific rights, historical-scene and reversible WordPress release review.

## Priorities and safe-release boundaries

Keep the six P0 external-image slots first: **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Their exact original URLs are already pinned in `qa/media-recovery/p0_guest_browser_disposition_pending_20261105.json` in PR #183; every origin HTTP status and visitor decode/transfer result remains **null**. Retriever-wrapper 400/403/404/500 values are not confirmed origin or guest-browser failures. Never treat same-subject archival photos (Florida Memory, NARA, USCG, USGS) as equivalent to the original without matching provenance, pixel comparison and item-level reuse clearance. Max preview width **960px with preserved ratio and no enlargement**; preserve accessible captions and historical-map legibility. Draft staging must carry original-URL rollback map, creator/license/credit, verified geometry, binary identity and visual proof before any separately authorized WordPress upload.

Current original-media thresholds: **15 originals >1.5 decimal MB**, totaling **47,096,779 bytes**; **14 >1.5 MiB**, totaling **45,553,777 bytes**. Halifax map media #1714 is the 1,543,002-byte boundary case. These are **stored original bytes, not measured visitor transfer**. First-party PNG posts 34–38, Malbone, Vasa and Halifax remain P1 after real P0 broken-image verification.

## Verification and limitations

Two new isolated files were committed: source binder `qa/media-recovery/validate_cdp_cohort_binding_20261108.cjs` (Git blob `ce40f96e456c4396332e945f1b52fffdd0df3ae0`) and 20-case regression suite `qa/media-recovery/test_cdp_cohort_binding_20261108.cjs` (initial Git blob `4d29c6ba39f475609a56720efc6ca5f0f501ff52`). **20/20 test scenarios passed in isolated V8**, covering full synthetic 61/355 and 66/361 cohorts, duplicate/missing rows, wrong sources, incomplete scroll, forged zero-image traffic, mismatched browser settings and fake positive reduction. The real pinned 66-row/361-URL manifest independently passed the binder's structure/identity validation. **Native Node CI and real network-enabled guest Chrome remain unexecuted**. No source/image binary was downloaded, no WordPress write, media mirror, homepage modification, production repair or subscription spend was performed.
