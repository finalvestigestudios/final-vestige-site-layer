# Archimedes Palimpsest — external media reliability / rights (2026-11-03)

Post **268**, “They Painted Over Archimedes”: frozen Oct 30 source archive `qa/media-recovery/parts/04.json` (Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`). Ten exact image source URLs/ALTs are preserved in [machine audit](../qa/media-recovery/archimedes_268_ten_source_rights_20261103.json). **The live WordPress post was not re-read:** public page inaccessible to the independent retriever; post content may have changed.

## Retrieval evidence: do not mistake tool errors for browser failures

All **10** exact URLs were attempted by the independent web retriever on Nov 3. Six Commons `Special:Redirect/file` URLs could not be retrieved with no origin HTTP status. Among four project-site `assets/img/` source URLs, slots **268:1, 268:4, 268:7** returned retriever wrapper **403** (not a verified server/browser status); **268:8** inaccessible without numeric origin response. **0 confirmed visitor failures**. All six **corresponding Commons File: catalog HTML pages** were readable and supplied exact filenames, intrinsic sizes and license claims. This proves catalog access, NOT working redirect bytes or decoded browser images. No image was downloaded or copied.

## Six catalog-matched sources, licensing and 960px derivatives (NOT APPROVED FOR REHOST)

| Slot | Catalog original pixels | Conditional no-upscale pixels | Catalog license signal |
|---|---:|---:|---|
| 268:0 | 665×448 | 665×448 | Commons PD-US statement (jurisdiction-sensitive); credit Matthew Kon |
| 268:2 | 10880×8160 | 960×720 | Commons CC BY 2.0; Ryan Baumann/Flickr + imaging team context |
| 268:3 | 2040×2720 | 960×1280 | Commons CC BY 2.0; metadata mentions manuscript owner |
| 268:5 | 8160×10880 | 960×1280 | Commons CC BY 2.0; compare institution licenses |
| 268:6 | 8160×10880 | 960×1280 | Commons CC BY 2.0; XRF/SLAC imaging contributors |
| 268:9 | 6600×9500 | 960×1382 | Commons CC BY 2.0; **Hyperides** text distinction |

**Key licensing ambiguity:** the [official project image bank](https://archimedespalimpsest.org/digital/image-bank.php) states its digital image dataset is CC BY 3.0; the five Flickr-origin Commons images display CC BY 2.0 terms, while underlying original manuscript/image metadata sometimes mentions owners. Do not silently replace one license with another; retain exact item authorship, license/version/links, changes and attribution. Direct project-site editorial photographs **268:1/4/7/8** are *not proven* to be bank dataset files or subject to the bank's CC BY 3.0 statement; their exact dimensions and reuse rights are unknown, so they stay HOLD. Slot **268:0** is **665px wide**: no 960px upscaling.

Commons catalog records (readable as of Nov 3):
- 268:0: https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg
- 268:2: https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg
- 268:3: https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg
- 268:5: https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg
- 268:6: https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg
- 268:9: https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg

## Release-safe recovery procedure

1. Site QA #154 retains the original P0 priority queue (**285:5, 287:5, 418:1–2, 407:1**). Add this 10/10 third-party exposure article as **P1** after browser P0, not a competing draft.
2. In **logged-out desktop/mobile Chrome**, scroll through the article and record each `img.src/currentSrc`, redirect chain, **Image GET final HTTP + MIME**, decoding/`naturalWidth`, screenshots and cold-cache encoded transfer bytes. If source has changed since Oct 30, regenerate the archive before asserting slot identities.
3. For an actually broken image: exact-source visual/crop equivalence; catalog item-specific rights and complete attribution; original intrinsic dimensions; 960px maximum **without upscaling**, and choose a color-managed WebP/JPEG derivative after quality comparisons. Hyperides must not become labeled as Archimedes; avoid misleading older/later imaging dates. Source rehosting must not be inferred from permissive license descriptions without confirming license chain and image-specific restrictions.
4. Only after item sign-off: WordPress **staging** Media Library upload, correct title/ALT/source/credit/license, preview desktop/mobile layout, verify canonical page and mobile/LCP, capture rollback image-source snapshot. **No production change or upload authorized in this sprint.**
5. Any **76% image transfer** claim needs comparable uncached CDP sessions and exact source/revision identity for all 61 articles/355 slots (see existing measurement gate); stored original dimensions, original-size MB and six large archival masters are NOT visitor transfer bytes.

Validation: [offline fail-closed source/copyright guard](../qa/media-recovery/validate_archimedes_268_20261103.cjs) and [33 baseline/adversarial assertions](../qa/media-recovery/test_archimedes_268_20261103.cjs); locally checked in isolated V8, **native Node CI and guest Chromium not run**.
