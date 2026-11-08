# Live WordPress image originals — 121-item recheck and 15-item decimal-MB reconciliation
**2026-11-08 Pacific. Read-only evidence. DRAFT PR #183. No production changes.**

## Source and scope
Two paginated authenticated `media.list` **read** operations on `finalvestige.com`, image-only, sorted by media ID (100 + 21 records), yielded **121 image-media originals** with reported combined original storage **70,554,906 bytes**. Independent `media.get(context=edit)` readback confirmed metadata for **1714** and **2148**. A separate `posts.list(status=publish)` returned **66 currently published posts**, and `posts.get(context=edit)` for **269** established its exact Halifax map source. These are CMS/storage observations, **not visitor browser HTTP, decoded image bytes, resource timings or a fresh full inline-image census**.

The immutable historical 2026-10-30 cohort is 61 posts / 355 stored inline images. The later expanded cohort of 66 / 361 images was assembled at mixed dates. Never combine their denominators and call it a paired performance measurement.

## The metric correction that resolves 13 versus 15
The previous 13-item report used **greater than 1.5 MiB = 1,572,864 bytes**. The later worklist used **greater than 1.5 decimal MB = 1,500,000 bytes**.

| Cutoff | Current oversized items | Stored original bytes |
|---|---:|---:|
| >1,500,000 B (1.5 MB decimal) | **15** | **47,096,779** |
| >1,572,864 B (1.5 MiB binary) | **14** | **45,553,777** |

Prior 13-item Nov 4 WordPress review: **43,522,829 bytes**. The **two-item difference** is now exactly reconciled, not a missing image or newly verified page bottleneck:

- **Media 2148** — [1927 Caernarvon levee archival photograph](https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg), added **2026-11-07**, **2,030,948 B**, WordPress metadata **1821×1190**, conditional non-upscale output **960×627**. This newly uploaded media item is above BOTH thresholds; specific published-post use has NOT been established.
- **Media 1714** — [Halifax harbour map](https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png), added **2026-10-29**, **1,543,002 B**, WordPress metadata **1280×1280**, conditional non-upscale output **960×960**. This item exceeds decimal MB but is **below** binary MiB; it was not part of the earlier 13-item `>1.5 MiB` inventory.

Arithmetic: `43,522,829 + 2,030,948 + 1,543,002 = 47,096,779 B`. The 15 account for approximately **66.75% of stored image-original bytes** in the current 121-item CMS inventory; this is **not** a transfer reduction, Core Web Vitals result, or measured user download.

## Exact visual-source custody for the two additions
**Halifax 1714** is not an orphan: fresh read-only Gutenberg source for [post 269, *The Watch Lost Its Hands*](https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/) contains `wp-image-1714`, `sizeSlug: "large"`, and an `img src` equal to the raw 1,543,002-byte PNG URL above. The image displays a map with meaningful geographic labels. CMS `src` does not prove the browser fetched all original bytes: it may receive a transformed `currentSrc` through Jetpack, srcset or responsive execution. **Keep the map readable at 1× and 2× DPR**; no 960px derivative, lossy conversion, or rights conclusion is authorized.

**Caernarvon 2148** is a *different historical event* from Halifax. Its existing WordPress metadata includes a NOAA source [wea00739](https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg), and names the Wikimedia Commons [cropped-file catalog](https://commons.wikimedia.org/wiki/File:1927_Mississippi_Flood_Blowing_Levee.jpg). Commons explicitly lists **1,821×1,190 and 2,030,948 bytes**, exactly matching WordPress media metadata; this is strong **metadata correspondence**, **not a verified identical-byte hash**. Commons catalogs the *1927* levee breach near Caernarvon, Louisiana, and a crop of archival magazine borders by Wisekwai. The catalog asserts NOAA U.S. government public domain, but original-vs-crop identity, rights/credit, date specificity and any extra restrictions remain review items. The Commons line “Archival Photography by Steve Nicklas, NOS, NGS” should **not** be interpreted as proof that Steve Nicklas personally photographed an event in 1927. NOAA catalog fetch returned a web retrieval **405**, not a visitor/origin-image failure. Existing WordPress media is NOT approval to overwrite/repost elsewhere.

## Practical engineering priority
1. **Broken P0 media first**: Site QA #154 retains guest-CDP capture of 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. A web-retriever wrapper 403/404/405 and a metadata mismatch do not mean a guest image is broken.
2. **Six oversized-first-party inline sources** for a later paired cold/warm study: five original 1672×941 historical-reconstruction PNGs #39–43 (13,267,538 stored bytes total, zero WordPress subsizes), plus Halifax map #1714 (1,543,002 stored bytes). Preserve explicit “reconstruction” disclosure and map labels. Existing HTML source is not runtime browser `currentSrc` proof.
3. **Avoid double counting Vasa**: originals #388/#389/#382 are 8.18/2.82/2.32 MB stored, but prior WordPress post 299 used Jetpack `fit=1024` URLs. Real wire requests likely differ; only a logged-out complete network capture can quantify.
4. **Keep the 76% claim on HOLD**: compare same historical photo, matched page/image cohort, same viewport/DPR, cache state and source identity, full lazy-scroll CDP `encodedDataLength`, clean origin/cached status, integrity screenshots and broken image counts. A 47MB storage sum cannot be used as a transfer baseline.
5. **No unauthorized localization**: rights and item provenance, displayed composition, ALT/credit and <=960px proportional derivatives are release gates. Stage *only* authorized media under new WordPress media IDs after separate approval, reversible single-image updates and before/after visual and wire QA. Never bulk-rewrite Gutenberg image blocks.

## Machine evidence and regression
[121/15 current WordPress metadata snapshot](../qa/media-recovery/wp_live_121_15_decimal_threshold_20261108.json) · [fail-closed read-only validator](../qa/media-recovery/validate_wp_live_121_15_decimal_20261108.cjs) · [32-case regression tests](../qa/media-recovery/test_wp_live_121_15_decimal_20261108.cjs).

**32/32 adversarial/control cases passed** in isolated V8 against the fetched committed audit and validator. Native Node CI and real logged-out browser evidence were not executed; production WordPress posts/media/theme/homepage, third-party binaries, source mirrors and billing were not touched.
