# P0 image-source identity fix — 2026-11-11

## Independently reproduced offline failure

The prior [P0 staging adjudicator](../qa/media-recovery/p0_staging_evidence_gate_20261111.cjs) bound a guest record's self-reported `stored_original_src` to the frozen image slot but did not require the network-requested `current_src` to be **that** published image. All other cold-capture fields could be internally consistent, yet a synthetic 404 for `https://unrelated.invalid/missing.jpg` was previously classified as `CONFIRMED_GUEST_BROKEN` for post **285:5**. This is a reproduced **software false positive using a test-only fixture**, **not** a real Final Vestige image failure.

## Safe repair

The adjudicator now returns `HOLD: SELECTED_SOURCE_NOT_THE_PUBLISHED_ORIGINAL` unless `evidence.current_src === item.original_src`. This applies to both broken and displayed classifications and to the aggregate verified-broken count. Image requests that have been redirected, proxied through Jetpack, selected from `srcset`, or otherwise rewritten remain **HOLD** until Site QA can supply independently reviewed source lineage. Do not strip query parameters, compare hostnames only, assume CDN links are equivalent, or mark unverifiable rewrites as broken. The existing network, cold-cache, status, geometry, screenshot-ID and rights checks remain intact.

Five new adversarial tests cover arbitrary external URL, alternate same-domain image, candidate URL substitution, false successful load and aggregate false-broken count. **53/53 exact-source V8 Node-compatible tests passed precommit**, including 48 original checks; postcommit verification must be separately recorded. The source-only [six-image / fifteen-original JSON ledger](../qa/media-recovery/p0_original_source_binding_audit_20261111.json) retains all exact URLs and has **null guest HTTP statuses and network bytes**.

## Acceptance and rights

Keep the Site QA #154 collector exclusive. The sequence remains **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Do not promote a proposed replacement without original-photo identity/crop, item-level commercial use rights, attribution, ALT/chronology, native dimensions and conditional <=960-pixel no-upscale verification. For TMI 285:5 the previously identified Commons original is 819×614; the publisher's 16:9 crop is **not** silently interchangeable. No automatic staging authorization.

Across the separate historical **61-post / 288-offsite** cohort and expanded **66-post / 361-inline** performance cohort, the reported **42 broken** remains visitor-browser-unconfirmed and the proposed **76% wire saving remains unmeasured**. The 15 WordPress originals >1.5 decimal MB total **47,096,779 stored bytes**; they are not measured image transfers. Docs/IMAGE-WEIGHT-WORKLIST.md lives in PR #183, not this branch. **No image binaries copied, homepage work, WordPress writes, deployment, merge or spending.**
