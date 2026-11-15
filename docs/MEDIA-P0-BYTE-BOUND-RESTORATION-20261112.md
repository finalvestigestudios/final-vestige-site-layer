# FV Media Recovery — byte-bound P0 staging barrier and exact-source handoff (12 November 2026)

**Scope:** Draft PR #1703 only; Site QA PR #154 owns the sole logged-out Chrome/CDP collector. No production, WordPress, third-party binary retrieval, external caching, Gutenberg rewrite, homepage design, merge or spend.

## Evidence read before changes

- `docs/IMAGE-WEIGHT-WORKLIST.md` is in draft PR #183, branch `qa/media-recovery-reviewed-20261030-1158`, blob `2acd06a4ca4317646006eb6591face3fe76fedec`; it is not on `main`.
- Existing PR #154 records a source-level third-party image dependency finding, **not** proven visitor failures.
- Historical frozen cohort: **61 posts / 355 image positions / 288 offsite references**; **42** reported broken, **none independently confirmed by a guest browser**. Do not silently combine with the newer **66 posts / 361 image positions**.
- Later WordPress media inventory: **15 original files strictly >1,500,000 decimal bytes**, **47,096,779 stored original bytes**; 11 inline-matched files represent **38,480,915 stored original bytes** across posts 34–38, 269, 299 and 621. Four oversized items have no published inline match; they may still be used on pages or as featured assets. No deletion or bulk optimization.
- Proposed **76% image-wire reduction remains unmeasured**. WordPress file storage, page-source tags and prior single-article examples cannot establish transfer-byte savings.

## Concrete safety defect and correction

The existing P0 adjudicator checked a 40-character capture Git SHA, screenshot SHA-256, reviewer rights SHA and candidate SHA-256 *as strings*; these pointers alone did not prove the represented bytes existed or matched the claimed capture, screenshot or asset. The previous sprint fixed wrong-CDP-request attribution, but staging review was still reachable with fabricated hashes and human booleans.

The new `verify_p0_review_evidence_20261112.cjs` requires **actual caller-supplied offline artifact bytes**: a capture JSON record whose Git blob SHA-1 matches the locked packet *excluding its own blob SHA*, screenshot PNG bytes matching its SHA-256, a rights-review JSON record whose Git SHA-1 matches and which binds slot+catalog+asset+credit/permission, and candidate binary bytes whose SHA-256 matches the proposed asset. The existing P0 gate now **refuses to issue even its non-writing staging-review packet** without these checks, after all prior exact-original, redirect, geometry, no-upscale and disclosure safeguards. Unsupported packets remain an observed/suspected HOLD, never a production action.

**Limits:** Matching a digest proves byte consistency, not that a genuine browser executed, the Git object resides in the expected repository, the PNG fully decodes, a photograph matches the original or legal reproduction rights exist. Site QA must independently read back Git objects and screenshot evidence; an editor must verify same scene/crop, donor restrictions and catalog rights. Synthetic tests are not live image checks.

## Primary-source catalog addition, no replacement approved

Florida Memory item [RC09237 — Sunshine Skyway bridge accident, May 9 1980](https://www.floridamemory.com/items/show/32083) documents the stopped car at the collapsed span, a **different photograph** from existing catalog lead RC09236 and from the publisher-linked image at slot `287:5`. The source is useful as a clearly disclosed *editorial alternative*, **not** a same-photo drop-in. The individual image's current reuse terms and scan/native pixel dimensions still need inspection. Historic chronology and State Archives attribution are mandatory. The other six-P0 candidate catalog records remain held for exact-pixel and rights review. [USGS's 1959 Hebgen Lake fault-scarp catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) explicitly says Public Domain but does not alone prove its photograph is identical to the published `407:1` asset.

[The machine-readable handoff](../qa/media-recovery/p0_and_oversize_attested_release_handoff_20261112.json) preserves **all six exact P0 published URLs**, prior *web-retriever wrapper* observations (not actual origin/browser statuses), six null guest status fields, archival candidates, individual rights holds, conditional <=960px information, all 15 oversized original URLs, source-use associations and no-write constraints.

## Safe restoration and measurement sequence

1. Site QA #154 collects six P0 images in existing order `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`, including logged-out full-scroll Chrome CDP requestId/redirect/final response, element `src`/`currentSrc`, status, MIME, decoding, CSS dimensions × DPR, screenshot, cache flags and true cold transferred image bytes. Classify network error separately from HTTP 404 and decode error.
2. Independent QA checks actual capture Git blob bytes and screenshot digest against this module, then examines the relevant item catalog, rights statement, donor/photographer limitations and exact scene/framing. A 960px **maximum**, no upscaling and output physical width >= painted CSS width × DPR are required; otherwise HOLD.
3. Only after rights/editor authorization, plan a reversible *staging-only* WordPress Media Library copy under a clearly credited filename, with old `src` recorded for rollback. Preserve accessible ALT/caption, original editorial scene and order. No blanket third-party mirroring or direct post-block mass replacement. Test `srcset`/`sizes` and LCP-vs-lazy behavior in staging before proposing any production change.
4. For P1 oversized originals, favor the five 1672×941 PNGs without generated subsizes (posts 34–38) **after** the six missing-image checks. Verify original creative rights, perceptual/label fidelity, 960×540 conditional exports and the actual image URL chosen by Jetpack. Vasa post 299 already uses transformed `fit=1024` URLs; it is **incorrect** to count its multi-megabyte stored originals as visitor bytes.
5. A 76% claim requires same-cohort before/after uncached browser `encodedDataLength` totals, preserving images and visual parity; report **100 × (sum(before bytes) − sum(after bytes)) / sum(before bytes)** across exactly the same 61 historical posts. Do not average per-post percentages and do not extrapolate that number to the newer 66-post cohort.

## Verification and release boundary

- Byte-bound verifier and its 12-case test file were run in **native Node, 12/12 PASS**, with local `git hash-object` values matching GitHub committed blobs.
- Existing updated 37-case P0 suite **37/37 PASS** in isolated V8 Node-style execution against exact GitHub readback, without real Chrome or native Node CI.
- All tests use **synthetic** fixture capture/screenshot/asset bytes. Site QA has not yet furnished a real visitor failure packet.
- Integration, independent screenshot decoding, authentic guest capture, licensing, GitHub CI and pixel-parity review remain required. No production-ready image or verified 76% result is asserted.
