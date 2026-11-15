# Image recovery, post 276 — Quebec Bridge (read-only, 2026-11-10)

**DRAFT / DO NOT MERGE / NO PRODUCTION WRITE.** Media-engineering scope only. Homepage visual design belongs to interim lead; Site QA #154 owns guest Chromium/CDP full-scroll browser verification.

## Exact CMS evidence and external-image observations

Historical, fixed **2026-10-30** corpus remains **61 published posts, 355 inline image references, 288 external-origin image positions**. A bounded six-source test fixture copied the `276:0–276:5` original URLs, ALT descriptions, and HTML-declared geometry from PR #183 `qa/media-recovery/parts/04.json`, original Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`. No newer WordPress readback is claimed for post 276. Live guest and origin HTTP statuses, decoded geometry and wire transfer bytes all remain **null**.

Machine-readable row-by-row exact URL audit: [`qa/media-recovery/quebec_276_six_1907_1916_archival_20261110.json`](../qa/media-recovery/quebec_276_six_1907_1916_archival_20261110.json), Git blob `fd39d7d055007974ec2c6d0dda3dd850b7053395`.

| Slot | Original host | Independent **web retriever** observation on exact published URL | Primary archival context | Conditional <=960px reference |
|---|---|---|---|---|
| 276:0 | cdn2.picryl.com | Image displayed | British Library Canadian Copyright Collection **HS85/10/18815**, F. E. Cudworth, bridge *under construction in 1907* | Commons archival 2,780×2,180 → **960×753**, not proof of PICRYL JPEG intrinsic size |
| 276:1 | historicbridges.org | Image displayed | HistoricBridges reproduction of the August 1907 **first collapse** wreckage, original source attributed in surrounding historical material to government engineers' 1919 report | **Unknown native JPEG**; Gutenberg's 1024×832 is declared geometry, not a measured original |
| 276:2 | ids.si.edu | Image displayed | **Exact Smithsonian/NMAH IDS** `NMAH-AC1026-0000002` in Quebec Bridge Photograph Collection (1907–1965) | **Unknown native JPEG**; hold |
| 276:3 | quebecblogue.com | Web retriever **520** error | Publisher exact-photo identity unresolved; nearby Smithsonian collection is only a **different-photo editorial alternative** | Unknown; hold |
| 276:4 | cdn2.picryl.com | Image displayed | **Separate 11 September 1916 center-span collapse**, PICRYL Commons-derived image; Commons category describes a 12,000×9,000 **TIFF** | TIFF reference **960×720** only; do not infer published JPEG native geometry or pixel identity |
| 276:5 | historicbridges.org | Image displayed | Completed bridge in historical reproduction; HistoricBridges cites 1919 engineering publications | Unknown native JPEG; Gutenberg 1024×607 declared, not confirmed intrinsic |

**Important:** web-image preview and wrapper 520 are **not browser CDP, direct origin HTTP status, image decode, or cold transfer size**. In particular **276:3 is a priority candidate for Site QA** but not yet confirmed broken.

## Visual-integrity / history gates

1. **276:0 pre-collapse date:** stored ALT currently says "shortly before" the 1907 failure. British Library/Commons catalog identifies only **1907** and does not independently substantiate how many days/hours before the collapse the photo was taken. Proposed ALT in audit removes the unsupported timing without changing published content.
2. **276:4 is 1916, not the 1907 disaster:** The second center-span lifting failure must be explicitly separated from the original southern-arm collapse. Never silently replace the 1916 scene with a visually plausible 1907 wreckage photo.
3. **276:2 is an exact Smithsonian image endpoint** but item-specific `CC0`/reuse authorization not established. National museum hosting is not universal rights clearance.
4. **HistoricBridges photographs are reproductions** of historical sources (some government reports), but publisher transformation/crop and specific source authorship require verification.
5. **276:3 has no confirmed identical-scene archival candidate.** Do not replace a publisher JPEG with a random wreckage photograph or call the failed text retriever a site 404.

