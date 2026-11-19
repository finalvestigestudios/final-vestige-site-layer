# Final Vestige image source custody — complete 66-post VIEW census (2026-11-17)

**Scope and separation:** Media Recovery draft PR #2747 only; Site QA #154 owns guest Chromium, network waterfalls and its existing collector. Interim lead owns homepage visual design. No production WordPress writes, third-party downloads/caching, content-block rewrites, merge, deployment or spend.

## Verified, live-source findings

Authenticated WordPress **published list 66/66** and VIEW read of **all 66 post bodies**: **361 inline `<img src>` slots**, **294 third-party-origin slots**, **67 first-party Jetpack slots**. External-origin breakdown: **154 direct external** and **140 via WordPress Jetpack**. There are **81 distinct origin-host labels**. Counts apply to WP VIEW HTML, not cold visitor network responses.

The historical Oct 30 worklist's **61 posts / 355 image slots / 288 offsite references** reconcile *exactly* to the 61 older posts in this fresh snapshot. **Five additional published posts** (IDs 1917, 1920, 1922, 1924, 1926) contribute **six image slots, all offsite-origin**. Thus the current 66/361/294 counts must NOT be described as broken-image growth or a 76% weight reduction. The separate historic Site QA 286-vs-Media Recovery 288 source-count discrepancy remains unresolved and may involve classification/snapshot differences.

For current HTML, **273** images omit one or both explicit dimension attributes; **301** omit `srcset` or `sizes`; **56** have an HTML width value over 960px. These values do NOT establish image transfer size, LCP or CLS, because browsers, Jetpack and CSS can select other sources or sizes. There are **two duplicate-src within-post image-slot pairs**; preserve both visual slots, but only count an actual shared network request once.

Top dependency hosts include Commons (124 image slots), upload.wikimedia.org (18), official Navy history (15), USGS S3 (9), Florida Memory (7), NASA image assets (5) and media.defense.gov (5). Exact post URLs, image slot indexes, authored VIEW image URLs and derived Jetpack-origin paths are in nine machine-readable slices; **every guest HTTP, decode and transferred-byte field is null** because this scan did not run guest Chromium. Derived origin paths are not proof of a direct GET.

## Highest-priority missing-image evidence

Keep existing Site QA six first: **285:5** SayMedia aerial, **285:2** UCS/NRC control panel, **287:5** Sunshine Skyway, **418:1** USCG/Defense portrait, **418:2** USCG debris, and **407:1** USGS Hebgen. Exact current VIEW URLs are pinned in [the rollup](../qa/media-recovery/live_66_source_census_rollup_20261117_1624pt.json). Previous independent web retrievers observed 404 for old SayMedia and Skyway original URLs, 403 for two USCG/Defense originals, and non-HTTP tool errors for UCS and USGS. **None is a confirmed guest-browser image failure.** Use #154 collector; do not duplicate it.

## Rights, source identity and image treatment

Individual item review remains mandatory. Official records include [USCG Scotch Cap image 210330-G-DE713-0002](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/), [USGS J. R. Stacy Hebgen photograph](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0), [Florida Memory RC09237](https://www.floridamemory.com/items/show/32083), and accessioned Navy NHHC Thresher photographs (catalog crosswalk in existing draft). These are **candidate records, not automatic authorizations or exact binary/frame matches**. Florida Memory's Skyway photograph is different from the original article color image, and the current Skyway publisher explicitly credits University Press of Florida; hold rehosting. Other agency-hosted images may carry third-party restrictions. NRC Flickr BY-NC-ND photographs are not cleared for monetized derivatives without additional permission. Verify license, attribution, depicted date, original crop/frame and master SHA-256 for each candidate.

For any later authorized replacement: source native dimensions; target **no more than 960px wide** while preserving ratio, **no upscaling** (a 600×463 preview stays 600×463), rights-safe WebP/AVIF where technically appropriate, preserved caption/ALT and historic accuracy, a reversible *reviewed draft/staging* WordPress media plan with media ID and rollback reference. This is a PLAN, not permission for production media upload or Gutenberg rewrites. Verify responsive output and screenshots before considering any deployment.

## 76% / 1.5MiB measurement gate

The reported **42 broken images** still have no verified guest failure inventory. The proposed **76% visitor-bandwidth reduction is not measured**. The **20 >1.5 MB stored WordPress originals** totaling **64,385,752 stored bytes** do not establish page downloads. On the same pages, devices, cache states and network conditions, measure a reproducible before/after **unique HTTP 200 image request byte sum** (positive transfers only), and preserve the complete image-slot count, decode, actual `currentSrc`, on-screen pixels, LCP/CLS and rights. Redirects and shared requests require deduplication using verified CDP chains; failed/missing images cannot be counted as savings. Report reductions only after controlled baseline and post-change evidence.

## Artifacts and acceptance

- [Nine immutable VIEW source slices](../qa/media-recovery/live_66_view_slice_1_20261117.json) through `live_66_view_slice_9_20261117.json` hold exact URLs and all 66 slot arrays.
- [Machine rollup](../qa/media-recovery/live_66_source_census_rollup_20261117_1624pt.json) pins source Git blob SHA-1 values, totals, high-dependency hosts and six P0 routes.
- [Offline strict validator](../qa/media-recovery/validate_live_66_view_20261117.cjs), [adversarial Node regression suite](../qa/media-recovery/test_validate_live_66_view_20261117.cjs). Run `node qa/media-recovery/validate_live_66_view_20261117.cjs` and `node --test qa/media-recovery/test_validate_live_66_view_20261117.cjs` in a checkout with the pinned files. No external HTTP or WordPress writes occur.

**Release state:** Draft QA only. All production image repairs and any media cache/store remain HOLD until Site QA guest failure + legal/image identity + staging/rollback checks are all satisfied.
