# SL-1 media-recovery source custody — 2026-10-30

**Scope:** [published WordPress post 221](https://finalvestige.com/2026/08/18/the-rod-was-supposed-to-move-four-inches/), *The Rod Was Supposed to Move Four Inches*. Read-only editor-context confirmation on Oct 30 found **seven** stored `Special:Redirect/file/` image sources, matching the 61-post census; no production edits.

Machine-readable crosswalk: `qa/media-recovery/sl1_primary_source_20261030.json`. Source gate: `validate_sl1.cjs`; negative tests: `test_sl1.cjs`. All seven Commons file record pages were resolved in an independent web viewer; that is **not** a visitor image request, HTTP 200 proof, or evidence that the article images load.

| Slot | Commons original size | Safe output cap | Attribution / nuance |
| --- | ---: | ---: | --- |
| 221:0 | 704×346 | **704×346** | U.S. Army; no exact Army accession ID obtained. Never upscale. |
| 221:1 | 729×589 | **729×589** | DOE/INEEL cutaway; historical INEEL figure **60-3227** is visible on page 138 of the official archive book. Commons date 2011 is not the drawing's original date. |
| 221:2 | 1454×1753 | **960×1157** | DOE reactor technical schematic; preserve line-work readability. |
| 221:3 | 346×253 | **346×253** | AEC reactor-core removal photo; provenance via English Wikipedia to Commons, higher-res accession not identified. Never upscale. |
| 221:4 | 1406×1881 | **960×1284** | DOE/INEEL 81-3966; **1981 retrospective documentation** of 1961 accident damage, not an accident-in-progress photo. |
| 221:5 | 1436×1113 | **960×744** | DOE/INEEL 61-9; Highway 20 contamination monitoring **Jan 4, 1961**. |
| 221:6 | 1402×1050 | **960×719** | Foundation pier demolition; Commons caption cites **INEEL 67-2587**, while author/date fields cite **INEEL 81-3966 / 1981**. This is an unresolved metadata conflict, not a settled photograph date. |

**Primary institutional source:** Idaho National Laboratory, *Proving the Principle*, [Chapter 15](https://inl.gov/content/uploads/2024/05/Chapter-15_Low-1.pdf), including first-page diagram `INEEL 60-3227`, and related Chapter 16 referenced on Commons. Note: some figures carry historical source IDs different from the Commons upload timestamp. Do not interpret a reproduction date as an original capture date.

**Seven file-record links:** [SL1nuclearpowerplant.JPG](https://commons.wikimedia.org/wiki/File:SL1nuclearpowerplant.JPG); [SL-1_-_Cutaway_of_reactor_and_control_building.png](https://commons.wikimedia.org/wiki/File:SL-1_-_Cutaway_of_reactor_and_control_building.png); [SL-1_-_Reactor_schematic.png](https://commons.wikimedia.org/wiki/File:SL-1_-_Reactor_schematic.png); [US_AEC_SL-1.JPG](https://commons.wikimedia.org/wiki/File:US_AEC_SL-1.JPG); [Sl-1-ineel81-3966.jpg](https://commons.wikimedia.org/wiki/File:Sl-1-ineel81-3966.jpg); [Sl-1-ineel61-9.jpg](https://commons.wikimedia.org/wiki/File:Sl-1-ineel61-9.jpg); [SL-1_-_Dismantling_of_the_foundation_piers.jpg](https://commons.wikimedia.org/wiki/File:SL-1_-_Dismantling_of_the_foundation_piers.jpg).

**Rights:** Commons labels the items U.S.-federal-government public domain, but one image is transwiki-sourced and INL/national lab material can involve contractor exceptions. Individual-item provenance, credits and non-endorsement must be confirmed before copying or WordPress localization. Preserve each canonical file page, source attribution and any appropriate author's credit.

**Cache and remediation plan (proposal only):** First collect logged-out real-browser image-element `currentSrc`, `naturalWidth`, response URL, redirect chain, HTTP status, content-type and encoded transfer bytes on desktop/mobile. Only confirmed failed or materially excessive assets proceed to rights review. Then obtain the exact licensed original file through permitted archive download, compute master SHA-256, render a `<=960px` no-upscale derivative preserving aspect ratio (do not resample 346px source upward), compare visually, attach item credit, use a separately authorized WordPress Media upload, verify responsive `srcset`/cached Jetpack delivery and screenshot the complete article. Do not bulk-rewrite Gutenberg blocks or alter the homepage design. Preserve the current original for rollback. Measure LCP/CLS and image transfer bytes before/after on identical conditions; the reported 42 broken and 76% savings are not verified.

**No WordPress writes, downloads of third-party image binaries, billing, or deploy.**
