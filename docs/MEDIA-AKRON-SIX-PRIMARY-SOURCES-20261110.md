# USS Akron media recovery — six exact original-source candidates (2026-11-10)

**Independent draft only. NO WordPress/public writes, no third-party image downloads/cache/mirroring, no homepage changes, no new collector, no spend or merge.** Existing Site QA PR #154 owns logged-out browser/CDP verification and the six P0 slots.

## Scope, provenance, and actual status

Read-only WordPress edit-source inspection showed all six original Wikimedia `Special:Redirect/file` URLs still embedded in published post **219**, with context-specific ALT descriptions. Each literal URL matches the October 30 frozen 61-post / 355-image inventory. All six exact redirect endpoints were attempted with the independent web text retriever on November 10 and returned **tool-inaccessible** (not actual guest browser or image origin HTTP 400/403/404). The Navy and Commons catalog pages were reachable as text, enabling archival *metadata* research. No image binaries, redirects, decoded dimensions, actual visitor bytes, cache-hit flags or native photographs were acquired. Every actual guest HTTP/wire/decode field remains `null`.

The source-bound six-row audit is [akron_219_six_navy_20261110.json](../qa/media-recovery/akron_219_six_navy_20261110.json); the exact 288-slot research register is [coverage_194_exact_pr1703_20261110.json](../qa/media-recovery/coverage_194_exact_pr1703_20261110.json). Their evidence is research, **not a confirmed restoration or proof of 6 broken images**.

## Source-identity mapping and conditional dimensions

| Slot | Catalog identification, scene and date | Catalog pixel metadata → conditional max-width 960px |
|---|---|---|
| 219:0 | Official U.S. Navy **80-G-1009363**, Akron over Lincoln Memorial, Washington DC, 1931–33 | 2650×2190 → **960×793** |
| 219:1 | NHHC **NH 43900**, Akron over lower Manhattan, circa 1931–33 | 5516×4241 → **960×738** |
| 219:2 | NHHC **NH 98039**, Akron off Panama Canal Zone with N2Y-1 in hangar opening, **March 15, 1933** | 5482×4160 → **960×729** |
| 219:3 | Navy **80-G-463185**, Akron launches N2Y-1 off Lakehurst, **May 4, 1932** | 740×581 → **740×581, no upscale** |
| 219:4 | NHHC **NH 97977**, approaching unspecified mooring mast, circa 1931–33 | 740×586 → **740×586, no upscale** |
| 219:5 | Commons `Akron kitchen.jpg` (Navy Recruiting Bureau provenance, original creator unidentified), crew member getting water at a wash basin | 590×765 → **590×765, no upscale** |

Catalog URLs and exact published redirect URLs, source dates, proposed ALT, creator/rights notes and release `false` flags are in the JSON ledger.

**Highest priority editorial/rights finding:** for **219:2 / NH 98039**, the U.S. Navy *primary catalog* describes an **official U.S. Army Air Corps photograph**. The Commons derivative tags it as a Navy federal work with U.S. Navy author. Those labels must not be collapsed into a claim that the Navy photographed the scene. Even if qualifying federal work can be public domain in the U.S., identify its actual authoring agency and reproduction provenance before declaring the Commons-specific file cleared. Proposed ALT adds the proper agency credit.

**Image provenance pitfalls:** The Commons versions of 219:3 and 219:4 were cropped to remove caption bars; their pixels are not proved identical to the larger official archival images. Source for 219:5 was *received by* a Navy office, which does not alone establish the original photographer or rights. The filename calls it a “kitchen,” but the scene is a crew member getting water at a wash basin; the site's existing ALT already makes that distinction correctly. 219:4 should not be swapped for Navy NH 42156, which documents a **different** mooring-approach scene in Sunnyvale.

The 5516×4241 Commons Manhattan original is listed around 14.06 MB, and NH 98039 PNG around 5.51 MB, but the published WordPress redirect explicitly requests `width=1280`. These original-file sizes **cannot** be claimed as visitor image transfers. Three of the published `?width=1280` sources have catalog original widths of just **740, 740 and 590px**; image delivery could avoid wasteful upsizing, but even that is not an observed transfer reduction.

