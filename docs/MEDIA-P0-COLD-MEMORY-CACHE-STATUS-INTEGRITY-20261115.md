# P0 image restoration: memory-cache false-positive fix and six-source status custody — 2026-11-15

**Scope:** Off-homepage media engineering in existing draft [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183), independent of Site QA browser collector [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). **Source-only QA; no media downloads, copying, uploads, published-post writes, production deploy, merge, or paid API use.**

## High-impact verified offline defect

The independent P0 adjudicator `qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs` required three CDP cold-cache flags to be explicitly false: `was_cached`, `from_disk_cache`, and `from_service_worker`. It **did not check `from_memory_cache`**. In a reproducible synthetic fixture a **memory-cached 404** (with valid request ID, matching final URL, zero decoded width and height) was incorrectly reported `BROWSER_CONFIRMED_BROKEN`. A memory-cached successful 200 was incorrectly treated as a freshly loaded source, and missing memory-cache metadata was treated as fresh. The independent browser classifier already demanded four cache-negative flags, so the adjudicator had an inconsistent security/evidence contract.

The amendment requires `from_memory_cache === false` in all source-adjudication paths, including failed-origin HTTP, successful 200 image, and 200 image decode errors. It changes **no underlying browser collector**, runtime WordPress behavior, media files, or user-visible design.

Four new adversarial tests now prove that cached 404, cached loaded 200, **omitted memory-cache metadata**, and cached decode error cannot be promoted to visitor evidence. The existing cold 404 and loaded image controls still pass. Locally executed **isolated V8 Node-compatible mocks: patched 40/40 PASS; old 36/40 (four false-positive test failures)**. This is not native Node or real Chromium; native CI must independently run:

```sh
node --check qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs
node --check qa/media-recovery/test_adjudicate_p0_guest_evidence_v1.cjs
node --test qa/media-recovery/test_adjudicate_p0_guest_evidence_v1.cjs
```

The two amended Git blobs are `f4c647581f701241f4256b82721ed776bc5a2c13` (adjudicator) and `e65aee5d4b9875a987ac9f20e142c1e3cba8eae8` (tests).

## Fresh source-reader status matrix, NOT browser 404 confirmations

The [machine-readable six-source audit](../qa/media-recovery/p0_memory_cache_proof_custody_20261115.json) retains exact original URL, archive-candidate URL, each web reader wrapper's response, and **null visitor/origin HTTP, currentSrc, natural dimensions and encoded image bytes**. On **November 15, 2026**, the external web retriever reported:

| P0 slot | External web-reader result | Primary catalog or alternate candidate | Rights / scene limitation |
|---|---|---|---|
| `285:5` | wrapper 404 | [Commons Three Mile Island 2010 original](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) | Public-domain dedication appears on catalog; original is 819×614, not the published 1200px 16:9 crop |
| `285:2` | wrapper 500 / inaccessible publisher redirect | [Migrated UCS article](https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/) | Specific Figure 4 panel; reuse and pixels not cleared |
| `287:5` | wrapper 404 | [Florida Memory #32083](https://www.floridamemory.com/items/show/32083) | Separate 1980-era archival image, NOT an identical-photo replacement |
| `418:1` | wrapper 403 | [USCG Pettit portrait VIRIN 210330-G-DE713-0002](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) | USCG public-domain catalog and credit instructions; original thumbnail/crop identity unproven |
| `418:2` | wrapper 403 | [National Coast Guard Museum Scotch Cap collection](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) | Same destruction scene may differ from article's original crop, item reuse check pending |
| `407:1` | wrapper 400 unsupported octet-stream | [USGS Hebgen fault scarp](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) | USGS lists public domain, photographer J. R. Stacy; exact image/file unknown |

A web reader refusing a binary, a publisher denying that reader, or a redirect failure **is not proof that a logged-out Chrome visitor sees a missing image**. Do not call any of these six broken yet. The historical “42 broken external images” is a reported figure only and **0 of the six currently have new cold-browser proof** in this audit.

## Non-overlapping Site QA handoff and release process

1. **Site QA #154 owns** full-scroll desktop/mobile *logged-out* Chrome capture, request IDs, final URL/redirect chain, MIME, actual CDP encoded transfer bytes, explicit **four false cache flags**, `currentSrc`, both natural dimensions, viewport/DPR and screenshot. A stale/partial event stream fails closed. Hand over its existing JSON; do not build a competing collector.
2. This module reconciles only already-captured evidence, preserving each frozen original image URL. Positive browser/DOM proof distinguishes loaded vs broken; cached or missing facts remain pending. A confirmed broken slot is still **not** an image license or publication authorization.
3. Compare *exact depicted scene, viewpoint, crop, author and catalog record* with any candidate before editorial selection. Florida Memory's Skyway image is a **different photo**, and USCG/USGS catalog custody does not independently prove uploaded binary identity or the right to use an arbitrary derivative.
4. Only with documented rights approval prepare a **reversible staging-only WordPress Media plan** with catalog permalink, creator, license/credit, original source URL, asset hash, media ID and restore URL. Cap at `min(960, original_native_width)` and calculate height preserving aspect ratio; do not enlarge TMI's 819px master. Check 1×/2× CSS display and maps/diagrams for loss of fine text.
5. To test the proposed **76% weight reduction**, compare the same complete 61-post or defined subset cold Chrome cohorts before/after, identical viewport/DPR/cache conditions, fully attributed CDP request-ID bytes including alternate and duplicate renditions. Never substitute 16 oversized originals' **49,107,665 stored bytes** for visitor network data or assert site-wide reduction from selective samples.

**Release status: HOLD.** No browser-proven original image failure in this batch, no approved replacement, no WordPress production write. P0 six-source integrity precedes the P1 >1.5 MB original-image work; Site QA and the interim homepage visual lead keep their respective ownership.
