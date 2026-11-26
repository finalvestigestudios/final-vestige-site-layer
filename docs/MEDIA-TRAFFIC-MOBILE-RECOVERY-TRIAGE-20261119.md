# Final Vestige Media Recovery: traffic-informed article image triage
**Evidence date:** November 19, 2026. **Traffic window:** October 20–November 18, 2026, site-local time. **Owner:** Media Recovery (article image reliability/performance, not homepage design). **Delivery:** isolated draft PR #2747; Site QA PR #154 retains the existing logged-out mobile/desktop collector.

## Verified traffic and exposure
Connected WordPress Jetpack Stats independently reported **38 browser page views** to Piri Reis #1917, **33** to Mesmerism #1924, **29** to Malbone #621, **27** to Antikythera #254, **20** to Lycurgus Cup #1920, **17** to Courrières #425 and **17** to Apollo 1 #434 in the 30-day window. These are views, **not proven arrivals from Claude's videos**. Stats referrers: Facebook **5**, YouTube **1**; the tagged Facebook organic-social bucket **1** with per-landing child read unavailable, so the exact campaign landing is UNKNOWN. Do not attribute those page totals to a campaign.

The machine-readable crosswalk [campaign_landing_media_triage_20261119.json](../qa/media-recovery/campaign_landing_media_triage_20261119.json) joins the **actual article URL, 30-day views, offsite/Jetpack image-slot counts, missing dimension/srcset flags, individual publisher-only HTTP 404 observations, oversized WordPress stored originals, six archival leads and explicit NULL desktop/mobile outcomes**. Its source of image records is the November 17 66-post/361-image snapshot, blob 9c9966be78d4e4abe7ec5bc9826ce56fbad8a1a0, not a fresh live browser capture. The October 30 61-post/355-image baseline remains a different cohort. The archived worklist docs/IMAGE-WEIGHT-WORKLIST.md was read from branch qa/media-recovery-reviewed-20261030-1158 at blob 71280920640a00551b4d2c2b54fa0f95e33030b8.

| Traffic/article priority | Specific source/layout issue | Recommended existing Site QA check |
| --- | --- | --- |
| P0 Tang #274 (8 views) | War History Online original 274:6 returned publisher-retriever HTTP 404 on Nov 18; same source is article OG image | Current guest inline and social-card image GET/MIME/decode, mobile screenshot; distinguish Jetpack cache |
| P0 Three Mile Island #285 (8 views) | SayMedia original 285:5 returned publisher-retriever HTTP 404; no exact rights-cleared replacement | Verify actual Jetpack/currentSrc visitor failure before any repair |
| P0 Skyway #287 (12 views) | St. Pete Catalyst original 287:5 returned publisher-retriever HTTP 404; OG image is a *different* source | Separate image 287:5 from OG; verify individually |
| P0 Teton #291 (8 views) | Source photo appears to show cleanup under a dam-breach caption | Editorial visual/caption check of 291:2 versus 291:5, not blind substitution |
| P1 Piri Reis #1917 (38 views) | 2 Commons redirect images without explicit size/srcset; separate 7,422,309-byte stored WP original | Cold mobile currentSrc/encoded bytes and CLS; don't infer original downloaded |
| P1 Mesmerism #1924 (33 views) | 1 direct Commons image without size/srcset; 4,462,854-byte stored WP original with Wellcome CC BY metadata | Verify mobile selected image, exact artwork, credit and actual transfer |
| P1 Malbone #621 (29 views) | 6 Jetpack first-party slots; 2 stored originals total 10,352,064 bytes with large authored resize hints | Check responsive selection and encoded mobile transfer, then propose ≤960px fit only if beneficial |
| P1 Antikythera #254 (27 views) | 7 direct Commons redirects, lacking size/srcset | Check guest mobile decode and CLS |
| P1 Courrières #425 (17 views) | 8 of 9 inline slots direct external and without paired dimensions | Check broken images, image reservation and actual LCP/CLS |

## Archival candidate identity / rights and proportional geometry
- U.S. Navy NHHC accession **80-G-227989**, https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html : possible Tang 274:6; **960 × 647 provisional**, same-frame/crop and item rights/credit **HOLD**.
- U.S. Coast Guard accession **210330-G-DE713-0002**, https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/ : Scotch Cap 418:1; official item indicates PD/cleared for release, but exact binary, credit and restrictions **HOLD**.
- Coast Guard Museum Scotch Cap debris preview https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/ : 418:2 **600 × 463** preview, **do not upscale**; original match and permission/credit **HOLD**.
- Florida Memory **RC09237**, https://www.floridamemory.com/items/show/32083 : Skyway **related but different** photograph; collection public-domain claim does not authorize silent image replacement.
- National Archives **NAID 28894685**, https://catalog.archives.gov/id/28894685 : Teton breach editorial candidate **960 × 675 provisional** from catalog dimensions; exact frame, item rights/credit and caption **HOLD**.
- USGS Hebgen fault scarp https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959 : 407:1 candidate; native image size, exact identity and caption **HOLD**.

## Mobile/CWV independent acceptance is still blocked
A November 19 public article fetch returned access errors including **HTTP 429** and other retriever failures; container outbound DNS resolution failed. No independent guest Chromium/mobile trace, numerical image GET, decoded dimensions, screenshot comparison, INP/LCP/CLS or cold CDP Image-transfer bytes was available. Therefore **ZERO independently measured mobile outcomes** and **ZERO newly confirmed visitor-broken images** in this batch. Previous November 18 publisher-source 404s do not demonstrate a present visitor-visible failure. Neither the previously reported **42 broken guest images** nor **76% reduction** has been independently proven.

The 76% gate requires separate mobile and desktop **cold** network tests of complete Image requests including CSS backgrounds and responsive sources, exact 61/66 cohort identity, noncached transfer bytes, actual image decode and no changed historical crop. No erroneous HTML error-response bytes counted as image savings. The **20 WP files above 1.5 million bytes** total **64,385,752 stored bytes**, not visitor wire bytes.

## Safe implementation boundary
After Site QA supplies a real failed image or high-impact measured mobile cost, confirm official item-specific provenance, same historical photograph/crop, rights/credit and proper caption; compute <=960px proportional **no-crop/no-upscale** derivative; stage in WordPress Media *only under separate editorial approval*, test desktop/mobile layout and visual parity, preserve canonical source, and prepare a reversible rollback. **No production WP writes, third-party downloads/rehosting, automatic cache, risky Gutenberg block rewriting, homepage changes, merges, deployments or subscription spend were authorized or performed.**

## Validator
[Fail-closed audit evaluator](../qa/media-recovery/validate_campaign_landing_media_triage_20261119.cjs) and [18 regression checks](../qa/media-recovery/test_campaign_landing_media_triage_20261119.cjs) reject fabricated mobile LCP/screenshot/guest HTTP, false 42/76 claims, invented campaign attribution, unsafe rights/cache approvals, wrong origin-slot mapping, stored-vs-transfer conflation and counterfeit source pins. **18/18 passed against exact committed file readbacks in isolated V8 with Node/test/assert shims**. Native Node and repository CI remain unrun.
