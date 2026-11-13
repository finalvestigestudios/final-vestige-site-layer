# Media Recovery — P0 cache-provenance false-positive correction (2026-11-13)

**Status: DRAFT / QA ONLY. DO NOT MERGE, DEPLOY OR WRITE WORDPRESS.**
This file documents a reproduced defect in the separate Media Recovery *evidence-intake gate*, not a finding that FinalVestige.com has broken images. Site QA #154 continues to own the sole logged-out Chrome/CDP collector.

## Defect, reproduced before patch

At prior Git blob `a54957ecafd83814668b85fd0f6ef01e50ae78c0`, `adjudicateP0()` correctly required `cache_disabled === true`, `from_disk_cache === false`, `from_memory_cache === false` and `from_service_worker === false`, **but did not check `guest.was_cached`**. A synthetic, otherwise consistent P0 `418:1` HTTP 404 / zero-pixel record could set `was_cached: true` or omit that field and still enter `GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED`. This is a misleading cache-ambiguous failure observation even though the function does not approve WordPress publication. No real guest response or outage was used to reproduce this defect.

## Fix and verification

The intake gate now **requires `guest.was_cached === false`** in addition to the original three negative cache-origin flags and `cache_disabled: true`. Unknown, null and true values fail closed as `HOLD: MISSING_OR_UNBOUND_ACTUAL_GUEST_CDP_EVIDENCE`. Existing valid synthetic cold-failure and cold-loaded flows remain unchanged.

- Updated intake gate Git blob: `2172e9134b1185a8d4232d96fd8f8fac2b39ac57`.
- Updated regression Git blob: `99a695847fc7677f80f17d42e53bced0b663d186`.
- **41/41** regression definitions ran successfully against the exact committed JS files in an isolated V8 runner using minimal Node assertion/test shims. The four additional cases cover cached 404, missing/null cache field, and cached-decoded 200 incorrectly classified as an original-source success. They are synthetic controls, **not real browser-image measurements**. Native Node execution of this newly modified suite, repository CI, guest Chrome/CDP and independent security review remain outstanding.
- Exact six-source read-only audit: [p0_uncached_provenance_six_status_20261113.json](../qa/media-recovery/p0_uncached_provenance_six_status_20261113.json); blob `a0745f41acc203da851914ff193f70015e191f6d`. Its six original URLs and wrapper observations are pinned to prior provenance blob `b489e23e7c68084660dd3c4a89caa788c1770b85`. All actual guest/origin response statuses, pixels, cold transfer bytes, binary hashes and conditional derivative dimensions are **null**, not guessed.

## Site QA #154 evidence contract

Site QA's existing P0 verification order remains **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. A future packet must attach an intact logged-out Chrome request/redirect chain and explicitly proven `was_cached:false`, `from_disk_cache:false`, `from_memory_cache:false`, `from_service_worker:false`, `cache_disabled:true`, network request ID, response status/MIME, currentSrc, page/full-scroll coverage, decoded natural size, DPR and screenshot digest. The collector must **not synthesize a false flag for missing events**; incomplete evidence remains HOLD. The intake function accepts claimed SHA strings only as pointers and independently fetched evidence must still be verified by Site QA.

Two P0 catalog matches are **preserve-by-default**, not image fixes: post `407:1` is linked as *Original* by the [USGS Hebgen Lake catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0), credited to J. R. Stacy and described as public domain; post `418:1` matches the official [Coast Guard Anthony Pettit portrait catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) by VIRIN `210330-G-DE713-0002.JPG` and published media URL. Neither establishes visitor success, original binary identity or WordPress-cache permission. The Coast Guard item's public-domain/release statement requests attribution and references DoD image-use limitations. The secondary `418:2` same-basename image at Lighthousefriends remains a photo/rights review HOLD. Where a confirmed failure exists, prefer the same historical photograph, not unmarked new imagery.

## 960px, permissions, and wire-weight gate

An archival candidate must pass item-specific licensing/reuse, credit, scene and crop review, actual source-master raster/hash/dimensions, no upscaling, at most 960px output width, relevant CSS × DPR geometry and caption/figure legibility, followed by a reversible *nonproduction* proposal. A published original's stored URL alone is not proof of the exact pixels served through runtime rewriting. No unlicensed copies, downloads or caching are authorized.

The frozen baseline is **61 published posts / 355 inline image slots / 288 source-classified external positions**; the 42 historically reported failures remain **guest-unconfirmed**. The 15 WordPress original attachments larger than 1,500,000 bytes total **47,096,779 stored bytes**; 11 are inline-matched in the expanded 66-post census (38,480,915 **stored** bytes). These are *not transferred image bytes*. A reported **76% reduction** requires complete, identically configured, uncached before/after visitor captures with strict CDP image-request mapping, same frozen source slots, screenshot and ALT/scene parity, and measured transferred bytes; no such claim is presently supported.

**Safety:** 0 WordPress post/media/plugin writes, 0 media binaries downloaded or mirrored, 0 homepage visual changes, 0 competing Site QA collectors, 0 merges/deployments, $0 subscription spending.
