# Media recovery: canonical original versus Drupal-style token (15 Nov 2026 PT)

**Draft #183 / Site QA #154 handoff. Unmerged, undeployed. No production changes.**

## Actionable new find — Hilo 1946, WordPress post 418 image slot 5

The [USGS catalog item](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) explicitly labels the photograph **Public Domain**, notes that the original photographic **source is unknown**, and exposes its **Original** hyperlink. Followed that original catalog link read-only:

- Editor source (transformed Drupal image): https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz
- WordPress VIEW Jetpack source (loses upstream token): https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?ssl=1
- **New USGS catalog Original (no Drupal styles path or itok):** https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/19460401_UNKNOWN_37-012_copy.jpg

The official Original URL and token-bearing transformed source both rendered in the independent web image interface on Nov 15. The Jetpack URL was previously tool-inaccessible. Neither observation includes a verified browser HTTP status or byte count. Both rendered images visibly show the same Cafe 100 and Hilo Products storefront, damaged vehicle and debris; exact pixel hash identity is **not** verified. This is a primary-hosted same-scene URL candidate, **not** approval for publication, caching, or WordPress upload.

**Site QA:** reuse existing #154 collector after six existing P0 images. For 418:5 compare the live Jetpack currentSrc and candidate direct USGS Original in a cold, logged-out desktop/mobile browser. Capture Image request URLs, redirects/status codes, cache flags, natural dimensions, MIME, complete CDP event chains, transferred encoded bytes, screenshots, and exact alt/caption. Only if current image fails but catalog Original loads should an isolated external-URL-only staging proposal advance through rights/editor review. WordPress may still Jetpack-proxy a changed editor URL, so confirm staged final currentSrc. No blanket CDN toggle.

## Honda Point post 288 image slot 5 — no safe substitute yet

USNI's token-bearing exact image rendered in the reader, and its tokenless Jetpack proxy was inaccessible to that reader. The [USNI March 2020 article](https://www.usni.org/magazines/proceedings/2020/march/chaos-devils-jaw-0) credits the US Naval Institute Photo Archive. [Navy NH 97985](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97985.html) depicts the same vessels but is not established as the identical frame; catalog credits a donated Naval Historical Foundation/Chambers collection. Do not substitute this archival image, or infer redistribution rights from government custody, without exact-image and rights review.

## Copyright, 960px, caching and weight

The USGS catalog says Public Domain but identifies the underlying original photographer/source as unknown. Preserve this uncertainty in any rehosting clearance review. No image binaries were downloaded or copied. Native image dimensions have not been measured: proposed review width = min(960, nativeWidth); height = round(width*nativeHeight/nativeWidth) after trusted measurement; never invent or upscale dimensions or crop away scene evidence.

The 61-post/355-inline-image/288-external-origin audit is a frozen baseline, distinct from subsequent live 66-post observations. The alleged 42 broken images are guest-browser unverified, and proposed 76% visitor-bandwidth reduction unmeasured. Last verified over-1.5MB inventory: 20 WordPress originals totaling 64,385,752 **stored** bytes, not measured browser transfers.

To claim measured reduction, cold-load matched 61 pages/viewports, ensure complete Image CDP event chains and cold transfers, and compare actual encodedDataLength for identical image slots. Formula is 100*(baseline_bytes - candidate_bytes)/baseline_bytes; incomplete or memory-cached requests are NOT_MEASURED. If eventually approved for isolated staging, snapshot a single slot's URL/ALT/caption, verify right/credit, compare desktop/mobile before-after, then allow one-slot rollback. No whole-post Gutenberg rewrites.

Files: [machine-readable source/rights/candidate ledger](../qa/media-recovery/official_original_route_pair_20261115.json), [fail-closed validator](../qa/media-recovery/validate_official_original_route_20261115.cjs), [18 native Node cases](../qa/media-recovery/test_official_original_route_20261115.cjs). Offline Node 22: 18/18 passed before commit; check exact blob custody after commit. No guest Chrome/CI claim. No WordPress production writes, media copies/caching, homepage design changes, deployments, merges or spend.
