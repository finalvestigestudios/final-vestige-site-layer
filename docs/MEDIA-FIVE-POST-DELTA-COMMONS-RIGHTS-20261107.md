# Media recovery delta: five new posts and six remote archival images (Nov 7, 2026)

## Verified scope
Authenticated read-only WordPress source of post IDs 1926 (1 IMG), 1924 (1), 1922 (0), 1920 (2), 1917 (2). Six exact Commons Special:Redirect/file URLs and their complete stored ALT texts are pinned in `qa/media-recovery/new_five_posts_six_commons_20261107.json`. **All six have no inline HTML width/height attributes**; runtime CSS/browser layout shift remains unknown. The Commons **file catalog HTML** was retrieved, not source JPEG response/status, and neither Chrome nor image bytes were measured.

**61 posts / 355 IMG refs** (Oct 30) versus **66 posts / 361 refs** (Nov 7, existing draft #1402) = net five and six. The new posts indeed carry six images, but **no complete 61-post original-URL diff** was performed here; do not pretend older sources are identical. These six third-party image references do not increase the 14 >1.5 MiB **WordPress originals**, currently **45,553,777 stored bytes**; stored bytes are not downloaded transfer.

## Catalog identity, credit, and safe 960-pixel geometries
| Slot | Catalog, pixels | License shown on catalog | Conditional no-crop preview |
|---|---|---|---|
| 1926:0 | [Vassil British Museum crystal skull](https://commons.wikimedia.org/wiki/File:Crystal_Skull_British_Museum_26072013_05.jpg), 1436×2001 | CC0 (Vassil) | 960×1338 |
| 1924:0 | [Wellcome M0006352 engraving](https://commons.wikimedia.org/wiki/File:%22Le_Baquet_de_Mesmer%22_Wellcome_M0006352.jpg), 2988×3538 | CC BY 4.0 (Wellcome) | 960×1137 |
| 1920:0 | [Chappsnet Lycurgus front](https://commons.wikimedia.org/wiki/File:Front_of_4th_century_CE_Roman_Lycurgus_Cup,_British_Museum_(1958,1202.1).jpg), 2720×3649 | CC BY 4.0 | 960×1288 |
| 1920:1 | [Chappsnet Lycurgus top](https://commons.wikimedia.org/wiki/File:Top_view_of_the_famed_Lycurgus_Cup_in_the_British_Museum,_showing_the_glass_both_green_and_ruby_red.jpg), 3024×4032 | CC BY 4.0 | 960×1280 |
| 1917:0 | [Piri Reis historic map](https://commons.wikimedia.org/wiki/File:Piri_reis_world_map_01.jpg), 1964×2619 | public-domain faithful reproduction | 960×1280 |
| 1917:1 | [Cantino planisphere](https://commons.wikimedia.org/wiki/File:Cantino_planisphere_(1502).jpg), 10643×4998 | public-domain mechanical scan | 960×451 |

**Important:** Cantino's Commons **35.99 MB original** is NOT downloaded visitor bytes: published redirect asks for `width=1280`. Four published sources request 1280, two request 900; source master bytes differ from current visitor bytes. 960px is a **preview cap**, not a demand to sacrifice map inscription legibility. Maintain full-resolution click-through/zoom options. Ensure the Lycurgus cup's green-to-red lighting distinction survives derivatives. Commons CC BY 4.0 entries require source author/license link and indication of modifications. Current post text includes source-credit terms, but complete attribution and rights compliance has **not** been assessed; rehosting is on HOLD.

## QA handoff and release plan
The existing Site QA #154/#1395 owns the six P0 **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. This new P2 batch MUST NOT duplicate their browser collector or outrank P0. Feed current sources into existing logged-out full-scroll Chrome probe for direct image request/redirect/final URL, image decode/natural pixel geometry, cache status, encoded wire bytes, screenshots. Image failure requires actual guest evidence, not a Commons HTML catalog result. If failing, first confirm exact photo and item-level rights, capture binary dimensions, stage (not deploy) a ≤960 no-upscale preview, preserve credit/ALT/map zoom, compare screenshots and prepare isolated approved single-block correction with rollback. No unlicensed scraping, automated blanket WordPress rehosting, homepage design edits, or subscription cost.

**Methods:** To establish a 76% wire improvement, compare matched cold browser before/after **on the same page and viewport**, dedupe image network requests, use CDP encodedDataLength totals with cache flags, and require visual parity/CLS pass. A file's original WordPress/Commons size cannot establish network transfer savings. The **42 reportedly broken remain guest-browser unverified**, **76% remains unmeasured**, **0 production repairs**.

**Tests:** 21/21 deterministic checks passed in isolated V8, including 20 intentional data-corruption rejections. Native Node CI and actual guest Chrome have not run. Commands: `node qa/media-recovery/validate_new_five_posts_commons_20261107.cjs` and `node --test qa/media-recovery/test_new_five_posts_commons_20261107.cjs`.
