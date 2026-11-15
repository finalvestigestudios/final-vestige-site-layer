# Media Recovery — JPEG/WebP raster-integrity hold (13 November 2026)

**Scope:** isolated draft Media Recovery PR #1703. The image-weight worklist was read from draft PR #183 (Git blob `2acd06a4ca4317646006eb6591face3fe76fedec`), because that file is absent from `main`. Site QA PR #154 owns all guest-browser/CDP captures; its existing six-slot order is unchanged. No WordPress, homepage, publication, source-image binary, caching, deployment, third-party license, or paid service is altered.

## Reproduced defect

The pre-fix `verifyP0ReviewEvidence` and `verifyP0SourceMasterEvidence` parsed JPEG/WebP **container headers** as dimensions. This is not pixel/raster decoding. An attacker or accidental corrupt file can present a plausible 1×1 JPEG with SOI, SOF, SOS and EOI but no valid compressed image, or a 30-byte WebP VP8X RIFF with only width/height and no VP8/VP8L payload. When SHA-256 hashes and declared dimensions are recomputed over those invalid bytes and rights fields are self-consistent, the old verifier could return `verified:true` for staging **review**. This was not publication authorization, but incorrectly promoted a visually unusable asset as byte-verified.

The revised verifier now fails closed with `CANDIDATE_FULL_RASTER_DECODE_REQUIRED` for JPEG/WebP replacement candidates and `SOURCE_MASTER_FULL_RASTER_DECODE_REQUIRED` for corresponding masters. This applies even to otherwise legitimate JPEG/WebP files until an independently decoded raster (bound to those exact bytes) is available. The existing fully decoded PNG path remains review-only, never a WordPress upload or rehosting permit. No fallback to unverified web-retriever display, image labels, document text, inferred photo identity, or SHA-only evidence is allowed.

## Evidence, tests and limitations

- Changed verifier: `qa/media-recovery/verify_p0_review_evidence_20261112.cjs`. Exact expected Git blob `bb1268f8fba5647abecef0cfcac2696c7e315bc4`.
- New adversarial regression: `qa/media-recovery/test_p0_raster_decode_admission_20261113.cjs`. Exact expected Git blob `da1fc10d4654720d4273683379e77cffb7dc7603`.
- Previously committed source-master suite remains `f64a3650803aa7c157a72fdb66d4bd8105f83dd3`; PNG decoder remains `d09669d0116a741fd1eccaa0631c73061125f8b2`.
- Local native Node v22.16.0: **18/18 tests passed** (six new genuine adversarial/control checks plus twelve existing source-master checks); source/decoder/test source copies independently matched the exact committed Git blob hashes, and revised verifier passed `node --check`. No CI, browser or image binary downloads were used.
- This change deliberately **does not** implement a full JPEG/WebP decoder. Real photographic JPEG/WebP candidates must stay on HOLD until a bounded independent raster decoder with byte-level digest binding, image orientation, target-DPR visual review and item-specific reuse rights can be introduced and tested. This cannot be bypassed by an editorial claim alone.

## Restoration and performance invariants

The historical frozen census remains **61 posts / 355 image tags**. QA #154 originally counted 286 external refs; Media Recovery's consistent classifier counted 288. The **42 reported broken originals have not been confirmed by real logged-out visitor browser measurements**. The six highest-priority slots remain `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1` with published URLs in `qa/media-recovery/p0_six_source_master_admission_20261113.json`. Prior 404/403/400/500 wrapper observations are *not* origin/guest HTTP statuses.

Fifteen WordPress original media items exceed **1.5 decimal MB**, totaling **47,096,779 stored bytes**. These are storage sizes, not cold user-device transferred bytes. The suggested **76% image weight reduction is unmeasured**. Source-master photo identity, editor-checked scene/crop, per-item copyright and credit, 960px maximum width, no upscaling, displayed CSS dimensions × actual DPR, and rollback are all mandatory before any proposed staging derivative.

**Safe next action:** Site QA #154 uses its existing collector to capture real failure evidence and screenshot bytes; Media Recovery may then implement an isolated, independently tested JPEG/WebP full-raster decoder/admission path or prepare license-cleared PNG review assets without changing source photographs. No original Gutenberg blocks or homepage design are to be touched in this PR.
