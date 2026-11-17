# Media Recovery: fail-closed output staging path (2026-11-04, nonproduction)

**Scope:** QA/media recovery draft PR #183 only. Homepage visual design belongs to the interim lead; Site QA #154 retains visitor Chrome/browser failure testing. No archive downloads, original media bytes, publisher image copies, WordPress production operations, third-party subscriptions or homepage edits in this change.

## Verified safety defect

The existing offline five-hero WebP derivative builder `qa/media-recovery/prepare_hero_derivatives.py` evaluated `target_root = Path(output_dir).resolve()` and *then* checked `target_root.is_symlink()`. `resolve()` follows an existing output symlink, so the symlink test was ineffective: an output path pointing to an otherwise permitted sibling directory could be accepted and local staged files written to a different-than-requested location. This does not establish a production compromise; it is a concrete local staging integrity issue.

The revised `validated_output_root()` checks the **requested absolute output path and every ancestor for symlinks before resolving**, and then preserves the existing rule excluding the originals folder and its descendants. It runs before image encoding or staged file creation. The builder still requires original SHA-256 match, explicit per-item rights self-attestation, image geometry and bounded 960px/no-upscale output, visual review, and a no-overwrite staging path. This guard is designed for controlled local batch processing; it is *not* an adversarial filesystem sandbox against concurrent symlink swaps (TOCTOU).

## Exact code and tests

- Changed existing builder: `qa/media-recovery/prepare_hero_derivatives.py` — commit `7a9dcfae680a0467741df0a837a956acd84e6f0a` (new file blob `692d103b5c0fff3c1b07c7f4bceda2b918cbaedc`).
- New repository regression: `qa/media-recovery/test_staging_output_root_20261104.py` — commit `6de1ef6f07832b1c99abb7bde62cfba3b72086f5`.
- Six focused filesystem cases: legitimate sibling folder allowed, source folder itself blocked, source descendant blocked, symlinked destination blocked, symlinked ancestor blocked, symlink back into source blocked. Assertions require no staging directory created in a refused scenario.
- **Executed six local native Python tests against a manually reproduced, byte-matching guard function: 6/6 pass**. The complete checked-out repository/Pillow integration suite was **not** available locally; the new committed unittest still requires native run and CI.
- Recommended native test command from repository root: `python -m unittest discover -s qa/media-recovery -p 'test_staging_output_root_20261104.py' -v`, then `python -m unittest discover -s qa/media-recovery -p 'test_prepare_hero_derivatives.py' -v`. Neither command accesses the website.

## Original five-image batch remains on hold

Five documented live first-party PNG reconstructions in posts **34–38**, media IDs **39–43**, total **13,267,538 original stored bytes**, are `1672×941`, reported with zero WordPress subsizes, and are candidates for **960×540 no-upscale WebP** only after rights/generator-term confirmation and visual QA. Source detail: `qa/media-recovery/five_png_no_subsizes_live_wp_20261103.json`. These original file sizes are not measured visitor transfer bytes, and currentSrc/actual Chrome network bytes remain unknown.

This change does **not** process those images. No media binary was downloaded, transformed, saved or staged; no site content changed. Derivative output remains gated on real licensed originals and per-item approvals.

## Independent P0 missing-image evidence (not conflated with this safety fix)

Existing priority remains Site QA #154's guest-browser sequence: **285:5, 285:2, 287:5, 418:1/2, 407:1**. A fresh independent web retriever check on November 4 again produced a wrapper-level **404** for `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` while successfully displaying `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`. This is source-host migration evidence, **not** visitor browser or publisher-origin HTTP proof, and not a reuse license. Exact binary identity, credit and rights are HOLD. Do not mirror or silently rewrite ALT; the published 1980 wreckage description also requires editorial review.

## Measurement and release gates

Pinned historical baseline: **61 published articles, 355 image slots, 288 offsite-origin refs on Media PR #183 inventory, 13 WordPress originals over 1.5MiB totaling 43,522,829 stored bytes**. Site QA #154 reports 286 offsite refs under its different classifier. Both counts are source-only. The founder-reported **42 broken** images are not verified visitor failures, and **76% image-weight reduction is not measured in paired actual browser transferred bytes**. Production repairs: **0**.

Before any local derivative is uploaded: rights/ownership and historical-image identity check; source hash verification; output visual QA and color/ICC review; proportional ≤960px no-upscale derivative; explicit staging review; real logged-out desktop/mobile GET/response/decode/CLS and byte measurements; editorial approval and rollback. This draft does not grant publication permission.

**Handoff:** Site QA #154 keeps the P0 browser runner and drafts; media recovery retains offline derivative correctness and rights/identity/960px release gates. No duplicated QA draft changes.
