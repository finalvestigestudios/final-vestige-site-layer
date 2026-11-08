# Source image classifier cold-network and geometry safety — 2026-11-08 PT

## Reproduced defect — synthetic fixtures, not production incidents

The shared offline image classifier previously labeled a service-worker/disk/memory-cached 404 as `confirmed_broken_in_probe_browser`; a 404 represented as **0 × 480** pixels was also marked broken. It also marked a 200 image with **960 × 0** pixels or unknown cache flags as `loaded_in_probe_browser`. Five exact V8 fixture outcomes were reproduced against the original blob `6735758566e42cf39c156f8571f72547c5ae37dc` before correction. The general article-byte helper separately accepted unknown cache flags as valid transfer bytes. These failures affect the reliability of future Site QA evidence; they are **not** confirmed failures among the 42 historical reports.

## Isolated correction and tests

Only `qa/media-recovery/browser_probe_core.cjs` is changed, not the guest Chrome collector or its Site QA PR #154. Its classifier now requires all three CDP cache flags **explicitly false** and both intrinsic dimensions consistent: zero-by-zero for confirmed broken or positive integer width and height for loaded. A genuine fresh HTTP 404, cold network error, or completed fresh image-decoding failure remains distinguishable. `scopeArticleImageWire` rejects missing/positive cache flags rather than counting a simulated byte transfer.

A separate **21-case** native Node regression file `qa/media-recovery/test_image_classifier_cold_geometry_20261108.cjs` is included; isolated V8 run against actual fetched existing modules: before patch **9/21** pass, after patch **21/21** pass (tiny URL shim in test runner). One older fixture in `test_browser_probe_core.cjs` was updated to explicitly represent a zero-by-zero and cold HTTP 403. Full native Node CI and a real guest Chromium run remain pending.

## Operational integration and hold

The current CDP collector emits `from_disk_cache` and `from_service_worker` from `Network.responseReceived`, but `was_cached` is only set to true on `Network.requestServedFromCache`. Normal collector output may omit `was_cached:false`; this stricter evidence gate will intentionally leave such results **unverified** until the existing Site QA collector/evidence preparation normalizes trustworthy cold request evidence. **Do not infer a false flag when the event stream was incomplete.** Site QA owns that collector. No parallel crawler or collector edits are proposed.

P0 inspection order is unchanged: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Exact published URLs and wrapper-only outcomes remain in `p0_guest_browser_disposition_pending_20261105.json`. The reported 42 browser-broken originals remain **UNVERIFIED**; proposed 76% wire savings **UNMEASURED**. Current storage inventory: 15 originals exceeding 1,500,000 decimal bytes, totaling 47,096,779 stored original bytes (not transferred bytes). Derivatives remain conditional to verified source size at max 960px, no upscale, identity/rights/attribution and editorial visual review. No images downloaded/cached; no WordPress, page, homepage, production, subscription or PR merge action.
