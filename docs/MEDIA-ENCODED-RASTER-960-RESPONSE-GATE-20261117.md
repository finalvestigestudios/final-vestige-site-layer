# Decoded raster custody for image-weight verification — November 17, 2026

**Scope:** Isolated Final Vestige media recovery engineering only; homepage design remains the interim lead's. Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns guest-browser collection. Draft media [#2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747) remains unmerged and undeployed.

## Confirmed measurement bug

The former evaluator compared browser `HTMLImageElement.naturalWidth` with a 960px cap. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/naturalWidth) specifies that this measurement is **density-corrected CSS pixels**; browser intervention can further change it. Therefore a 1920px-wide encoded resource reporting `naturalWidth=960` could pass a purported 960px-**file** cap. That does not certify the size of the downloaded raster.

The patched `qa/media-recovery/slot_parity_61_20261117.cjs` now requires `raster_width_px`, `raster_height_px`, `raster_probe='decoded_network_payload'` and a 64-hex `raster_sha256` from each baseline and candidate image response. It enforces **encoded** target width ≤960px, no encoded upscale in either axis, ≤2% raster/DOM aspect ratio deviation, ≥480px long-edge legibility for both raster and density-adjusted DOM readings unless the original is smaller, and identical evidence across shared GETs. Missing payload evidence means **HOLD**, not an inferred pass.

**Important:** the schema records collector-reported dimensions and SHA; it cannot itself authenticate that the image was downloaded or that the bytes were decoded. Site QA must cross-check raw response/trace, the reported hash, pixel dimensions, and visible screenshots. Capturing hash/dimensions for audit does **not** authorize storing or mirroring third-party media.

## Verification and primary source evidence

The actual updated CJS code and test suite were fetched back from GitHub at HEAD `9b412663f7bcd1ae1d8f40d61f70f52a21534814`. **79/79 regression functions passed in isolated V8 with compatibility shims** after retaining the pre-existing small-DOM-image legibility requirement. This is **not** a native Node execution or CI result; both remain unverified.

[Machine ledger](../qa/media-recovery/encoded_raster_6slot_source_evidence_20261117.json) carries six exact current WordPress VIEW origin/Jetpack URLs, prior method-specific status checks, no fabricated visitor outcomes, archival candidates, item rights, and nullable native pixels. On this sprint's independent reader recheck, the *exact* Skyway 287:5 and encoded SayMedia 285:5 **origin** URLs returned **404**. Guest Jetpack behavior remains unknown. [Official USGS 407:1 archive](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) loaded and names J. R. Stacy and Public Domain; the site-published image URL matches its Original link in the prior ledger, but binary digest and pixels remain unknown. A 403 from an agency host to a retriever does not prove the visitor's Jetpack copy fails.

## Rights and replacement pathway

Preserve the original photograph, crop, chronology and credit. USGS 407:1 has an especially promising official exact-URL match and public-domain statement; Coast Guard 418:1 has an official catalog lead but unverified exact binary; Scotch Cap 418:2 Museum preview is **600×463** and may not be upscaled; Florida Memory Skyway **RC09236** is different-frame historical context only and is not an interchangeable replacement. The Three Mile Island 285:5 alternative is **different-frame** even where public-domain attribution exists. Skyway 287:5 relocated commercial publisher file is **rights-uncleared**. No replacement has been licensed, downloaded, staged or approved.

Once Site QA proves a specific visitor failure and editorial/rights review approves an *exact frame*, inspect original master pixel size and SHA256 in an authorized temporary process, calculate `target_width=min(960, master_width)`, preserve aspect ratio and no upscale, keep title/ALT/caption/credit and immutable asset mapping, prepare a reversible **staging-only** WordPress media proposal, and compare same-page cold mobile/desktop transferred bytes, decode, visual and LCP/CLS. Do not modify raw Gutenberg blocks or production WordPress absent explicit release authorization.

## Sitewide denominator and savings caveat

The historical worklist at commit `f69a12cd9241ea0f39cfcb74c669bb6f7fb10357` reported **61 posts/355 image slots/288 external**. Current snapshot has **66 posts/361 slots/294 external**; they are separate cohorts. The user-reported **42 broken images are not verified in guest Chromium**. The proposed **76% reduction is unmeasured**; neither stored original bytes nor self-reported reductions establish transferred image bytes. The 20 originals >1.5 MB (decimal) total **64,385,752 stored bytes**, not guest requests. The older 286-vs-288 external classification remains a snapshot/methodology question.

**HOLD:** no image copying, scraping, WordPress production writes, caching/rehosting, post-block rewrites, homepage changes, merges/deploys or paid services. Site QA retains its existing collector; no duplicate was built.
