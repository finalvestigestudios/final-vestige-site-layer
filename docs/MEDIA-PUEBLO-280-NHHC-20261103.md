# USS Pueblo / NHHC six-image recovery batch — 2026-11-03

**Scope:** Published Final Vestige [post 280](https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/), *The Sledgehammers Broke First*. No homepage, Site QA draft, production content, source image binary, or user-facing WordPress file changed.

## Actual source and transport evidence

Authenticated, **read-only** WordPress post #280 last modified **2026-11-02T21:39:55** and published, has **six** `<img>` URLs and ALT strings, all six identical to the frozen October 30 `qa/media-recovery/parts/03.json` (**blob 49183f66f880f7c4dfd363acca906876877f2e5e**). Every stored source URL uses `www.history.navy.mil`. The six exact URLs, the original ALT strings and source metadata are in [machine-readable audit](../qa/media-recovery/pueblo_280_20261103.json).

Independent `web.open` attempts made November 3 produced **five tool-wrapper 502 errors** for 280:0–3,5 and **one inaccessible/no numeric status** for 280:4. These are *not confirmed HTTP 502s from Navy origin and not visitor-browser failures*. Site QA must inspect actual logged-out desktop/mobile `currentSrc`, redirect chain, final image GET/status/MIME, `naturalWidth` and `decode()`, full lazy-scroll screenshot and cold-cache CDP `encodedDataLength`. Guest statuses and bytes remain **null**. Do not add six to the reported '42 broken' count.

## Navy records: 5 subject matches + one unresolved live accession

| Live slot | Official archive | Historical identification | 960px maximum (conditional; NOT an asset) |
| --- | --- | --- | --- |
| 280:0 | [428-GX-USN-1129207](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html) | Pueblo off San Diego, PHCS J. M. Lahr, 19 Oct 1967 | master 3263×2244 → **960×660** |
| 280:1 | [NH 75559](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html) | Sailor drawing coffee aboard Pueblo, 1967 | **height unknown** |
| 280:2 | [NH 75561](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html) | Pueblo crew mess, 1967 | **height unknown** |
| 280:3 | [K-64683](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html) | **One** released sailor checks in after crossing Bridge of No Return, 23 Dec 1968 | master 6184×4978 → **960×773** |
| 280:4 | [DANFS Banner II](https://www.history.navy.mil/research/histories/ship-histories/danfs/b/banner-ii.html) | Related USS Banner (AGER-1), live photo accession and original date **not established** | **height unknown / identity HOLD** |
| 280:5 | [K-64728](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html) | Released sailors eating at UN Advance Camp, 23 Dec 1968 | **height unknown** |

**Geometry caveat:** The Navy catalog's “1280×1280” *medium download labels* refer to a rendition bounding box, not necessarily exact image width and height. Never treat them as intrinsic pixel dimensions. The 3263×2244 and 6184×4978 figures are the **catalog high-TIFF master** dimensions, not measured pixels of the exact currently published JPGs. The displayed photo and master crop are not yet visually or hash matched.

**Potential caption integrity:** 280:4 ALT refers to the Banner “after the Pueblo incident prompted changes,” without establishing that its actual picture was photographed after January 1968 or that it depicts a change. Preserve published text and request editorial side-by-side confirmation. There is a separately identifiable **related, not interchangeable** [NH 68705](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68705.html) photograph of USS Banner dated **12 May 1969**, TIFF 6312×4750 (possible 960×722). **DO NOT swap live 280:4 for NH 68705** without a deliberate scene/crop/credit decision. 280:3 is a check-in scene featuring one crewman, not a group pose.

## Rights and WordPress recovery gate

NHHC's [official copyright/citation guidance](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) explains that qualifying official federal photographs can be reproduced with accurate Archives credit and without altering substantive content; non-government/donor material still requires its own rights resolution. The catalog sometimes explicitly lists “Copyright Owner: NHHC” while also presenting Navy government imagery. **Archivist custody and an official page do not automatically establish reuse clearance for each underlying binary.**

**No image downloads/copies or WordPress mutations authorized here.** After **Site QA** confirms the exact bad visitor-facing slot, establish a chain of custody (actual returned `currentSrc`, original file hash if lawfully obtained, official identifier, date, scene match, rights and credit). Seek publication sign-off; in staging only, generate a versioned 960px-max / no-upscale derivative from a rights-cleared image with verified intrinsic dimensions and correct aspect ratio, prefer WebP/AVIF after fidelity comparisons, preserve ALT/captions, and keep a one-slot rollback manifest (original URL, WP media ID, original image block hash). Test mobile and desktop screenshots, HTTP/MIME/decode, speed and image appearance before a reviewed release. Production edits remain **HOLD**.

## Quantification and verification

Source-level census remains **61 posts / 355 slots / 288 offsite-origin references / 13 first-party originals over 1.5 MiB**. Neither “42 broken browser images” nor “76% downloaded-image-weight saved” is verified. The `qa/media-recovery/evaluate_image_wire_20261103.cjs` CDP methodology needs cold paired traces and precise source identities before making a claim. All six slots have **null guest browser statuses, null image-transfer bytes and zero approved replacements**.

[Fail-closed validator](../qa/media-recovery/validate_pueblo_280_20261103.cjs) + [33-case adversarial regression suite](../qa/media-recovery/test_pueblo_280_20261103.cjs): **33/33 passed using exact GitHub committed sources in isolated V8 CommonJS emulation** (not native Node CI, not Chrome). This work is isolated to Media Recovery PR #183. Site QA PR #154 retains P0 browser queue **285:5, 287:5, 418:1–2, 407:1**; Pueblo remains P1 until that queue is cleared.
