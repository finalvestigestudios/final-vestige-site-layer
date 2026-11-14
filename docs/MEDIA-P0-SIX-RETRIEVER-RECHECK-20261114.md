# FV Media Recovery — Six P0 sources, refreshed external-retriever disposition (14 Nov 2026)

**Evidence boundary:** Six exact published image URLs from the prior read-only WordPress editor snapshot of 8 November (ledger Git blob `04df35ce25f99626c7b754c1d7eed0f3f006e3f4`) were rechecked through the independent web retriever on 14 November. These are **web-tool wrappers, not origin HTTP or logged-out browser status codes**. WordPress editor source was **not freshly re-read** in this batch. No page-image bytes, cold Chrome results or network transfer sizes were collected.

| Slot | Fresh wrapper outcome | Exact candidate / provenance | Disposition |
|---|---|---|---|
| 285:5 | 404 Not Found | [Commons 2010 TMI photo](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg), PD-self catalog, 819×614; **different year/frame** from incident photo | Different-scene editorial alternative only; HOLD |
| 285:2 | 500 inaccessible redirected target | [UCS migrated image path](https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg) also inaccessible in retriever; technical NRC figure identity and rights unresolved | HOLD |
| 287:5 | 404 Not Found | [Same-publisher relocated JPEG](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) **renders** 1980 wreckage and Summit Venture, **not** the later replacement bridge; publisher credits University Press of Florida | No automatic relink, copy or inaccurate ALT; HOLD |
| 418:1 | 403 Forbidden | [Coast Guard catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/), inaccessible to retriever; prior VIRIN/public-domain assertion requires item-level review | HOLD |
| 418:2 | 403 Forbidden | [Lighthousefriends same-basename debris image](https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg) renders; exact bytes, crop, Coast Guard Museum courtesy rights unverified | HOLD |
| 407:1 | 400 unsupported binary/octet-stream | USGS same-record thumbnail lead; tool MIME limitation does not establish site breakage | HOLD |

Complete original URLs, date-stamped method-specific results, candidate relationships, item-level rights holds, natural-dimension unknowns and no-upscale 960px constraints are in [machine-readable audit](../qa/media-recovery/p0_six_retriever_recheck_20261114.json). This is a prioritized P0 handoff, **not** a new all-post census.

## Repair order and quality gates

1. **Site QA #154 owns the guest CDP collector** and must first capture each original image's actual `currentSrc`, final request status/MIME, request/redirect identities, uncached event chain, decoded natural dimensions, rendered CSS box/DPR and true encoded bytes. Do not translate web 403/404/500 into guest 403/404/500.
2. If a particular image is proven broken, select between a same-photo same-publisher relocation (identity and permission still required) or a **different archival scene** requiring explicit editorial approval and accurate ALT/caption/date. Navy, Coast Guard, Florida Memory and USGS catalog hosting does **not** automatically authorize copying.
3. Before staged First-Party WordPress Media, verify exact item reuse rights, attribution, visual scene and crop, native dimensions and a conditional proportional derivative width = min(native width,960), with **no upscaling**. A 960px image at DPR2 is full density only to 480 CSS px; map labels and sharpness require independent visual review.
4. Any proposed replacement is reversible and review-only, with old URL retained for rollback. Measure actual cold network bytes with source-equivalent duplicate-transfer accounting; 76% reduction remains **unmeasured**. No Gutenberg post-block rewrites until separately approved.

The new validator pins the six original/candidate URL identities and rights descriptions, refuses fabricated origin/guest results or permission changes, and keeps every replacement on HOLD. **63/63 native Node.js tests passed** plus source syntax and validator CLI locally on the committed-input files. No repository CI or real Chrome tests were executed.

Historical benchmark remains **61 posts / 355 stored images**, with **288 offsite media references** in Media versus Site QA's **286** (two documented proxy-origin classification differences). The reported **42 broken images have not been verified by guest browser**. The latest 16 WordPress originals over 1.5 decimal MB hold 49,107,665 **stored** bytes—not established visitor wire bytes.

**Scope separation:** Media recovery-only files on draft #1655; zero overlap intended with Site QA #154's browser collector or interim lead's homepage design. No image binaries copied, third-party caching, WordPress production changes, merges, deployments or subscription costs.
