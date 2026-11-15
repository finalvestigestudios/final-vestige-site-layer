# Published non-homepage pages: image-source resilience pilot — 2026-11-14 PT

**Disposition: review-only P1, not a browser failure finding.** Separate from Site QA draft #154, the frozen 61-post/355-image census, and homepage visual design. No Gutenberg markup, assets or production code are altered.

## Read-only scope and exact custody
Authenticated WordPress `pages_get(context=edit)` on **12 explicitly selected, published, non-homepage pages**: 1484, 1480, 2017, 2088, 2089, 529, 77, 76, 531, 525, 1304 and 1868. This is a sample of 92 published pages, **not** an all-page claim; homepage page 6 was deliberately excluded. The machine ledger `qa/media-recovery/published_pages_media_pilot_12_20261114.json` preserves exact 49 stored inline image source URLs, their page/slot, dates, ALT and declared dimensions, as well as explicit null guest-network status fields.

| Source class | Stored image slots | Context |
|---|---:|---|
| YouTube `i.ytimg.com` | 40 | Films page 529, linked Shorts card thumbnails |
| Awin `www.awin1.com/cshow.php` | 2 | Sponsored pages 2088 and 2089 |
| Google Drive `drive.google.com/thumbnail` | 1 | Podcast episode 1484 cover |
| Wikimedia `upload.wikimedia.org` | 3 | Podcast episode 1484 historical views |
| First-party `finalvestige.com` | 3 | Apollo 1 Evidence Atlas 2017 |
| **Total** | **49** | **46 external**; source dependencies only |

### Functional identity check on 40 film thumbnails
All 40 stored YouTube thumbnail URLs on [Final Vestige Films](https://finalvestige.com/watch/films/) match their paired `youtube.com/shorts/<videoID>` link by exact video ID. All 40 thumbnail images have decorative `alt=""` **with** an accessible anchor label and visible card title. This is *not* evidence that every thumbnail loads in a guest browser, and the empty ALT is not independently an accessibility defect. Existing page video presentation, CSS and homepage are out of scope.

### Editorial and conversion-sensitive exceptions
- [Podcast episode 1484](https://finalvestige.com/podcast/the-textbook-found-open-in-the-ruins/) links cover artwork through `https://drive.google.com/thumbnail?id=1V8rMf0ovXiJbJLLq77uLwfMHghlH7sMM&sz=w1600`. **Public visibility, account permissions, MIME, redirect and browser status are unknown.** If it fails in guest Chrome, seek owned artwork with proven creator rights before any staging proposal. Three historical photos on that page are hosted directly on Wikimedia; verify precise Commons file/license individually, not site-wide.
- [Mini Museum sponsored page 2088](https://finalvestige.com/mini-museum-history-collectibles/) references `https://www.awin1.com/cshow.php?s=4236132&v=89949&q=552988&r=3055117` as an image. [Cold Case sponsored page 2089](https://finalvestige.com/cold-case-mystery-games/) references `https://www.awin1.com/cshow.php?s=4959313&v=46005&q=620613&r=3055117`. These are **dynamic affiliate creatives**; browser privacy/ad-blocking can influence loads, and moving/caching them risks affiliate terms and attribution. **Do not mirror, rewrite, cache or replace without network failure evidence and program authorization.**
- [Apollo 1 Evidence Atlas 2017](https://finalvestige.com/apollo-1-evidence-atlas/) references three first-party NASA-captioned image URLs. Source location does **not** independently establish exact NASA photograph identity, creator credit or copyright status. Keep original caption dates and scene identity.

## WordPress storage and 960px plan
Fresh 2026-11-14 read-only, two-page Media API census: **125 original image attachments**, with **16 originals strictly >1,500,000 decimal bytes, totaling 49,107,665 stored bytes**. No new large originals; 73,381,251 bytes across the full 125 stored-originals census. **These are storage sizes, not browser transfer bytes.** The historical 61 posts/355 inline image positions and 42 alleged broken remain a separate frozen-source audit. The proposed 76% visitor wire savings remain unmeasured.

For any future first-party/cache candidate: obtain guest-browser 200/MIME/decoded currentSrc and encoded transfer bytes (Site QA #154 owns its six P0 image queue), exact same historical scene and rights/creator/credit authority, source master dimensions, responsive CSS width at actual DPR, and editorial approval. Derivative **at most 960px wide without upscaling**, preserve aspect and reasonable visual sharpness; at DPR 2 a 960px candidate is insufficient above 480 CSS pixels. For copyrighted sponsor banners or unlicensed third-party images, no download/WordPress upload is permitted. After permission, prepare a *reversible, isolated staging-only* URL/attachment mapping with old src/srcset/ALT/credit preserved for rollback, then compare same page and viewport under uncached network before considering any release. Do not assume HTML physical thumbnails exist because WordPress advertises virtual Jetpack sizes.

## Verified engineering
Offline audit validator `qa/media-recovery/validate_published_pages_media_12_20261114.cjs` fail-closes on source/slot/video mismatch, invented guest statuses, false release rights, unapproved homepage/WordPress changes, 960px rule violations, and a mislabeled 76%-reduction. Regression suite `qa/media-recovery/test_published_pages_media_12_20261114.cjs` has 42 positive/adversarial cases. Exact committed JSON/validator/tests passed **42/42 isolated V8 with Node-compatible shims**; **native Node, full CI, real guest browser and actual on-wire savings not executed**.

## Release, responsibilities and next evidence gate
This P1 pilot covers twelve extra **published pages** and does not duplicate or modify the Site QA #154 browser collector. Site QA retains six primary P0 post slots **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Only once actual guest failures exist should editors decide rights-cleared scene-identical fallback media. For this P1 queue, prioritize Drive cover (rights/content ownership check) and both dynamic affiliate banners for observation, then any Shorts cards whose natural dimensions are zero. Do not assert broken status from web-retriever wrappers or ad-block behavior alone.

**No** third-party image downloads, image caching/rehosting, WordPress production writes, Gutenberg rewrites, CSS/homepage design changes, merges, deployments or subscription spend in this batch.
