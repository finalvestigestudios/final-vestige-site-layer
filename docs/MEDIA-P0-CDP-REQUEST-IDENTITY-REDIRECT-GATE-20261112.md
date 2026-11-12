# P0 selected-request identity and redirect provenance gate — 2026-11-12

**Scope:** Isolated draft Media Recovery PR #1703; no edits to Site QA #154 collector, homepage design, Gutenberg posts, WordPress uploads, third-party binaries, licensing or production.

## Reproduced software defect (synthetic, not a live outage)
The previous gate accepted a guest packet whose `published_original_src` matched frozen P0 418:1 but whose `current_src`, request and final response were **all a completely unrelated failing image URL**. Synthetic CDP-like HTTP 404 plus zero decoded pixels was credited as `GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED` for 418:1. This is erroneous source attribution, not proof that the Coast Guard image failed. The fixture and pre/post disposition are recorded in [machine audit](../qa/media-recovery/p0_cdp_request_binding_audit_20261112.json).

## Corrective controls
- Bind the observed selected `current_src` and request URL to the exact original frozen source of each of six P0 image slots. Different URL, CDN rewrite, Jetpack proxy, srcset selection or signed-query transformation is **HOLD** until Site QA independently establishes same-element DOM-to-request identity and an explicitly reviewed extension to the gate. Do not guess this binding.
- For the allowed case where an actual original request redirects, a simple `redirect_chain_verified:true` boolean is insufficient. Require 2–10 explicit ordered CDP-ID-bound steps, identical start and final response URLs, intermediate 301/302/303/307/308 statuses, final response status equality and no repeated URLs.
- The gate still performs only **preliminary triage** on caller-supplied records. It is not cryptographic proof that the guest run happened: capture blob and screenshot require independent Site QA Git readback, browser event provenance, screenshot review and raw-vs-selected image reconciliation before rights or staging review. The gate grants zero publication, caching or WordPress permission.

## Evidence and priority
The [original P0/oversize bridge](../qa/media-recovery/browser_handoff_6_p0_15_oversize_20261110.json) contains six exact frozen URLs, retriever-wrapper codes and catalog candidates (Commons, Smithsonian, Florida publisher, Coast Guard/National Coast Guard Museum, USGS). The new JSON audit explicitly carries **null** origin HTTP, guest response, currentSrc, decoded pixels and cold transfer bytes rather than repurposing retriever 404/500/403/400. P0 sequence is 285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1. Every candidate remains subject to exact-scene comparison, item-level copyright/credit, native dimensions, no-upscale and ≤960px only when display CSS×DPR permits. Detailed maps and exhibits must keep readable full-resolution access.

## Verification and unaltered boundaries
**37/37 isolated V8 Node-style tests pass** against the proposed patched source (26 existing, 11 new); original unpatched source was independently reproduced accepting the unrelated 404 as a false failure. Native Node CI and genuine visitor Chrome are not claimed as executed. Historical frozen 61/355/288 differs from expanded current 66/361. The historically reported 42 broken images are unconfirmed by logged-out guest Chrome. The claimed 76% transfer improvement is unmeasured: measure unique uncached CDP encoded image bytes on the same complete 61-post cohort, not average percentages or WordPress stored originals. The 15 >1.5 decimal MB originals total 47,096,779 **stored** bytes, not network transfer.

No external binary retrieval, cache, source replacement, WP writes, homepage design change, merge, deployment or subscription expenditure authorized or performed.
