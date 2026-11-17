# Media recovery evidence — Forrestal post 289, 2026-11-04

**Scope:** source-only recovery engineering in draft PR #183; not a deployment, source-to-browser conclusion, WordPress write, permission to download, or license transfer. Site QA #154 owns guest-browser checks. The interim homepage lead owns homepage visual design.

## Frozen CMS source and independently checked media

The October 30 snapshot `qa/media-recovery/parts/03.json`, Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`, contains six exact external `src`/ALT pairs for article **289**, [They Thought They Had Ten Minutes](https://finalvestige.com/2026/08/19/they-thought-they-had-ten-minutes-forrestal/). This sprint **did not** authenticate against fresh WordPress content. All six frozen image elements lack HTML width and height pairs. Treat any CLS concern as a hypothesis until real lab evidence.

On **2026-11-04**, the independent web image retriever **displayed the exact published source URL** for slots **289:0, :1, :2, :3, :5**, but failed to render `289:4` with a **retriever-wrapper 403**. This is *not* proof that `media.defense.gov` served a 403 to visitors. All actual browser image GET statuses, redirects, final `currentSrc`, pixels/decode, and cold CDP bytes remain **NULL**. Five displays cannot prove that Final Vestige's Jetpack/runtime rendition loaded.

| Slot | Source host | Independent retriever | Authority / candidate | Relationship | Conditional maximum output geometry |
|---|---|---|---|---|---|
| 289:0 | upload.wikimedia.org | displayed | [Commons original catalog](https://commons.wikimedia.org/wiki/File:USS_Forrestal_A-4_Skyhawk_burning.png) (1396×1110) | Catalog match, file not rehashed | 960×763 |
| 289:1 | specials-images.forbesimg.com | displayed | [NHHC / NARA **USN 1126565**](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1126000/USN-1126565.html) (5686×4469) | **Different** firefighting photograph | 960×755 |
| 289:2 | k.sinaimg.cn | displayed | [NHHC / NARA **USN 1124808**](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1124000/USN-1124808.html) (6210×4970) | **Different** after-fire flight-deck photograph | 960×768 |
| 289:3 | k-static.appmobile.cn | displayed | [NHHC / NARA **USN 1126644**](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1126000/USN-1126644.html) (5688×4504) | **Different** firefighting photograph | 960×760 |
| **289:4** | **media.defense.gov** | **retriever wrapper 403** | [DVIDS **6947585** / VIRIN **210811-N-SG189-1105**](https://www.dvidshub.net/image/6947585/farrier-firefighting-school) (5448×3625) | Exact archival VIRIN in published URL; no binary hash | 960×639 |
| 289:5 | d1ldvf68ux039x.cloudfront.net | displayed | [DVIDS **985674** / VIRIN **130726-N-ST310-007**](https://www.dvidshub.net/image/985674/uss-forrestal-memorial-ceremony) (1200×1808) | Exact photo ID in CDN path; no binary hash | 960×1446 |

**Geometry:** listed source dimensions are **catalog metadata for candidate masters**, not decoded image binaries or measurements of published image derivatives. Compute the proposed width as `min(960,catalog_width)` and height as `round(catalog_height * target_width / catalog_width)`. If an actual lawful master differs, abandon these inferred values. No enlargement, automatic cropping, stretched imagery, or forced 960-pixel width. The DVIDS photo 289:5 is portrait, so 960px is a *width cap*, not a height cap.

### Historical provenance and licensing controls

- **289:4 is 2021 simulation training** at Farrier Firefighting School, **not July 29, 1967 footage**. DVIDS attributes it to U.S. Navy MC2 J. Keith Wilson and labels it Public Domain / Released.
- **289:5 is a July 26, 2013 memorial portrait** of instructor Paul Anderson next to Gerald W. Farrier's plaque, not a 1967 on-scene image. DVIDS attributes it to U.S. Navy photographer **David Todd**, lists 1200×1808, and labels it Public Domain / Released.
- The selected NHHC catalog entries for 289:1–3 are historically appropriate subject-level *alternatives*, **not identical scans**. Never use a replacement with ALT/caption claiming it is the previously published photograph or the original crop.
- [NHHC Photo Archives](https://www.history.navy.mil/our-collections/photography.html) says **most, not all** collection photos are public domain, and that the researcher must determine permissions. The listed “Copyright Owner: National Archives” does not establish a general license to reuse every item. DVIDS requires compliance with [its content restrictions](https://www.dvidshub.net/about/copyright). Commons' USGov label is provenance evidence but does not settle binary history and attribution by itself.

**Rights: HOLD for every slot.** Do not download or cache the published third-party photographs or official catalogs, mirror to WordPress, rewrite Gutenberg blocks, or claim a visitor defect based on retriever limitations.

### Proposed WordPress staging sequence — not authorized for execution

1. Site QA finishes existing higher-priority P0 guest-browser queue **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**. Without touching Site QA's scripts, queue **289:4** next for the exact published media.defense.gov source, then inspect 289:1–3 hotlink risks if coverage permits. Record actual final Image GET/status, failed/error text, `currentSrc`, naturalWidth/decode, MIME, cold encoded bytes, screenshots and lab LCP/CLS; distinguish proxy from published URL.
2. If an image is **confirmed broken in visitors' browser**, establish *exact photo identity* for a same-scene replacement. For different NHHC scenes, obtain editorial sign-off for a revised description and event chronology. Rights, credits and item-specific license checks are mandatory.
3. **Only with separate approval and rights clearance**, stage a derivative from the lawful master in a nonproduction isolated directory; integrity/hash record, no-upscale width ≤960, retain colors/crop/historical specificity, compress WebP/JPEG with side-by-side comparison, record actual resulting bytes. Do not promote catalog geometry as file inspection.
4. Obtain explicit approval before WordPress Media Library upload. If publishing is later authorized, preserve existing blocks and links until a tested rollback exists. Confirm before/after real guest-browser decode/currentSrc, visual screenshot, zero unexpected shift, and cold transferred-byte attribution. Revert on broken image, identity mismatch, attribution discrepancy or content degradation.

### Evidence and reproducibility

- [Six-slot machine-readable status + candidate/rights ledger](../qa/media-recovery/forrestal_289_nhhc_dvids_20261104.json).
- [Fail-closed offline validator](../qa/media-recovery/validate_forrestal_289_20261104.cjs).
- [23 mutation and positive regression cases](../qa/media-recovery/test_forrestal_289_20261104.cjs): validated **23/23 against the exact committed blobs in a V8 compatibility harness** (not native Node or real Chrome).
- Note: `chrome 403` is not established; **289:4 observed only a tool-wrapper 403**. No verified error rates, actual image-transferred bytes, 76% savings, media copies, WordPress writes, subscription spend or homepage changes.

Site-wide October 30 baseline remains **61 posts / 355 inline sources / 288 external-origin sources / 13 WordPress originals >1.5MiB**; claimed “42 broken” remains browser-unconfirmed and “76% transfer reduction” remains unmeasured. **Production repairs remain zero**.
