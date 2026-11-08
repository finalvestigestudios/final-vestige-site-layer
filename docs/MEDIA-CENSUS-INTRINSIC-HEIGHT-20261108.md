# November 8, 2026 — historical-image census intrinsic-height safety correction

**Ownership:** Media Recovery draft PR #183 only. Site QA #154 owns guest Chrome/CDP collection, and the interim lead owns homepage visuals. This patch changes neither.

## Reproduced before correction (synthetic, not a visitor observation)

The source census `proofKind` in `qa/media-recovery/image_census_coverage_core.cjs` previously checked `natural_width` only. An apparently loaded historical photograph with **960×0** intrinsic pixels was marked `loaded`, and an HTTP 404 image with **0×480** was marked `broken`. In both cases `assessPage` returned COMPLETE. If supplied to the site-wide census, contradictory geometry could be mistakenly accepted as conclusive evidence. The separate P0 adjudicator was recently hardened, but the general 61/66-post census still had the gap.

## Safe change

The independent `proofKind` path now requires **two positive safe integer dimensions** for loaded photographs and **both exactly zero** for browser-confirmed broken images. Invalid, missing, fractional, string or contradictory intrinsic height becomes `unresolved`, which fails page and complete-run status closed. Existing source URLs, network/CDP request evidence, HTTP/MIME, cache checks and rights/publication holds are unchanged. Legitimate zero-image post 1922 remains allowable.

## Regression record and scope

The additional `test_image_census_natural_geometry_20261108.cjs` file has 22 cases: 2 valid controls, 16 malformed-height tests, 2 full-run failure proofs, an image-free article and a full valid census. Replayed against the exact former helper in isolated V8: **4/22 PASS, 18/22 FAIL** (the bug is reproducible). Replayed against the proposed patch in the same environment: **22/22 PASS**. These are synthetic offline regressions, not real Chromium/Node CI. Run `node --test qa/media-recovery/test_image_census_natural_geometry_20261108.cjs` in an authenticated checkout and rerun the existing P0 probe/census suites.

## Real-world evidence and production gate

The initial 61-post / 355-inline-image inventory (expanded mixed-date 66/361) remains a **source manifest**, not a visitor-browser census. The reported 42 broken images remain browser-unverified; 76% network weight reduction remains unmeasured. Fifteen WordPress originals exceed **1,500,000** decimal bytes (14 exceed 1.5 MiB), totaling **47,096,779** stored bytes, not browser transfer bytes.

P0 browser queue remains **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. When Site QA produces a complete guest-browser evidence export, require exact currentSrc, network request ID/status, cold cache flags, naturalWidth and naturalHeight, byte lengths, full-page scroll and visual/caption comparison. Do not exchange originals for merely same-topic photographs. Cached WordPress staging, a ≤960px no-upscale derivative, and every reuse-right/attribution decision remain on hold until item-level approval; historic maps must retain legibility and an original-resolution viewing route.

**Boundaries:** no HTTP/download/cache, image mirroring, WordPress writes, post rewrites, homepage work, new agent, paid subscription or production fix. Only draft branch code/tests/documentation. Site QA #154 is notified separately after exact Git blob SHA verification.
