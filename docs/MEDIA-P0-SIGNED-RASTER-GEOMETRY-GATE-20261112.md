# Media Recovery: Signed raster identity, PNG CRC and actual output geometry — 2026-11-12 PT

**Scope:** Isolated Media Recovery draft [PR #1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703). Site QA [PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) remains the sole logged-out Chrome/CDP collector. No homepage design, WordPress API writes, publication changes, asset downloads/uploads, third-party caching, deployment, merges or subscription spend.

## Read and historical ground truth

- [Image weight worklist](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/qa/media-recovery-reviewed-20261030-1158/docs/IMAGE-WEIGHT-WORKLIST.md) is on **draft PR #183**, not the default or recovery branch; blob `2acd06a4ca4317646006eb6591face3fe76fedec`.
- Historical frozen **61 posts / 355 published raw image slots**, including **288** offsite slots, and all original URL/ALT positions preserved by prior read-only WordPress checks. The **42** historically reported failures are **not authentic guest-browser-confirmed**. A separate newer cohort is **66 posts / 361 images**, not interchangeable with the frozen group.
- **15** WordPress originals strictly over **1,500,000 decimal bytes** total **47,096,779 stored-original bytes**, of which **11** matched inline references across eight published posts total **38,480,915 stored bytes**. These values are NOT actual cold network transfer sizes; Vasa's Jetpack transformations and five PNGs with no subsizes especially require actual `currentSrc` measurement.
- A proposed **76% reduction** is still unmeasured site-wide. The existing 61-post cold-wire gate must ingest actual complete Site QA uncached CDP image transfer events before reporting a byte-weighted percentage.

## High-value defect: cryptographically consistent but non-image bytes

The previous byte-bound `verify_p0_review_evidence_20261112.cjs` established matching Git and SHA-256 hashes, but checked screenshots using only a PNG magic prefix and candidate assets using merely nonzero length. Thus an arbitrary string, HTML, or malformed image with self-consistent supplied hashes could satisfy the byte-consistency portion of staging admission; the P0 outer gate's 960px geometry had no independent evidence that the **binary** had the claimed width/height.

**Remedy on this draft only:** The verifier now SHA-checks the submitted bytes, then structurally parses a screenshot PNG (signature, IHDR, CRC-verified chunks, nonempty IDAT, IEND) and proposed candidate PNG/JPEG/WebP dimensions. The *encoded candidate* dimensions must equal `review.geometry.output_width/output_height`. Signed HTML, SVG, truncated or corrupt PNG, bogus JPEG, missing geometry and size mismatches return a denied, non-writing result. Existing outer admission retains frozen original URL/CDP request binding, per-item rights, exact-scene/crop or disclosed editorial alternative, credit, native dimensions, output width <=960, no upscale and CSS×DPR fidelity checks. PNG candidate dimensions and screenshot dimensions come from actual supplied bytes, not the accompanying annotation.

**Important limitation:** This is structural/metadata validation, not full raster decode, visual equality, verified browser provenance, EXIF-orientation reconciliation, true copyright clearance, or proof any P0 asset is broken. An image with a plausible container can still fail decoding. Require independent image decode and visual side-by-side in staging before even considering a licensed image replacement. JPEG/WebP output is not optimized, converted or cached by this code.

## Exact committed source, tests and execution

- Verifier: `qa/media-recovery/verify_p0_review_evidence_20261112.cjs`, Git blob **`77a8539b91d48d40efecebe52dde058103d772bf`**.
- Regression suite: `qa/media-recovery/test_verify_p0_review_evidence_20261112.cjs`, Git blob **`0ef3fde626918ecb4f4dd7430639ed0c04fd4bd7`**.
- **24/24 native Node v22.16.0 regressions passed** with the two locally executed files matching GitHub Git blob hashes exactly (`git hash-object`). Test cases include signed arbitrary text/SVG, malformed CRC, truncated IDAT/IEND, claimed output dimensions inconsistent with bytes, hash mismatch, rights/source binding, and valid **synthetic** PNG, JPEG and WebP reference assets. During tests a 1x1 PNG fixture with an invalid IDAT CRC was rejected as designed, replaced with a correct synthetic fixture, and retested successfully.
- This is still a **synthetic software QA result**, not a real logged-out visitor check. GitHub Actions CI and the complete unchanged 37-case integrated P0 suite were not rerun in this sprint.

## Site QA handoff and restoration decision

Keep browser-first queue **285:5 -> 285:2 -> 287:5 -> 418:1 -> 418:2 -> 407:1**. Refer to [existing six-URL / fifteen-original machine handoff](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/8ce4fae5a327d5e121fdc2d5174ea9b48e87dbed/qa/media-recovery/p0_and_oversize_attested_release_handoff_20261112.json) (blob `0098216405f3415e57d2a3f13969bdb87ffbcd30`) for actual published URLs, known archival catalog candidates and rights status. Its browser HTTP/status/transfer fields are **null** and must stay unknown until Site QA provides authentic evidence. For proposed replacement assets, attach actual screenshot bytes and output asset bytes: signed claims of 960×540 alone now cannot pass the staging-review boundary.

**No source image was replaced, downloaded, localized, compressed, uploaded or published.** The code cannot authorize production or third-party caching.
