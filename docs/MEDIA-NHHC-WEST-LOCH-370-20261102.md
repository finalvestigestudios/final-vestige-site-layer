# Media recovery — West Loch post 370 NHHC source crosswalk (2026-11-02)

**Scope:** Read-only investigation of **all eight current-source image slots** in *The Lines Were in the Fire*. The four offsite `history.navy.mil/bin/imageDownload` dependencies have exact original-source archival catalog matches; the other four slots already use `finalvestige.com/wp-content/uploads/` and must not be rehosted without a demonstrated issue. This batch is not a confirmed missing-image count or production repair. Media Recovery PR #183 only; Site QA PR #154 owns guest-browser checks.

## Primary-source identity and evidence

| Slot | NHHC primary record | Date and scene | Independent exact image URL retrieval |
|---|---|---|---|
| 370:0 | [80-G-276907](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276907.html) | 1944-05-21 West Loch burning LSTs, T-8/T-9 | web retriever timeout, HTTP null |
| 370:1 | [80-G-202485](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/80-G-202000/80-G-202485.html) | **1943-11-06 Bougainville**, comparative USS LST-353 scene, NOT the West Loch disaster | retriever inaccessible, HTTP null |
| 370:3 | [80-G-276940](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276940.html) | 1944-05-22 grounded, burned USS LST-39 | web retriever timeout, HTTP null |
| 370:4 | [SC 427947](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/sc-series/SC-400000/SC-427947.html) | 1944-05-22 firefighter scene, **Army Signal Corps Collection** | retriever inaccessible, HTTP null |

The 370:4 catalog says the nearby vessel was **probably** USCGC *Woodbine* and the destroyed ship **may be** USS LST-480. Do not silently convert those possibilities into categorical captions. The 370:1 photograph documents the same ship in 1943—not the 1944 explosion. Image selector (`image=`) must be retained when matching the Navy dynamic endpoint; `rendition=` selects presentation size, not photo identity.

Official NHHC pages advertise 319×319 and 1280×1280 low/medium **rendition labels**, but these labels do **not** establish actual decoded image dimensions. The catalog's high-resolution TIFF metadata are 4320×4530 (370:0), 5860×4890 (370:1), 6254×5002 (370:3), and 6084×4942 (370:4). These are **not** measured dimensions of the displayed JPEGs. Thus the image derivative is **max width 960 px, no upscaling, height unknown until real image bytes + orientation verified**. No JPEG was downloaded, hashed, resized, or rehosted.

## Rights and reproduction gates

NHHC [Photo Archives guidance](https://www.history.navy.mil/our-collections/photography.html) says most photographs are public domain but that its collection includes privately donated/other-origin images; staff do not conclusively confirm copyright and users remain responsible for clearance. NHHC [scanning and citation policy](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) says **official government photos** can be reproduced with appropriate archive credit; it does not mean every NHHC-hosted photograph may be mirrored. NARA custody alone is not copyright proof. For 370:0/1/3 the item itself identifies a U.S. Navy photograph; 370:4 is explicitly Army Signal Corps origin. Before release, verify the precise binary, item-level rights/credit and the selected scene/crop; preserve creator, title/archival number, event date and original caption qualifications. All `rights_cleared_for_rehosting`, `wp_media_upload_allowed`, and `post_rewrite_allowed` remain **false**.

## Safe WordPress cache/recovery plan — staged, not executed

1. Site QA #154 first checks guest logged-out Chrome at desktop/mobile for each slot: `img.currentSrc`, `complete`, `naturalWidth`, decoded dimensions, **CDP request ID**, final response URL/status/MIME, cache headers, encoded transfer bytes, and screenshot. Retrievers timing out or blocking are **not** browser 404s.
2. If a specific image is truly broken, inspect the archive-approved original/medium binary under explicit rights clearance, compare to historical published identity, calculate SHA-256, and produce an **sRGB 960-pixel maximum-width non-upscaled** WebP/JPEG candidate with original aspect and EXIF orientation; retain a credited master separately. The 1280×1280 rendition label must not be misread as a square image.
3. Stage only the approved derivative as a new WordPress Media Library attachment with provenance, credit/licensing note and preserved ALT/caption. Avoid post-wide Gutenberg block rewrites. Isolate one image-slot substitution with post revision/backup and revert plan; do **not** touch homepage visual design.
4. Compare guest browser image rendering and request-ID attributable bytes before/after, retain screenshots and rollback proof. No production edits under the present permission boundary.

## Reproducibility

Machine ledger: `qa/media-recovery/nhhc_west_loch_370_source_crosswalk_20261102.json` (source part `02.json`, blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`). Offline validator/test: `validate_nhhc_west_loch_20261102.cjs` and `test_nhhc_west_loch_20261102.cjs`. **30/30 cases PASS** in *post-commit isolated V8 replay with URL compatibility shims*, including 27 fail-closed data mutations and dynamic Navy selector tests. **Native Node CI and actual browser metrics remain unexecuted**.

Site-wide baseline unchanged: **61 published posts, 355 source image refs, 288 third-party origin refs, 13 WP originals >1.5 MiB**. **42 reported failures not browser-verified, 76% savings not measured, and 0 production media repairs**. No downloads, unlicensed scraping, subscription spend, WordPress writes or Site QA draft edits.
