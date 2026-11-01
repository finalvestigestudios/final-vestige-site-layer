# Florida Memory seven-image recovery and rights plan — Okeechobee (2026-10-31)

**Scope:** Final Vestige published post **432**, *They Buried the Dead Apart*. This is a read-only archival and source-integrity batch, **not seven confirmed broken pictures**. Do not alter the homepage or independent Site QA #154 work.

## Current WordPress vs census

Authenticated WordPress `posts.get(id=432, context=edit)` on October 31 returns `status=publish`, post modified `2026-08-28T03:07:30`, **7/7 identical stored image URLs and 7/7 complete ALT strings** against the frozen 61-post source inventory. All seven are direct `www.floridamemory.com/fpc/...` hotlinks. Their previous independent image viewer paths redirected to non-www endpoints and failed in the **viewer**, not in a measured guest Chrome browser. The viewer wrapper cannot establish source HTTP 404/403, actual decoded images, transfer bytes, or a broken visitor experience. This sandbox also fails DNS for finalvestige.com and floridamemory.com before HTTP, so no origin HTTP response was obtained here.

## Exact original-image candidate map (publisher originals, not substitute photos)

| Slot | State Archives identifier | Primary catalog record | Archival description / date |
|---|---|---|---|
| 432:0 | PR04493 | https://floridamemory.com/items/show/4144 | Funeral service for hurricane victims, West Palm Beach/Woodlawn Cemetery, 1928 |
| 432:1 | RC17068 | https://floridamemory.com/items/show/38362 | Avenue A flooded, Belle Glade, **September 1928**; more specific than broad article ALT |
| 432:2 | RC10673 | https://floridamemory.com/items/show/33289 | Demolished automobile garage, Belle Glade, 1928 |
| 432:3 | N031889 | https://floridamemory.com/items/show/141398 | State Board of Health headquarters at Pahokee, 1928, staff named; **archive does not substantiate "disaster-response headquarters"** |
| 432:4 | RC04344 | https://floridamemory.com/items/show/27848 | Coffins stacked beside canal, Belle Glade, 1928 |
| 432:5 | RC07668 | https://floridamemory.com/items/show/30741 | Burial of victims, West Palm Beach, 1928 |
| 432:6 | MSF-PB11548-001 | https://floridamemory.com/items/show/340182 | Historic African American mass-burial site photographed **2001**, not a contemporary photograph taken in 1928 |

The source file names and canonical /fpc/ paths are recorded alongside original article URLs, complete ALTs and expected publisher identifiers in `qa/media-recovery/florida_432_primary_20261031.json`. **Catalog-path identity is not a cryptographic original-file match.** Do not assume non-www endpoints work in a browser just because the archive uses those routes.

### Newly verified, unusually useful rights clarification

Unlike many other archive collections, Florida Memory explicitly states in its [State Archives photo FAQ](https://floridamemory.com/share/order-info/faq.php) that it offers *all images* with the **Creative Commons Public Domain Mark 1.0** (PDM 1.0), described as free of known copyright restrictions. This is a **publisher rights representation**, not a Creative Commons license granting a new warranty and not proof that a specific cached binary is the identified archival image. The FAQ asks users to credit materials under Florida Statutes §257.35(6). The [disclaimer](https://floridamemory.com/learn/about/disclaimer.php) also notes state law and potential donation conditions. Preserve the source title, collection and identifier and attribute **State Archives of Florida, Florida Memory** with the record link. Individual item review, possible donor issues, exact binary matching, editorial/caption integrity and WordPress release approval remain **HOLD**.

The Florida Memory [digitization guidelines](https://floridamemory.com/learn/about/guidelines.php) describe a **600px access JPEG target** and a 120px GIF thumbnail. That is a programme guideline, **not a measurement of these seven JPEGs**. All seven actual original pixel dimensions and bytes remain unknown. Never upscale a 600px source to 960px.

## Conditional local-cache / WordPress plan

1. **Actual guest-browser proof first.** Capture a logged-out Chrome tab for post 432 with all seven `currentSrc` values, full redirect chains, Image-type network request URL/HTTP status/content-type/encoded transfer bytes, `naturalWidth` and `naturalHeight`, an in-page screenshot and cache/service-worker flags. Confirm whether redirects to `https://floridamemory.com/fpc/...` produce successfully decoded images. Avoid browser extensions or authenticated-session differences.
2. **Exact source and rights review.** For an individually verified failed image, re-open its above original State Archives catalog, compare crop and visible subject, log current / replacement binary SHA-256, and approve the item-specific PDM-1.0 provenance plus statutory archive credit; retain 2001 chronology for 432:6. Do not replace with a thematically similar, historically different photograph.
3. **Derivative only from approved master.** Compute dimensions **after** opening the actual master. Target `width = min(original_width, 960)`; preserve full aspect ratio using proportional nearest-integer height; no enlargement/cropping/watermark removal. Compare grayscale text/detail/contrast, EXIF orientation, and accessibility ALT. WebP or JPEG is acceptable after visual QA; no subscription or paid scans required.
4. **Staging and narrow release.** Stage only the approved derivative and separate attribution data. Prefer normal WordPress Media Library responsive `srcset`/Jetpack behavior and stable first-party URL; never change Gutenberg HTML in bulk or replace original image blocks on production without a separate explicit approval. After approval, first trial a single image in staging and verify post permalink, figure link, caption, ALT, desktop/mobile, and fallback.
5. **Measure rather than claim.** Record before and after *decoded original image identity* plus CDP encoded bytes for the same article image requests and viewport/cache conditions. Compare 61-post/355-source inventory without conflating 13 stored originals >1.5MiB with visitor bytes. The advertised **42 broken** and **76% weight reduction** remain **unverified** until an actual before/after visitor waterfall supports them.

## Machine-readability and regression

`qa/media-recovery/florida_432_primary_20261031.json` binds all seven exact source URLs and full ALTs to official IDs, original /fpc/ paths and proposed canonical host paths; records program-wide PDM-1.0 and individual `HOLD`; sets guest HTTP/MIME/currentSrc/bytes/decoded/dimensions and visitor savings to `null`; and forbids WordPress writes. `validate_florida_432.cjs` checks these properties against the earlier frozen 25-source census; `test_florida_432.cjs` covers 44 positive/negative scenarios, including wrong catalog item/date, fake browser status and premature publishing. **44/44 exact-committed-source test cases passed in isolated V8 with Node test/assert shims; native Node CI and logged-out Chrome remain unrun.**

No original photograph binaries acquired, no WordPress writes, no production repairs, no homepage design changes, no Site QA code edits, no subscription spend.
