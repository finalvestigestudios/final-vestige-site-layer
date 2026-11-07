# Archimedes Palimpsest: post 268 external media source, rights and geometry review (2026-11-06 PT)

**Safe isolated Media Recovery QA; no homepage visual design or production WordPress changes.**

## Live source and metadata evidence

Authenticated WordPress `posts.get(context=edit)` for published post **268**, *They Painted Over Archimedes*, last modified **2026-10-30T01:10:13**, established **10 exact inline source URLs**. Of these, **six** are Wikimedia Commons `Special:Redirect/file` and **four** are Archimedes Palimpsest Project `/assets/img` media. **All 10 omit explicit stored `width`/`height` attributes.** Actual rendered CLS needs a real browser; theme and lazy-load rewriting may differ.

[Full ten-row machine-readable ledger](../qa/media-recovery/archimedes_268_primary_rights_geometry_20261106.json) pins URL, source ALT/caption, original catalog page, native-pixel metadata where available, conditional no-upscale 960px dimensions, rights assertions, source-retriever method and NULL guest/real-origin HTTP status.

| Image slot | Exact primary/catalog evidence | Catalog original (pixels) | Conditional no-upscale preview | Rights review |
| --- | --- | ---: | ---: | --- |
| 268:0 | [Archimedes Palimpsest.jpg](https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg) | 665×448 | **665×448**, NEVER upscale to 960 | Commons public domain assertion is **US-specific** |
| 268:1 | Project `/assets/img/imaging_x8.jpg` | unknown | HOLD | Project website asset is not proved image-bank-licensed |
| 268:2 | [UV folio, 9737603804](https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg) | 10880×8160 | 960×720 | Commons CC BY 2.0; project bank CC BY 3.0 |
| 268:3 | [Heiberg-UV, 9737623542](https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg) | 2040×2720 | 960×1280 | Same item-level dual assertions |
| 268:4 | Project `/assets/img/imagecapture-capture2b.jpg` | unknown | HOLD | Asset-specific rights |
| 268:5 | [Processed undertext, 9734386225](https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg) | 8160×10880 | 960×1280 | Commons CC BY 2.0; project bank CC BY 3.0 |
| 268:6 | [XRF iron map, 9734104759](https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg) | 8160×10880 | 960×1280 | Commons CC BY 2.0; project bank CC BY 3.0 |
| 268:7 | Project `/assets/img/imaging_x12.jpg` | unknown | HOLD | Asset-specific rights |
| 268:8 | Project `/assets/img/imaging_x9.jpg` | unknown | HOLD | Asset-specific rights |
| 268:9 | [Hyperides, 9734660151](https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg) | 6600×9500 | 960×1382 | Commons CC BY 2.0; project bank CC BY 3.0 |

**Important rights nuance:** the [official Archimedes Palimpsest Image Bank policy](https://archimedespalimpsest.org/digital/image-bank.php) explicitly states **CC BY 3.0 Unported**. Yet the **five separately reviewed Wikimedia Commons file records** for Image Bank derivatives explicitly display **CC BY 2.0 Generic**, from a reviewed Flickr transfer. Some embedded photograph metadata additionally states that rights reside with the manuscript owner. This does **not establish a legal conflict or violation**—multiple legitimate grants may coexist. It *does* require selection and documentation of a reliable item-specific license, credit, license hyperlink and adaptation notice before copying/rehosting. A museum credit alone is not a waiver; the non-image-bank project website photographs have **no individually verified reuse grant**. None is cleared by this audit.

**Important dimensional trap:** Wikimedia Commons `Archimedes Palimpsest.jpg` is only **665×448** on its file page, while stored FV src asks for `?width=1280`. One other Commons image asks for `width=1280`; source query width is neither decoded bytes nor proof of upscaling. Always use actual decoded pixels and no-upscale geometry. The other five catalog-backed previews are *conditional calculations*—not created/optimized files, actual browser sizes, or guaranteed matching binary crops. For dense manuscript lettering, provide an accessible rights-cleared master/detail-view link where possible, rather than aggressively shrinking evidence.

## HTTP evidence and what is *not* a broken-image claim

Public web-retriever attempts for `imaging_x8.jpg`, `imagecapture-capture2b.jpg` and `imaging_x12.jpg` reported wrapper **403 Forbidden**. `imaging_x9.jpg` and the initial Commons redirect could not be accessed by that retriever. These tool-layer errors do **not** demonstrate visitor HTTP failures or blocked page images; all guest/browser and actual origin HTTP statuses, `currentSrc`, natural dimensions and transferred bytes remain **NULL**. Confirm or refute with **Site QA #154's existing logged-out CDP collector**. Do not duplicate the browser probe or add these ten slots to the alleged “42 broken.”

## Safe WordPress media / performance plan — NOT executed

1. Preserve Site QA's **P0 six** suspicion order: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Only after that, inspect post 268 (ten slots) with a real guest Chrome/mobile full scroll; save final request/redirect chain, image response, `naturalWidth/Height`, screenshot, ALT, `currentSrc`, frame geometry and cold cache-disabled `encodedDataLength`.
2. For *visitor-confirmed* failed assets, match **exact folio, imaging modality, color treatment, crop and period**, not a loosely similar picture. Never interchange UV and XRF maps, Heiberg and later reconstructions, or Hyperides and Archimedes folios.
3. Record the **item-specific copyright basis**, credits, Commons and project license variants, attribution/changes notice, and permitted redistribution. Only then consider authorized WP Library copies. No blanket mirroring, unlicensed scraping or caching of third-party media. For originals lacking native size, do not propose a 960px derivative until verified.
4. Stage and QA a rights-cleared copy with max 960px wide/no upscaling, correct responsive `srcset` and intrinsic dimensions, and preserve detailed manuscript legibility. Maintain a reversible one-slot source URL → WordPress Media ID and license/credit mapping. Apply nothing to published Gutenberg blocks without separate permission and an editor preview.
5. Compare same-page same-viewport **cold guest network** before/after with the [existing PR #183 wire comparator](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183). The old **76% improvement estimate is not a measured transfer saving**. The **13 WP originals >1.5MiB totalling 43,522,829 stored bytes** are a separate optimization cohort and storage is not visitors' network weight.

**Inventory chronology:** frozen **61 posts / 355 inline** in original QA issue #154; later live-read inventory **66 posts / 361 inline** plus 83 published pages / 20 inline references. These ten post-268 sources were already counted in the early sitewide inventory; this batch adds item-level metadata and licensing scrutiny, **not ten net-new site images**.

## Checks

`node --check qa/media-recovery/validate_archimedes_268_20261106.cjs`

`node --test qa/media-recovery/test_archimedes_268_20261106.cjs`

An isolated V8 function execution checked the real committed JSON against the proposed offline validator and rejected **25 deliberately unsafe mutations before commit**. Native Node tests, CI and logged-out guest Chromium have **not** been executed in this run. All live WordPress writes, downloads/rehosting, new subscriptions and homepage changes = **0**.