## Read-only → staged restoration, only if visitor failure confirmed

1. **Site QA #154 (no duplicate collector)** tests the six original high-priority slots **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1** in logged-out guest Chromium first, then Akron 219 as appropriate. Capture exact `currentSrc`, full-scroll `img.complete`, both nonzero `naturalWidth/Height`, CDP response status and redirect history, cache/service-worker flags, transferred bytes and screenshots. Unknown or tool-inaccessible must stay `UNVERIFIED`.
2. For any *actually broken* source, acquire a replacement **only after** exact photograph/crop comparison, catalog item rights review (especially creator agency, donor-origin material, Commons cropping), legal reuse/attribution, editorial scene and chronology sign-off. Store the source URL, creator, source accession, source date, license evidence, alt and caption. Do not treat another photo of USS Akron as an exact-photo replacement.
3. If rights-approved, make a unique **staged** 960px-max derivative (not 960×960 bounding-box distortion), preserving original smaller sizes; use quality-controlled WebP/JPEG only if image labels and historical details remain legible. Keep high-resolution archival viewer link where needed. Plan first-party WordPress Media Library with explicit intrinsic width/height, responsive `srcset/sizes`, lazy-load below-fold, and a prominent unchanged lead image where relevant. Verify page render and responsive semantics in staging.
4. Require scoped review, pre-change WordPress block/ALT/URL snapshot, screenshot/asset checksum, written approval, rollback path and guest-browser acceptance before *any* separately approved production write. This batch does **not** authorize a write or download.

## Performance methodology; 76% claim remains unmeasured

Use separate **uncached, complete, logged-out visitor network** captures for a fixed and explicitly declared cohort (historical 61 posts/355 inline refs, not mixed with later 66-post/361-image set). Associate each actual request/response with the **post + stored image slot + runtime `currentSrc`** after Jetpack rewrites, rather than equating stored URLs with downloaded bytes. Use transferred `encodedDataLength`/response sizes from intact CDP events, exclude cached and service-worker resources, record missing/failed images separately rather than counting them as successful 0-byte compression, and include visual parity and LCP/CLS review. Before/after comparisons must use the same exact original photo and source identity, or an individually licensed and editorially approved restoration must be reported as a *replacement*, not image compression. Only then compute `(baseline_sum - candidate_sum)/baseline_sum`. A source-only 76% estimate is neither measured nor achieved.

The reported **42 broken external originals** are not confirmed in guest browsers. The 61/355 historical inventory has 288 offsite-upstream source slots; **194 catalog-researched, 94 still pending**. This changes research coverage, **not broken status**. The 15 WordPress originals >1.5 decimal MB total **47,096,779 stored bytes**, not wire bytes; 11 are known inline across eight posts (IDs 34–38, 269, 299, 621) and deserve staged encoding/label review *after* P0 real failures. The other four oversized stored assets must not be deleted because they could be used in non-inline contexts.

## Engineering and QA verification

- New **6-source provenance and rights JSON**, separate **288-slot exact-source coverage audit**.
- Deterministic offline [validator](../qa/media-recovery/validate_akron_219_coverage_194_20261110.cjs) guards original URLs, catalog provenance, source/slot binding, Army Air Corps attribution, proportional 960px handling, null guest results, zero rights or publishing permissions, every 282 unrelated row remaining unchanged, and coverage 194/288.
- [27 adversarial/control regression tests](../qa/media-recovery/test_akron_219_coverage_194_20261110.cjs) **passed 27/27 against exact committed GitHub files** using isolated V8 with Node-compatible `fs/path/node:test/assert` shims. **Native Node CI and real guest Chromium have not been run.** No browser claims follow from these synthetic checks.

No Site QA draft/collector files changed. No downloads, caches, WordPress production writes, public repairs, homepage design work, paid tools or merges.
