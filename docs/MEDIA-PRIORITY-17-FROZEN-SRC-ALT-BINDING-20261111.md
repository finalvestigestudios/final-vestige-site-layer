# Media recovery: exact-source-bound 6 P0 + 11 P1 evidence — 2026-11-11 Pacific

**Status:** isolated draft code and audit only. **No WordPress/site writes, no image downloads, caching/rehosting, rights decisions, homepage work, merges, deploys, new browser collector, or subscription spending.**

## Proven source-level batch

Recovered `docs/IMAGE-WEIGHT-WORKLIST.md` from draft PR [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) (blob `2acd06a4ca4317646006eb6591face3fe76fedec`); it is **not** on `main`. Reconciled all eight frozen Oct 30 Gutenberg source parts **61 posts / 355 inline image slots** against the existing six-item P0 browser handoff and 15 original media records.

New [17-row machine-readable exact-source ledger](../qa/media-recovery/priority_17_frozen_source_binding_20261111.json):
* **6 P0 suspected third-party failures:** original HTML `src`, exact post URL/slot/ALT, original independent *retriever wrapper* observation and authoritative candidate catalog; **all guest HTTP, physical decode and transferred network bytes remain null**.
* **11 P1 inline-referenced >1.5 million-byte originals**, exactly matched by `post_id` **and actual published `src`** rather than merely attachment name. They span 8 posts (34–38, 269, 299, 621), and their original files total **38,480,915 stored bytes**. Importantly, Jetpack 1024-width delivery URLs in post 299 are **not** the same as native-size stored original URLs.
* The full oversized media inventory has **15** originals and **47,096,779 original stored bytes**. The four unmatched originals have not been proven unused in featured images, pages or custom components; **do not delete**. This total establishes neither transferred visitor bytes nor the proposed **76%** saving.

The ledger pins all eight exact frozen Git blob hashes and the bridge blob `d1a9c7a499510ec37bcdba5858d45165752587e0`. It does not represent live browser evidence, copyright clearance or production approval.

## Reproduced measurement integrity issue — frozen source not enforced

Existing `measure_image_transfer_pair_20261111.cjs` only matched source-ledger **SHA as a string**, expected slot identifiers, stable `image_identity`, and CDP current/request URLs. It did **not** compare the slot's stored Gutenberg original source URL or ALT with the **actual frozen record**. Therefore a synthetic valid-looking cold image pair from an unrelated photograph could return a post-level reduction while purporting to represent an inventory-bound slot.

New [frozen-source-bound comparator](../qa/media-recovery/compare_priority_17_frozen_source_pair_20261111.cjs) adds a **fail-closed step before the already existing transfer + selected-physical-pixel visual-parity evaluator**:

1. Validate the pinned 17-row 61/355 snapshot, six P0/eleven P1 groups, native dimensions and stored-original totals.
2. Require exact `post_id`, canonical post URL, slot key, baseline **and** candidate `stored_original_src`, `dom_img_src`, and `dom_alt` against frozen archival source. Candidate asset URL/crop changes still pass through the existing independent rights and scene gates; no implicit licensing decision.
3. A P0 URL can only become `SOURCE_BOUND_ONLY_SITE_QA_P0_ADJUDICATION_REQUIRED`; **web-retriever 403/404/500 cannot be transmuted into a guest HTTP status**. Site QA #154 alone collects and adjudicates logged-out Chrome CDP evidence.
4. P1 comparison must also pass completed, uncached HTTP 200 image-body request evidence, distinct request-ID byte accounting, selected-resource **physical** dimensions at DPR, unchanged crop/object-fit and identity. The resulting status is deliberately **priority subset only**, never whole-page, CWV, sitewide saving or publication approval.

36 isolated V8 Node-compatible regression tests against the exact GitHub committed source **PASS (36/36)**: alternate source/ALT, wrong page, fake guest status, cached HTML or 404, missing CDP body, tiny physical pixels at 2× DPR, changed crop, P0-to-P1 confusion, Jetpack original-vs-delivery mismatch, exact and sub-76% synthetic byte ratios. **Native Node CI and genuine logged-out Chromium remain unrun.** No production change has been validated.

## Priority source/rights and conditional width queue

| Priority | Position | Authoritative lead | Historical scene / rights gate | Width |
| --- | --- | --- | --- | --- |
| P0 | 285:5 | [Wikimedia Commons TMI 2010 photograph](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) | Public-domain claim at item; published 16:9 crop from 4:3 source requires framing parity | 819×614 max; no upscale |
| P0 | 285:2 | [1979 President's Commission report](https://www.tmia.com/sites/tmia.com/files/media/Presidents-Commission.pdf) | Emergency-feedwater maintenance tags, **not** the PORV command-indicator scene; retouched-source and federal authorship/rights review | 604×590 candidate; no upscale |
| P0 | 287:5 | [Florida Memory RC09236](https://floridamemory.com/items/show/32082) | 1980-05-09 accident photograph **different** from original publisher image; chronology/photographer/reuse review | Native pixel dimensions unresolved; no automatic 960px |
| P0 | 418:1 | [U.S. Coast Guard accession](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) | Chief Pettit **portrait**, not the destroyed lighthouse; catalog PD statement needs item-specific verification | Native dimensions unresolved |
| P0 | 418:2 | [National Coast Guard Museum archive](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) | Same ruins scene credited USCG; no demonstrated binary identity, item rights or full native dimensions | Museum preview 600×463, not proof of original resolution |
| P0 | 407:1 | [USGS 1959 Hebgen Lake fault scarp catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) | USGS original-source URL lineage / J. R. Stacy credit; guest browser and actual dimensions outstanding | Unknown pending binary/selected-resource evidence |

For the 11 P1 original files, the ledger retains the conditional maximum-width derivative dimensions (up to 960px). The Halifax image is a detailed map; it must retain a legible zoom/original rather than be compressed solely for a byte target. The five 1672×941 reconstructions have unverified creator rights; Vasa imagery carries item and museum-credit restrictions. **None is approved for WordPress rehosting**.

## Required safe execution order

First, Site QA's **existing** guest collector checks `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`; capture page/slot, stored and selected src, response redirects and MIME, CDP final Image status, `dataReceived` body, completed encoded bytes, cache flags, natural dimensions, current-resource physical decoded dimensions, DPR, painted CSS/crop, screenshot hash and failed request lifecycle. This exact bound ledger is a read-only evidence review input, **not** a competing collector.

Only after a real failed image is confirmed, independently review same-scene photograph, copyright license and attribution, natural pixels, 960px no-upscale target, and staging comparison. A WordPress media cache/upload plan must be manually authorized in a separate change, with source ID, immutable original URL, licensed asset provenance, credit/caption and rollback, never a direct hotlink/mirror based on wrapper 403/404.

For any later 76% claim: collect **two or more matched full 61-post / 355-slot uncached guest runs** with stable browser profile and scroll, *all* article Image request IDs and unique completed network-byte totals, content/asset/ALT parity, before-and-after performance and readability evidence; compare `(sum(before unique actual CDP encoded bytes) - sum(after)) / sum(before)`, **not** stored originals, simple averages or only 11 selected files. An additional 66-post snapshot is a separate cohort and must never be silently combined.

**Current state:** 42 historical alleged failures are **not confirmed by available visitor-browser evidence**; no actual 76% reduction measured; production image repairs 0. All source changes remain HOLD until independent visual, historical and rights approvals.
