# Media recovery: published-page sources and New London podcast image integrity — 2026-11-06

**Workstream:** Media Recovery PR #1228, complementary to Site QA #154 and existing image recovery PR #183. All actions read-only to WordPress. No homepage design changes, image copies, caching, CMS writes or spend.

## Additional WordPress page cohort — previously outside article audit

WordPress `pages.list(status=publish, per_page=100)` returned **83 published pages** on November 6. This is a distinct content type from the 66 published article `posts` (legacy report: 61 posts / 355 stored inline `<img>` refs; more recent read-only post recensus: 66 / 361). **Do not add page and post counts without reconciling routes and duplicate browser requests.** Only the eight high-priority pages below were fully read using `pages.get(context=edit)`; **not** a complete 83-page image scan. The source-only 8-page audit is `qa/media-recovery/eight_priority_pages_markup_media_20261106.json`, anchored to blob `460644e0228412b38f3e9e6e3a1508e02e47f539`.

| Page | Stored inline images | Material observation |
|---|---:|---|
| 2088 Mini Museum | 1 | Awin dynamic creative `/cshow.php`, no declared dimensions; **do not cache or remove tracking** |
| 2089 Cold Case | 1 | Another Awin dynamic `/cshow.php`, no declared dimensions |
| 2017 Apollo 1 Evidence Atlas | 3 | Three local Final Vestige NASA-referenced uploads, stored with dimensions; may require independent reuse documentation |
| 1484 New London podcast episode | 4 | One Google Drive thumbnail `sz=w1600` + three Commons images; all four missing explicit dimensions |
| 1579 Focus fieldbook | 2 | First-party WebP images with dimensions |
| 6 Home | 4 | Three first-party images + one Final Vestige Jetpack transform; **read only, design remains with interim lead** |
| 1868 Preparedness Archive | 0 | No stored inline `<img>` in page source, not a claim of no rendered CSS/JS media |
| 1304 Public Record | 0 | Same limitation |

**Eight pages, 15 source-level inline references:** 8 first-party, 1 first-party Jetpack, 3 direct Wikimedia, 2 Awin dynamically served banners and 1 Google Drive thumbnail. **Six stored references lack explicit dimensions.** WordPress source is not a browser: no CSS background-image, responsive picture selection, theme image, JavaScript-created image, featured media, or other network dependency is thereby verified. These page images are additional review candidates, **not 15 new broken images**.

## Four exact podcast image slots: primary catalog crosswalk

All four sources and their stored ALT were read directly from live WordPress page 1484 on Nov 6. Audited sources, conditional geometry and rights gates are in `qa/media-recovery/podcast_1484_drive_commons_four_20261106.json`.

