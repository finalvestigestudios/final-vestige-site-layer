# Scotch Cap 418 — complete six-slot source recovery and correctness review (2026-11-03)

Read-only archival engineering for [published investigation](https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/) on isolated Media Recovery draft PR #183; **not a production fix**. Source/ALT identities come from SHA-pinned October 30 `qa/media-recovery/parts/01.json` blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`; the worklist reports a prior November 3 live CMS six-slot check, not repeated here.

## New cross-transport evidence

All six **exact published URLs** are recorded in [machine ledger](../qa/media-recovery/scotch_418_six_slot_verified_transport_20261103.json). On Nov 3, independent viewer **displayed original 418:4 Hawaii Magazine photo** and **418:5 USGS styled image**. Both are positive evidence of retrievability through that viewer, **not Chrome or final HTTP 200**. USCG 418:1 and 418:2 produced `web.open` wrapper 403; **418:1 nevertheless displayed in image search**. Original USCG 418:0 and 418:3 text retrieval did not yield numeric origin status. **Zero actual visitor-browser failures verified.** Do not count 403 wrappers as origin failures or declare the whole post broken.

## Four institutional same-scene recovery paths — NOT replacement approval

* **418:0** — National Coast Guard Museum's [winter old/new lighthouse photo](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/), linked **600×480**; before 1946, distinct from post-1950 replacement light.
* **418:1** — [Coast Guard photo gallery](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) identifies the exact portrait photo ID **210330-G-DE713-0002.JPG**, describes public-domain clearance and DoD use/credit limitations. The USCG photo caption uses **Anthony Pettit**, while the same historian's [museum article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) casualty list uses **Anthony L. Petit**; spelling **editorial HOLD**, no automatic correction.
* **418:2** — Museum's corresponding [debris2](https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg) thumbnail **600×463**.
* **418:3** — Museum's corresponding [remains](https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/6_-Scotch-Cap-remains-e1728394850930-600x474.jpg) thumbnail **600×474**. Both show matching historical subject and filenames but lack verified source-binary/crop equivalence. Museum credits USCG. Item-level reuse and visual checks remain mandatory.

The **exact published 418:4 image presently displays in independent viewer**; replacement would be needless without real browser failure. The [NOAA historical photo library](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg) describes a related 1946 man-on-pier scene, **not proven the same photograph**; publisher image rights remain unknown.

For **418:5**, the independent viewer displayed the exact [USGS styled source](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz), while the official [USGS catalog](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) links an unstyled original with the **same filename** and labels usage Public Domain. USGS says the photographer/source is **unknown**: do not overstate rights or blindly cache without item review.

**Provenance trap:** NOAA Ocean Exploration's separate [Scotch Cap Lighthouse Debris page](https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-features-geology-media-lighthouse-debris/) calls the destruction a **1964** tsunami, conflicting with the April 1, **1946** Coast Guard record. That NOAA page/photo must **not** silently become an illustration of the wrong year.

## Stage-only, no-cost plan

Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns cold logged-out desktop/mobile browser and lazy-scroll evidence at 418:1/2 first, then 418:0/3, while 418:4/5 serve as expected-working controls. Capture `src/currentSrc`, final request/redirect, numeric HTTP+image MIME, naturalWidth/Height, `decode()`, screenshot and complete image-type CDP encoded bytes. Flag 200 HTML, HTTP errors, bad decode and wrong-scene loaded photos distinctly.

For a **confirmed broken visitor image only**, visually compare source and official candidate, resolve per-item credits/license and exact historical scene; derive **≤960px wide, original aspect, never upscale** (museum versions remain 600px), optionally stage private optimized WebP/AVIF and JPEG fallback on WordPress after separate authorization, retain ALT/caption and original URLs for rollback, conduct mobile/desktop screenshot QA and 3 paired cold-transfer captures before release. No original images downloaded/copied, no binary dimensions or bytes invented, no CMS changes or costs.

Site baseline **61 published investigations / 355 stored image slots / 288 external origin refs / 13 over-1.5MiB original WordPress assets** is older inventory, not fresh guest measurements. Reported **42 broken** and **76% transfer reduction** both remain unverified. **0 production repairs.**
