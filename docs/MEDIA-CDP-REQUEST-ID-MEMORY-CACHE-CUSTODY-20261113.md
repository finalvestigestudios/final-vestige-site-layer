# Media recovery — exact-CDP-request memory-cache integrity (13 Nov 2026 Pacific)

**Draft-only, isolated media code correction.** Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) remains owner of the logged-out Chrome collector and P0 queue. This change touches only the existing Media Recovery draft [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183); **do not merge #183 wholesale** (its overall diff spans unrelated work). No WordPress production writes, media binaries, homepage layout work, cache/rehost operations, deployments, merges, or paid services.

## Reproduced defect, corrected

The request-ID-scoped article-image transfer aggregator previously required `was_cached === false`, `from_disk_cache === false`, and `from_service_worker === false` but *omitted* `from_memory_cache === false`. With a synthetic, correctly bound CDP request ID and URL, an image result already labeled loaded, valid image MIME, and `encoded_data_length=5000`, an independently changed network row with `from_memory_cache:true` was counted as **5000 cold article bytes** and `complete:true`. That is a **test-induced integrity false positive**, not a real observed Final Vestige visitor transfer.

The revised aggregator requires all **four** cache-provenance fields explicitly false. Memory-cached **true** and missing/unknown both cause `article_bytes:null` / HOLD. This agrees with the existing Chrome collector and paired-wire comparison. It does not change the collector or its source classifier.

- Old exact core blob: `3c5b3cb50ac6d793415c232ad0df1898af8d9c04`.
- Corrected core blob: `dff2fc4738cd7ede48cd9dee905295839ebd4275`.
- Regression definitions: `0eb28fa99d02c225747240c891871b7884fdcbfe` (prior `c8af5f3ccae9fb4d0a9f8ad06847e82754629dfa`).
- **33/33** post-patch V8 unit checks passed using the *exact revised source* with test-only Node/assert and URL identity shims. **13/13** postcommit machine-audit integrity checks passed. Native Node, full repository CI, and actual guest Chrome **not executed** in this runner.

## Real six-source P0 queue — status distinctions

The companion [machine JSON](../qa/media-recovery/request_id_memory_cache_custody_20261113.json) preserves all six literal published image URLs, source-catalog lead, item-level copyright hold, 960px/no-upscale conditional sizing, and this sprint's external web-retriever wrappers:

| Image slot | Web-retriever wrapper only | Release |
|---|---:|---|
| Three Mile Island `285:5` | 404 | HOLD |
| Three Mile Island `285:2` | 500 inaccessible redirect | HOLD |
| Skyway `287:5` | 404 | HOLD |
| USCG portrait `418:1` | 403 | HOLD |
| Scotch Cap debris `418:2` | 403 | HOLD |
| Hebgen Lake `407:1` | 400 unsupported binary | HOLD |

**All six real origin HTTP statuses, logged-out browser statuses, currentSrc/pixel validity and encoded transfer bytes remain UNKNOWN**. Wrapper outcomes must never be promoted to visitor failures. The historical claim of **42 broken external images** remains guest-unverified.

Primary record / rights leads (not published or locally cached):
- [USCG Anthony Pettit portrait](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) identifies `210330-G-DE713-0002.JPG`, and explicitly notes public domain/cleared for release while reserving DoD image-use restrictions and credit. Native dimensions and exact published crop must still be checked.
- [USGS Hebgen fault scarp 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) and [alternate USGS catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) identify J. R. Stacy, public-domain source, and two official Original paths. These are catalog leads, not a verified binary match.
- [Florida Memory collision aftermath RC09236](https://www.floridamemory.com/items/show/32082) is an authoritative **different photograph**, subject/time appropriate only after an explicit editorial replacement decision; not an exact-image restoration of the [St. Pete Catalyst publisher photograph](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/), credited to University Press of Florida.
- UCS moved-publisher figure, Scotch Cap secondary-host copy, and SayMedia movie still have insufficient independent republication rights. **No unauthorized mirror/cache/download.**

## Visitor-first recovery / media derivative decision gate

1. Site QA #154's **existing** cold, logged-out browser collector must capture requestId, final `currentSrc`, image request and response MIME/status, complete transfer, the four cache provenance flags, DOM `naturalWidth/naturalHeight`, screenshots and scroll/viewport/DPR. The classifier must confirm an *actually visible* failed image before production remediation is considered.
2. A proposed archival replacement must preserve the **exact photograph and meaningful crop**, or carry an explicit and reviewed different-scene/period editorial caption. Establish source master, item rights, attribution, and intrinsic dimensions; do not assume Navy/USCG/NARA custody confers universal rights.
3. Any legally approved local copy or WordPress media variant is a **future staged proposal only**. Retain the source URL and original article markup as rollback reference. Maximum 960px wide **without upscale**; check CSS render width × DPR first (960 physical px supports at most 480 CSS px at DPR 2). Preserve captions, accessibility/ALT disclosure, maps and fine historical details.
4. To evaluate the quoted **76% reduction**, run matched cold before/after browser captures over the same verified post/slot/viewport cohort. Deduplicate by exact CDP request ID and sum eligible encoded transfer bytes, not WordPress original storage; compare `100*(baseline-candidate)/baseline`. A single lab pair is not sitewide field evidence.

## Frozen and expanded denominators

Historical reference **61 posts / 355 inline / 288 offsite** remains separate from later **66 posts / 361 inline** research. Fifteen WordPress originals exceed 1.5 **decimal** MB and total **47,096,779 stored bytes**; eleven used inline account for **38,480,915 stored bytes**. Their original file sizes do not establish visitor wire bytes or the asserted 76% reduction.

**Next move:** Use Site QA's unchanged six-slot queue for real cold visitor failures. If a broken image is established, choose the first exact-scene, independently rights-cleared asset for *reversible staging only*. Do not substitute different scenes silently.
