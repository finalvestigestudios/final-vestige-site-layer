# St. Francis Dam / post 166 — six-source archival media recovery (Nov 10, 2026)

**Isolated engineering draft only. DO NOT MERGE OR DEPLOY. No WordPress writes, public media changes, third-party binary downloads/caching, paid APIs, homepage design, or duplication of Site QA #154's browser collector.**

> **Additional live WordPress source verification, Nov 10:** Authenticated **read-only** `posts_get(context=edit)` returned published post #166, last modified `2026-11-02T21:39:29`. Extracted all **7/7** live Gutenberg `<img>` source URLs and ALT strings (one first-party and six external), with **7/7 literal URL and ALT matches** to frozen Oct 30 fixture. [Exact machine-readable live readback](../qa/media-recovery/stfrancis_166_live_wp_source_match_20261110.json). This establishes that the historical six external dependencies **remain embedded in the live post**, NOT that the browser loads/decodes them successfully or that reuse rights are cleared. No WordPress write occurred. This readback was created after the first 25-test archival validator snapshot; all original audit and reconciliation SHA pins remain intact.

## Exact frozen sources and retrieval semantics

The Oct 30 published-source fixture `qa/media-recovery/parts/07.json` (Git blob `21095161e633aba093b74c0ead9936c9f6186d00`) records six external image positions **166:1–166:6** in [They Checked the Dam That Morning](https://finalvestige.com/2026/08/18/they-checked-the-dam-that-morning/). Every literal source URL and stored ALT matches the 288-position recovery census. The six exact source endpoints were opened through a **web text retriever** Nov 10; all six were **tool-inaccessible**. This does **not** mean six real 404/403 origin errors, failed image decodes, or visitor-visible broken images. We have **no direct origin HTTP status, cold guest browser/CDP status, runtime-selected src, decoded intrinsic geometry, response transfer bytes, or binary identity**. All those fields remain NULL.

[Six-slot machine-readable audit](../qa/media-recovery/stfrancis_166_six_loc_usgs_ucla_20261110.json) · [full 288-position register, 228 researched](../qa/media-recovery/coverage_228_exact_pr1703_20261110.json) · [fail-closed validator](../qa/media-recovery/validate_stfrancis_166_20261110.cjs) · [25-case regression suite](../qa/media-recovery/test_stfrancis_166_20261110.cjs).

| Slot | Exact-source catalog/primary record | Catalog pixels | Conditional <=960 px | Rights / integrity hold |
| --- | --- | ---: | ---: | --- |
| 166:1 | [LOC HAER CA-298](https://www.loc.gov/item/ca3095/), original `tile.loc.gov/.../sheet/00002a.gif` | unknown | **unknown** | LOC's compilation dates **after 1968**, not an eyewitness 1928 illustration; exact drawing sheet content, underlying copy rights, and small-label legibility unverified. |
| 166:2 | [Commons St. Francis abutment](https://commons.wikimedia.org/wiki/File:St._Francis_abutment.jpg); USGS H.T. Stearns 682 | 1,400×806 | **960×553** | Commons federal-work/PD attribution; direct original USGS page unavailable. Original-crop and credit check. |
| 166:3 | [Commons Twisted Tracks](https://commons.wikimedia.org/wiki/File:Twisted_Tracks.jpg); [USGS Flickr item](https://www.flickr.com/photos/usgeologicalsurvey/11449413284/) | 1,400×1,017 | **960×697** | Commons identifies **CC BY 2.0** Flickr transfer. Preserve photographer/agency, required license link, changes notice; do not waive attribution based only on USGS origin. |
| 166:4 | [Commons St. Francis after failure](https://commons.wikimedia.org/wiki/File:St._Francis_Dam_after_the_1928_failure.jpg); USGS H.T. Stearns 665 | 1,400×1,043 | **960×715** | Post-disaster March 17, 1928 view, Commons PD-USGS claim; primary USGS binary unverified. |
| 166:5 | [Commons Standing section](https://commons.wikimedia.org/wiki/File:Standing_section.jpg); LAPL TESSA | 1,250×936 | **960×719** | **Priority rights/ALT issue**: Commons applies a US **1931–1963 publication/nonrenewal** rationale while describing a **1928 photo**; actual publication date and renewals unknown. Caption calls it “central” section, while catalog says remnant of the eastern side. Do not assume PD or exact location. |
| 166:6 | [Commons man at crack](https://commons.wikimedia.org/wiki/File:Man_pointing_at_crack_in_Saint_Francis_Dam_after_its_collapse.jpg); [UCLA Los Angeles Daily News collection](https://digital.library.ucla.edu/catalog/ark:/21198/zz00253zg8) | 4,431×5,760 | **960×1,248** | Commons page shows **CC BY 4.0**; structured metadata also mentions **BY-SA 4.0**. UCLA direct catalog access denied. Clarify controlling rights/attribution and whether caption's “surviving block” is visually provable. |

**Geometry is a *calculation from catalog metadata only*:** `targetWidth=min(960, catalogWidth); targetHeight=round(catalogHeight*targetWidth/catalogWidth)`. This is **not a prepared or approved derivative** and not the image currently delivered to visitors. The LOC drawing requires a separate technical-diagram readability decision, not blind 960px downscaling. In particular, a 960px-wide portrait image can still be much taller than 960px while preserving aspect ratio.

### Caption proposals, NOT publication authorizations

- **166:5:** “A remaining standing section of St. Francis Dam and adjacent wreckage after the 1928 collapse.”
- **166:6:** “A man points to a crack in damaged St. Francis Dam concrete following the March 1928 collapse.”
- **166:1:** describe only the HAER Los Angeles Aqueduct documentation until sheet 00002a's actual map content is independently inspected. A later HAER survey cannot be labeled a contemporary 1928 eyewitness image.

## Reversible, rights-gated first-party delivery proposal

1. Site QA #154 acquires real **logged-out**, fully scrolled desktop+mobile Chrome/CDP evidence for the six pinned P0 failures first: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Preserve the immutable published source key, effective `currentSrc`, cold uncached source/redirect HTTP, `naturalWidth×naturalHeight`, waterfall bytes, screenshots, and reproduction count. Only treat a *genuinely confirmed failure* as restoration work.
2. For any confirmed broken item, document exact archival catalog/photograph scene and original license **per item**; where a museum/agency hosts a copy it is not proof the photograph is government-authored. Record mandatory author, institution, license URL, modifications, caption/context and credit. Disallow candidate substitution across different photographs unless separately justified and editor approved.
3. After rights and scene identity are approved, create a **staged first-party WordPress Media Library copy** only under separate explicit production authorization. Prepare lossless archival source preservation and a <=960px web rendition with no upscale (retain separate zoom/full-quality link for text-heavy drawings). Compute pre/post color and visual diffs; preserve original crops, captions, semantic ALT, layout height, historical date and attribution.
4. Publish by individually reviewed, reversible post edits only after a full backup/source-block checksum and approval; retain original URL/ALT/attachment ID for rollback, with guest tests on desktop/mobile and CWV `LCP/CLS`. No scripted mass Gutenberg block rewrite, no blanket third-party mirroring, no rehosting until authorized.

## Weight/claim controls

Historic **61 posts / 355 inline images / 288 external-origin slots** is the Oct 30 frozen research denominator, distinct from the later **66 posts / 361 tags** live snapshot. Research coverage **228/288 = 79.2%** is not site image health. A count of **42 “broken images” is not guest-browser confirmed**. The desired **76% weight reduction is not measured**: report `(sum(cold_original_matched_slot_bytes) - sum(cold_candidate_matched_slot_bytes)) / sum(cold_original_matched_slot_bytes)` only after a same-cohort, uncached, complete before/after CDP network+decode capture, with source/scene integrity gated; do not treat new photo substitutions as a compression comparison. No savings can be calculated if either cohort is incomplete or denominator zero.

**15 WordPress original files >1,500,000 bytes** (decimal threshold) account for **47,096,779 stored original bytes**. Eleven appear inline in eight newer posts, but these bytes are not visitor transfer bytes, and the other four must not be assumed unused. Those P1 optimizations follow actual P0 breakage triage.

## Engineering evidence and exclusions

- Batch audit Git blob **`fc3edafdb8c3fe0e49027e3276b952e49cb59672`**.
- Reconciled 288-position ledger Git blob **`7093fc6f58f085074c0832bf141510b42496dc8e`**; only **166:1–166:6** changed versus the previous 222-register blob `d5db23b0ac958a6f3438f147500b54d9b0511bfc`. All **other 282** rows preserved verbatim.
- Source validator blob **`034952ad07fbcabee60b9768a46037fa471401e4`** and regression suite blob **`7eb9a7c9ef6b1ce4c56991a3a362c1f8b75c08c4`**.
- **25/25** isolated V8 execution of the committed tests **PASS**, including URL/ALT fidelity, unknown HTTP/visitor fields, zero external-media publication permissions, rights constraints, true conditional sizing, other-row immutability and corpus coverage. **Native Node tests/CI and authentic Chrome remain outstanding.**
- No photo binaries were acquired, downloaded or cached. No WordPress production post/media writes, image rehosting, homepage CSS/visual work, deployments, paid API calls, or subscriptions. This draft is **NOT ready to merge**.

Site QA #154 retains the sole guest-browser evidence collector; do not duplicate or modify its draft.
