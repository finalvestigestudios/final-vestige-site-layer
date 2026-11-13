# Media Recovery — byte-bound JPEG/WebP full-raster review preflight (2026-11-13 PT)

## Scope and concrete engineering change

Draft PR #1703 only. No WordPress post/media writes, homepage design changes, downloads, scraping, cache or production releases.

Prior `verify_p0_review_evidence_20261112.cjs` accepted only PNG for the already restricted staging-review step, because JPEG SOF and WebP VP8X headers do not establish that an image actually decodes. The existing fake 25-byte JPEG / 30-byte WebP regression remains denied. This sprint adds `verify_image_pixels_pillow_20261113.cjs` and **wires it into both** (1) candidate derivative bytes and (2) rights-bound original source-master bytes.

- Local Python 3 + Pillow (tested here with Python and Pillow **12.3.0**) is an **optional review-machine dependency**, not a new web service, runtime CDN, WordPress plugin or paid subscription. When absent/failed, decoder returns null and the existing named `CANDIDATE_FULL_RASTER_DECODE_REQUIRED` or `SOURCE_MASTER_FULL_RASTER_DECODE_REQUIRED` HOLD continues.
- Node sends only already-supplied candidate bytes to `python3 -I -B -c` via `spawnSync`, **no shell, URL handling or filename argument**. Python reads stdin in memory only and loads the **complete** JPEG/WebP raster using Pillow, with truncation disabled.
- Caps: 32 MiB input, 40,000,000 pixels, 5-second subprocess timeout, output <=4 KiB, on POSIX a 3-second CPU/768 MiB address-space limit and zero-sized file output; EXIF orientations other than 1, animated WebP, malformed/truncated files or metadata/decoded geometry disagreement all HOLD.
- Cross-check decoded `{width,height,format}` against structural JPEG/WebP parsing and against the declared source-master/derivative dimensions. Existing rights SHA-256 binding, PNG integrity gate, 960px maximum width, never-upscale, aspect/crop guard, DPR and editor/guest evidence gates remain unchanged. These are eligibility checks for an isolated **staging-review packet**, never permissions to cache, upload, or publish.
- Pillow's decoder is a native dependency: keep this offline, use only approved locally supplied images, update Pillow through normal maintained environments, and run in a sandbox for untrusted media. Image decompression does not establish visual scene identity or copyright permission.

## Verification and limitations

- **Executed locally in native Node v22.16.0:** 11/11 isolated full-raster decoder tests PASS using *synthetic, locally generated* 2×1 JPEG and WebP pixels plus header-forgery, truncation, unsupported formats, oversized input, missing Python executable and non-Buffer negative controls. The tested decoder source was Git blob-identical to the new committed decoder. No third-party image binary was obtained.
- Added 10 integration regressions covering both source-master and derivative/candidate paths, valid synthetic JPEG/WebP, bogus geometry, EXIF rotation, truncation and missing decoder. **Native execution of this integration suite and repository CI remain outstanding** (and positive tests skip when Pillow is unavailable). Earlier 18/18 Node master/adversarial tests ran in prior sprint, but have not been replayed on this new HEAD.
- Prior 42 alleged broken originals are **not** 42 verified browser failures: Site QA PR #154 retains the only logged-out CDP collector and queue `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. No new origin HTTP response, `naturalWidth`, `currentSrc`, screenshot-byte or actual network transfer evidence was captured in this sprint.
- Historical research baseline: 61 posts / 355 image slots, 288 recovery-classified external references (QA #154 snapshot counts 286; per-post discrepancies at 285 and 291 await source-slot reconciliation). Expansion to 66 posts / 361 tags is a distinct later cohort and must not be conflated.
- Oversized WordPress baseline: **15 originals >1,500,000 decimal bytes, 47,096,779 stored bytes**; 11 inline referenced in 8 posts, 38,480,915 **stored** bytes. Vasa already uses Jetpack variants; do not count originals as visitor transfer. Proposed **76% transferred-byte saving remains unmeasured**. A legitimate claim requires same URLs and content/source scene, cold logged-out before/after, `encodedDataLength`, media mime/status, no service-worker/disk/memory cache, image decoded, and layout parity.

## Source/copyright/derivative HOLDs

Existing machine-readable six-P0 audit and 288-slot mapping remain canonical; do not duplicate, silently rename or repurpose those source URLs. Research candidates include official USCG Scotch Cap catalog, USGS Hebgen Lake catalog, and Florida Memory's five Sunshine Skyway chronology photographs; the Florida Memory alternatives are **different scenes**. Navy NHHC private-donation and University Press of Florida items require **item-specific reuse authorization**; a government-hosted URL or catalog credit alone is insufficient. A conditional derivative must not exceed **960px width**, must not upscale, and must preserve full-frame identity, legible maps/captions and correct ALT chronology.

## Release handoff

1. Site QA #154 obtains actual logged-out visitor evidence for the existing six images, without editing its collector to satisfy this sprint.
2. For a genuinely failed original, editorial review verifies original/candidate scene and permissions, records exact source-master binary and candidate SHA-256, legal credit, native geometry and target CSS×DPR.
3. Run the integrated local preflight in a maintained Python/Pillow review environment and confirm screenshot pixel/scene parity; **stage only through independent authorization**, preserve reversible WordPress source and rollback plan.
4. After an independent cold Chrome before/after, compare actual transfer and layout stability. Nothing in this PR authorizes production edits or 76% claims.

Read-only code and tests only; no external image binaries, rehosting, WordPress writes, page-block rewrites, homepage work, deployment, merge or spend.
