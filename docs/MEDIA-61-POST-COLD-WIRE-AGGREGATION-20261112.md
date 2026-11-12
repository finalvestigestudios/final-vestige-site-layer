# Cohort-wide image-transfer measurement: fail-closed 61-post aggregator (2026-11-12)

**Owner:** Media Recovery draft PR #1703, not Site QA #154; **no production change**. Historical WordPress source census is locked to the exact 355-row blob \`a9706c72ad6f17a68113aa87fc063f70d0ca0c34\`. Worklist \`docs/IMAGE-WEIGHT-WORKLIST.md\` was read from draft PR #183 (blob \`2acd06a4ca4317646006eb6591face3fe76fedec\`); absent on main / PR #1703. Site QA's source-only PR #154 is not modified.

## New measurement guard

\`aggregate_historical_image_wire_20261112.cjs\` is an **offline** third-stage, exact-slot cohort rollup, consuming already-collected Site QA cold CDP pair evidence. Unlike a single-post 76% figure, it requires **all 61 historical posts and all 355 original WordPress image positions**, exactly once, with original URL/ALT evidence bound to the frozen editor-source census and explicit \`WP_EDIT_SOURCE_MATCHED_FROZEN\` provenance. Each before/after post pair is independently re-adjudicated through the existing \`compare_cold_pair_visual_parity_20261111.cjs\` quality gate, itself calling \`measure_image_transfer_pair_20261111.cjs\` for image-request HTTP 200/MIME, redirect, cache, decoded-source and unique-request byte checks. Missing post, slot, actual bytes, original source, image quality or changed crop returns **HOLD and null savings**; zero substitution or missing-image silence allowed.

Only then does it compute \`100 × (sum of completed uncached baseline Image encodedDataLength − sum after) / sum baseline\`, weighting by **actual transferred bytes**, never mean of article percentages or WordPress stored-original sizes. Each historical article is visited cold exactly once. Tests with **synthetic** 1,000→240 bytes at 355 distinct image slots return 76% for that fake complete input, explicitly **NOT actual 76% site performance**.

**Scope restriction is deliberate:** the current published cohort was separately reported as **66 posts / 361 images** on Nov 8, so even a fully measured 61/355 historical cohort does **not** establish current-sitewide 76%, traffic-weighted savings, CSS/background asset savings, whole-page weight, actual reduction in the 15 stored WordPress originals or deployment readiness. The current-sitewide claim and production permission flags remain **false by construction**.

## Actual current evidence / QA handoff

The historical **42 reported broken** remain guest-unconfirmed. The six existing P0 Site QA collector positions are \`285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1\`; **no competing collector** is introduced. For each future pair, QA must preserve exact WordPress source and ALT, cold guest currentSrc, complete Image request/redirect status and cache evidence, selected physical pixels versus CSS × DPR, screenshot and object-fit/position. Attach \`published_original_src\`, \`published_alt\`, \`published_source_provenance\` for each record before invoking cohort rollup.

The 15 WordPress originals exceeding 1.5 decimal MB still total **47,096,779 bytes of stored originals**, 11 inline matched originals **38,480,915 stored bytes**. Neither value is a visitor-transfer baseline; no legitimate 76% reduction can be calculated from them.

**Verification:** Isolated V8 against the *actual exact committed dependency source* and *actual 355-image audit* before committing: 14/14 adversarial/control simulated-evidence checks passed. The committed Node test file has 18 cases; native Node CI and actual logged-out Chrome remain unexecuted, and there are **zero measured real HTTP outcomes**.

No images fetched or mirrored, copyright rights inferred, 960px variants generated, WordPress posts/Media Library updated, homepage design altered, PRs merged or deployed, or subscriptions charged.