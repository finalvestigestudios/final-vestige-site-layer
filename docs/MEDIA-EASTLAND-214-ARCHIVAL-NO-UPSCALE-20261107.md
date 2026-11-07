# Eastland post 214 — source recovery and visual truth, 2026-11-07

**Isolation:** media engineering only, independent of homepage design, Site QA #154 collector, and prior media recovery PRs. No WordPress writes, source image downloads, caching, uploads, money spent, or post rewrites.

## Source and method
Fresh, authenticated, read-only WordPress **post 214**, modified **2026-11-02 21:39:34**, contains exactly **six inline image URLs**, all lacking explicit HTML image width/height. All six identical URLs and ALTs match frozen 2026-10-30 site inventory `qa/media-recovery/parts/07.json` (61 posts, 355 image slots, 288 offsite upstream). This is **source evidence, not browser load evidence**. Direct `web.open` attempts to all six exact source URLs were inaccessible to the web retriever; no actual origin HTTP response or guest-browser decoding can be inferred.

## Material discoveries
- **214:2** Chicago Daily News tug **Kenosha** Commons photograph is only **475×381** (2012 crop from 500×397 predecessor). Its safe preview must remain **475×381**, not 960px, with particular attention to whether cropping omits rescue context.
- **214:1** LOC 1915 panorama catalog master **2475×662** has a conditional **960×257** derivative. No center crop; removing edges loses the historic waterfront and rescue context.
- **214:3** photograph of **Helen Repa** is a **1915 newspaper image** listed as **4 August 1915**, distinct from the **24 July 1915** event; current Commons master **1786×920 → 960×495**. Neither publication date nor uploader date should be presented as shutter date.
- **214:4** direct LOC Bain **ggbain.19623** image relates to a Commons full-size 4153×5697 scan, but published `19623v.jpg` pixel geometry is **not verified**. Commons catalogs a conflicting **1910** date for “Reviving EASTLAND victim”; editorial review must check original LOC description before assuming photograph chronology. **No derived dimensions are approved**.
- **214:5** NARA **281841** (Commons 3000×2402 → conditional 960×769) documents the overturned ship **after the rescue/recovery mission** according to NARA's official Chicago exhibition, not an action shot of rescue. NARA *custody* does not prove the unknown photo author was a US federal employee; confirm rights individually.
- **214:0** LOC Bain **ggbain.19622**, LCCN 2014699553, is cataloged as overturned `7/24/15`. Unknown exact delivered JPEG dimensions → no speculative preview size.

## Catalog and rights
Primary catalogs: LOC `https://www.loc.gov/pictures/item/2014699553/marc/`, `https://www.loc.gov/item/2007661460/`, NARA `https://www.archives.gov/chicago/highlights/eastland`. Secondary item metadata: Wikimedia Commons `File:EastlandKenosha.jpg`, `File:Helen_Repa_Eastland_Disaster_photo.png`, `File:Photograph_of_The_Eastland_(upside_down)_on_Chicago_River,_Chicago._-_NARA_-_281841.jpg`. LOC says Bain has **no known restrictions**, but does not grant ownership/permission. Commons marks historical photographs PD-US; verify exact source, photographer, publication and individual treatment before rehosting. Keep photographer/institution credits in captions. **All rights/cache/WP authorization held false.**

## Staging plan, no production writes
1. Site QA #154, not this workstream, runs its existing logged-out Chromium/CDP collector at 360px and 1440px for existing six P0 image dependencies first, then Eastland 214:0–5. Record actual `currentSrc`, redirect-chain, Image request ID, HTTP and MIME, `decode()`/natural geometry, full-scroll screenshots and cold encoded bytes. Forward evidence through existing #1395 adapter. Retrieval-wrapper errors are NOT broken-image counts.
2. If a visitor-visible failure is verified, obtain right-cleared candidate from **exact catalog item**, compare source composition/crop and record item-level custody. Preserve each historic caption and alt. Resize only when verified original pixels permit, ≤960px, aspect-preserving, no upscale. Do not transcode lossy details or OCR labels without visual check.
3. Stage WordPress Media Library derivative only after license review and manual editorial approval; record attachment ID, copyright and credit, screenshot before/after at both viewports, rollback URL, and paired cold-browser Image GET bytes. **Do not rewrite Gutenberg blocks** as part of source audit. Any future surgical block replacement would require fresh hash/modified optimistic lock and separate approval.
4. **76% transferred-image savings is NOT measured.** Do not calculate a real visitor effect from 13 oversized WordPress originals (43,522,829 stored bytes). Site-wide claims require identical 61-post cohort before/after verified actual wire totals, no altered images missing or substituted, and no cache contamination.

Tests: `node qa/media-recovery/test_eastland_214_archival_20261107.cjs`. No external dependencies, no network.
