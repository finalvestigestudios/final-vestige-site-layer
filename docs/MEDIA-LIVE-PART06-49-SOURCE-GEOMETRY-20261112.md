# Part06: last third of the frozen 61-post media census — verified source-only audit

Date: 2026-11-12 (Pacific). Owner: Media Recovery, isolated draft PR #1703. Corresponding frozen inventory: PR #183 `qa/media-recovery/parts/06.json` Git blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`. Historical source research: PR #1703 `coverage_288_exact_pr1703_20261110.json` blob `4965a862f7de7de46c1f4a1e26f3ca70a8c38805`. Worklist `docs/IMAGE-WEIGHT-WORKLIST.md` was found in draft PR #183 (blob `2acd06a4ca4317646006eb6591face3fe76fedec`), not on main.

## Fresh, read-only evidence

Authenticated WordPress edit-context `posts_get` of published posts 218, 217, 216, 215, 214, 213, 211 and 190 yielded **49 inline image tags**. Original 2026-10-30 image source URLs match **49/49**, and ALT attributes match **49/49**; no slots added or removed. **43/49 lack both HTML width and height**; 6/49 have both; zero partial pairs, zero literal `srcset`. All 49 are offsite: 28 Wikimedia Commons redirect URLs and 21 other external URLs. All 49 retain historical provenance/candidate records; **24 have a conditional ≤960px dimension lead**, not a license to generate or upload. The machine audit preserves exact published URLs and reference provenance. Source markup cannot confirm browser loading, layout shift, origin HTTP codes, cache behavior or transferred bytes.

## Priority and release gates

Site QA PR #154 owns the existing *single* logged-out Chrome/CDP collector. Its P0 queue remains `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Do not create a second collector or change homepage appearance. Next assess this Part06 subset only after the P0 queue. For each candidate confirm image URL and final noncached request chain, status, MIME, decoded dimensions, currentSrc, CSS display width × DPR, and transferred bytes. Distinguish transient retriever wrapper errors from real guest failures.

Every replacement remains HOLD until individually checked for (1) same historical scene/crop/pixels, (2) authoritative archive provenance and donor/contractor copyright restrictions, (3) attribution, (4) native dimensions and text legibility, (5) no upscaling and an appropriate ≤960px responsive derivative *only when it suffices*, and (6) editor approval. Stage candidates in a private, rollback-capable media manifest, preserving the original URL, ALT, caption, and a checksum; never hotlink-remap or rewrite published Gutenberg blocks by automation. None has been downloaded, cached, or rehosted.

## Performance measurement

The reported **76% saving** needs matched *cold* baseline/candidate browser measurements of **actual transferred image bytes** on the same cohort, viewport, DPR, cache disabled, comparable content and same source identity, plus decoded-image quality review. WordPress **15 originals >1.5 decimal MB sum to 47,096,779 stored bytes**; these storage sizes do not establish visitor traffic or achievable savings. 11 such originals are inline matched across eight published posts; the remaining four may appear outside post-body images. Preserve text/legend legibility in maps/figures and offer original resolution when justified.

## QA execution

Run `node qa/media-recovery/validate_live_part06_49_20261112.cjs` and `node --test qa/media-recovery/test_live_part06_49_20261112.cjs` on this PR's checkout. The validator enforces frozen source registry identity, source/ALT equality, slot and cohort binding, copyright holds, 960px cap, and forbids fabricated guest-status/wire measurements or release permissions. Native CI/guest browser verification remains pending until executed. **No WordPress writes, third-party image binaries, homepage modifications, PR merges, deployments, or subscription spend.**
