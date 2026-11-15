# Final fourteen external images: completed archival research coverage, not confirmed repairs (2026-11-10)

**DRAFT PR #1703 only. NO WORDPRESS WRITES, DOWNLOADS, CACHE, LICENSE APPROVAL, DEPLOYMENT OR HOMEPAGE DESIGN CHANGES.** Site QA #154 owns logged-out browser confirmation.

## Result
Read-only WordPress raw published HTML checked against the frozen October 30 census for posts **190, 274, 288, 431**. All **14/14** exact original src URLs match. Historical ALT equality was not tested. These are the final 14 slots in the 61-post, 288-external-image recovery register. **288/288 now have at least one source-research record, 293 evidence records; zero guest browser failures have been verified.** Do not confuse the final 14 with the separate historical claim of 42 broken third-party images.

Independent web retriever displayed 10 exact stored originals, failed for 4 (190:1, 274:3, 274:6, 431:5). Failures are wrapper errors, **not origin 404**. Direct native HTTP from isolated container had DNS resolution errors; source GET statuses, transferred bytes, decoded dimensions and visitor experience remain unmeasured.

## Exact source mapping and conditional width

| Slot | Web retriever observation | Primary/catalog attribution | Candidate max pixels | Priority |
|---|---|---|---|---|
| 190:1 | Retriever unavailable | Library of Congress, stereo 1s46043; William H. Rau (1904) | Native uncertain | P1 |
| 274:0 | Displayed | Naval History and Heritage Command, NH 42273 | 960×587 | P1 |
| 274:3 | Retriever unavailable | NHHC NH 45641; V-5 crewman A.L. Rosenkotter at after escape hatch, July 1930 | Native uncertain | P1 |
| 274:5 | Displayed | U.S. Navy/National Archives photograph 80-G-227991, Commons catalog | 960×703 | P2 |
| 274:6 | Retriever unavailable | NHHC/NARA official Navy photo 80-G-227989 | 960×780 | P1 |
| 288:1 | Displayed | NHHC NH 69059; museum-held/donated historical photograph | 960×753 | P2 |
| 288:3 | Displayed | NHHC NH 84820, photograph by Aston | 960×801 | P2 |
| 288:4 | Displayed | NHHC NH 84822; photograph by Aston | 960×778 | P2 |
| 288:5 | Displayed | U.S. Naval Institute, Proceedings magazine historical photo (primary photographic catalog unlocated) | Native uncertain | P1 |
| 431:1 | Displayed | ASCE Geo-Institute case study; underlying historical map source to confirm | Native uncertain | P1 |
| 431:2 | Displayed | Provincial Archives of Alberta A15276 via Wikimedia Commons | 960×728 | P1 |
| 431:3 | Displayed | ASCE Geo-Institute case study; appears credited to Mei et al. (2008) context, exact figure unconfirmed | Native uncertain | P1 |
| 431:4 | Displayed | Alberta Geological Survey; Dr. John Allan 1934 danger-zone map | Native uncertain | P1 |
| 431:5 | Retriever unavailable | Fourtildas, own photographic work, 24 Sep 2006; Wikimedia Commons | 960×720 | P1 |

All exact source URLs, current ALT, proposed ALT, rights restrictions, archival catalog URLs and guest status nulls are in [machine-readable audit](../qa/media-recovery/remaining_14_all_primary_provenance_live_20261110.json). Numeric size limits refer to a catalog original and assume identity validation; they are not proof of the deployed derivative's resolution. Never enlarge a smaller image. Maps and scientific drawings require zoomable native versions with legible labels.

