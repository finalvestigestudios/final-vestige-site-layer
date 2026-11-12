# Source-classifier reconciliation: QA #154 versus media recovery #183

**Date:** November 11, 2026 (Pacific). **Scope:** offline forensic audit, draft PR #1703 only.

## Verified correction

The committed Site QA #154 code (blob `cdadab899abed4dfd222e75a5616a98390dca4ea`) reserves `jetpack_proxy` for **first-party** `i0.wp.com/finalvestige.com/...` paths. The exact two discrepant third-party Jetpack URLs, `285:1` (Squawkpoint) and `291:0` (National Archives blog), classify as `external` under that code. Therefore **the current classifier excluding these two as first-party cannot explain the 286-vs-288 count difference**.

Replayed that classifier's absolute-URL categories against the eight original archived part files (their eight blob SHAs are pinned in the audit): **61 posts, 355 images; 60 first-party, 7 first-party Jetpack proxy, 170 generic external, 118 Commons redirects = 288 offsite**. Compared to the QA historical aggregate CSV (61 posts/355 images/286 offsite), 59 posts agree; only post 285 and post 291 differ by exactly +1. The archive slots and original URLs are in the linked JSON.

**Caveat:** The raw Gutenberg HTML fed into the original QA 286-count run was not preserved in the aggregate CSV. It may differ from the frozen eight-part #183 snapshot. A different older classifier or CSV aggregation/export behavior also remains possible. The precise historical cause is still **unproven**. This audit falsifies one hypothesis on the code+source pairing; it does not prove what was fed into the old runner.

## Files and validation

- [61-row exact-count replay, two source URLs, rights and NULL browser statuses](../qa/media-recovery/qa154_classifier_semantics_replay_20261111.json).
- [Fail-closed verifier](../qa/media-recovery/validate_qa154_classifier_semantics_20261111.cjs).
- [19 native Node test cases](../qa/media-recovery/test_qa154_classifier_semantics_20261111.cjs).

## Site QA handoff

Keep Site QA #154's existing guest-browser collector and six P0 originals in its established order: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Locate the exact 286-count original input snapshot, code revision, or export timestamp; compare to the eight frozen source files. Do **not** overwrite the historical QA CSV or assume a Jetpack defect from this evidence. Actual visitor image HTTP, image-body/decode, currentSrc and per-request wire bytes remain absent.

42 reported broken images = guest-unconfirmed; 76% claimed cold image transfer reduction = unmeasured. Fifteen WordPress originals >1.5 decimal MB occupy 47,096,779 stored bytes, not actual visitor transfer. Neither of the two source images is cleared for commercial caching/rehosting. Conditional derivatives must be <=960px/no upscale, provenance/rights reviewed, with staging-only visual QA and rollback before any separately approved production change.

Zero image binaries downloaded, license assumptions, WordPress media/posts edits, homepage design writes, merges, deployments or paid tools.
