# Media Recovery: 170-page-body exact-reference cross-check, 15 November 2026 Pacific

**Read-only evidence only. Existing draft PR #183, separate from Site QA #154 and the homepage design lead. No production change or media download.**

## What was actually checked
The authenticated WordPress REST PAGE list returned **92 published and 78 draft pages**. Each of the **170** page bodies was subsequently read in this run (VIEW for published, EDIT for draft). All 170 reads returned a content string. Each was searched for the exact path filename **and** `data-attachment-id` string corresponding to the two remaining oversized originals that the previous 66-post-body plus featured-image audit could not place. **0 exact matches across 170 page bodies.** This is **not an orphan finding**: a page may reference an image indirectly by ID, shortcode, metadata, CSS, JavaScript, template, plugin or other post type; calls were not an atomic database snapshot.

Machine-readable, page-ID-level evidence: [170-row custody ledger](../qa/media-recovery/wp170_pagebody_last_two_crosscheck_20261115.json). The ledger provides per-page ID/status/listing-modified time, comparison needles, original media URLs/metadata, and null visitor status fields. The modified timestamps are a post-scan list read, not an immutable body digest or proof of a zero-race snapshot.

## Remaining two original files (exact live WordPress media metadata)

| Attachment | Source URL | Stored original size | Native size | Proportional review size | Rights / disposition |
| --- | --- | ---: | --- | --- | --- |
| 482 | `https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png` | 2,293,016 B | 1672×941 | **960×540** | Unknown provenance; hold, do not delete |
| 2148 | `https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg` | 2,030,948 B | 1821×1190 | **960×627** | NOAA original / Wikimedia crop attribution; item review, hold |

These **4,323,964 bytes** are stored originals, **not visitor transfers** or possible savings. Both are already WordPress media files; the candidate dimensions are only conditional no-upscaling review geometries, not permission to produce, cache, replace, or publish derivatives. Do not infer site speed gains from these two files while page exposure remains unproven. Existing 20 originals >1,500,000 B still total 64,385,752 stored bytes; 11 are inline in eight articles and seven of the other nine were previously reconciled to featured media, a published biography page, and draft pages.

**Source and rights note (2148).** The original archival catalog is [NOAA `wea00739`](https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg). [Wikimedia Commons' 1927 Caernarvon crop](https://commons.wikimedia.org/wiki/File:1927_Mississippi_Flood_Blowing_Levee.jpg) explicitly documents a crop by Wisekwai from the NOAA historical photograph, describes a public-domain U.S. government source, and lists a **1821×1190** original with **960×627** preview. Do not credit the NOAA scan's archival-photography contact as the 1927 shutter operator without item-specific evidence. Never assume one public-domain descriptor licenses all unrelated archival items. The WordPress file shares these dimensions and catalog description; **byte-for-byte identity was not checked**.

**Source and rights note (482).** A UUID-like PNG filename, blank image-library ALT/caption/credit and empty copyright field do not establish authorship, licensing or obsolete status. Remain on license/custody hold.

## Safe decision and next exact actions

1. **No deletion or site rewrite.** The no-page-body-hit observation does not settle dynamic theme/template uses, featured-card rendering, CSS backgrounds, embeds, custom fields or unpublished custom post types. Inspect those separately if safe read-only access exists, without changing the interim lead's homepage design.
2. **Site QA #154 owns browser truth.** Continue its six priority logged-out desktop/mobile captures and then the two `itok`-loss cases (Honda 288:5, Hilo 418:5); do not create a duplicate collector. Require `currentSrc`, HTTP/redirect chain, cold cache indicators, decoded width/height, actual encoded image transfers, screenshot and request IDs. Original external source reader rejection is not a 404 in the guest browser.
3. **Fix real breakage first.** Only after a *specific* failed visitor slot and same-scene rights-cleared primary source are established, stage a single-slot reversible replacement and visually compare before/after ALT, caption, crop, layout, responsive behavior, desktop/mobile. Restore on failure; no bulk Gutenberg block rewrites. No caching/rehosting of third-party files unless rights are resolved.
4. **Weight claim must be network-based.** For the historic fixed **61-post/355-inline** cohort, collect a real logged-out cold-browser transfer ledger of exactly the requested site image resources. Save page ID, actual request URL/currentSrc, final HTTP, image bytes, redirects, failed requests and device profile; compare baseline and staged output with matching 61 pages, viewports, cache status, request attribution and sampling. Define `reduction=(baseline_image_transfer_bytes-proposed_image_transfer_bytes)/baseline_image_transfer_bytes` and do not claim **76%** without observed complete event-chain evidence. The current **66-post/361-image** census is not interchangeable with the older cohort. The historical **42 reported original-source failures** still await guest-browser verification.

## Offline validator and regression evidence

- [Fail-closed audit validator](../qa/media-recovery/validate_wp170_pagebody_last_two_crosscheck_20261115.cjs) checks 170 unique page IDs (92 published, 78 drafts), four literal search patterns, two exact original URLs and media metadata, native dimensions/960px proportionality, null guest HTTP/wire values, no orphan declaration, rights holds, no 76% claim and Site QA ownership.
- [Node test definitions](../qa/media-recovery/test_validate_wp170_pagebody_last_two_crosscheck_20261115.cjs) include 19 adverse edits plus baseline, for **20 test definitions**. On committed audit bytes, **15/15 isolated V8 checks** executed: one baseline and 14 independent unsafe mutations all behaved as required. Native Node/CI not executed in this run; no deployment or automated guest browser evidence.

## Production and ownership boundary

Zero WordPress writes, uploaded/downloaded media, cached third-party binaries, homepage modifications, post-block rewrites, subscription expenses, merges and deployments. Rights and 960px staging stay **HOLD**. No visitor image HTTP status or actual percentage saving is supplied by this audit.