## High-value visual findings requiring *manual* review
- **288:5 — incorrect photographic perspective.** Published ALT says *aerial* but USNI source depicts an elevated **shoreline** perspective of destroyers. Correct only with editorial approval.
- **431:4 — misleading time context.** AGS confirms this is **Dr John Allan's 1934 danger-zone map**, not a 1903 contemporary hazard map. Preserve blue/red danger-zone keys and all labels.
- **431:2 — pre-slide chronology.** Provincial Archives of Alberta A15276 identifies the photo as **before** the 1903 disaster. Commons flags need for a separate US public-domain rationale despite Canadian PD status.
- **431:3 — annotated photographic composite.** Yellow highlighted aerial zone plus a separate geographic inset require accessibility and legibility; secondary publication has no established licensing.
- **274:0 — unsupported motion.** NHHC NH42273 captions Tang **off** Mare Island; existing 'underway' ALT goes further than the cited historical record.
- **274:3 — retriever failure, reliable primary candidate.** NHHC NH45641 / Navy photo 030808-N-0000X-001 depicts Rosenkotter testing the Momsen lung in 1930; verify exact original vs secondary press file before substitution.
- **190:1 — vintage stereograph.** LOC 1s46043 says Engine 15 **deserted** in Hurst Building collapse; LOC copyright notice says William H. Rau, 1904 and no known restrictions (not federal authorship). Preserve stereograph pairing/labels.
- **288:1, 288:3, 288:4 — exact Navy catalog numbers** NH69059, NH84820, NH84822 matched visible printed labels. The latter two are credited to photographer Aston, and NH69059 to San Francisco Maritime Museum; archival custody does not itself prove US-government authorship.

## Rights/copyright policy
- **US Navy 274:0 and 274:5** archival descriptions give credible federal-government PD rationale. Verify the exact posted image and derivative provenance; **no rights are pre-cleared**.
- **288:1/3/4** private/donated photos in NHHC custody require item-level US publication/license review.
- **431:1/3** modern ASCE Geo-Institute images may incorporate protected scholarly diagrams, aerial composites and maps. No mirror.
- **431:4** Alberta Geological Survey hosting does not grant blanket commercial reuse.
- **431:5** Fourtildas 2006 photo is licensed **CC BY-SA 3.0/GFDL**; if reused, apply exact attribution, author/license links, and change/derivative obligations.
- **190:1** LOC no-known-restrictions advisory is not a government work claim.

## WordPress staging plan
1. Site QA #154 uses its existing collector to visit the six P0 originals **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**; then test the four additional inaccessible sources from this batch. Record post URL, actual final `currentSrc`, GET response, `img.complete`, `naturalWidth/Height`, `PerformanceResourceTiming.encodedBodySize/transferSize`, blocked/CORS and console messages, plus screenshots at 360 and 1280 CSS px. Cached vs cold runs must be distinguishable.
2. Only if truly missing, match exact artwork and scene with catalog original. Obtain item-specific commercial reproduction permission/PD rationale, file-version metadata, attribution and accessible ALT. Do not swap one historical scene for a different one merely because it illustrates same topic.
3. In separate staging-only approval, use rights-cleared source, compute aspect-correct <=960px width, generate modern compressed formats where suitable, retain high-resolution zoom for charts/maps, upload **only** authorized asset through WordPress Media Library, record new media ID and rollback metadata. No Gutenberg post block rewrite without an explicit approved mapping and diff.
4. Compare page-level image transfers, LCP and CLS, cached and cold mobile/desktop, before/after. **76% reduction must be computed from measured cold transferred image bytes**, `100 × (baseline - after) / baseline`; do not substitute attachment disk size or sum of duplicated URLs. Record `srcset`, DPR and CDN rewrites.
5. Maintain the established 15 originals >1,500,000 bytes / **47,096,779** stored bytes worklist. `docs/IMAGE-WEIGHT-WORKLIST.md` was not available on default or recovery branch; this is a historical baseline, not a fresh live media measurement.

## Verification
- Source: frozen 2026-10-30 61-post inventory and read-only 2026-11-10 WordPress `posts_get(context=edit)` for four posts.
- Checked with [fail-closed validator](../qa/media-recovery/validate_complete_288_20261110.cjs) and [17 native Node test cases](../qa/media-recovery/test_complete_288_20261110.cjs) when available; isolated V8 invariant checks before commit. Native CI/Chrome have not been run in this environment.
- Files here are audit and QA only; no first-party media assets are embedded. Site QA own draft #154 is untouched.
