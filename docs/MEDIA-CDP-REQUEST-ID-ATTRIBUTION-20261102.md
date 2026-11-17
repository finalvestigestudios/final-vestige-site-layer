# Media Recovery — CDP request identity, unbound image traffic, and five-source recheck
**Date:** 2026-11-02  | **Scope:** draft media-engineering PR #183 only  | **Status:** no production modifications

## Defect reproduced and corrected

The historical image browser classifier formerly selected the **last** matching Chrome DevTools Protocol (CDP) `Image` response for a DOM `currentSrc`, using canonical URL equivalence and `findLast()`. If a page made two actual network requests for the same photograph (preload, responsive rendition, retry, theme use, or a repeated request), one could return HTTP 200 while another returned 404. Associating the later request with the DOM element could wrongly assert that a historical photograph was missing or loaded.

Article-photo network-byte accounting also attributed every matching canonical URL to the article, even without evidence that a specific request was used to display its DOM image. That can count a same-photo preload or unrelated UI request as article bytes, distorting a purported percentage reduction.

The correction is **conservative, not a new repair**:
1. The Chrome monitor retains the CDP `Network.requestWillBeSent` `requestId` through redirect, response, and loading events. The classifier now publishes `request_id`, `matching_cdp_image_request_count` and `ambiguous_network_request_identity`.
2. A stored image with **multiple matching independent Image requests** is `ambiguous_network_request_identity`, not confirmed broken or verified loaded. This can temporarily reduce completed census coverage, intentionally. A redirect chain under one CDP ID remains one request.
3. New `qa/media-recovery/request_id_wire_core.cjs` measures article bytes **only** from unique, precisely matched CDP request IDs attached to successfully decoded, network-verified stored image slots. Two DOM image slots may share one CDP request and count bytes once. An extra unbound request for the same canonical historical image fails the complete page-weight gate instead of being silently credited as savings. Unrelated logo/UI traffic remains excluded.
4. `browser_probe_chrome.cjs` emits `probe_version:4`, `article_wire_attribution_mode:'strict_cdp_request_id'`, `article_wire_evidence_complete`, and reason codes. `compare_wire_core.cjs` requires these v4 attestations on **both** before/after runs. Legacy v3 runs are deliberately **not comparable** for a savings-grade claim. No schema upgrade claims are inferred for older files.

This fix is within Media Recovery #183 and does **not** edit the independent Site QA #154 implementation.

## Verification

**190/190 isolated JavaScript regression cases passed** against actual GitHub-committed sources using an explicit URL/URLSearchParams and CommonJS compatibility shim: 74 request-ID/comparison/CDP-integration cases and 116 existing classification/census/transfer/proxy/redirect cases. The Chrome module also parsed in isolation. These are **not** native Node CI runs, real browser requests, measured visitor transfers, or production acceptance tests.

New tests include a same-URL 200/404 CDP conflict; two 403s; two successes with an unbound request; distinct historical crop selectors; same-filename Commons redirects; first-party Jetpack resize identity; a unique bound retry; cached and transport-failed image responses; duplicate network IDs; shared DOM uses; extra unbound size-variant requests; logo traffic exclusions; and synthetic v4 before/after comparison.

**Exact commits (in order):**

| Commit | Deliverable |
|---|---|
| `375c874e7759dc51d9d80561fbe302fd498fb5eb` | strict request-ID wire core |
| `f44f00b49936c6286296693157b8dbe2f3d6a610` | 23 request-ID wire regression cases |
| `ecbcfa3401091d50ad8765df2101faf2077c6839` | expose CDP ID in slot classifier |
| `dd003033af54bb6f8dbedde32556d08d3607c18e` | v4 browser monitor and strict wire provenance |
| `dcd7977341dbeb832e7cdda1e3cc9fc02661e89e` | v4 paired-comparison evidence gate |
| `6827e7ae781f1471b48c85678eaf36ea35417d5e` | v4 synthetic comparison fixtures |
| `2073d9a1ebb1f3b9418df5f3a5cea97c0287649f` | explicit ID for unrelated chrome fixture |
| `20a94f0b6446d40e4e7e13e6d7959e37232f4f3c` | remove ambiguous `findLast` attribution |
| `b119981ea57f96dda69af03c71d8fe28b3c35723` | 9 ambiguity regressions |
| `ccc4fb43e994b105c618172486a939db3eb3f36e` | 6 event-to-classifier-to-wire CDP regressions |
| `1baf5caef657a9c9a455a887d3c86fbdb121e3e7` | P0 five-source recheck ledger |

