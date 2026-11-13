# Frozen-Source Byte Binding for Historical Image Wire Measurement — 2026-11-12 PT

## Scope and source custody

Read [`docs/IMAGE-WEIGHT-WORKLIST.md` in draft #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183); it does not exist on main or this draft. [Site QA #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns the guest Chrome/CDP collection and original six-image queue. This change is isolated to [Media Recovery #1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703). It does not collect image requests, change media content, or authorize a publication.

**High-impact defect reproduced in synthetic offline tests:** `aggregate_historical_image_wire_20261112.cjs` previously accepted a caller-provided parsed audit and claimed blob SHA, but did not calculate the Git blob SHA from the audit's *actual bytes*. With one historical source URL altered in a synthetic copy, paired fixtures altered consistently, and a mock positive cold-pair comparator, the prior module reported `VERIFIED_HISTORICAL_61_POST_INLINE_IMAGE_COHORT_ONLY` and a synthetic **76%** reduction. This was *not* live visitor measurement, a real attack or evidence of an image failure. It shows a provenance bypass in the measurement **software**.

## Code change

- New `qa/media-recovery/bind_exact_historical_audit_20261112.cjs` authenticates the complete raw audit `Buffer` using Git object framing (`blob <byte-count>\\0` + bytes) and SHA-1, checks against hard-pinned frozen audit blob `a9706c72ad6f17a68113aa87fc063f70d0ca0c34`, rejects untrusted claimed hashes, and parses UTF-8 with fatal decoding. Memory bound: 16 MiB. A merely parsed object or reformatted JSON is HOLD, even if values appear equivalent.
- The 61-post aggregator now requires **raw Git audit bytes** as its first parameter, not a parsed object. The old parsed-object call signature is deliberately fail-closed; consumers must pass `fs.readFileSync` (raw `Buffer`) from a trusted exact Git checkout or equivalent authenticated readback. The audit is parsed *only after* cryptographic verification.
- Malformed null rows and non-string slot values now HOLD rather than causing an unchecked `.split` exception.
- Updated existing 61-post integration regressions to pass raw audit bytes; added parsed-object, source-byte alteration and JSON-reformatting adversarial tests. There is no compatibility bypass.

## Reproduction and verification

- Original historical aggregator Git blob `f7b7b6806c62f88f6f74c4228bd7e07ad7af7624`; corrected aggregator blob verified after commit.
- Actual complete frozen source ledger is still Git blob `a9706c72ad6f17a68113aa87fc063f70d0ca0c34`, **61 posts, 355 image slots**, 288 historical offsite positions and 67 historical first-party positions. Its SHA is verified by GitHub contents readback; content was not changed.
- Synthetic before/after code reproduction: prior V8-loaded aggregator with a mocked positive pair comparator produced 76% on an altered image source, while corrected implementation HOLDs the same altered audit. The simulated 76% is not a performance result.
- **15/15 native Node v22.16.0** focused cryptographic binder checks passed locally (valid Git framing, byte mutation, equivalent reformatted JSON, incorrect claimed hash, invalid UTF-8/JSON, scalar input, parsed-object bypass, oversize input). Additional V8 isolated *mocked comparator* integration exercised all 61 posts / 355 slots on the committed aggregator: synthetic control status correct; forged blob, changed audit source, missing post and changed ALT all HOLD.
- **Limitations:** The updated *full* historical Node integration suite and GitHub CI have not been executed in the connected repository; no Site QA real CDP evidence has been supplied. The code-mode comparator and byte-binding mocks are not a substitute for those. No visitor-visible 404/403, compression gain or CLS claim is made.

## Recovery queue, rights, optimization

Site QA retains the existing sequence **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**; no competing browser collector. An actual failed request must bind the selected DOM image and response/decode events before restoration consideration. Navy, Coast Guard, USGS, Florida Memory and archive catalog URLs are **candidates**, not automatically reusable binary permissions or exact scenes; editor-approved exact identity (or clearly disclosed historical substitute), item-level rights/credit, original-resolution and crop review are mandatory. No original should be mirrored merely because its host returns an inaccessible wrapper status.

Conditional 960px *maximum width* does not mean all images should be resized to exactly 960px: never upscale; preserve aspect ratio, DPR adequacy, high-resolution map/diagram labels and full-size scholarly figures. Favor rights-cleared, optimized WebP/JPEG/PNG derivatives in **WordPress Media** only after isolated visual QA and explicit production approval; staged rollback retains originals and original URLs.

The `42 broken` figure is historical, **not guest-browser confirmed**. The proposed 76% network transfer reduction is **unmeasured**. The historical 61/355 audit is distinct from the newer 66-post/361-inline cohort. Fifteen WordPress originals exceed **1.5 decimal MB**, totaling **47,096,779 stored bytes**; 11 are inline-matched in eight published posts (38,480,915 stored bytes), but these are *not* measured visitor transfer bytes. A defensible aggregate requires the same cold guest CDP methodology for every historical post, unique completed Image request byte totals, and matched identity, visual/crop and browser conditions. No site-wide or present-66-post savings may be claimed from a sample.

## Safety and handoff

No binaries were downloaded, cached, scraped, mirrored, or transformed. No WordPress writes or risky Gutenberg block changes, homepage visual work, Site QA collector changes, merge, deploy, purchases or subscription spend. Changes remain an **unmerged draft**. Site QA should provide raw, independently attributable guest evidence only through its existing workflow; Media Recovery will apply authenticated source and licensed replacement safeguards without duplicating that collector.
