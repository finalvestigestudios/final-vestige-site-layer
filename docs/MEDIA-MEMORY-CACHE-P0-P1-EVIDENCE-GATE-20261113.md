# FV Media Recovery — memory-cache provenance false-positive fix (2026-11-13 PT)

**Draft-only; PR #183, complementary to Media Recovery #1703 and Site QA #154. No production writes.**

## Reproduced defect in the existing offline QA modules

1. Before this change, a synthetic, correctly source-bound Chrome-like Image 404 with zero intrinsic pixels but `from_memory_cache:true` was classified `confirmed_broken_in_probe_browser`. That is not defensible uncached guest evidence.
2. Before this change, the cold image-wire comparator accepted a synthetic baseline of 1,000 bytes and candidate of 240 bytes as `LAB_PAIR_MEASURED: 76%` even when the candidate response claimed `from_memory_cache:true`. A memory-cached response is not evidence of bytes actually transferred over a cold network run.
3. The general article-image byte aggregator also failed to disqualify explicitly memory-cached image requests.

These are **synthetic QA defects**, not proof that a FinalVestige.com guest saw a 404, that 76% was achieved, or that an image should be replaced.

## Corrected gates

- `qa/media-recovery/browser_probe_core.cjs`, Git blob `750a576ea2d451ed2be05ae2cd5d292073a84b38`: require **all four explicit false values** `was_cached`, `from_disk_cache`, `from_memory_cache`, `from_service_worker` before classifying an image as definitively loaded/broken or admitting its bytes to the article-only tally. Unknown/missing = HOLD.
- `qa/media-recovery/compare_cold_image_wire_v1.cjs`, Git blob `5ff97e286d915fa3d02bd44f66adccbe98433d00`: require the same cache-provenance veto for every matched CDP request in the paired baseline/candidate measurement. Baseline and candidate must both pass.
- Browser core tests, blob `1ed3749c9898632a4006fe03cbb7967c05485ad1`: synthetic memory-cached 404, unknown memory-cache provenance on 404 and decoded 200, and article-byte aggregation against a separately prevalidated slot.
- Pair-comparison tests, blob `d5a7b820009c4d11c866bc8e36116f2a1a4f2314`: memory-cached candidate, memory-cached baseline, and absent candidate flag fail closed.

**Verification:** 70/70 postcommit isolated V8 regression assertions PASS on independently fetched committed Git source and test blobs, using explicit test-only CommonJS, URL and assert shims. This is **not** a native Node or full CI run; those remain required.

## Site QA handoff — no competing collector

Site QA #154 owns the actual logged-out Chrome/CDP collector, including P0 queue `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Record a provably uncached complete request-event lineage and the exact published/current/final image URLs, status, MIME, intrinsic pixel dimensions, encoded network bytes and redirect chain. If the collector cannot reliably establish `from_memory_cache:false` from its full browser-event record, report **UNKNOWN**, not an invented false value. Do not turn an external search/retriever wrapper into actual guest status.

## Sizing, rights and performance boundaries

The official `docs/IMAGE-WEIGHT-WORKLIST.md` is in **draft #183**, not the main branch. Historical frozen site sample: **61 posts, 355 inline image slots**, approximately **42 reportedly broken** with **zero independently verified guest-browser failures**. Expanded live source cohort **66/361** is not the same measurement sample. **15** WordPress originals exceed **1.5 decimal MB**, total **47,096,779 stored bytes**; **11** are inline-linked across eight posts, total **38,480,915 stored bytes**. These are CMS storage figures, not network transfer. The proposed **76% reduction remains unmeasured**.

A true reduction requires a matched full-scroll, same-article and same-source cold guest-browser baseline/candidate with valid *noncached* response bytes, identical viewport/browser configuration, complete image census and no missing or failed images. One synthetic 1,000→240 pair says nothing about actual 61-article aggregate performance. The 960px no-upscale/DPR, exact-scene, rights/attribution and visual-integrity requirements remain unchanged.

No third-party binaries were retrieved, cached or rehosted. No WordPress posts/media were changed. No homepage work, duplicate browser collector, merge, deploy or subscription spend.

## Source of truth / handoff

- [Site QA #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154)
- [Media Recovery #1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703)
- [Prior six-image exact-source/unknown-browser audit](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/ad28827fbc03406cbfb099dced316a0d3ddc2305/qa/media-recovery/p0_request_event_custody_20261113.json)
- [11-image oversized inline inventory](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/3424157cce5d270bfa4cbf2e26cae6b6dfe3ba12/qa/media-recovery/p1_11_density_audit_20261113.json)

**Release decision: HOLD.**