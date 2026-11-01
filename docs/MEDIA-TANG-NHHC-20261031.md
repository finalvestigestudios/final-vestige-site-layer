# USS Tang seven-slot Navy image custody, rendering-risk and 960px plan (2026-10-31)

**Scope:** Published post [274 — Twenty-Four Feet from Air](https://finalvestige.com/2026/08/19/twenty-four-feet-from-air-uss-tang/). **Production changes: none.** This is an isolated Media Recovery PR #183 review; Site QA PR #154 and homepage visual-design files are untouched.

## Authoritative current WordPress readback (read-only)

WordPress `posts.get` using `context=edit` returned **publish**, modified **2026-10-29T16:02:05**, with **seven inline image tags**, **seven exact URL matches** and **seven full ALT string matches** against frozen `qa/media-recovery/parts/04.json`. This proves stored Gutenberg source identity at that moment, **not** successful guest decoding. All **seven** source references are hosted externally. The full unaltered URLs and ALT strings, each catalog URL, rights status and source dimensions are in `qa/media-recovery/tang_274_nhhc_20261031.json`.

## Seven source records and conditional derivative geometry

| Source slot | Official archival catalog / provenance status | Catalog master dimensions used for conditional geometry | ≤960px target |
|---|---|---:|---:|
| 274:0 | [NH 42273](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-42000/nh-42273-uss-tang--ss-306-.html), accession embedded in Commons filename | Commons master 5019×3070 | **960×587** |
| 274:1 | [80-G-227987](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-g-227987-uss-tang--ss-306-.html), official subject-match candidate; binary unverified | NHHC TIFF 4908×5948 | **960×1163** |
| 274:2 | [NH 84498](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84498.html), official torpedo subject candidate; binary unverified | NHHC TIFF 6216×4876 | **960×753** |
| 274:3 | [NH 45641](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-45000/NH-45641.html), same-scene candidate for third-party photograph, **not** exact binary match | Commons same-scene 1906×2100 | **960×1058** |
| 274:4 | [80-G-344565](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/japanese-surrender/allied-prisoners-of-war/80-g-344565.html), accession encoded in NHHC `image=` selector | NHHC TIFF 1464×1938 | **960×1271** |
| 274:5 | [80-G-227991](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227991.html), accession in Commons filename | Commons master 5670×4150 | **960×703** |
| 274:6 | [80-G-227989](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html), War History Online filename + Commons source attribution; crop unverified | Commons master 1910×1288 | **960×647** |

**Dimension caveat:** These are **archival source/reference metadata**, not measured `naturalWidth` values of Final Vestige's current image URLs, and not transfer sizes. NHHC TIFF dimensions and Commons derivatives can differ by crop; a target is only applicable if editorial and asset verification selects that *same image geometry*. No upscaling, forced crop or replacement merely because the historical subject is similar.

## Three concrete historical-integrity findings

1. **274:1 — photograph location needs clarity.** NHHC **80-G-227987** says O'Kane posed with **22 rescued aircrewmen upon return to Pearl Harbor in May 1944**. They were rescued *off Truk*, but the group photo was **not taken at Truk**. Proposed ALT (editorial review only): *“Lt. Cmdr. Richard H. O'Kane with 22 American aircrewmen rescued off Truk, photographed after USS Tang returned to Pearl Harbor in May 1944.”*
2. **274:2 — two torpedoes, not one.** NHHC **NH 84498** labels **Mark 18-2 electric (top)** and **Mark 16-1 chemical (bottom)**. Current ALT names only Mark 18-2. Proposed ALT, **only if current crop actually shows both**: *“Mark 18-2 electric torpedo (top) and Mark 16-1 chemical torpedo (bottom), photographed at Newport Torpedo Station during World War II.”*
3. **274:5–6 — dates and crop.** NHHC's **80-G-227991** collection entry explicitly dates Kingfisher rescue **1 May 1944** while a separate Navy museum entry describes **20–30 April**. Do not silently collapse this catalog discrepancy. For **274:6**, Commons' 1910×1288 master and NHHC's 6060×4926 TIFF differ visibly in aspect ratio, so a crop- or rendition-mismatched photograph would be a provenance error even if the subject is the same. Compare the actual current `currentSrc` image and chosen master before proposing a change.

The 1930 escape-lung image **274:3** is a contextual USS V-5/Narwhal test photograph. It must not be presented as contemporary footage of Tang's October 1944 escape.

## Rights and cache-release gates

NHHC catalogs identify photos as official U.S. Navy imagery, and Commons often labels such works public domain; **the catalog is not blanket permission to mirror every hotlinked derivative**. Review each exact record for copyright exceptions, Commons rendition/modification rights, source credits, and any modern third-party image rights. All seven records remain `rights_status=HOLD`, `wordpress_upload_authorized=false`, `source_sha256=null`, and `original_pixels_verified=false`.

Only after per-item rights approval, source-binary identity verification, and confirmed visible browser failure or measured weight benefit: obtain the authorized exact master (not an unlicensed hotlink copy); pin URL, credit and SHA-256; create a maximum-960px no-upscale derivative preserving native geometry; visually inspect with source/caption; stage **without** touching published Gutenberg blocks; verify WP media responsive `srcset` and Jetpack behavior; independently compare logged-out Chrome image HTTP status, decoded `currentSrc`, encoded transfer bytes, mobile LCP and CLS; request separate production authorization.

## Evidence and limitations

This run independently read the live *editor source* but the isolated HTTP container could not resolve **FinalVestige.com, history.navy.mil or Wikipedia** (DNS resolution errors), so no guest-browser image request status, redirect, MIME, decoded dimensions, screenshot or wire bytes were collected. DNS failure **in the tool environment** is not an actual site's 404 or visitor outage.

The **42 purported broken images** and **76% alleged image-weight reduction** remain unverified. The existing **61 posts, 355 stored image references, 288 external source references and 13 Media Library originals over 1.5 MiB** remain the site-wide inventory baseline. This batch **does not repair seven images in production**.

**Engineering:** `qa/media-recovery/validate_tang_274.cjs` and `test_tang_274.cjs` enforce exact frozen URLs/ALT, official catalog identity, item credit, provenance/crop qualification, ≤960px targets, false browser data rejection and rights holds. **102/102 synthetic tests (1 positive and 101 fail-closed) passed against committed source in isolated V8.** Node-native execution/CI and real guest Chromium remain outstanding.
