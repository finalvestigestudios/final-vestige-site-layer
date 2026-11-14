# Media integrity: draft Artifact Editions page 2429 / asset 2432 — November 14, 2026

**P1 pre-publication visual-integrity HOLD.** No live 404, guest-browser failure, or visitor byte reduction has been established. This draft Commerce/Artifact Editions audit does not change homepage visual design or duplicate Site QA #154's six-image collector.

## New authenticated read-only WordPress evidence

The published-post list remains 66. The WordPress pages API returns page **2429** (“Artifact Editions — Original History Objects | Final Vestige”) as **draft**, modified 2026-11-12 01:54:55. Its raw content has one image whose source is a manually suffixed first-party path ending **editorial-concept-1024x576.png**. Its srcset lists another manually suffixed **editorial-concept-768x432.png** at 768w, the 1024x576 URL at 1024w, and the original PNG at 1280w. The exact four references, full image source URLs, sizes attribute, ALT and flags are preserved in the linked JSON audit.

The WordPress media API returns attachment **2432**, uploaded 2026-11-12 01:53:45, parent page **2429**, original **1280×720 PNG** storing **2,010,886 bytes**. It advertises 1024×576 and 768×432 renditions as **virtual:true**, with first-party Jetpack image proxy URLs based on the **original filename with fit query parameters**. It does *not* advertise the two suffixed filename URLs embedded in the draft. CMS virtual sizing does **not** prove those physical paths do not exist — no HTTP GET or filesystem inspection was performed.

**Concrete risk:** the draft's one image has **three unadvertised source references** (one src plus two srcset entries), representing **two distinct physical-path candidates**. Its original is separately advertised. A future browser may select a candidate that fails to resolve; this is a *potential prelaunch breakage*, not a confirmed public outage.

## Safe reversible plan — not applied

First obtain a logged-out browser test of the **draft preview only if accessible to an authorized tester**. Inspect selected currentSrc, natural/decoded pixels, response MIME/status, the 768/1024 physical paths, responsive CSS box and DPR. If those hardcoded paths are not functional, consider a *small reviewed draft-only* URL substitution with the two **media API-provided Jetpack proxy URLs**, retaining original 1280w entry, declared aspect ratio, ALT “Concept art, not finished merchandise,” and sizes/decoding/loading semantics. Keep an exact original block snapshot for rollback. Do **not** rewrite post blocks wholesale, publish the draft, or alter any production page.

A theoretical 960×540 rendition is dimensionally possible without upscaling, but does not exist in this audit and may only support 480 CSS px at 2× DPR. Larger approved responsive renditions may be needed. Neither first-party storage nor a WordPress attachment establishes creator permission or clearance to use a concept image in commercial context. Confirm actual item provenance, rights, portrayal and captions before any new derivative or publish action. No binaries were downloaded, cached, resized or rehosted.

## The 16-original / 61-post source crosswalk

The frozen October 30 source baseline is **61 posts / 355 inline images**. A November 8 read-only scan counted **66 published posts / 361 raw image tags**. Of then-existing oversized WordPress originals, **11 images referenced inline across eight published posts** accounted for **38,480,915 stored original bytes**. Four other older originals (#482, #405, #293, #2148) totaling **8,615,864 stored bytes** were not found in that **post-only** scan; they may be referenced from other pages, featured images or blocks and are **not a deletion list**.

The November 14 WordPress media snapshot shows **125 image attachments**, including **16 originals strictly above 1,500,000 decimal bytes = 49,107,665 stored bytes**. New attachment **#2432** (2,010,886 bytes) was absent from the November 8 122-image census and is now confirmed **attached to draft page 2429**, rather than unused. The byte identity is exact: 38,480,915 + 8,615,864 + 2,010,886 = **49,107,665**. These **storage** figures do not establish browser transfer volume or any 76% weight reduction.

Priority published external-source image slots remain **285:5, 285:2, 287:5, 418:1, 418:2 and 407:1**, exclusively owned for guest-browser verification by **Site QA #154**. The historical **42 allegedly broken originals remain unconfirmed**; the claimed **76% real transferred-byte saving remains unmeasured**. The established Coast Guard, USGS, Navy, Florida Memory and other archival candidate ledgers remain on rights, same-scene, crop and visitor-status HOLD.

## Offline reproducible quality gate

Run these from the repository root:

- node --check qa/media-recovery/audit_wp_virtual_srcset_20261114.cjs
- node --check qa/media-recovery/test_wp_virtual_srcset_20261114.cjs
- node --test qa/media-recovery/test_wp_virtual_srcset_20261114.cjs
- node qa/media-recovery/audit_wp_virtual_srcset_20261114.cjs qa/media-recovery/draft_2429_virtual_srcset_20261114.json

Expected CLI status: **HOLD_UNVERIFIED_VIRTUAL_FILE_PATH**, **3** unsupported path references and **4** image URL references checked. The 36 native Node tests cover source/draft identity, virtual/proxy mismatch, responsive geometry, no false HTTP or byte claims, time-separated source baselines, rights-operation restrictions and adversarial mutations. This is pure local file processing; it makes no network requests or production writes.

**Release remains blocked:** no approved media replacement, CMS production edit, risky Gutenberg rewrite, homepage design change, merge, deployment, subscription spend or image copying is authorized by this work.
