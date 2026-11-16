# Media Recovery: Florida Memory PDM and Navy accession custody (2026-11-16 PT)

**Scope:** independent Media Recovery draft PR #183, not homepage design or Site QA browser collector #154. This is a read-only provenance, rights and image integrity batch. **HOLD**: no external binary downloads, image mirroring, WordPress uploads, published Gutenberg rewrites, merging, deploying or paid calls.

## Evidence collected

- Fresh authenticated WordPress **EDIT and VIEW** reads, unchanged revisions: post 287 (2026-11-02T21:40:01), post 288 (2026-08-19T14:37:40) and post 432 (2026-08-28T03:07:30).
- 19 image tags total across the three posts (6+6+7); 11 targeted exact EDIT/VIEW URL+ALT rows in [JSON custody audit](../qa/media-recovery/primary_rights_11slot_crosscheck_20261116.json): Skyway 287:0/287:5, Honda Point 288:0/288:4, and all 7 Okeechobee 432 slots.
- **All browser GET status, decoded size, wire bytes, screenshot, native file size and source binary hash remain unverified.** An authenticated WordPress VIEW URL is *not* a logged-out browser `currentSrc` observation. Crawler 403/502 responses are tool-access outcomes and cannot be reported as image-serving failures.
- Strict [offline custody validator](../qa/media-recovery/validate_primary_rights_11slot_crosscheck_20261116.cjs) plus [25-case baseline/mutation regression suite](../qa/media-recovery/test_validate_primary_rights_11slot_crosscheck_20261116.cjs). The validator and 24 adversarial mutations passed **isolated V8** execution; native Node CI remains pending. The validator forbids 42-broken/76%-saved claims, false rights/WordPress authorizations, HTML-as-binary substitutions, inconsistent catalog geometry and stale source identities.

## Material new rights clarification

Florida Memory's official [ordering FAQ, copyright question 9](https://floridamemory.com/share/order-info/faq.php) says **all images on Florida Memory are offered with Creative Commons Public Domain Mark 1.0**, signifying no known copyright restrictions, and requests credit under **Florida Statutes §257.35(6)**. **PDM is a statement of public-domain status, not a contractual license**; it does not establish that another publisher's similarly themed photo may be cached. This supports an improved *collection-level rights review* for the seven actual Florida Memory source URLs in post 432 and the different-scene RC09236 archive candidate—not automatic WordPress upload. Each candidate still needs verified item-to-file identity, precise archival credit, noncopyright restrictions review and editorial signoff. The [official Skyway RC09236 record](https://floridamemory.com/items/show/32082) identifies a May 9, 1980 photograph of a car at the collapsed span. It is **not verified as the identical photographic frame** for publisher-origin slots 287:0 or 287:5. Their *current publisher imagery* remains copyright-unknown; Florida Memory's PDM does not transfer to it.

The [Navy NHHC Photo Archives policy](https://www.history.navy.mil/content/history/nhhc/our-collections/photography.html) separately says most Navy collection photos are public domain, **but the Photo Section cannot confirm the status of every image** and donor-origin assets require care. Accordingly NHHC NH 69586 and NH 84822 remain **item-level rights HOLD**; the broad [Navy Archives policy](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) addressing *official government photos* should not be applied automatically to private donated photographs.

## Image-specific high-value mappings

| WP slot | Primary record | Relation/geometry | Release |
|---|---|---|---|
| 288:0 | [NHHC NH 69586](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html) | Same accession text as authored URL; catalog high TIFF **6256×4862**, theoretical 960×746; TIFF not fetched | HOLD: source hash, photographic identity, individual rights |
| 288:4 | [NHHC NH 84822](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84822.html) | Original ibiblio URL basename `h84822.jpg` maps to official accession; high TIFF **6158×4992**, theoretical 960×778 | HOLD: same pixel/crop, rights; avoid rehost |
| 432:3 | [Florida Memory N031889](https://floridamemory.com/items/show/141398) | Exact accession basename; caption currently calls it *post-hurricane disaster-response* headquarters, beyond catalog description | Editorial fact-check HOLD, no edit |
| 432:6 | [Florida Memory MSF-PB11548-001](https://floridamemory.com/items/show/340182) | Exact accession basename; catalog identifies **2001** photograph of historic mass-burial site | Keep 2001-vs-1928 distinction |
| 287:0, 287:5 | [Florida Memory RC09236](https://floridamemory.com/items/show/32082) | Same disaster but different scene; neither publisher image is replaced | No rights inheritance or image swap |

The **960px dimensions for Navy** are proportional *calculations from official catalog HIGH-file dimensions*, not decoded dimensions of the actual WordPress image binary. Every other image in this batch has unknown native geometry; **never upscale**. Use exact image/caption rather than a thematically similar archive shot.

## Staging-only restoration protocol

1. Site QA #154 captures genuine logged-out cold desktop+mobile `currentSrc`, final image GET/MIME/redirects/cache, `naturalWidth` and `naturalHeight`, CDP encoded-wire bytes, lazy-scrolled screenshot and complete page layout review. This batch creates **no new browser collector**.
2. Media Recovery compares the failed source to its **same-frame** archival image, records rights/credit, verifies real binary SHA-256/native pixels, and computes `width=min(960,native_width)`, `height=round(native_height*width/native_width)`; no upscaling or licensed-asset scrape.
3. Only after independent human review may a *reversible staging* WordPress media candidate be proposed. Preserve original post/caption/block source, maintain rollback URL and verify 360px/1440px layout, image decode, CLS and measured cold visitor bytes before **separate production authorization**.

Historical 61-post/355-image and later 66-post/361-image cohorts remain distinct. The reported **42 broken external images are not guest-browser proven**; **76% visitor-byte improvement is not measured**. The last 20 WordPress originals over 1.5 MB total **64,385,752 stored bytes**, not actual visitor transfers.

**Production changes: none.** All audit and test changes are source-only on draft PR #183.
