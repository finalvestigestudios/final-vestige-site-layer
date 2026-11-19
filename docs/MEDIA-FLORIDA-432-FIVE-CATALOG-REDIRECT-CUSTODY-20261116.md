# Florida Memory post 432: five source-accession closes and www redirect evidence
Read-only Media Recovery batch, 2026-11-16 PT. No homepage design work, image download, paid API, WordPress production mutation, post-block rewrite, rehost, deploy or merge.

## Five previously accession-only source references now mapped to official catalogs
| Slot | Existing exact WordPress origin image URL | Verified indexed official catalog | Catalog identity/date |
|---|---|---|---|
| 432:0 | https://www.floridamemory.com/fpc/prints/pr04493.jpg | https://floridamemory.com/items/show/4144 | PR04493, funeral service, Woodlawn Cemetery subject, 1928 |
| 432:1 | https://www.floridamemory.com/fpc/reference/rc17068.jpg | https://www.floridamemory.com/items/show/38362 | RC17068, Avenue A flood in Belle Glade, September 1928 |
| 432:2 | https://www.floridamemory.com/fpc/reference/rc10673.jpg | https://floridamemory.com/items/show/33289 | RC10673, demolished automotive garage, Belle Glade, 1928 |
| 432:4 | https://www.floridamemory.com/fpc/reference/rc04344.jpg | https://floridamemory.com/items/show/27848 | RC04344, coffins by canal, Belle Glade, 1928, not roadside RC04343 |
| 432:5 | https://www.floridamemory.com/fpc/reference/rc07668.jpg | https://floridamemory.com/items/show/30741 | RC07668, burial of storm victims, West Palm Beach, 1928 |

Together with previous catalog-pinned 432:3 (N031889) and 432:6 (MSF-PB11548-001), all seven original Florida Memory sources in this article have catalog-accession/source-path mappings. The five mappings in this batch come from search-indexed PRIMARY Florida Memory catalog extracts containing the accession, Image URL, title, and date, not a fresh successful HTTP fetch of the official catalog page. Direct catalog fetches were blocked in the public web retriever (403).

## Exact network-method distinction
Each of the five existing www.floridamemory.com original image routes gave a web retriever **tool error 500** describing a redirect to the matching bare-domain floridamemory.com image path that the retriever could not access. That is **NOT** observed origin HTTP 500 or visitor-visible image failure. Bare-domain destinations were inaccessible to the tool. Two sampled Jetpack proxied URLs also were inaccessible, with no numeric HTTP result. Site QA #154 is owner of the existing logged-out browser probe, not this lane. It must collect image currentSrc, GET status/MIME, redirects, natural decoded dimensions, screenshot, CDP encoded bytes and post revision. Do not count these five tool errors among the alleged 42 broken images.

## Rights, historical correctness and 960px
Florida Memory official FAQ Q9, https://floridamemory.com/share/order-info/faq.php, says all images bear CC Public Domain Mark 1.0, indicating no known copyright restrictions, and asks for State Archives of Florida credit under Florida Statutes §257.35(6). PDM describes known copyright status rather than granting a new license. Item-level archival identity, credit placement and use review remain required for any proposed copy. The existing ALT for 432:1 is geographically broad; official catalog specifically says Avenue A in Belle Glade. Preserve historical context and do not silently rewrite captions. Do not confuse RC04344 canal scene with RC04343 roadside image.

These five candidates have **zero downloaded and decoded source binaries**. Their actual native dimensions, SHA-256, same-frame/crop identity, HTTP response and visitor transfer bytes remain NULL. No proportional derivative dimensions may be calculated until native dimensions are verified. Any later reviewed derivative has maximum width 960px, must retain aspect ratio and never upscale source pixels.

## Proposed isolated, reversible WordPress Media plan (NOT authorized execution)
1. Obtain a documented Site QA visitor-broken image at the actual Jetpack currentSrc before any repair, then determine whether the existing first-party proxy already serves an acceptable image.
2. After individual source/rights/credit confirmation, use an expressly permitted primary-origin image binary, check JPEG MIME and actual decoded source geometry, compare original and archived frame/crop, record binary SHA-256, and assess whether WordPress or a permitted cache is needed at all.
3. For an explicitly approved change only, prepare one 960px-max derivative without enlargement, retain source-credit metadata, stage independently, compare logged-out desktop/mobile before-and-after visual/layout/decode and bytes, keep original URL, post revision and media ID for rollback.
4. Do not bulk rewrite Gutenberg blocks or alter homepage design. No staging or production upload is authorized by this audit.

## Measurement posture and offline verification
Historical 61 published posts / 355 inline references are a different cohort from later 66 / 361. The 42 reported broken originals remain guest-browser unconfirmed; 76% image transfer savings unmeasured. Twenty originals >1.5 decimal MB total 64,385,752 **stored** bytes, not actual network transfer. Run the exact scoped validator with: node qa/media-recovery/validate_florida432_catalog_redirect_20261116.cjs qa/media-recovery/florida432_five_catalog_redirect_custody_20261116_1326pt.json. Regression command: node --test qa/media-recovery/test_florida432_catalog_redirect_20261116.cjs. The evaluator rejects status invention, false rights clearance, native-size invention, permissive cache/upload/rewrite, cross-item swaps, and source-pin changes.

Media Recovery draft #2747 remains isolated/unmerged; Site QA #154 retains the pre-existing six P0 browser checks ahead of these five non-P0 images. Evidence is in the machine audit and test sources under qa/media-recovery/.
