# USS Akron (post 219) — exact Navy catalog and browser-release audit

**Date:** 2026-11-01. **Branch:** `qa/media-recovery-reviewed-20261030-1158`; draft PR #183 only. **Scope:** six historical image slots for [The Airship Had No Life Jackets](https://finalvestige.com/2026/08/18/the-airship-had-no-life-jackets/). No homepage visual work, Site QA #154 code, WordPress write, asset download, licensed image cache, or spending.

## What was actually verified

Authenticated read-only WordPress `posts.get(id=219,context=edit)` returned published status and modification `2026-10-29T15:54:20`. All **6/6** present `<img src>` and full `alt` attributes match the October 30 authenticated frozen census `qa/media-recovery/parts/05.json` (GitHub blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`). A local direct HTTP/DNS attempt could not resolve `finalvestige.com` or `commons.wikimedia.org`; it does not indicate a public outage. Official NHHC and Commons **text catalog** matches do not establish live visitor image GET success. **No browser HTTP code, currentSrc, naturalWidth, content-type, transfer bytes or visible broken-image screenshot exists from this batch.**

## Six original references, exact catalog identity and proportional targets

| Slot | Exact primary photo catalog / caveat | Commons original geometry | Conditional ≤960px width, never upscale |
|---|---|---:|---:|
| 219:0 | 80-G-1009363 | 2650×2190 | 960×793 |
| 219:1 | NH 43900 | 5516×4241 | 960×738 |
| 219:2 | NH 98039 | 5482×4160 | 960×728 |
| 219:3 | 80-G-463185 | 740×581 | 740×581 |
| 219:4 | NH 97977 | 740×586 | 740×586 |
| 219:5 | No individual Navy catalog ID confirmed; Commons-only recipient history | 590×765 | 590×765 |

All six currently use Commons `Special:Redirect/file/... ?width=1280`. The **three small originals** (740px, 740px, 590px wide) are **narrower than the requested 1280px**; that does *not* prove the remote service actually upscaled them, and no transfer-weight savings are measured. NH 98039 is a very large archival **PNG**; the official NHHC catalog also offers a medium JPEG, potentially a lower-transfer rights-cleared derivative *if* identical pixels and permitted use are verified. Catalog original dimensions are **not** the visitor transfer dimensions.

## Five official photo records (not generic similar pictures)

- **219:0 / 80-G-1009363:** [official NHHC record](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/aircraft-us/aircraft-usn-a/uss-akron-zrs-4/80-g-1009363.html) — USS Akron over Lincoln Memorial, Washington, D.C.; Navy photograph received 1957, exposure circa 1931–33. Existing [Commons file](https://commons.wikimedia.org/wiki/File:80-G-1009363_(30087379334).jpg) cites or matches the archival identifier. Exact image byte identity is not verified.
- **219:1 / NH 43900:** [official NHHC record](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-43000/NH-43900.html) — USS Akron over southern Manhattan, circa 1931–33. Existing [Commons file](https://commons.wikimedia.org/wiki/File:USS_Akron_(ZRS-4)_in_flight_over_Manhattan,_circa_1931-1933.jpg) cites or matches the archival identifier. Exact image byte identity is not verified.
- **219:2 / NH 98039:** [official NHHC record](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-98000/NH-98039.html) — Akron in Panama Canal Zone with N2Y-1 suspended, 15 March 1933; original Army Air Corps photograph. Existing [Commons file](https://commons.wikimedia.org/wiki/File:NH_98039_USS_Akron_(ZRS-4).png) cites or matches the archival identifier. Exact image byte identity is not verified.
- **219:3 / 80-G-463185:** [official NHHC record](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-460000/80-G-463185.html) — Akron launches N2Y-1 #A8604 near Lakehurst, 4 May 1932; Commons version cropped. Existing [Commons file](https://commons.wikimedia.org/wiki/File:USS_Akron_releases_its_N2Y_1_aircraft.jpg) cites or matches the archival identifier. Exact image byte identity is not verified.
- **219:4 / NH 97977:** [official NHHC record](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97977.html) — Akron approaches mooring mast, circa 1931–33; Commons version cropped. Existing [Commons file](https://commons.wikimedia.org/wiki/File:USS_Akron_approaches_mooring_mast.jpg) cites or matches the archival identifier. Exact image byte identity is not verified.

**219:5:** [Commons Akron kitchen file](https://commons.wikimedia.org/wiki/File:Akron_kitchen.jpg) identifies a sailor getting water and says the image was received by the **Navy Recruiting Bureau in 1932**; it lists the **original creator unknown** and no unique NHHC accession. This source supports the described scene but **does not prove that a federal employee created it**, even though Commons applies a U.S.-Navy government-work tag.

**Material credit mismatch:** Primary [NH 98039](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-98000/NH-98039.html) explicitly calls the photographer **U.S. Army Air Corps**, while Commons labels the work with a Navy-employee public-domain rationale. The current WordPress **figcaption correctly identifies the Army Air Corps**, and must remain so; the reuse rationale should be checked against actual federal authorship, rather than relying on the wrong-service copyright label.

### Right-to-cache and image-identity release gates

1. First require Site QA #154 to capture logged-out desktop/mobile `currentSrc`, matched network request/redirect, status, MIME, encoded bytes, `naturalWidth` and a screenshot **for any failed image**. Avoid treating Commons redirects or tool timeouts as actual failures.
2. Confirm exact catalog photo identity, not merely a similar airship or crash image; record master SHA-256 only after an authorized binary inspection. The current Commons file crop may not be pixel-identical to NHHC large originals.
3. Review item-specific publication rights, photo credits (Army Air Corps for NH 98039, unknown author for kitchen), Commons/license conflicts and nonendorsement restrictions. **All reproduction, first-party caching and upload gates remain closed.** No bulk mirroring.
4. Once authorized, generate aspect-preserving no-upscale ≤960px images, choose JPEG/WebP only when visual detail remains equivalent, record hashes/dimensions, register as WordPress media in staging, verify responsive `srcset` and ALT/figcaption preservation, and only then consider a reviewed per-block replacement. Do not raw-rewrite Gutenberg markup.
5. Benchmark same-page guest desktop/mobile requests and LCP/CLS **before and after** any approved change. The existing site-wide **61 posts / 355 images / 288 external refs / 13 large originals** are source or storage counts, **not page-transfer data**. The previously quoted **42 broken images** and **76% savings** remain unsupported; production repairs still **zero**.

**Engineering:** machine ledger `qa/media-recovery/akron_219_nhhc_20261101.json`, validator `validate_akron_219.cjs`, tests `test_akron_219.cjs`. Independent of Site QA #154 and homepage lead.
