# Pulaski / Big Burn — exact archived-image identity and browser-evidence gate

**Audit:** 2026-10-30 · **Scope:** published WordPress post **428**, [*The Way Out Was Underground*](https://finalvestige.com/2026/08/20/the-way-out-was-underground-ed-pulaski-1910/) · **Previous work:** source inventory from `qa/media-recovery/parts/01.json`; separate Site QA PR #154 retains the 61-post origin-classification baseline.

## What was actually checked

A **fresh read-only WordPress editor-context `posts.get`** returned post 428 as `publish`, modified **2026-10-29T18:28:59**, with six `<img>` elements. All six exact `src`/ALT pairs match the repository's prior source inventory. One image is first-party; the other **five** are directly hosted by two cultural-heritage institutions (four University of Idaho Library / one Library of Congress).

The **five original, exact stored external-image URLs all rendered through the independent web image viewer** on 2026-10-30. This is a genuine independent *viewer decode* of the source URL, **not** an HTTP response/status observed from FinalVestige.com in a logged-out browser, and not a guarantee that the site's referrer policy, CDN rewriting, user agent or mobile clients can retrieve the same image. **We did not observe browser `naturalWidth`, HTTP response codes, cache provenance, transferred bytes, original file hashes or a controlled image-weight baseline.** All those fields remain `null` in the JSON ledger.

## Exact historical-source crosswalk

| Slot | Stored remote URL | Archival item / accession | Institution's subject and date | Rights evidence |
| --- | --- | --- | --- | --- |
| 428:1 | `https://objects.lib.uidaho.edu/bigburn/bigburn23.jpg` | [Big Burn 23, **8-B498b**](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn23.html) | Barnard-Stockbridge; Wallace burning at night, **20 Aug 1910** | Institution states public domain based on publication date |
| 428:2 | `https://objects.lib.uidaho.edu/bigburn/bigburn38.jpg` | [Big Burn 38, **8-C05b**](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn38.html) | Barnard-Stockbridge; burned timber along Placer Creek, **1910** | Institution states public domain; PD Mark |
| 428:3 | `https://objects.lib.uidaho.edu/bigburn/bigburn10.jpg` | [Big Burn 10, **8-X90**](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn10.html) | Barnard-Stockbridge; Wallace ruins viewed from Samuel's Hotel, **Aug 1910** | Institution states public domain; PD Mark |
| 428:4 | `https://objects.lib.uidaho.edu/bigburn/bigburn18.jpg` | [Big Burn 18, **8-X545e**](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn18.html) | Barnard-Stockbridge; Pacific Hotel ruins, **Aug 1910** | Institution states public domain; PD Mark |
| 428:5 | `https://tile.loc.gov/image-services/iiif/service%3Agmd%3Agmd427m%3Ag4274m%3Ag4274wm%3Ag016871905%3A01687_1905-0001/full/pct%3A25/0/default.jpg` | [LOC **sanborn01687_005**, digital ID **g4274wm.g016871905**](https://www.loc.gov/item/sanborn01687_005/) | Sanborn Fire Insurance Map of Wallace, **Sep 1905**, first/index sheet | LOC Sanborn collection states public domain and free to reuse, with prescribed institutional credit |

**Important visual-context safeguard:** The Sanborn image is a **1905 historical baseline**, not a 1910 fire scene. The current stored ALT calls it a 1905 map and is consistent. The first sheet includes the index **and** local street detail; do not substitute another sheet without checking whether the article's explanation depends on this exact layout.

For Big Burn 23/38/10/18, University of Idaho individual item pages provide a preferred citation, studio credit, source identifiers, dated descriptions and rights language. The official collection's [item-citation guidance](https://lib.uidaho.edu/digital/home/help.html) says to use the individual item page's rights and attribution. Institutional public-domain determinations are positive reuse evidence, **not** a substitute for our own item-level attribution/identity review. The LOC collection expressly permits reuse, but the site must still maintain appropriate credit and avoid misrepresenting a historical source.

## 960px / WordPress cached-derivative plan — NO PRODUCTION CHANGE

1. **P0 browser acceptance:** logged-out Chromium desktop + mobile, screenshot each post image, capture the actual `currentSrc`, `naturalWidth`, network response status, content type, redirect target, encoded transfer bytes and cache state, especially for the source URLs above. Record failed request *and* visible fallback. Mark broken only on observed failure, not domain or image-viewer availability alone.
2. **Rights and binary gate:** only after editorial and reuse review authorizes a particular historical original, retrieve that *single* permitted image through its official download endpoint; preserve catalog ID, URL, title, date, source credit, license/rights evidence and SHA-256. No unlicensed scraping or bulk mirroring.
3. **Dimensions:** read the **actual downloaded original intrinsic dimensions and orientation**; calculate `target_width = min(960, original_width)` and `target_height = round(original_height * target_width/original_width)`. Do **not** upscale, crop evidence-bearing details, or infer original size from stored Gutenberg markup (`1024×1487` etc.). Current derivative width/height are intentionally `null`.
4. **Staged WordPress delivery only:** create a separately reviewed media-library upload with a visible credit, historical context and stable archival item link. Confirm generated thumbnail/`srcset`/`sizes`, correct 960px capped rendition, responsive layout/CLS and CDN caching, without modifying raw Gutenberg post blocks or changing the source link. Defer any exact-block edit until explicitly approved. Keep originals and prior URLs for rollback.
5. **Release gate and claim verification:** compare the same URLs, browser versions, network conditions, cache state, viewport and device class before/after. Sum **encoded image bytes actually transferred** once per unique network request, not original library sizes or duplicate DOM references. Measure LCP/CLS separately. The founder's **42 broken-image** and **76% saved weight** figures remain **unverified**.

## Evidence files / scope

- Machine-readable 5-row ledger: `qa/media-recovery/pulaski_bigburn_primary_20261030.json`. Every row has the exact CMS URL/ALT, authoritative item, institutional rights statement, original-resolution `null`, 960px/no-upscale gate and `null` actual guest-browser status/bytes.
- `qa/media-recovery/validate_pulaski.cjs` and `test_pulaski.cjs` enforce the exact five catalog identities against the source census, prohibit invented image status/bytes/dimensions, and fail closed on rights or WordPress release toggles.
- This batch complements rather than modifies Site QA #154; its aggregate counts remain **61 published posts, 355 source images**, with **286** earlier Site QA offsite vs **288** current media inventory pending identical-input reconciliation.
- **Nothing was repaired in production:** five independent web viewer decodes and five official archival identity matches; zero browser-proven failures, zero copied images, zero WordPress uploads/edits, zero subscription spend and zero performance improvement claims.
