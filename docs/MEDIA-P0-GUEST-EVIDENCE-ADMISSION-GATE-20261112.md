# P0 guest-image evidence admission gate — 2026-11-12

**Scope:** Isolated Media Recovery draft PR #1703. Site QA #154 owns the sole logged-out Chrome/CDP collector. No browser duplication, live WordPress edits, uploads, third-party asset copying/caching, homepage design changes, merges, deployments, or spend.

## Verified offline defect and correction

The earlier source-readiness triage in validate_p0_primary_rights_scene_20261112.cjs can return STAGING_REVIEW_ONLY from a self-asserted BROWSER_CONFIRMED_BROKEN string, any 40-character purported evidence SHA, and scene/rights/editor booleans. This is a **synthetic trust-boundary weakness**, not a real browser failure or WordPress vulnerability. That softer status must not be used to stage assets by itself.

The new independent read-only p0_guest_evidence_release_gate_20261112.cjs accepts the six pinned original post, page and image URLs only. It requires a Site QA evidence packet with explicit cold guest CDP response and completion provenance, HTTP status, zero-positive-pixel coherence, full-scroll and cache controls, screenshots, and Git evidence pointers. A successful 200 plus decoded image returns GUEST_IMAGE_LOADED_KEEP_ORIGINAL. Missing or contradictory evidence is HOLD. Wrapper retriever codes are explicitly **not** visitor HTTP status. A Git SHA is only a locator until Site QA independently fetches and verifies its content.

For a coherently broken guest image, staging eligibility further requires an exact candidate catalog match, item-level reuse evidence and credit, asset SHA-256, verified same photograph **or** disclosed different-photo editorial alternative with revised ALT, staging/editor signoff, and no-upscale / aspect / CSS×DPR quality checks. The geometry gate rejects 960px output at 640 painted CSS px on a 2× screen. Every result retains production_write_allowed=false, wordpress_upload_allowed=false and third_party_cache_allowed=false.

## Original source mapping retained

| Frozen source slot | Current external image host | Existing candidate evidence | Restriction |
|---|---|---|---|
| 285:5 | images.saymedia-content.com | https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg | Candidate is 4:3, published source 16:9; 819px native limit |
| 285:2 | blog.ucsusa.org | https://www.si.edu/object/report-presidents-commission-accident-three-mile-island-need-change-legacy-tmi%3Asiris_sil_765655 | Retouched panel may differ from archival figure |
| 287:5 | stpetecatalyst.com | https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg | Same-publisher moved URL, permission and exact pixels unverified; Florida Memory alternatives are different photos |
| 418:1 | media.defense.gov | https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/ | USCG catalog accession matches filename, check credit/limits and bytes |
| 418:2 | www.history.uscg.mil | https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/ | Multiple distinct ruins scenes; rights and identity hold |
| 407:1 | d9-wret.s3.us-west-2.amazonaws.com | https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0 | USGS catalog identifies Stacy photo as public domain; actual image bytes unverified |

No real Site QA guest evidence packets were available at the time of this commit; all six visitor HTTP/decode statuses remain unknown. Previous independent web retrieval wrappers (404, 500, 404, 403, 403, 400) are **not actual origin HTTP or logged-out guest results**.

## Native regression and frozen scope

Run: node --test qa/media-recovery/test_p0_guest_evidence_release_gate_20261112.cjs

**26/26 native Node tests passed locally** on exact source and test Git blob contents before committing. These are synthetic evidence fixtures only; GitHub CI and real visitor Chromium remain unrun.

Frozen historical census: 61 posts, 355 images, 288 offsite. Newer 66 posts and 361 inline positions are separate. Historical 42 reportedly broken still guest-unconfirmed. The 15 WordPress originals >1.5 decimal MB total 47,096,779 stored original bytes; 11 published-inline matches total 38,480,915 stored bytes. A proposed 76% wire-byte reduction is not measured; use the prior 61-post cold CDP transfer aggregator before reporting any historical cohort metric.

**Next operational step:** Site QA #154's unchanged P0 browser queue 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Use the new admission gate only on authenticated evidence after readback, then prepare reversible rights-cleared staging proposals, never automatic live post rewrites.
