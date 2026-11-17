# Three Mile Island: six-source recovery and rights-hold memo — 2026-11-01

**Scope:** Published post [285](https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/), *The Light Said Closed*. Independently re-read authenticated **WordPress posts.get** with context=edit: status publish, last modified **2026-09-08T10:06:47**, all **6/6 stored external source URLs and ALTs** exactly match frozen census `parts/03.json`. Not rendered browser DOM. No WordPress writes.

## External-retriever observations (specific URLs in JSON ledger)

- **285:0** `live.staticflickr.com/7278/7447166686_...`: web retriever **403 Forbidden**. Exact NRC Flickr photo ID **7447166686** is a publicly indexed official photo page. This is **not** visitor-browser 403 proof.
- **285:1** Squawk Point image via `i0.wp.com/www.squawkpoint.com/...`: independent web retriever displayed an image. Jetpack on a third-party origin does **not** convert it into a first-party rights-cleared asset.
- **285:2** UCS image `blog.ucsusa.org/.../DBD-42-Figure-4-tmi-panel.jpg`: retriever failed after redirect to `blog.ucs.org` (wrapper code **500**), **not evidence** of an origin HTTP 500. Individual origin licensing unknown.
- **285:3** Insider-hosted control-room photo displayed through independent viewer. Image may portray an April 1, 1979 presidential visit, but catalog photo identity is **not proven**; do not silently change ALT or republish the Insider image.
- **285:4** Commercial Pixels listing of NRC/Science Photo Library reactor-core graphic displayed in independent viewer; royalty/reproduction terms of the commercial copy are **not established by the federal origin of underlying concept**. Exact NRC official diagram record located. No commercial-asset copying.
- **285:5 P0** SayMedia/HubPages transformed image URL `images.saymedia-content.com/.image/.../the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg` returned **(404) Not Found from independent web retriever**. This is a **specific observed retrieval error**, not confirmed visitor-browser 404. The publisher's article credits a Three Mile Island photograph taken **June 6, 2010** to Wikimedia Commons, and Commons file [Three mile island 062010.jpg](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) is **819×614** with an author public-domain dedication. Candidate relationship is **publisher credit, not proven same pixels**; owner and crop/hashes must be confirmed. Current ALT omits modern 2010 date.

## Source/credit crosswalk and conditional sizing

| Source slot | Authority record | Relationship to live image | Known candidate original | Conditional ≤960px plan |
| --- | --- | --- | ---: | ---: |
| 285:0 | [NRC Flickr 7447166686](https://www.flickr.com/photos/nrcgov/7447166686) | Exact Flickr image ID; not binary-matched | unknown | unknown |
| 285:1 | [Squawk Point publisher](https://www.squawkpoint.com/2019/02/information-overload-2/) | Original master/credit unknown | unknown | unknown |
| 285:2 | [NARA 540034 via Commons](https://commons.wikimedia.org/wiki/File:Control_room_Number_2._Nuclear_Regulatory_Commission_inspector_looking_at_meters._-_NARA_-_540034.tif) | **Different** control-room candidate | 3000×2023 | 960×647 |
| 285:3 | [NRC/INL Carter visit](https://commons.wikimedia.org/wiki/File:President_Carter_in_the_TMI-2_Control_Room_(cropped).jpg) | Related scene, **not verified exact photo** | 855×688 | **855×688; no upscale** |
| 285:4 | [NRC core end state](https://www.flickr.com/photos/nrcgov/7447162290) / [Commons derivative](https://commons.wikimedia.org/wiki/File:Graphic_TMI-2_Core_End-State_Configuration.png) | Same diagram work candidate; commercial retailer image not authorized | 1772×2623 | 960×1421 |
| 285:5 | [Commons self-photo 2010](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) | Publisher-credit candidate pending exact photo check | 819×614 | **819×614; no upscale** |

**Crucial chronology caveat:** NRC Flickr metadata often says "Taken" in 2008 or 2012 despite descriptions identifying **1979 archival images**. Those are likely digitization/upload metadata, not photographic exposure proof. Do not misdate 1979 events from Flickr "taken" alone.

**Reuse/credit:** NRC [photo gallery guidelines](https://www.nrc.gov/reading-rm/photo-gallery) state government-produced media normally lacks copyright restrictions but some collection media is copyrighted. Commons item declarations require item-specific review. Third-party Squawk Point, UCS, Insider, SayMedia and Pixels URLs are never licensing grants. ALL items remain rights **HOLD**.

## Concrete next repair gate — 285:5 before any cache or Gutenberg edit

1. In logged-out desktop and mobile Chrome on the article, scroll the image into view; capture figure index, rendered `currentSrc`, `naturalWidth/Height`, Image-type request status, redirect chain/final URL/content-type, encoded bytes, screenshot. Distinguish `404`, decoding, CSP/hotlink denial, lazy-load-not-triggered, and a fallback that renders a different picture.
2. Compare original SayMedia/HupPages photograph (where legally accessible) with Commons 2010 file; establish **same exact photograph, not merely similar aerial view**. Record master hash, license/author credit. No unauthorized scraping/bypass.
3. For an *approved* exact image only, prepare a 819×614 (not 960px upscale) local derivative, compare visually and document responsive WordPress staging. Preserve permalink, figure positioning, caption, and correct 2010 context; any ALT edit needs separate editorial approval.
4. Fix only through approved controlled staging. A read-only source mapping and independent retriever 404 are insufficient authorization for production image replacement.

**Metrics:** 6/6 CMS source/ALT matches, 3 image displays, 3 retriever errors (403, redirect 500 wrapper, 404). Visitor browser failures **unknown**, original/on-wire bytes **unknown**, 42 broken **unverified**, 76% saved **unmeasured**, 13 >1.5MiB WordPress **originals** remain independent queue. No images downloaded, licensed assets duplicated, third-party anti-hotlink bypasses, WordPress writes, homepage changes, or purchases.

**Executable evidence:** `qa/media-recovery/tmi_285_nrc_recovery_20261101.json`, `validate_tmi_285.cjs`, `test_tmi_285.cjs`. Validator is offline, rejects invented browser statuses, wrong original URLs, unsupported rights clearance and upscaling. Native Node CI must be executed separately from isolated V8 tests.
