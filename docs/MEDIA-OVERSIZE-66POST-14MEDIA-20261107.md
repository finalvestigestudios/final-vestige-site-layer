# Final Vestige media recovery: November 7 source-only 66-post / 14-large-media census

This is an incremental, **nonproduction** update to existing Draft PR #1402, not a competing draft or a change to Site QA #154. Read-only WordPress `posts.list`, **66/66** `posts.get(edit)`, and image `media.list` pages 1–2 on November 7, 2026. No downloads, browser rendering or CMS writes.

## Major verified change
- **66 published posts; 361 stored raw inline `img src` references; 118 image Media Library records.**
- **14 original assets strictly over 1.5MiB** (1,572,864 bytes): **45,553,777 original stored bytes**. Former 13 / 43,522,829 remains correct for the older capture, not the current one.
- Added **#2148** on November 7: `1927-caernarvon-levee-explosion-noaa-archive.jpg`, **2,030,948 bytes**, **1821×1190**. Conditional maximum **960×627**, preserving aspect ratio. In current 66 published raw post bodies it is **not** an inline or featured image; could appear on pages/drafts/templates, so do not delete or say unused.
- [NOAA primary photo record wea00739](https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg) identifies the Caernarvon dynamiting scene (dated 1927) and archival photographer Steve Nicklas. [Commons](https://commons.wikimedia.org/wiki/File:1927_Mississippi_Flood_Blowing_Levee.jpg) identifies the **1821×1190 cropped edition** and editor Wisekwai, with a US government public-domain designation. Different crop is not identical to NOAA's archival full image. Retain this distinction, item-level rights review and attribution; do not assign a specific day of April without proof.

## Current published-post raw image mapping
- **10 of 14** large originals appear in **seven** posts; matched original stored bytes **36,937,913**. Five **1672×941 PNGs** in posts **34–38**, media 39–43, have **no WordPress subsize metadata**; combined **13,267,538 stored bytes**, conditional preview **960×540** after text/transparency/visual rights inspection. Do not assert these are delivered at full original size without a browser trace.
- Malbone post **621** contains two direct-source large JPGs (media **1257/1258**), **10,352,064 stored bytes**; photo credit GeneralPunger **CC BY-SA 4.0** on 1257 and NYPL provenance/rights review on 1258.
- Vasa post **299** contains three first-party large JPEGs (media **382/388/389**), **13,318,311 stored original bytes**, while stored source URLs are **Jetpack `i0.wp.com?fit=1024`**. Prior PR #1402 found **seven strict exact original-src matches**; the three extra Vasa records arise from **filename-correlated proxy matching**, not necessarily a website change. Vasa creator rights (Anneli Karlsson; Karolina Kristensson) still require review.
- Four original media **2148,482,405,293** have no direct inline/featured reference *within these 66 published posts only*: **8,615,864 stored bytes**. The Water Resilience manual attachment (#405), founder photo (#293), new NOAA crop (#2148), and PNG #482 must **not** be classified as unused or deleted without checking pages, templates, draft posts, background CSS, media attachment views, and social previews.

## Next safe actions
1. Existing **Site QA #154** continues its **six P0** external-image browser checks (285:5, 285:2, 287:5, 418:1, 418:2, 407:1) and #1395 already owns evidence acceptance. No duplicate collector.
2. For PNG posts 34–38, Malbone 621 and Vasa 299 capture matched cold guest desktop/mobile full-scroll `currentSrc`, `naturalWidth`, source status/MIME, and **CDP encodedDataLength** with cache controls. Candidate 960px derivatives must preserve scene, annotations, credit, ALT and layout, plus copyright permission and rollback. Distinguish **original stored bytes** from delivered bytes, LCP and CLS; don't infer the claimed 76%.
3. No production post block rewrites, uploads, image caching/rehosting, deletions, homepage changes or subscription spend.

**Never assert** the reported **42 broken images** are visitor-confirmed, or that **76% wire reduction** was achieved. Every image's guest HTTP, decoded result and bytes remain `null` in the machine audit.