The five-source ledger is `qa/media-recovery/p0_retriever_status_recheck_20261102.json`; this is **independent web-retriever evidence**, not guest Chrome or origin server status.

## Five priority external-source checks

| Image | Published URL | Independent web-retriever result | Institutional or publisher recovery route |
|---|---|---|---|
| Three Mile Island **285:5** | `https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg` | retriever 404; **not verified origin/browser 404** | NARA April 10, 1979 aerial image, NAID 540012 (different photograph). NARA “No Known Copyright” note is not item-level reuse approval. |
| Sunshine Skyway **287:5** | `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` | retriever 404; **not verified visitor failure** | Relocated publisher `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` rendered 1000×649 in web viewer; publisher credits University Press of Florida. Redistribution permission **HOLD**. Image shows 1980 aftermath, while current ALT mentions later replacement bridge. |
| Hebgen Lake **407:1** | `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg` | retriever 400 **unsupported binary/octet-stream**; **not origin 400** | USGS catalog credits J. R. Stacy, labels item public domain; alternate Original path `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg` displayed as 1000×1000 viewer image. Exact binary identity and guest decode **HOLD**. |
| Scotch Cap **418:1** | `https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG` | retriever 403; **not verified browser 403** | Official USCG photo catalog item `https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/` links the same VIRIN. Official item identifies public-domain/cleared status and credit/DoD usage restrictions; binary hash missing. |
| Scotch Cap **418:2** | `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg` | retriever 403; **not verified browser 403** | National Coast Guard Museum article publishes a same-named **debris2** derivative at **600×463**. Distinct *debris1/debris3* scenes are explicitly excluded; redistribution rights and binary match **HOLD**. |

Viewer sizes **are not verified original-master intrinsic sizes**. Conditional illustrative bounds: publisher Skyway viewer **960×623**; USGS square viewer **960×960**; Museum Scotch Cap **600×463**, **never upscale**. All require actual source-binary and visual fidelity validation before creating a 960px rendition. For 285:5 and 418:1, do not invent geometry.

## Source cache and WordPress media plan (NOT executed)

First ask Site QA #154 for logged-out desktop/mobile browser proof: actual `src` and `currentSrc`, all CDP Image request IDs/redirect chains and final HTTP/MIME, `naturalWidth/Height`, exact element screenshot, cache state, wire bytes and confirmed identity. For canonical URL collisions, retain all request IDs as unresolved unless an explicit DOM↔CDP correlation can be established. A 42-image broken count remains *unverified*.

For a verified missing asset, prioritize **same-scene** archival file from the named authoritative primary catalog, check creator and third-party rights **per item**, record accession/photographer/date and intended caption, compare pixel content and source hash, and obtain reproduction clearance where necessary. With authorization, create a derivative **at most 960 pixels wide, aspect preserved, no upscaling**, test on an isolated staging page including CSS aspect ratios and accessible ALT, and capture equivalent before/after logged-out image waterfalls. Only after separate production approval should the WordPress Media Library host the rights-cleared derivative with stable attachment metadata, responsive `srcset`, cache headers, and reversible original URL/caption inventory. This engineering PR does not perform any of those media writes, edits or downloads.

**Performance comparison conditions:** only the same published image identities, same content and screenshot quality, same browser/viewport/scroll coverage, cache-disabled uncached Image requests, and complete v4 request-ID evidence can support a ratio `100×(before_article_wire_bytes−after_article_wire_bytes)/before_article_wire_bytes`. A missing, HTTP-failed, blocked or indecipherable image contributes *unknown*, never an artificial zero-byte optimization saving. The claimed **76%** is still not measured.

## Status and handoff

Frozen scope remains **61 published posts, 355 stored image references, 288 external references and 13 WordPress originals above 1.5 MiB**. The five 1672×941 inline PNGs without recorded 1024px variants total **13,267,538 original storage bytes**; whether visitors download full originals is unknown. The headline **42 reported broken images remain unverified**, the **76% weight reduction remains unmeasured**, and **0 production images have been repaired**.

No unlicensed scraping, image binaries downloaded/copied, copyright permissions assumed, production WordPress changes, post-block rewrites, homepage visual-design edits, Site QA draft edits, or subscription spend occurred. Native Node CI and a working logged-out Chrome CDP network pass are still needed to confirm the fix under a real browser. All release conditions are **CLOSED/HOLD** until met.