Sources: [British Library-origin Commons catalog](https://commons.wikimedia.org/wiki/File:Quebec_bridge_(HS85-10-18815).jpg); [Smithsonian finding aid](https://americanhistory.si.edu/collections/archival-collection/sova-nmah-ac-1026); [HistoricBridges first/second bridge narrative](https://historicbridges.org/bridges/browser/?bridgebrowser=quebec/quebec/); [PICRYL 1916 caption](https://picryl.com/media/quebec-bridge-collapse-of-the-suspended-span-5a20eb); [Wikimedia 1916 TIFF category](https://commons.wikimedia.org/wiki/Category:Bridge_collapses_in_Canada). PICRYL/Commons *public-domain labels* and archival custody are **observations**, not final item-specific licenses or identical-image proof.

## Rights-first, reversible media restoration plan (NOT executed)

- **Gate 1 — failure proof:** Site QA's existing logged-out CDP full-scroll collector records `post/slot, stored original src, currentSrc, GET status, cache flags, naturalWidth/naturalHeight, decoded pixels, transferSize / encodedDataLength, timeline, viewport`. Triage failed image loads and blocked/unsupported formats. Site QA retains P0 queue `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1` ahead of 276:3. Do not duplicate its collector.
- **Gate 2 — candidate archival identity:** for each proved-broken original, obtain first-party item/creator, date, scene/crop match and item ID. If substitute is a **different** photo, flag as editorial substitution, not recovery. Document attribution and licenses for U.S. *and* Canadian material. 1907 vs 1916 categorization is mandatory.
- **Gate 3 — media rights, image quality:** only with cleared, documented permission, stage a locally reproducible derivative `width=min(960,verified_native_width)`, preserve aspect ratio/colour/legibility, provide a higher-resolution source link for detailed drawings. Capture bytes, SHA-256, visual crop comparison, ALT and provenance. Never upscale or assume Commons TIFF = PICRYL JPEG.
- **Gate 4 — staged WP Media, never automatic post rewrite:** after a separate publication authorization, prepare optional WordPress Media Library upload as **unpublished** stage with attribution metadata and a stable first-party media URL; test image URLs and source licensing. Keep original CMS block HTML untouched until an editor signs off on exactly which `src`/ALT change will be made, and retain the original serialized block for byte-for-byte rollback. **No WP upload or block rewrite is approved here.**
- **Gate 5 — performance measurement:** run same browser/viewport, logged-out, no service worker, cache-cold baseline and candidate captures. Pair post+slot and exact source/approved scene identity. Define `saving_pct = 100*(sum(original_image_wire_bytes)-sum(candidate_image_wire_bytes))/sum(original_image_wire_bytes)` only for successfully observed uncached image requests and matched cohorts. Do not add stored WordPress file sizes, CDN estimated bytes, or failed loads to denominator. Track LCP/CLS and mobile appearance after any staged source swap.

## Existing site-wide baselines, not achieved reductions

The **42 reportedly broken third-party originals are not yet proven broken in a real guest browser**; independent retriever errors cannot certify them. The proposed **76% reduction in transferred image weight is UNMEASURED**. The more recent **66-post/361-image** live set must not be mixed with historical **61-post/355-image** baseline. **15 media-library original files strictly >1,500,000 bytes** sum to **47,096,779 stored-original bytes**; 11 are referenced in eight published posts and total **38,480,915 original bytes**, but these are not guest transfers. Preserve maps and engineering-diagram readability; no blind 960px compression.

The full 288-position reconciliation [`coverage_240_exact_pr1703_20261110.json`](../qa/media-recovery/coverage_240_exact_pr1703_20261110.json), Git blob `8a68908881f9c0d9d7af95ed78cf65a86ff4fcae`, now has **240 unique researched / 48 pending / 245 source-evidence rows**, retaining 282 unrelated rows verbatim. Six image-source positions researched is not six images repaired.

## Technical verification and strict release outcome

Files and exact Git blob SHA identifiers:

- Six-image audit: `fd39d7d055007974ec2c6d0dda3dd850b7053395`
- Reconciled 288-position register: `8a68908881f9c0d9d7af95ed78cf65a86ff4fcae`
- Frozen six-source fixture: `fce71a16786e2c6b5ff80d7d0b7ce754067f94b5`
- Evidence verifier: `611363375b0813774eec12bbaabbf0ddd6dde197`
- Regression suite: `cdb4a7ff9311464a6551e638b9a1eaa8d2ed5265`

**30/30 postcommit tests PASSED** using isolated V8 with Node-compatible shims against all five exact committed GitHub files, plus zero validator findings. **Actual native Node CI and genuine guest Chrome/CDP have not run.** The source-custody and release-gate code is deliberately offline. **Zero** binary downloads, caches, WordPress media/post writes, homepage changes, merges or spending. Remain **DRAFT / HOLD**.
