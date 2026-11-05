# SL-1 post 221: seven-image archival dimensions and chronology — November 5, 2026

**Scope and independence.** Post 221, *The Rod Was Supposed to Move Four Inches*, was absent from the prior detailed image-recovery worklist. This four-file, source-only draft is an **independent P2 archival batch**. It is not a browser probe, live-site repair, or homepage design change; it does **not** modify Site QA draft #154 or Media Recovery draft #183. Priority remains browser-confirmed failures at Three Mile Island → Sunshine Skyway → Scotch Cap → Hebgen Lake.

## Exact-source and catalog evidence

[Machine-readable seven-row ledger](../qa/media-recovery/sl1_221_seven_catalog_20261105.json) pins all seven source URLs and ALT text from the frozen October 30, 2026 article snapshot **Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`** in Media Recovery #183. These are **not fresh live WordPress reads**. Every published `Special:Redirect/file` filename was reconciled to its *individual* Wikimedia Commons file catalog; all catalog HTML pages were retrievable. **No source binary or original post image was downloaded**. All actual guest Chrome response codes, decoded pixels, cached bytes, image network request IDs and publisher-origin HTTP codes remain **NULL**.

| Slot | Commons source file | Catalog master px | Conditional no-crop output px | Key handling |
|---|---|---:|---:|---|
| 221:0 | SL1nuclearpowerplant.JPG | 704×346 | **704×346** | Already smaller than 960; never upscale. Army PD attribution is Commons-supplied. |
| 221:1 | SL-1 - Cutaway of reactor and control building.png | 729×589 | **729×589** | Smaller than 960; keep legible fine diagram labels and PNG transparency. |
| 221:2 | SL-1 - Reactor schematic.png | 1454×1753 | **960×1157** | Preserve technical labels, full vertical extent and source format; proof image required. |
| 221:3 | US AEC SL-1.JPG | 346×253 | **346×253** | Very low-resolution archival master; do **not** stretch or call 960px. |
| 221:4 | Sl-1-ineel81-3966.jpg | 1406×1881 | **960×1284** | Commons records **1981 retrospective photograph**, not a 1961 on-scene image. |
| 221:5 | Sl-1-ineel61-9.jpg | 1436×1113 | **960×744** | Commons dates Highway 20 contamination check **January 4, 1961**. |
| 221:6 | SL-1 - Dismantling of the foundation piers.jpg | 1402×1050 | **960×719** | **P1 metadata/date discrepancy** before editorial action; see below. |

Catalog dimensions describe the Commons *original files*, not decoded dimensions observed on FinalVestige.com and not necessarily the same pixels as any altered redirected rendition. Derivative sizes are *only* arithmetic proposals: width = min(original catalog width, 960); height = nearest integer preserving master aspect ratio. **No derivatives exist**, no rights/caching permissions have been granted, and no site-visitor performance benefit has been measured.

### Historically important metadata discrepancy: slot 221:6

The [Commons item](https://commons.wikimedia.org/wiki/File:SL-1_-_Dismantling_of_the_foundation_piers.jpg) labels the photo **1981** and photographer identifier `INEEL 81-3966`, but its own transcribed original caption ends `INEEL 67-2587`. More importantly, the official Idaho National Laboratory / DOE publication [*Proving the Principle*, chapter 16, printed page 155](https://inl.gov/content/uploads/2024/05/Chapter-16_Low-1.pdf#page=6) **visibly prints `INEEL 67-2587` below the corresponding dismantling photograph**. The original source confirms the conflicting catalog identifier; it **does not independently prove the photograph was taken in 1967**. Consequently leave year `null`, do not silently relabel it as a 1961 disaster or a 1981 event photo, and request editorial adjudication against the primary caption. No published ALT/caption was altered.

Other source-catalog records: [Army plant photograph](https://commons.wikimedia.org/wiki/File:SL1nuclearpowerplant.JPG), [cutaway](https://commons.wikimedia.org/wiki/File:SL-1_-_Cutaway_of_reactor_and_control_building.png), [schematic](https://commons.wikimedia.org/wiki/File:SL-1_-_Reactor_schematic.png), [AEC recovery](https://commons.wikimedia.org/wiki/File:US_AEC_SL-1.JPG), [retrospective 1981](https://commons.wikimedia.org/wiki/File:Sl-1-ineel81-3966.jpg), [Jan 4 contamination checks](https://commons.wikimedia.org/wiki/File:Sl-1-ineel61-9.jpg).

## Copyright and WordPress/cache plan (all actions HOLD)

Commons descriptions identify these as U.S. Army, AEC, INEEL or DOE-produced U.S. government works under public-domain categories. That is strong **research metadata**, not automatic confirmation that a specific scanned file may be republished without item-by-item attribution, rights and identifiable-person reviews. Retain full original credits and links. For each slot: compare *exact pictured scene*, confirm original attribution and reuse conditions with the owner/primary archive, obtain any necessary authorization, inspect master pixels, SHA-256 the rights-cleared binary, retain archive catalog URL, prepare only the allowed ≤960-wide uncropped preview (never upscale), and visually compare historical scene, legibility and crop with the original before authorizing storage.

**Future approved workflow only:** preserve original post block markup, screenshots, captions and rollback snapshot; upload a derivative as a **new** WordPress Media Library attachment with documented credit/license/source and immutable provenance; stage a targeted post image reference replacement outside production; verify image decode, natural width/height, mobile and desktop full-height screenshots and semantic ALT unchanged; measure actual uncached browser image-wire bytes before/after with identical full post inventory and viewport; obtain separate publication approval; only then apply an exact minimal block reference change with tested rollback. Never mirror the entire Commons/third-party library or rewrite Gutenberg blocks in bulk.

## Performance and coverage boundaries

The existing **61-post/355-image/288-upstream-external** census is frozen October 30; it is **not** a live November 5 full-site re-crawl. The claimed **42 broken images are still not browser-confirmed**; this source-audit batch supplies **zero actual visitor HTTP statuses**. A separate read-only WordPress media inventory identified **13 first-party originals over 1.5 MiB totaling 43,522,829 stored bytes**; that is not wire weight. Five direct first-party 1672×941 PNG originals in posts 34–38 total 13,267,538 stored bytes, with possible 960×540 derivatives **only after ownership/fidelity checks**. The alleged **76% reduction** has **not** been established by paired, cache-disabled visitor-transfer logs. Do not treat pre-existing broken images as zero-byte optimization savings.

**Tests:** `node --test qa/media-recovery/test_validate_sl1_221_catalog_20261105.cjs` and `node qa/media-recovery/validate_sl1_221_catalog_20261105.cjs`. The offline validator fails closed on wrong original URLs/ALT, dimension exaggeration, fabricated HTTP outcomes, invented performance claims, missing rights HOLD, unapproved uploads, chronology changes, and missing or duplicate slots. No network access or WordPress credentials are used.

**Release status:** 7/7 catalog records reconciled at the source-text level; 3/7 masters <960px wide; one documentary date/ID conflict; 18 isolated validator mutation controls passed; full Node CI and live Chrome still needed; **0 production image repairs**. 
