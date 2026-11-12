# Media Recovery: bounded PNG IDAT / scanline integrity gate (Nov 12, 2026 PT)

**Owner:** image restoration/performance only. **Draft PR #1703 only.** Site QA #154 owns the actual guest Chrome/CDP collector and six-slot P0 order; interim lead owns homepage visual design.

## Concrete failure mode and mitigation

The earlier byte-bound verifier checked PNG chunk CRC and IHDR geometry but **did not inflate IDAT**. A synthetic PNG with valid signature, IHDR, IDAT chunk CRC and IEND but nonsensical compressed image data therefore passed the PNG-shape function. A signed hash over corrupt bytes cannot establish that a screenshot or proposed replacement can decode. This could create a misleading staging-review packet; it was **not** a demonstrated live-site broken image.

New independent \`qa/media-recovery/png_decode_guard_20261112.cjs\` is now called by the existing \`verify_p0_review_evidence_20261112.cjs\` for BOTH screenshot and PNG candidate. It validates the full PNG chunk chain/CRC, valid bit-depth/color-type pairing, indexed palette existence, contiguous IDAT, bounded zlib inflation, expected scanline byte budget for noninterlaced and Adam7, and filter-byte values 0–4. Hard bounds: input <= 32 MiB; inflated scanlines <= 64 MiB. Corrupt deflate, truncated/extra scanlines, CRC mismatches and oversized decoded footprint cause **HOLD**. It never downloads, mirrors or changes media. **This is still not pixel-level visual review, full cross-format decoding, rights clearance or an authorization to replace any image.** JPEG/WebP remain structural metadata checks. A complete browser render/decoding and side-by-side scene/crop comparison remain mandatory.

## Native verification and boundaries

- 16 unit tests of the bounded PNG module, including control 1×1 source, multi-IDAT and Adam7; adversarial CRC-valid corrupt deflate, bad filters, mismatched row lengths, invalid palettes, unknown critical chunks, CRC, and decompression budget.
- 4 integration tests against \`verifyP0ReviewEvidence\` checking signed screenshot and signed candidate fail closed, while intact synthetic PNG permits only review with \`production_write_allowed:false\`, \`third_party_cache_allowed:false\`.
- Local native Node \`node --test\`: **20/20 pass**; local module SHA and test SHA matched GitHub blob hashes. Repository CI and actual logged-out guest browser were not run.

## Evidence and restoration priorities

The frozen October 30 cohort is **61 posts / 355 image tags (288 external positions)** with 42 *historically reported* broken externals, **zero current guest-browser failure verdicts supplied**. The newer 66-post/361-image cohort must be measured separately. The six-P0 queue stays: \`285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1\`. The existing machine ledger \`p0_and_oversize_attested_release_handoff_20261112.json\` pins exact original URLs and candidate catalog leads (Wikimedia Commons, Coast Guard, USGS, Florida Memory) with visitor HTTP statuses **null**; do not promote web-retriever 403/404 to origin results. Exact-photo identity, item-specific reproduction rights, credit, source dimensions, upscaling prohibition and maximum 960px width all remain mandatory; map fine-print must remain zoomable.

Fifteen >1,500,000-byte WordPress stored originals total **47,096,779 stored bytes**; 11 inline-matched originals across 8 posts total **38,480,915 stored bytes**. These are **not** transferred bytes; some are already served through Jetpack transformed URLs. A purported **76%** sitewide improvement is still unmeasured: compare matching **cold browser Image GET encodedDataLength** across all 61/355 historical source slots with before/after visual parity and CSS×DPR legibility. Missing cache/HTTP/slot evidence = HOLD, not estimated reduction.

## Reversible staging only, not an implementation authorization

After Site QA proves a specific broken original, review authoritative item-level catalog, image license and exact photo/crop; obtain allowed binary **only with documented permission**, verify decoded image, dimensions <=960px without upscaling and adequate DPR/label legibility, then prepare a WP media-library staging-only reference/attribution/rollback plan. Do not automatically rewrite Gutenberg blocks or publish a substitute historical scene. **No binary transfer, scraping, production WordPress write, homepage visual change, merge, deployment, or paid call performed in this sprint.**
