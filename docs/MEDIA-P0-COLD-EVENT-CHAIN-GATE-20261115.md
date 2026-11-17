# P0 six-image cold CDP event-chain integrity — 2026-11-15

**Scope:** Read-only, off-homepage media-recovery work on existing draft [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183). Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains the **only** full-scroll guest-Chromium collection pipeline. No WordPress writes, media downloads, external image mirrors, rights clearance claims, homepage design changes, merges, deploys, or subscription spend.

## Verified safety defect and correction

Seven added adversarial regression cases reproduced a pair of **offline evidence-acceptance defects** in `qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs`:

1. `run.probe_version < 3` erroneously passes for a **missing**, **string** `"4"`, or **fractional** `3.5` collector version (JavaScript coercion). Such a record can be treated as a completed P0 browser census without establishing that it follows the supported collector schema.
2. Four explicit false cache flags (`was_cached`, `from_disk_cache`, `from_memory_cache`, `from_service_worker`) were sufficient for a synthetic loaded-image or browser-404 classification **even when `cold_event_chain_complete` or `cold_network_transfer_proven` was absent or false**. A partial CDP event stream with manually copied cache-negative values could masquerade as a genuinely uncached image response.

**Fix:** Require an integer collector version >= 3, both derived CDP attestations explicitly true, the existing four cache flags explicitly false, and unchanged strict request ID / final source / MIME / decoded-pixel reconciliation. All new cases remain pending when lineage is unproven. The already-verified loaded and HTTP-404 controls still pass. These are synthetic defects in QA adjudication, **not proof any production image is missing**.

**Before patch:** 40/47 isolated V8 checks passed; seven newly added adversarial checks reproduced failures. **After patch:** 47/47 passed against the actual GitHub-committed validator and tests (V8 with Node-compatible module/assert/URL shims). **Native Node, GitHub CI, and logged-out Chrome remain unrun.** Reproduce on a Node environment with:

```sh
node --check qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs
node --check qa/media-recovery/test_adjudicate_p0_guest_evidence_v1.cjs
node --test qa/media-recovery/test_adjudicate_p0_guest_evidence_v1.cjs
```

**Exact changed blobs:** source `59c3aa8f712d2d4c0ff492c6b27fc0d90a0b1b29`; tests `32a04171ad74c37301345d1c06741a49c8d9dc39`; [machine-readable six-source ledger](../qa/media-recovery/p0_cold_cdp_event_chain_custody_20261115.json) `d81f6635a84a124aab9e66306275d506ab2f7796`.

## Live-source retriever repeat, with no invented visitor status

Independently re-opened the six exact WordPress-stored original image URLs through an external web retriever on **2026-11-15**:

| Article image key | Web reader result | Guest browser HTTP | Primary-source / publisher recovery candidate |
|---|---|---|---|
| `285:5` (Three Mile Island) | wrapper 404 | **Unknown** | [Commons, 2010 image](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) — native 819×614, no 960px upscale or blind 16:9 crop |
| `285:2` (TMI panel) | wrapper 500, inaccessible publisher redirect | **Unknown** | [UCS migrated article](https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/) — Figure 4 rights and exact diagram identity HOLD |
| `287:5` (Skyway) | wrapper 404 | **Unknown** | [Florida Memory catalog](https://www.floridamemory.com/items/show/32083) — separate photograph, not an identical-photo drop-in |
| `418:1` (Coast Guard portrait) | wrapper 403 | **Unknown** | [USCG official catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) — public-domain catalog claim, exact crop and credit review HOLD |
| `418:2` (Scotch Cap) | wrapper 403 | **Unknown** | [National Coast Guard Museum](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) — scene and permission review HOLD |
| `407:1` (Hebgen) | wrapper 400, unsupported binary MIME | **Unknown** | [USGS catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) — public-domain catalog claim, actual file identity HOLD |

The [JSON ledger](../qa/media-recovery/p0_cold_cdp_event_chain_custody_20261115.json) preserves all six **exact published original URLs**, retriever methods/codes, separate null origin/guest statuses, primary catalog links, identity relationship, rights, known native dimensions, conditional maximum 960px geometry and all publication/rehosting holds. A web-wrapper failure is neither a confirmed origin response nor browser-visible breakage.

## Required Site QA handoff and release plan

Give the existing [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) collector ownership of one complete logged-out, uncached, desktop/mobile pass for the six P0 slots. It must supply the correct `probe_version`, full pre-navigation CDP Image lifecycle, two derived cold attestations, all four false cache flags, request ID, final URL and redirect lineage, `currentSrc`, pixel dimensions, MIME and encoded transfer bytes. A partial event capture remains unknown.

Only after a **confirmed broken image** and rights/scene/credit review should the editor prepare a reversible staging-only WordPress Media entry: preserve the original image URL and Gutenberg block; record new media ID, full original image hash, exact source catalog permalink, photographer/license/credit, ALT/caption decision, proposed original-to-media mapping, and rollback source. Generate a visually reviewed derivative no wider than `min(960px, original_native_width)`; avoid changing diagrams, charts or archival labels blindly. **No production post-block rewrite or third-party binary caching is authorized.**

To assess the alleged **76% image-weight reduction**, require paired, matching complete visitor CDP request-ID captures for the **same exact source slots**, browser version, viewport/DPR and cache conditions. Compare *transferred image bytes*, not WordPress library storage. Historical source census remains **61 posts / 355 raw inline images**, reported **42 broken** remains unconfirmed in cold visitor evidence, and the previously verified **16 originals strictly >1.5 decimal MB (49,107,665 stored bytes)** are a separate P1 issue. Do not equate those stored bytes with network savings.

**Release disposition:** HOLD; no actual visitor-broken images verified this batch, no asset replacement, no WordPress production change.
