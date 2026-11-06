# Final Vestige: complete 83-page media census — 2026-11-06

**Ownership:** Media Recovery draft PR #1228. Complements Site QA #154's existing visitor-browser collector, Media Recovery #183's docs/IMAGE-WEIGHT-WORKLIST.md, and the interim lead's homepage design. Strictly WordPress read-only source inspection.

## What was checked
WordPress pages.list(status=publish) then individually read **83/83** published pages with pages.get(context=edit). Seven JSON shards contain every page ID, permalink, CMS modification timestamp, literal stored <img src> URL and page/slot, stored width/height, origin class, missing guest evidence and rights HOLD. Previous eight-page sample is expanded to all 83 pages. Source inventory does **not** include theme/CSS backgrounds, picture/runtime selections, JS media, featured-media requests or actual guest-image failures.

**Validated counts:** 83 pages; **8** contain source-level images; **20** slots; **17** distinct stored URLs; **8** offsite slots; **10** lack at least one declared dimension. Offsite comprises 3 Wikimedia direct, 3 Awin dynamic affiliate banners, 1 Google Drive thumbnail, and 1 Suunto retail CDN. There are 11 direct first-party images and 1 first-party Jetpack transform. **Zero** visitor HTTP/decoding or transfer observations.

## Previously uncatalogued pages
- /about/bryan-rhodes/ (page 234) has one first-party author image without declared dimensions.
- /collection/ (page 78) has four stored images including a Suunto merchant URL requesting width=1390 and the **same Cold Case Awin creative** embedded on its dedicated landing page. Do not rehost retailer/affiliate assets or alter tracking. A width query parameter is not a measured native width, wire size or approved 960px derivative.

## Restoration and performance handoff
1. Site QA #154 continues its existing six P0 guest-browser checks (285:5, 285:2, 287:5, 418:1, 418:2, 407:1), capturing currentSrc, HTTP, naturalWidth, image transferred bytes and screenshot. Do not infer broken status from tool wrapper 403/404.
2. Then check 1484:0 Drive podcast artwork, 78:2 Suunto merchant image, 78:3 Cold Case Awin on Collection, 2088:0 Mini Museum Awin, 2089:0 Cold Case landing. These are **unverified candidates**.
3. For genuinely failing, individually rights-cleared archival images only: match same historical scene and source record, log license/credit and master SHA-256, derive <=960px width **without upscale**, verify crop and caption. Detailed maps/panoramas require a separately legible original viewer. Any WordPress media upload or post edit requires explicit authorization and staging parity.
4. For affiliate and retailer images, prefer merchant-approved embeds over unauthorized caching. Do not remove tracking or copy third-party files.
5. The 66 published articles (361 stored inline images; 294 offsite) remain a separate content type, not 66 pages. Neither their source counts nor the page census establish 42 actual broken images or a 76% reduction in real cold-browser transferred image bytes. The 13 >1.5MiB WordPress originals sum to 43,522,829 *stored* bytes, not visitor wire totals.

## Safety / verification
Seven audit shards, an aggregate rollup, fail-closed JS validator, and 22-case Node regression suite. Baseline passed in isolated V8, nine intentionally corrupted input variants correctly rejected in V8. Native Node CI has not been run. WordPress production writes 0; third-party downloads/caches 0; homepage design edits 0; new spend $0.
