# Media Recovery — Archimedes post 268: ten-image source and rights review
**2026-11-01. Independent draft PR #183, not deployed.**

## Observed and verified
Authenticated **read-only WordPress** post 268 (*They Painted Over Archimedes*), published, modified **2026-10-30T01:10:13**, was re-read via `posts.get(context=edit)`. Each of ten actual Gutenberg `<img>` **exact source URLs and full ALT texts** equals the frozen post-268 census in `qa/media-recovery/parts/04.json`, Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`. Escaping/quotes are handled in the readback comparison (an apostrophe inside a double-quoted ALT is not a delimiter).

This verifies the CMS's stored source only. Neither a working page nor a failed visitor image is proven. **No guest-browser HTTP statuses, encoded-transfer bytes or natural image dimensions are available.** A direct network probe from the isolated tool runner failed DNS for the site and official external domains **before HTTP**.

### Actual source-URL access observations from an independent web retriever
* `268:1` — `https://archimedespalimpsest.org/assets/img/imaging_x8.jpg`: **rendered in retriever**; subject appears to be the obscured/painted page. Status code, response transfer bytes, original pixel dimensions and guest-browser result **unknown**.
* `268:7` — `https://archimedespalimpsest.org/assets/img/imaging_x12.jpg`: **rendered in retriever**; imaging/scanning apparatus visible. Browser result and transfer **unknown**.
* `268:4` — `https://www.archimedespalimpsest.org/assets/img/imagecapture-capture2b.jpg`: retriever attempted a **www → apex** redirect, but **could not display** the apex target. Not an HTTP-404 or a confirmed broken site image.
* `268:8` — `https://archimedespalimpsest.org/assets/img/imaging_x9.jpg`: retriever could not display. No guest-browser status established.
* `268:0, 2, 3, 5, 6, 9`: six exact Commons `Special:Redirect/file` URLs were not displayed by the retriever; **their individual Commons file catalog pages were retrievable**. This is a tool/redirect limitation, not six verified failures.

Only **2/10** source URLs rendered in the retriever; the other **8/10 are inconclusive**, NOT eight broken photos. All statuses in the machine-readable ledger remain **null**, as they should.

## Exact file records, rights differences and no-upscale 960px proposals
| Slot | Publisher/catalog | Original file dimensions (catalog metadata only) | Conditional target | Individual rights gate |
|---|---|---:|---:|---|
| 268:0 | [Commons: Archimedes Palimpsest.jpg](https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg) | 665×448 | **665×448**; never enlarge | Commons claims public domain in US; original Matthew Kon attribution; validate underlying image rights |
| 268:1 | Project site `imaging_x8.jpg` | Unknown | Hold | Site presentation photo; no proven item-level license |
| 268:2 | [Commons file 9737603804](https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg) | 10880×8160 | **960×720** | Commons CC BY 2.0 badge vs project dataset CC BY 3.0 description |
| 268:3 | [Commons file 9737623542](https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg) | 2040×2720 | **960×1280** | Same CC BY 2.0 / CC BY 3.0 metadata discrepancy |
| 268:4 | Project site `imagecapture-capture2b.jpg` | Unknown | Hold | Site presentation photograph; no proven item-level license |
| 268:5 | [Commons file 9734386225](https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg) | 8160×10880 | **960×1280** | CC BY 2.0 on file; project dataset uses CC BY 3.0 language |
| 268:6 | [Commons file 9734104759](https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg) | 8160×10880 | **960×1280** | Same split; XRF credits also implicate SLAC |
| 268:7 | Project site `imaging_x12.jpg` | Unknown | Hold | Site presentation photo; no proven item-level license |
| 268:8 | Project site `imaging_x9.jpg` | Unknown | Hold | Site presentation photo; no proven item-level license |
| 268:9 | [Commons file 9734660151](https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg) | 6600×9500 | **960×1382** | Same CC BY 2.0 / CC BY 3.0 metadata discrepancy |

**Why license scopes must remain separate:** The project's [2008 primary dataset README](https://archimedespalimpsest.net/0_ReadMe.html) says its **digital data set** is licensed under **CC BY 3.0 Unported**. The [TEI consortium's independent description](https://tei-c.org/activities/projects/archimedes-palimpsest-project/) corroborates that dataset release. However, the *five individual Commons file pages* display **CC BY 2.0** as their active file-license badge while carrying a description mentioning CC BY 3.0. Conservatively preserve both references and apply the correct item-specific license and attribution after review. Crucially, **neither dataset-wide declaration automatically proves that four separate Project website presentation JPEGs are licensed for republishing**. Do not download them, treat hotlink access as a license, or silently substitute a related folio.

## Explicit release sequence (currently HOLD)
1. Site QA #154 conducts ordinary network-connected **logged-out Chrome desktop and mobile**, scrolls fully to lazy-load, records exact post slot, active `currentSrc`, Image-request final URL/status/MIME/bytes, `naturalWidth`, the redirect chain, screenshot and profile. Start **268:8 and 268:4** (retriever inconclusive), then remaining sources; coordinate rather than duplicating Site QA's classifier.
2. Media Recovery proves a candidate is **the exact same historic photograph** (image/crop/folio), determines per-file rights and the complete credit/license/change notice, and documents original SHA-256. For the four site photographs, get a specific reuse basis or leave the external reference pending. Do not rely on a different but visually similar page.
3. Only with source rights and separate approval, create a derivative at **min(original width, 960)**, aspect preserved and never upscale; preserve manuscript handwriting readability and XRF coloration; record local master and output hashes, encoded byte sizes, and review side-by-side image quality. The six Commons source dimensions here are from catalog records and **not** browser `currentSrc`.
4. Stage an approved cached/WordPress Media Library image and source-credit metadata *without* overwriting existing files or changing Gutenberg blocks. Any **production** media upload or post edit requires separate explicit authorization, guarded backup/diff and independent acceptance check. This sprint authorizes **none**.
5. Measure real *before and after* page image network bytes under the identical Chromium viewport/cache/scroll protocol and visual acceptance. The previous `76%` is an unproven assertion; an image **restored from failure** is not a compressor saving. Previous `42 broken images` likewise remains unverified.

## Delivered safety QA
* `qa/media-recovery/archimedes_268_source_rights_20261101.json`: ten full exact original URL+ALT source records, viewer state distinctly classified as retriever-only, archival file links and original dimensions where verifiable, rights holds and proposed ≤960px dimensions.
* `qa/media-recovery/validate_archimedes_268.cjs`: deterministic fail-closed validator against existing `parts/04.json` (no duplicate Site QA source classifier); verifies the **same exact Commons filename** in each stored redirect and catalog page, and rejects malformed/null catalog records.
* `qa/media-recovery/test_archimedes_268.cjs`: 31 native Node tests on the exact committed source blobs (one positive + 26 adversarial), with verified local Git blob equality; all **31/31 pass**. The exact committed validator was also executed in isolated V8 against the actual committed full source census and new manifest: **PASS, zero errors**. Hosted CI and real Chrome not executed.

**Site-wide context unchanged:** 61 published posts, 355 stored image-reference slots, 288 external slots / 286 distinct external URLs, 13 Media Library originals >1.5 MiB; 42 alleged broken photos and 76% claimed reduction not verified. **Production images repaired: 0.** Zero WordPress content/media writes, no raw media downloads or mirrors, homepage design untouched, no subscriptions or costs.
