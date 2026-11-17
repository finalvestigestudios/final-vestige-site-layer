# Final Vestige Media Recovery — Florida Memory post 432, seven archival originals (2026-11-04 Pacific)

**Owner:** Media Recovery draft PR #183. **Scope:** post 432, *They Buried the Dead Apart* (Okeechobee Hurricane, 1928). **State:** verified publisher-catalog crosswalk, **not** confirmed visitor-broken media, no production repair. No overlap with homepage design or Site QA PR #154 implementation.

## Concrete batch and evidence provenance

- Frozen WordPress image-source inventory: `qa/media-recovery/parts/01.json`, exact Git **blob** `948bc1b65b42799aa40cfdb810ddf6ffd80886b6` (2026-10-30). All 7 URL/ALT rows have **no recorded HTML width or height**. Not a fresh WordPress read.
- Read publisher-indexed Florida Memory catalog pages, matching **every exact item image path**; this is a materially stronger primary-source ID than a filename-only replacement suggestion. Seven published image references, seven distinct item IDs, seven matching `/fpc/` paths. Metadata retrieval was via indexed publisher pages, not original-image binaries.
- An independent text retriever could not access two selected direct `www.floridamemory.com` JPGs after redirects to the non-`www` host (tool-wrapper 500). **Do not report an image origin 500, browser 500, or visitor broken image.** Five other direct originals not individually tested. A browser might successfully follow the canonical-host transition.
- Actual origin responses, guest-Chromium Image GET statuses, redirects, decoded `naturalWidth`, pixel dimensions, MIME, CDP `encodedDataLength`, CLS/LCP, and SHA-256 binaries are **all unknown**. Metadata from search indexing does not establish image renderability. All status fields in the machine JSON are null.

## Exact archival item custody and historical truth

| Source slot | Official Florida Memory ID | Catalog page | Catalog dating / integrity note |
|---|---|---|---|
| 432:0 | PR04493 | https://www.floridamemory.com/items/show/4144 | 1928 funeral at Woodlawn Cemetery (West Palm Beach) |
| 432:1 | RC17068 | https://www.floridamemory.com/items/show/38362 | September 1928 Avenue A flooding, Belle Glade |
| 432:2 | RC10673 | https://www.floridamemory.com/items/show/33289 | 1928 ruined automotive garage, Belle Glade |
| 432:3 | N031889 | https://www.floridamemory.com/items/show/141398 | 1928 State Board of Health headquarters, Pahokee, includes named personnel |
| 432:4 | RC04344 | https://www.floridamemory.com/items/show/27848 | 1928 coffins along canal at Belle Glade; **NOT** similar adjacent RC04343 roadside photo |
| 432:5 | RC07668 | https://www.floridamemory.com/items/show/30741 | 1928 burial in West Palm Beach |
| 432:6 | MSF-PB11548-001 | https://www.floridamemory.com/items/show/340182 | **Photographed in 2001**: modern historic African American mass-burial site, **not** a period image of the 1928 hurricane |

**Editorial P1 nuance:** Source 432:6 is a **2001** site-documentation photograph of a 1928-era burial site. The frozen ALT correctly identifies the site but does not give the image date. Keep the distinction explicit in future captions, accessible text, or restoration plan; do not misdate the photo as 1928. No caption or Gutenberg block was changed.

## Copyright and item-specific custody

Florida Memory is a digitization program of the State Archives of Florida, not a blanket licensing grant. The archive's `Rights` fields in search-indexed records were blank or not explicit; do not interpret a blank as public domain. The agency's disclaimer is at https://www.floridamemory.com/learn/about/disclaimer.php, and state agency context is https://dos.fl.gov/library-archives/archives/florida-memory/. Historical items can be subject to donor restrictions or photographer copyright; the **2001** Florida Bureau of Historic Preservation photo is especially distinct. Before copying, obtain item-level reuse and proper credit terms for each ID. No hotlink URL change should be justified merely by an archival match.

## 960px no-upscale staging and WordPress release HOLD

1. Site QA #154's existing guest-browser P0 queue remains **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**. Post 432 follows as a non-duplicating P2 cohort. Capture each of its 7 actual `src/currentSrc` pairs, final Image requests (including redirects), HTTP status, image MIME, `naturalWidth`/`naturalHeight` and `decode()`, network bytes and viewport screenshot after lazy-load scrolling, on desktop and mobile. Record documented absence of failure as well as failure.
2. For any confirmed broken source, use the catalog's **same item ID** and compare image content/crop (not just same filename). First ask the Florida State Archives about current authorized and stable delivery URL, item-specific reuse, attribution and metadata before considering any local copy. Do not replace the 2001 scene with a 1928 photo without editorial signoff.
3. Only after cleared access, capture the original's SHA-256, license/credit evidence, **intrinsic pixel width and height** from authorized file and visual master comparison. All seven current original pixel dimensions are **unknown** (catalog physical inches do **not** imply pixel geometry). Proposed `width=min(960,intrinsicWidth)`; proportional `height=round(intrinsicHeight*width/intrinsicWidth)`. **Derivative pixel dimensions remain null** pending legitimate binary measurement; never enlarge an original or alter the historical crop.
4. Stage losslessly labeled source + responsive WebP/AVIF where appropriate with JPEG fallback, preserve historic textual details and non-distorted proportions, and attach a caption/credit/source manifest. Any permitted WordPress Media Library upload is a **separate later founder-approved release**; this draft performs no uploads, rehosting, scraping, rewriting, URL hot-swap, external hotlink proxy change or paid work.
5. Verify with guest browser before-and-after on the exact same post, document request-ID-based **uncached CDP bytes**, image decode and screenshot, and roll back with the original URL/Media ID if visual identity or rights fail. Duplicated image URL requests are counted once. Do not assert a site-wide **76%** weight gain without a complete matched **61 posts / 355 slots** measured comparison and approval attribution.

## QA and test delivery

Machine audit: `qa/media-recovery/florida_memory_432_seven_originals_20261105.json`; validator: `validate_florida_memory_432_20261105.cjs`; 24-case native Node-ready mutation suite: `test_florida_memory_432_20261105.cjs`. **23/23 compatible checks passed** executing exact GitHub-fetched validator logic in isolated V8 with a pathname-only URL shim; native Node/crypto blob-hash test and repository CI still outstanding. Validator guards 7 exact published source + ALT identities against frozen part, all 7 item pages, 2001 catalog dating, source vs retriever-vs-visitor HTTP distinction, unknown binary geometry, rights HOLD and disabled WP/localization release flags.

**Sitewide baseline unchanged:** 61 posts, 355 stored inline image slots, 353 distinct exact URLs, 288 offsite-origin references, 13 WordPress >1.5 MiB originals totaling 43,522,829 **stored** bytes. “42 broken” remains visitor-browser unverified; “76% reduction” is not measured against actual transferred bytes. **Production repairs: zero.**
