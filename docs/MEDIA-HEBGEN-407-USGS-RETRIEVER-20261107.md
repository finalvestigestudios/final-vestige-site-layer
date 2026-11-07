# Hebgen Lake 407 — primary USGS origin response and source-credit recovery (2026-11-07)

**QA-only; not a WordPress deployment.** Scoped to the exact eight published stored external image references in the frozen 2026-10-30 Media Recovery census (`parts/02.json`, blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`), post 407. This is **not** a fresh WordPress fetch. The USGS catalog and exact image URLs were independently checked on 2026-11-07. Public browser access to FinalVestige.com and authenticated visitor request evidence remain unavailable.

## High-value findings

- **8/8 images have authoritative USGS catalog pages** mapped by matching described scenes; **7/8 original URLs eventually rendered within the web image viewer**. Slot `407:3` *initially* returned a generic inaccessible message, but **the exact same URL rendered when clicked from the official USGS catalog**. This is a concrete reason not to label generic tool failures as broken visitor images.
- Slot **407:1** original image URL was rejected by the viewer with a **400 wrapper error: unsupported `binary/octet-stream` content type**, while the catalog's **medium rendition** rendered. It could reflect metadata/MIME handling incompatible with some clients, but neither the source's actual HTTP status nor a guest Chromium decode failure is known. **P0 verification is justified**; don't change it automatically. The official alternate is a distinct derivative, not an independently authenticated source master or a preapproved cache.
- **Two public-domain-labeled USGS catalog records explicitly credit nonfederal photographers**: `407:2` Professor **William B. Hall**, Montana School of Mines; `407:3` **Mrs. Steven W. Nile**. Preserve these exact credits and do not assume federal employee authorship or automatic rehosting rights from the USGS hosting domain alone.
- `407:6` is a **1970** Seismic Geyser photograph (John Brandow, USGS), while `407:7` is a **2023** landscape (Mike Poland, USGS). Maintain dates, not a narrative implication of contemporaneous 1959 images.

## Staging-only repair path

1. Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns logged-out Chrome evidence. First capture each `currentSrc`, response redirect/status, MIME, `naturalWidth`, `complete`, screenshot, and encoded transfer size in post 407. Test slot `407:1` most urgently, and `407:3` to rule out transient tool artifacts. Ingest results into [#1395](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1395) rather than building another collector.
2. If a guest decode/network failure is **actually** shown, compare against the **individual USGS catalog's** Original/Medium derivatives; verify same scene/crop and exact binary or deliberate, editorially approved change. Note publication rights and source-specific photographer credits. `rights_gate=HOLD` for every row pending proof. No hotlink workaround or bulk-image mirroring.
3. Once licensed/authorized exact assets have been obtained by an approved operator, measure real source pixels and SHA-256. Create a ≤960px, aspect-preserving **no-upscale** file. Provisional display math is included for only three figures **based on stored HTML geometry, NOT native size**: `407:2` 960×674, `407:3` 960×684, `407:7` 960×723. Never claim these are generated derivatives or native geometry.
4. Stage in WordPress (not production) only after approval: media ID, responsive `srcset` with 960px max target, correct `width`/`height`, unchanged caption/credit and preserved permalink. Compare same-UA/DPR/viewport cold-cache mobile waterfall, `naturalWidth`, screenshot, CLS/LCP and CDP-transferred image bytes before and after. Rollback on any historical mismatch or unintended cropping. No Gutenberg block rewrite in this PR.

## Counting and reproducibility

The historic census is **61 posts, 355 inline stored source references**; later snapshot is **66 posts, 361 references**. Do not mingle cohorts. The user's “42 broken images” remains **not browser-verified**, and “76% weight reduction” remains **unmeasured**; thirteen >1.5-MiB originals represent **43,522,829 bytes of Media Library storage**, not proven user-transfer bytes. `hebgen_407_usgs_evidence_20261107.json` records eight exact source URLs, named authoritative catalogs, viewer outcomes and null browser outcomes. Run:

```
node qa/media-recovery/validate_hebgen_407_20261107.cjs qa/media-recovery/hebgen_407_usgs_evidence_20261107.json
node --test qa/media-recovery/test_hebgen_407_20261107.cjs
```

No production images repaired, no downloads, uploads, rehosting, WordPress writes, homepage edits, subscription or spend. This work complements the existing Media Recovery worklist [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183), not Site QA's collector or interim homepage design.
