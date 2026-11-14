# P0 407:1 — source/rights/guest-evidence schema hardening (2026-11-13)

**Draft only; no WordPress, media, homepage, merge, deployment or billing changes.** This supplements PR #1655; Site QA #154 owns the existing cold Chrome collector. Existing worklist: `docs/IMAGE-WEIGHT-WORKLIST.md` in draft #183, blob `2acd06a4ca4317646006eb6591face3fe76fedec`.

## Concrete defect and correction

Prior validator [`qa/media-recovery/validate_usgs_407_dual_original_20261113.cjs`](../qa/media-recovery/validate_usgs_407_dual_original_20261113.cjs) approved the unchanged positive audit but also accepted **20 of 20 independent synthetic tampering cases**, including public-domain assertion=false, a conflicting new caching-authorization field, fabricated alternate browser pixels, the wrong FV post URL, and an invented alternate retriever 404. These were false acceptances of **machine-readable evidence**, NOT observations of the live website. The corrected module locks exact field sets for the root and all eight nested records, source post identity, date, caption, USGS catalog and rights citations, still enforces unknown guest HTTP/bytes and bans writes/caching. **38/38 isolated V8 regression checks passed**, combining 18 pre-existing and 20 new cases; native Node, CI and guest browser were not run.

## What the original URLs actually establish

- Published post: https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/
- Published image: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg
- Same USGS catalog Original link: https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0
- Alternate official USGS catalog: https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959
- Alternate catalog image link: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg

The published original produced an external **web retriever wrapper 400 (unsupported binary)**. The alternate rendered in that retriever. Neither constitutes a guest-origin 400/404, successful page load, license release or proof of identical bytes/pixels/crop. Item catalog identifies a **Public Domain** USGS photograph by **J. R. Stacy**. Maintain a separate rehosting/credit and historical-image review before any local copy.

## Release gates / performance

Site QA should preserve the original six-P0 order and supply uncached Chrome CDP request ID, `currentSrc`, real final status/MIME, failed loads / `naturalWidth`×`naturalHeight`, all four negative cache flags, encoded transfer bytes and desktop/mobile screenshot. On confirmed failure, compare *exact visual scene*, photographer/credit and original/candidate crops and inspect native image pixels. A derived responsive file is capped at **min(960 px, native width)**, never upscaled; ensure CSS rendered width × DPR fits and preserve map/photo detail. Only after item-rights review should an authorized editor consider a reversible *staging* WordPress media attachment with a rollback map; no post block auto-rewrites.

The historical 61-post/355-inline inventory, **42 unverified** alleged broken images, **15** WordPress originals >1.5 decimal MB (**47,096,779 stored bytes**) and proposed **76%** byte reduction remain separate, unverified baselines. Actual transfer reduction requires the **same uncached cohort**, matched CDP requests, total encoded baseline versus candidate bytes and visual parity; storage size is not network transfer.

[Machine-readable mutation result](../qa/media-recovery/usgs_407_rights_status_schema_hardening_20261113.json). Source and test blob IDs and exact commit are recorded in the PR conversation after committing.
