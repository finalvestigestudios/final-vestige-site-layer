# Site-wide image source host-risk crosswalk — Nov 11, 2026 Pacific

## Boundary and source custody
This sprint is owned by FV Media Recovery, not the interim homepage-design lead. Reviewed `docs/IMAGE-WEIGHT-WORKLIST.md` in draft PR #183 (SHA `2acd06a4ca4317646006eb6591face3fe76fedec`) and Site QA PR #154 before working. The worklist does not live on `main`. The historical 61-post / 355-image / 288-offsite snapshot is intentionally separate from the later 66-post / 361-image live cohort.

Source register: `qa/media-recovery/coverage_288_exact_pr1703_20261110.json`, SHA `4965a862f7de7de46c1f4a1e26f3ca70a8c38805`. This release is a deterministic **offline reinterpretation of existing source URLs and archived web-retriever observations, NOT an actual visitor-browser audit**. It does not claim to have transferred or downloaded any images.

## New verified exposure batch
All **288 unique external-source positions** distribute across **80 upstream hosts**. The largest are:
- `commons.wikimedia.org` — **118** source positions (mostly Special:Redirect/file), across 20 posts.
- `upload.wikimedia.org` — **18** direct source positions, across 10 posts.
- `www.history.navy.mil` — **15** source positions, across 4 posts, with **12** unique archived retriever-wrapper 4xx/5xx warnings. Navy imagery may belong to donated collections.
Those three represent **151/288 = 52.43%** of external-source positions. This describes **shared-host exposure**, not proven concurrent outage, request cost, or public-page transfer volume.

**27/288 distinct positions** had an external *web retriever wrapper* 4xx/5xx somewhere in the frozen source evidence. They include P0 exact URLs, especially `285:5` and `287:5` (retriever 404), `418:1` and `418:2` (retriever 403), and `407:1` (retriever unsupported-binary 400). Do **NOT** relabel them actual origin HTTP, Chrome responses, failed decodes, or the historic **42 reported broken images**. The original 42 still lack an independently verified per-slot visitor-browser failure list. No measured proof for the proposed **76% network-byte reduction**.

**Two Jetpack proxy URLs** (`285:1` and `291:0`) have `i0.wp.com` delivery but third-party original hosts Squawkpoint and NARA's blog. Treat the original host as distinct from actual runtime delivery. The 286 vs 288 historical QA aggregate discrepancy remains unresolved; the present classifier already recognizes these as offsite.

### Ready-made Site QA batches, without a second collector
Use the existing PR #154 logged-out Chrome/full-scroll collector: first `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Record exact post/slot and frozen URL/ALT, resolved `currentSrc`, final requestId URL, uncached response status/MIME, body/decode dimensions, CSS size/DPR, actual transferred bytes and screenshot. Then sample the Navy 15 and the seven Florida Memory images, followed by Commons redirect clusters (118) on multiple different posts. Verify host siblings individually before calling a host-level outage. A visual comparison is essential: HTTP success alone is insufficient for a historically accurate photo.

For each browser-confirmed broken item: item-level archival record and license/credit; native dimensions; exact same-scene/crop comparison; staged uncached source versus candidate screenshots; rollback. Limit derivatives to `min(960,native_width)`, preserve aspect, provide full-size zoom for labels/maps and do not upscale at DPR2. No automatic mirroring. Navy's official [Photo Archives policy](https://www.history.navy.mil/our-collections/photography.html) notes official and donated collections and makes it the researcher's responsibility to obtain necessary clearances. Florida Memory, Coast Guard and archive-hosted files likewise need individual rights checks.

## Oversized WordPress assets, after P0
**15** originals exceed 1.5 decimal MB, totaling **47,096,779 stored original bytes**; eleven inline-referenced originals total **38,480,915 stored bytes**. Five inline PNGs in posts 34–38 have zero registered WordPress subsizes. This is not guest wire size and cannot prove a 76% improvement. Run baseline/candidate paired cold browser captures and visual parity checks before advertising savings.

## Reproducible artifacts (isolated draft #1703)
- `qa/media-recovery/upstream_host_risk_288_20261111.json`: all 80 host groups, all 288 slot IDs, exact example URL by host, 27 individually enumerated wrapper-warning URLs/status codes, all six P0 original URLs and existing replacement candidate catalogs, rights and conditional 960px values.
- `qa/media-recovery/validate_upstream_host_risk_288_20261111.cjs`: offline fail-closed 288-source conservation, URL/slot/host, warning wrapper, original candidate and rights assertions.
- `qa/media-recovery/test_upstream_host_risk_288_20261111.cjs`: 1 positive + 22 adversarial tests. **23/23 equivalent precommit pure V8 checks passed.** Committed Node suite, GitHub CI and actual browser tests have not been run; do not claim them.

No WordPress production writes, image downloads, caching, licensing assumptions, risky Gutenberg rewrites, homepage work, merges, deployments or subscription spend. Media Recovery PR #1703 remains draft.
