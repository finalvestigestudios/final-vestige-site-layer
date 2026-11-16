# Final Vestige media: two-reference origin-census discrepancy (2026-11-16)

**Status: READ-ONLY, HOLD.** No external media download, WordPress upload, license assumption, published post/block edit, homepage-design change, merge, deployment, or subscription spend. This isolated branch is intentionally based on `main` rather than the 731-file/1,152-commit draft Media Recovery [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183). Site QA's independent [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) continues to own guest-browser collection.

## High-value result — all 61 posts reconciled

Both independent, historical, **stored-inline-markup** censuses count precisely **61 published posts and 355 `<img src>` references**, but report **286** (Site QA #154) versus **288** (Media Recovery #183) offsite references. Directly fetched and compared the exact QA CSV against all eight machine-readable Media Recovery inventory parts at immutable refs, with source-blob pins in [the 61-row evidence](../qa/media-recovery/source_census_delta_61posts_20261116.json). **59 of 61 post counts match; only two posts account for the entire +2 discrepancy**:

| Post and relevant slot | Site QA offsite | Media Recovery offsite | Exact URL and classification question |
| --- | ---: | ---: | --- |
| Three Mile Island, post **285**, slot **285:1** | 5/6 | 6/6 | `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1` — Jetpack proxy, upstream **www.squawkpoint.com**, not Final Vestige |
| Teton Dam, post **291**, slot **291:0** | 5/6 | 6/6 | `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1` — Jetpack proxy, upstream **text-message.blogs.archives.gov**, not Final Vestige |

Media Recovery classifies each of those original source URLs as **external**. They are the only offsite Jetpack-proxied images in the two discrepant six-image posts. They are therefore plausible explanations for the count difference, **not a proven cause**: #154's original full WordPress source snapshots are not available in this isolated comparison; snapshots may differ. Never claim QA's classifier is wrong until the two snapshots and exact classifier input are compared. The NARA archival article for slot 291:0 is [The Unforgettable Calamity (2016)](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/). Its image appearing in an archive page does **not** mean its WordPress visitor delivery is confirmed.

## Engineering evidence and acceptance

- [Machine-readable 61-post source reconciliation](../qa/media-recovery/source_census_delta_61posts_20261116.json) includes all per-post counts, both suspect exact URLs, two upstream hosts, eight source-part blob IDs, QA CSV blob ID, and all browser HTTP/decode/transfer statuses explicitly **null**.
- [Fail-closed offline Node validator](../qa/media-recovery/verify_source_census_delta_20261116.cjs) rejects unpinned provenance, missing or duplicate rows, count drift, false HTTP statuses, invented transfer savings, publishing, premature rights releases or unsupported 960px dimensions.
- [19 native Node tests](../qa/media-recovery/test_verify_source_census_delta_20261116.cjs) **passed locally on Node 22.16.0**, including 18 negative mutations. A passing offline test establishes only evidence consistency, not web health.
- Run: `node --test qa/media-recovery/test_verify_source_census_delta_20261116.cjs` and `node qa/media-recovery/verify_source_census_delta_20261116.cjs`. GitHub-hosted CI is not required for this review and was not invoked.

## Safe media and rights decision

**Do not replace either image solely because it appears offsite, and do not upload/cache its binary without verified per-item rights.** The NARA source is a promising primary-source identification for Teton Dam, not an item-specific republication grant; Squawkpoint is a third-party publisher whose rights remain unverified. Both remain `rights_status=HOLD`, with no master binary hash, native dimensions or exact-frame match.

If a real logged-out browser failure is later established, retain the previous original URL, attribution and post revision for rollback; verify the exact archival frame/crop and rights; stage the 960px max-width derivative in a private WordPress media environment only after approval. Use `min(960, decoded_master_width)` and proportional height based on decoded pixels; never upscale a smaller master or convert an HTML catalog page into an image URL. Require before/after screenshots, ALT/caption preservation, currentSrc, GET status, content type, decoded natural dimensions and network transferred bytes before proposing a production action. No automated Gutenberg rewrite is permitted.

## Site QA handoff and key program thresholds

**Do not duplicate #154's browser collector.** Keep the existing six P0 slots first (`285:5,285:2,287:5,418:1,418:2,407:1`). After those, compare `285:1` and `291:0` in the existing capture flow using cold guest `currentSrc`, redirects, GET status, MIME, naturalWidth/Height, screenshot and actual transfer bytes. Only then investigate whether their proxy classification explains the stored-source delta. Nothing here proves a 404, image decode failure, rights violation or visitor-visible outage.

The reported **42 broken originals are still unconfirmed in guest Chromium** and **76% image-weight reduction is not a measured reduction in visitor network bytes**. For any savings claim compare like-for-like fully loaded images and transferred CDP bytes at identical viewports, cache and scroll protocol: `(before_image_transfer_bytes - after_image_transfer_bytes) / before_image_transfer_bytes * 100`. Exclude page HTML/JS and stored upload sizes. The later **66-post/361-image** census is a different cohort and must not silently replace the historical 61/355 denominator. The current **20 WordPress originals over 1.5 decimal MB totaling 64,385,752 bytes** measure stored files, not delivered payloads.

**No production or external image request was used for this reconciliation.** The exact read-only source refs, 61 rows and two differentiated upstream proxy URLs make this evidence reproducible and useful without making a false broken-image claim.
