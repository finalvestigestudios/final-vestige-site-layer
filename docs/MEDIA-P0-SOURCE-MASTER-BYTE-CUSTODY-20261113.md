# P0 source-master byte custody at final staging-review intake — 2026-11-13

## Verified gap and change

The existing P0 intake required a SHA-bound *candidate derivative* plus a rights-review document but relied on caller-supplied `review.geometry.native_width/native_height`. An otherwise fully claimed review could specify an invented large master and make an upscaled derivative appear acceptable. The metadata-only 960px preflight added earlier did not cure this custody gap because it was not wired into the P0 admission path.

This change **connects an actual candidate source-master byte buffer** to the existing P0 review intake, and requires source-master SHA-256 equality in review and the existing SHA-bound rights document, explicit original-master reuse rights, declared source-master provenance, and native dimensions obtained from the supplied master bytes. After that it enforces <=960px width, no upscaling, and full-frame aspect consistency. The existing derivative/screenshot hash and source-slot evidence rules remain unchanged.

* Scope: `qa/media-recovery/verify_p0_review_evidence_20261112.cjs` and `qa/media-recovery/p0_guest_evidence_release_gate_20261112.cjs`, plus new focused Node regressions.
* SHA-bound master is the **approved archival/publisher source master for the candidate**, not the already failing offsite published URL. It is mandatory for the final `STAGING_REVIEW_PACKET_ELIGIBLE_NO_WRITE` path; missing bytes now stay `BYTE_BOUND_SOURCE_MASTER_REQUIRED`.
* PNG receives deflate/scanline decode checking through the existing PNG verifier. JPEG and WebP only receive container/geometry inspection; the returned `source_master_raster_decode_verified:false` explicitly prevents claiming decoded-pixel proof for them. Full raster decode, scene/crop comparison, screenshot review and rights/legal assessment remain mandatory separate gates.
* A review packet is **not** authorization to cache, scrape, mirror, upload, edit WordPress, merge or deploy.

## Source and performance custody

Source-of-truth worklist: draft PR #183 `docs/IMAGE-WEIGHT-WORKLIST.md`, blob `2acd06a4ca4317646006eb6591face3fe76fedec` (not on main). Historical source cohort: 61 posts / 355 image slots / 288 offsite by Media Recovery, 286 by Site QA #154 (two post-level differences unresolved). Six original P0 URLs and dated web-retriever-only observations are in `qa/media-recovery/p0_six_source_master_admission_20261113.json` (blob `3a54fe6e1635d408b1069fc53d669b9ce2ae69e3`). Retrievers yielded 404/500/404/403/403/400 in order, **not** independently authenticated origin or guest-browser HTTP responses. Site QA retains exclusive logged-out Chrome/CDP collector and unchanged six-source order.

Primary-source leads: USGS official Hebgen Lake catalog (https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) marks J. R. Stacy's image public domain and links a different image path; U.S. Coast Guard Scotch Cap portrait catalog (https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) describes release and credit conditions. Neither is a binary-identity or WordPress caching permit. Publisher-moved Skyway image remains rights/scene HOLD. Florida Memory alternatives are different historical scenes, not identical replacements.

**No visitor-visible failure has been confirmed for any of the 42 historical suspects.** Claimed 76% transferred-image saving remains unmeasured. Fifteen >1.5 decimal MB WordPress originals are 47,096,779 *stored* bytes, not on-wire transfer. The five no-subsize reconstruction PNGs may display at CSS width 1024px; DPR/legibility testing is required before 960px derivative use.

## Validation and handoff

`test_p0_source_master_byte_binding_20261113.cjs` contains twelve focused positive/adversarial native Node test cases on real signed miniature PNG bytes. The end-to-end repository gate and logged-out guest Chrome remain outside this test scope. Verify test execution on exact commit before promotion. No Site QA collector change and no production change. Any item-level media derivatives require rights clearance, independent visual parity and reversible staging-only plan.
