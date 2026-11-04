# P0 media recovery: Sunshine Skyway post 287 — publisher image-host migration and misleading ALT

Evidence date: **2026-11-04**. Scope: image performance / broken third-party media **only**, isolated from interim lead's homepage design and Site QA PR #154. No site or WordPress modifications.

## Concrete finding: published 287:5 URL is stale in independent retrieval

The six `<img>` elements of published post **287**, [The Warning Was a Man Waving](https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/), were freshly read from WordPress via authenticated **read-only** `posts_get(id=287, context=edit)` on November 4. Post status `publish`, last modified `2026-11-02T21:40:01`. **All 6 src URLs and 6 ALT strings** exactly match the pinned October 30 source census `qa/media-recovery/parts/03.json` (Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`). Exactly **one** IMG (287:0) has a width/height pair (`1024×672`); the other five do not. Potential CLS is **not measured CLS**.

Independent `web.open` retrieval on **each exact stored original** showed five images (`287:0..4`) and reported **404 on `287:5`**. This 404 is the **web retriever's reported outcome for the requested binary URL, not a confirmed origin HTTP response or an actual logged-out visitor Image GET**. Final rendered `currentSrc`, Jetpack rewriting, redirect, image decode, MIME, wire bytes and mobile behavior remain unknown.

- Published/WordPress source **287:5**: `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` — web retriever reported **404**.
- [Publisher's 2020 article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/) now displays an image under **`https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`**, which **displayed** in the independent image viewer. The published original and new media-host asset have the same filename but **no binary/hash/crop equality verified**.
- The publisher attributes the image to **University Press of Florida**. This is a copyright attribution, **not reuse authorization**; downloading, local WordPress storage, republication and caching are **HOLD**.

**Site QA P0 ask:** Start with exact published 287:5 versus the publisher's current media-host version and working **287:4 federal court photo control**, preserving the standing higher-priority 285:5/285:2 queue. Capture desktop/mobile logged-out screenshot; element `src/currentSrc/srcset`; redirect and final Image GET HTTP, content-type, `naturalWidth/Height`, `decode()`, failure events, cold CDP transferred bytes, CLS. **If 287:5 is successfully proxied by Jetpack in actual Chrome, do not call it broken or swap it merely because the older publisher path tool-404s.**

## Visual-history mismatch independent of broken-link question

The actual displayed publisher media photograph shows the old bridge's wreckage, the `Summit Venture` and piers. It **does not show the 1987 cable-stayed replacement**. Yet live WordPress `287:5` ALT reads: “The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.” That wording is unsupported by the visible publisher photo. The adjacent figure caption is a general reflection about the replacement, not an affirmative photo license. Flag this separately as **P1 EDITORIAL**, not a browser-404 count; image crop identity remains unverified for the original stale URL.

## Candidate matrix: primary archival provenance, historically different images

| Target | Catalog/asset | What it shows | Pixel sizing / provenance | Rights and release |
|---|---|---|---|---|
| 287:5 same-filename candidate | [Publisher article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/); [current media host](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) | 1980 collision damage, no replacement | Intrinsic original binary dimensions **not decoded**; `max-width:960px`, calculate height only after master decode; no upscale | Photo credit **University Press of Florida**; **HOLD**, permission not granted. Not binary-proven identical. |
| 287:5 optional *different image* | Florida Memory [K894127](https://www.floridamemory.com/items/show/131903), H. Milo Stewart, circa **1987**; [Commons rendition](https://commons.wikimedia.org/wiki/File:View_of_the_old_and_new_Sunshine_Skyway_bridges_from_St._Petersburg,_Florida,_1987.jpg) | Older cantilever and newer cable-stayed bridges together | Commons original **600×595px**, 46 KB catalog file, proposed max **600×595**, **never enlarge to 960** | Commons uploader labeled CC0, but a third party's tag does **not itself prove authority** to dedicate Stewart's photo. Florida Memory original rights and intended commercial use need item-level review. **HOLD**. |
| 287:5 optional *different image* | Florida Memory [K893521](https://www.floridamemory.com/items/show/131305), Robert M. Overton, **1989** | Aerial old/new bridge comparison | Dimensions not decoded, conditional `≤960px`, no enlargement | **HOLD** for item-level state archives rights and editorial signoff. Later photo, not 1980 wreckage. |
| 287:0 existing control | Stored Washington Post archival photo | 1980 car beside destroyed span | **1024×672 HTML geometry → 960×630** conditional derivative (not actual JPEG master sizing) | No redistribution license presumed; leave original unchanged. |

Florida Memory pages intermittently returned tool-side 403 when opened; item titles, creator/date and IDs were independently found from indexed archival catalog text, and the Commons file page itself was successfully inspected. This **is not a Florida Memory visitor outage**. [NTSB investigation DCA80AM050](https://www.ntsb.gov/investigations/Pages/DCA80AM050.aspx) confirms the accident's chronology but does not supply a license for these independent photos.

## Safe staged resolution, not production deployment

1. **Browser-proof gate:** Site QA #154's **existing** logged-out Chrome/CDP runner must confirm the actual 287:5 Image GET status and decoded render. Work from `currentSrc` after any proxy/transformation. A content-retriever 404 alone does not authorize a rewrite.
2. **Photo-identity gate:** Compare the old published photo where accessible, publisher current asset, and any proposed archive image side by side; record crop, subject, date, attribution and exact page context. Different archival photo → explicit editorial decision, never silent substitution.
3. **Rights gate:** Obtain specific permission or validated applicable public-domain/license metadata from original rights owner. A third-party repost, agency catalog, Commons label, hotlink permission or publisher attribution alone is insufficient for commercial copying. **No unlicensed scraping, hotlink mirroring or downloads.**
4. **Size gate:** Decode an authorized master in staging. Deliver ≤960px-long/width derivative with proportional dimensions, never upscale smaller assets (K894127 only 600px wide). Prefer a responsive `srcset` with smaller variants; select file format after visual QA, not by blindly changing extension. Store original credit, source URL and terms in attachment metadata.
5. **WordPress staging gate:** If approved, upload a licensed file to a **staging** media library only; minimally change this one `wp:image` rather than rewriting article blocks. Preserve text and authorship, correct ALT to what the selected image actually depicts, set intrinsic `width`/`height` or `aspect-ratio`, preserve caption attribution, verify links, lazy loading below fold and display on mobile/desktop. Nothing in this PR makes a WordPress write.
6. **Performance and integrity gate:** Compare the same logged-out cold page/device and request identities **before/after**: CDP encoded/decoded bytes per actual image GET, `currentSrc`, LCP/CLS and visual screenshots. Deduplicate reused requests. The separate [source-identity gate](../qa/media-recovery/claim_source_identity_gate_20261103.cjs) is required before any sitewide 76% transferred-weight claim. A 13-original >1.5MiB storage list is **not** proof of visitor transfer savings.

## Exact artifacts / safety

- [Six original URLs, reader-status matrix, candidates, item-level rights/960px ledger](../qa/media-recovery/skyway_287_original_host_migration_20261104.json).
- [Deterministic fail-closed validator](../qa/media-recovery/validate_skyway_287_20261104.cjs).
- [48-assertion regression suite](../qa/media-recovery/test_skyway_287_20261104.cjs), including **47 mutation cases**; execute with `node qa/media-recovery/test_skyway_287_20261104.cjs` from repository root. Isolated exact-source V8 replay passed; native Node CI and logged-out Chrome not run in this environment.

Scope boundaries: baseline **61 published posts / 355 stored images / 288 offsite-original refs / 13 WordPress originals >1.5MiB**. **42 reported broken images unconfirmed in guest browser; 76% claimed reduction unmeasured; 0 production repairs.** No files downloaded or rehosted, WordPress posts modified, homepage styling changed, existing Site QA drafts rewritten, or subscriptions purchased.
