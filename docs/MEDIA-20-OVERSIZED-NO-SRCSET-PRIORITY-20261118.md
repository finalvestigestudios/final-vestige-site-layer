# Oversized originals: evidence-based inline priority — 2026-11-18 06:22 PST

**Draft only / HOLD.** Scope is published investigation image performance, *not* interim lead's homepage design. This is a reproducible **metadata classification**, not image download, traffic benchmark, WordPress patch or authorization to localize a photograph.

## Basis and reconciled threshold

Historical `docs/IMAGE-WEIGHT-WORKLIST.md` is not at current `main` or this draft's head; its intact historic Git blob is `9cdf7af84175883775aaebf55ffa5ca77b33e423` (2026-10-30, 61 published posts). The pinned updated [20-original media-to-inline crosswalk](../qa/media-recovery/live_20_oversized_to_66_post_inline_crosswalk_20261117.json) is Git blob `66aa70b1982237015b87b1901ea0100fe9e64181`, based on the November 17 **66-post** published corpus.

The new [20-item machine ledger](../qa/media-recovery/oversize_20_inline_priority_20261118.json) and [fail-closed validator](../qa/media-recovery/oversize_20_inline_priority_20261118.cjs) separate a strict decimal **1.5 MB = 1,500,000 bytes** from binary **1.5 MiB = 1,572,864 bytes**: **20** originals exceed decimal MB but **19** exceed MiB. Halifax map media #1714 (1,543,002 bytes, post 269:1) accounts for the one-item unit-threshold difference in the November 17 cohort. The historical October 30 count of 13 >1.5 MiB also reflects a *different media inventory/date*, so the two reports must not be directly treated as a like-for-like trend.

## Major actionable finding: five published inline PNGs lacking srcset

Five **first-party Jetpack URLs** in the original 66-post crosswalk explicitly have `has_srcset=false`, all request `resize=1024,576`, and their **five uncompressed/stored originals sum to 13,267,538 bytes**. These are best **incremental bandwidth-measurement candidates** after visitor-failure P0 checks, *not* proven 13.27MB network downloads:

| Slot | Stored original bytes | Published article |
| --- | ---: | --- |
| 34:0 | 2,892,087 | [San Francisco lost its water](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) |
| 38:0 | 2,836,245 | [The cisterns beneath San Francisco](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) |
| 35:0 | 2,552,136 | [The boat that refused to die](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) |
| 36:0 | 2,498,247 | [The city that went underground](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) |
| 37:0 | 2,488,823 | [How Petra made water flow through stone](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) |

The ledger preserves the actual published `i0.wp.com` URL and exact owning post for each row; all live GET status, browser `currentSrc`, decoded raster, response hash and transferred byte fields are **null**. A public retriever opened the [Malbone article](https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/) today, but separate image requests were inaccessible to that retriever; container DNS also failed for i0.wp.com. Neither is a verified user-visible image failure.

**Other reconciled lanes:** 11/20 stored originals have exactly one source-URL-matched inline slot, totaling 38,480,915 *stored* bytes. Six of those 11 have srcset and need selection measurement, including Malbone 621:0 and 621:1; 9/20 originals representing 25,904,837 stored bytes have **no exact inline use in these 66 posts**, not proof of orphaning on pages, featured media, downloads or unpublished content. Do not delete them.

## Site QA #154 handoff, not a duplicate collector

1. **Visitor missing-image priority remains first:** slots 285:5, 285:2, 287:5, 418:1, 418:2, 407:1 and Tang 274:6. Independent source-level 403/404 findings do not prove failures through Jetpack.
2. **Next measure 34:0, 38:0, 35:0, 36:0 and 37:0**, then Malbone 621:0–1 at desktop and mobile with Site QA's *existing* logged-out Chromium collector. Capture loaded `currentSrc`, final HTTP GET, decode, true decoded encoded raster size, content SHA-256, unique cold network request IDs and body/wire bytes, source screenshot, LCP and CLS. Distinguish original library storage from transfer. Record page revisions and identical capture conditions for any subsequent staging comparison.
3. Before proposing a 960px target, confirm native raster pixel dimensions, aspect ratio, legibility, caption and item-specific reprocessing rights. Even a first-party upload can originate from someone else's copyrighted archive. Reject upscaling, arbitrary lookalikes, license/credit removal, and unexpected image crops.
4. For an authorized exact image only, create a **staging-only** proportionate derivative with width `min(960,native_width)`; compare raster SHA, subject/credit, accessibility and actual bytes; plan a reversible WordPress Media Library attachment/reference update *only after explicit approval*. Do not rewrite Gutenberg blocks or overwrite masters.
5. The headline **76% reduction** remains **unverified** without complete, reproducible before/after transfer logs, unique request accounting and independent visual comparison. The 61-post historical cohort must be compared with itself rather than conflated with the newer 66-post census.

**All statuses:** 42 supposed missing browser images unknown; rights clearance HOLD; production writes 0; rehosts 0; homepage changes 0; subscription spend $0; merge and deploy prohibited. [15-case native Node regression suite](../qa/media-recovery/test_oversize_20_inline_priority_20261118.cjs) exercises unit counts, exact URL/source and false-claim guards. Full CI/guest Chromium remains separate and pending.
