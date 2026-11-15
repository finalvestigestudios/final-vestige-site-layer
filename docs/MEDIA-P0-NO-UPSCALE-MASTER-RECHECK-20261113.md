# Media Recovery — six P0 retriever outcomes and source-master geometry preflight (2026-11-13 UTC)

## Ownership and source integrity

This is **Media Recovery draft PR #1703**, NOT Site QA's draft #154. Site QA keeps the sole guest Chromium/CDP collector and the P0 queue `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Interim lead owns homepage visual design. No WordPress writes or rewrites, asset downloads, mirroring, cache, deployment, merge, or spend.

Read `docs/IMAGE-WEIGHT-WORKLIST.md` from draft PR #183 at Git blob `2acd06a4ca4317646006eb6591face3fe76fedec` (not present in main or recovery branch). Preserve two distinct cohorts: frozen 61 posts/355 source tags and expanded 66 posts/361 source tags. The Site QA 286-versus-Recovery 288 external count is unresolved at the source-slot level (post 285 and post 291 differences); do not silently mix denominators.

## Fresh source-only recheck

The six **exact WordPress-original** URLs were reopened in an external web retriever on November 13, 2026 (not a logged-out Chromium session). Results below are **retriever-wrapper outcomes**, never verified origin HTTP or visitor browser statuses:

| P0 slot | Retriever outcome | Candidate next check |
|---|---|---|
| 285:5 | 404 | Commons Three Mile Island 2010 photograph is a different scene; no silent replacement |
| 285:2 | 500/inaccessible redirect | UCS blog migrated path; validate publisher identity and figure/copyright |
| 287:5 | 404 | Same-publisher `media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` **displayed** in retriever; exact pixel/crop and rights unverified |
| 418:1 | 403 | Official USCG item 2002905913 catalog/filename relationship; item copyright/credit and binary must be resolved |
| 418:2 | 403 | Coast Guard original vs Lighthousefriends same-basename image; no exact pixel identity or rehost permission |
| 407:1 | 400/unsupported octet-stream | USGS catalog-linked `.../thumbnails/image/img7535.jpg` **displayed**; item describes public-domain J. R. Stacy photo, binary equality unknown |

Evidence: `qa/media-recovery/p0_six_source_master_admission_20261113.json` Git blob `3a54fe6e1635d408b1069fc53d669b9ce2ae69e3`. Exact URL, candidate, code, uncertainty, 960px ceiling and HOLD are stored on each of six rows. 18/18 read-back integrity assertions passed; no local authenticated origin-browser capture was possible.

## New derivative-geometry safety preflight

`qa/media-recovery/verify_no_upscale_derivative_20261113.cjs` (Git blob `32860a42025f0dc18b2bf26b0d91d084fc38c959`) compares **supplied** master/derivative dimensions and insists that:

1. both records bind to the same declared source-master SHA-256 and item-level reuse-rights evidence;
2. derivative width is **no greater than 960 pixels**, and neither derivative dimension exceeds the original;
3. full-frame aspect ratio is preserved, allowing one-pixel rounding but holding a materially different crop; and
4. every outcome, including passing geometry, prohibits production writes and third-party caching.

This is a **metadata consistency preflight, not an image-byte verifier or license determination**. A passing `GEOMETRY_PRECHECK_PASS_NO_RELEASE` still has `master_artifact_bytes_verified_here:false` and `image_scene_identity_verified:false`. A future caller must validate the actual authorized source-master raster bytes and SHA-256, candidate raster bytes and SHA-256, decoded dimensions, item-level permissions, credit, screenshots, editor sign-off and guest/CDP failures **separately**. It must not treat declarations alone as authority for WordPress or caching.

Native Node v22.16.0: `node --test qa/media-recovery/test_no_upscale_derivative_20261113.cjs` **15/15 pass** (test blob `57d8698e3cccf2e106f14b3391b16ad8e6620917`), including 961px width, native 819px photo falsely enlarged to 960px, height-only upscale, altered crops, bad digests and missing rights assertions. This helper is isolated and **not yet wired into existing staging/release processes**. It does not change the behavior of the existing P0 byte-integrity validator; integration and genuine browser test remain separate future QA work.

## Visitor proof / rights / rollback

Before any replacement: Site QA's existing collector must provide exact rendered `currentSrc`, response URL/redirect chain, uncached network status and MIME, requestId, decoded natural width and height, screenshot PNG bytes/sha, rendered CSS geometry and DPR, and genuinely failed `<img>` evidence. Only then decide whether to retain original, use an authorized same-scene canonical publisher URL, or request item-cleared WordPress media with a maximum 960px no-upscale derivative (and full-resolution zoom for maps/figures). Record captions and alt accuracy, then test in staging with reversible mapping and editor approval; no direct bulk Gutenberg block rewrites.

The historical **42** reported broken original-source positions are not yet guest-confirmed. The headline **76%** reduction is **not measured**: compute it only from actual paired uncached CDN/guest CDP image transfer bytes over the same post cohort and content, not from stored originals or requested resize parameters. The 15 WordPress originals over 1.5 **decimal** MB total **47,096,779 stored bytes**. Larger originals with transformed Jetpack `fit=1024` URLs are not equivalent to visitor transfer; missing WordPress subsizes on five 1672×941 reconstruction PNGs also require displayed CSS width × DPR checks before a proposed 960px derivative.

## Release state

All six original-source statuses remain guest-null, rights and exact binary equality unverified; six HOLD. Two corresponding candidate sources displayed in web retriever, not in verified visitor Chrome. No replacements staged, cached, uploaded, merged or deployed. Continue Site QA #154, do not duplicate its draft or collector.