| Slot | Current source and historical identity | Catalog native pixels | Safe maximum-width preview | Rights/recovery hold |
|---|---|---|---|---|
| **1484:0** | `drive.google.com/thumbnail?id=1V8rMf0ovXiJbJLLq77uLwfMHghlH7sMM&sz=w1600`, podcast artwork | **UNKNOWN** | **UNKNOWN** | Google Drive thumbnail is a dynamic external dependency; `w1600` is a request parameter, **not** measured pixel geometry or transfer bytes. Ownership, permissions, actual origin/visitor status and archival original must be checked. Do **not** download/rehost on URL alone. |
| **1484:1** | New London School **before** 1937 explosion; [Commons catalog](https://commons.wikimedia.org/wiki/File:New_London_School_before_explosion.webp) | **960×685** | **960×685** | Commons asserts public-domain status in US based on nonrenewal, with territorial caveat; individual source provenance/right review remains HOLD. No enlargement. |
| **1484:2** | New London School **ruins** after explosion; [Commons catalog](https://commons.wikimedia.org/wiki/File:New_London_School_explosion.jpg) | **760×609** | **760×609** | Commons asserts US public-domain nonrenewal, cites Associated Press original; requires item-level verification, especially AP history. **Never upscale to 960** or replace with a different crop. |
| **1484:3** | **2016** modern New London memorial; [Commons catalog](https://commons.wikimedia.org/wiki/File:New_London_School_Explosion_Memorial.jpg) | **3840×2160** | **960×540** | **CC BY-SA 2.0** by QuesterMark; attribute author, original and license, identify any image modification, review share-alike obligations. This is **not a 1937 event photo**. Derivative unmade and republication HOLD. |

One important historical-detail control: Commons reports the ruins photograph's catalog metadata with a 17 March 1937 date yet its description depicts aftermath of the **March 18, 1937 explosion**. Treat catalog metadata as source data, not justification to change the known event date or article caption. Neither scene should be swapped with an image from another era.

**Awin caution:** Landing-page ad creatives are externally controlled affiliate display images with tracking/attribution functions. Reserve layout geometry only after measuring decoded natural dimensions in a guest browser; changing image URLs or self-hosting banners could break commercial attribution and may violate merchant licensing. This audit does not approve it.

## Safe restoration and optimization sequence

1. **Keep Site QA's existing browser collector and P0 queue.** Verify visitor-facing failures of 285:5 / 285:2 / 287:5 / 418:1 / 418:2 / 407:1 **before** expanding to 1484:0 and the six dimensionless page assets. Capture the actual logged-out desktop/mobile `currentSrc`, Chrome Image HTTP status/failure, `naturalWidth`/`naturalHeight`, network cache flags and actual encoded transfer bytes. A web-retriever wrapper 403/404 is **not** guest-browser failure evidence.
2. For a **confirmed failing** page 1484 image, first match the **exact scene**, archival license and attribution. For Drive artwork, get proof of rights and a legitimate original from the owner. Preserve pre-event / aftermath / contemporary memorial identities.
3. Only after item-level rights clearance, create a locally staged **≤960px, no-upscale** derivative, preserving aspect and no irreversible crop. Where the source is <=960px already, keep its native dimension; preserve zoom access for detailed maps and diagrams.
4. QA in staging: compare natural pixel dimensions, image decoding, ALT/caption context, 960px/no-upscale, credits and CC BY-SA terms; measure paired **cold browser image wire bytes** using the existing Media Recovery measurement gates. Backup original markup and document rollback. Seek explicit production publication authorization before any WordPress write.
5. **Do not advertise 76% savings from 13 WordPress originals' 43,522,829 stored bytes.** The 13 records are >1.5 MiB in storage, not necessarily emitted at that size on the wire. Five PNGs from posts 34–38 with no responsive subsizes and two Malbone JPEGs remain optimization candidates **behind actual missing images**.

## Evidence and QA

- Existing `docs/IMAGE-WEIGHT-WORKLIST.md` is readable on PR **#183 branch** `qa/media-recovery-reviewed-20261030-1158`, but was not present on **main** when checked. It already contains a six-image guest adjudicator and cold network measurement logic; **no duplicate browser collector** was added.
- New four-slot validator `qa/media-recovery/validate_podcast_1484_20261106.cjs` requires exact current URLs, catalog identity, explicit unknown guest HTTP and bytes, rights HOLD, distinct historical scenes, and no-upscale output.
- `qa/media-recovery/test_podcast_1484_20261106.cjs`: **24/24 committed-source regression checks passed** using an isolated V8 Node-compatible adapter. **Native Node CI and actual guest browser remain unexecuted**.
- Current guest-verified 42 broken: **UNKNOWN**, not confirmed. Achieved 76% browser-transferred savings: **UNKNOWN**, not measured. WordPress production writes **0**, repaired images **0**, downloaded third-party binaries **0**, third-party caches **0**, homepage design edits **0**, extra spend **$0**.

This is a source-verified expansion beyond the post-only 66/361 inventory. It does **not** establish that the podcast artwork or affiliate banners actually fail. The next useful trigger is Site QA's logged-out failure record, after which image-by-image restoration can proceed through rights and visual-review gates.
