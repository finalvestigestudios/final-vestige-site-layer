# Florida Memory candidate rights clarification and catalog-retriever audit — 2026-11-13

**Scope:** FinalVestige.com inline-image reliability and archive research only; entirely separate from homepage design. **Draft-only. No writes to WordPress, image downloads, caching, replacement, merge or deployment.**

## Significant new authoritative rights evidence

Florida Memory's **official [ordering FAQ](https://floridamemory.com/share/order-info/faq.php)**, question 9, says that **all images on Florida Memory are offered under Creative Commons [Public Domain Mark 1.0](https://creativecommons.org/publicdomain/mark/1.0/)**, meaning free of *known* copyright restrictions. The FAQ explicitly asks for credit in accordance with **Florida Statutes §257.35(6)** and directs users to contact the State Library and Archives about credit/use questions. The archive's [disclaimer](https://floridamemory.com/learn/about/disclaimer.php) also describes state law and individual deeds of gift. The **Public Domain Mark is not a license** or a guarantee of exact item authorship; preserve the archive item number, photographer and credit and check any conflicting individual notice. This newly documented sitewide policy substantially improves the reuse-evidence trail for **Florida Memory's own items**, **not** for the separately published St. Pete Catalyst photograph.

The official FAQ text was verified in **fresh search-index output** on Nov 13; a direct web-retriever open returned a **403 wrapper**. The wrapper is **not** a verified archive server HTTP response or guest-browser finding.

## P0 287:5, five original archival item IDs, no silent replacement

The original published image URL is `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`. On Nov 13 the web retriever returned a 404 wrapper; the same-publisher migrated `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` **displayed an image**. Neither observation establishes actual visitor failure, cryptographic photo identity, scene/crop parity or republication permission.

Five official archival item catalogs previously researched were each reopened on Nov 13 and produced **retriever 403 wrappers**. Three had fresh current search-index item metadata; prior records establish the other two. These are *not five confirmed archive outages*. Their respective item IDs, source paths and historical limitations are:

| ID | Period | Scene | Disposition |
| --- | --- | --- | --- |
| [RC09236](https://www.floridamemory.com/items/show/32082) | 1980-05-09 | Car and broken bridge approach immediately after collapse | Alternate photograph only |
| [DGM0236](https://www.floridamemory.com/items/show/267897) | 1982-02 | Bridge damage two years later | Alternate photograph only |
| [PR01070](https://www.floridamemory.com/items/show/1042) | 1986 | Replacement bridge under construction | Alternate photograph only |
| [K894127](https://www.floridamemory.com/items/show/131903) | circa 1987 | Old/new spans | Alternate photograph only |
| [K894293](https://www.floridamemory.com/items/show/132066) | 1989 | Aerial view of both spans | Alternate photograph only |

**Decision:** Do not substitute an archive photograph for the publisher image without a disclosed editorial image change. The moved publisher image deserves same-scene screenshot/credit review, but cannot be mirrored or uploaded solely because its URL displays. Archive images may enter a rights/credit-informed editorial shortlist; all remain **HOLD** pending specific image identity, full-raster source dimensions/hash, visual/ALT integrity, source credit and the existing Site QA guest-browser evidence.

[Machine-readable five-item audit](../qa/media-recovery/florida_memory_pdm_and_catalog_wrappers_20261113.json) separates the observed web retriever wrapper codes from deliberately **null** origin HTTP, guest HTTP, native pixels, compressed transfer bytes and hashes. [Fail-closed validator](../qa/media-recovery/verify_florida_memory_candidate_policy_20261113.cjs) and [12-case regression suite](../qa/media-recovery/test_florida_memory_candidate_policy_20261113.cjs) protect those distinctions.

## Recovery / WordPress caching plan — not authorization

Site QA **#154** retains exclusive ownership of the Chrome logged-out cold full-scroll collector and P0 sequence `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. The Media Recovery draft's new evidence is **research-only**; do not duplicate the collector or modify another draft.

For an actual guest-confirmed broken source: obtain exact `currentSrc` and CDP request, response and completion IDs, redirect chain, cache flags, decoded/natural pixels, `encodedDataLength`, and cold screenshots. Authenticate the specific master binary and its documented rights. If and only if review approves caching, prepare a **staging-only** media proposal using a fully decoded, SHA-256-bound source and conditional derivative width **min(960, original width)**, retaining original aspect ratio, no upscale and a zoom/original-access pathway for label-dense diagrams. Record exact suggested ALT and credit, visual-diff at phone/Desktop DPR, one-slot rollback identity and staging editor approval. Never rewrite bulk WordPress post blocks or alter production here. If rightsholder consent is unavailable, prefer a properly attributed original-source link or an approved different-photo editorial treatment.

## Weight / 76% measurement discipline

The [reviewed worklist](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/refs/pull/183/head/docs/IMAGE-WEIGHT-WORKLIST.md) separates the **frozen 61 posts / 355 inline images / 288 offsite sources** from the expanded **66 posts / 361 inline** count. Historical **42 reported failures** have **zero actual cold guest-browser confirmations**, so do not call them repaired or broken.

The latest read-only WordPress inventory documents **15 originals >1,500,000 stored bytes** totaling **47,096,779 bytes**; 11 originals appear inline across eight published posts (**38,480,915 stored bytes**). Five 1672×941 PNGs in posts 34–38 lack generated subsizes and are strong P1 page-weight candidates *only after* P0 and rights/visitor measurement. Vasa's Jetpack `fit=1024` images may already transfer much less than storage size. Malbone archival maps require legible labels and alternative high-resolution access.

To test any **76% transferred-image-byte reduction**, instrument paired cold visitor sessions on the **same full-scrolled URL, device/DPR and identical image-source/slot cohort**, explicitly disable caches and service worker, and sum genuine CDP image-request transferred bytes. Formula: `100*(before_wire_bytes-after_wire_bytes)/before_wire_bytes`. Do not substitute media-library storage bytes, image metadata sizes or retriever errors for real transferred bytes; do not treat scene replacements as successful compression.

**Verified this sprint:** Five fresh archive catalog web opens returned 403 *retriever wrappers*, not origin/browser statuses; official FAQ PDM1.0 and statutory credit requirement retrieved through current authoritative search indexing; 12/12 postcommit exact-source isolated V8 checks passed. Native Node/CI/CDP verification not performed. No financial spending or production modification.
