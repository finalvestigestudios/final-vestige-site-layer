# Media recovery — legacy 61-post wire-claim v4 event-chain gate (2026-11-15 PT)

**Isolation:** Media Recovery draft [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183), not Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) or homepage visual design. No WordPress writes, binaries, mirror/cache, new collector, deployments or paid services.

## High-value correction
The newer single-pair comparator `compare_cold_image_wire_v1.cjs` already rejects collector version < 4 and Image CDP responses without completed cold-event-chain and transfer proof. The **separate older 61-post site-wide comparator** `weight_claim_pair_gate_20261102.cjs` did not enforce those attestations at its own entry point. The common `scopeByRequestId` verifies source identity, encoded data length and four cache-negative booleans but **does not inspect** `cold_event_chain_complete` and `cold_network_transfer_proven`. It was consequently possible for an otherwise syntactically complete old/synthetic browser log to be passed to a site-wide measurement path without verified request lifecycle proof. This is a **measurement-software integrity risk**, not evidence of a production image outage or 76% realized savings.

**Change:** both baseline and candidate must have integer `probe_version >= 4`, exactly `verified_pages=61`, and every *slot-bound* Image CDP request must explicitly attest `cold_event_chain_complete:true` and `cold_network_transfer_proven:true`. Missing/false flags now fail the comparison as `NOT_MEASURED`, never as a transferable byte saving. Prior source equivalence, active rendered src, loaded decoding, four cache-negative flags, requestId reconciliation, exact 61/355 scope and unchanged-source attribution checks remain in force. This does **not** approve media migrations.

## Evidence and tests
- Exact committed source blob: `d79335b8cead9d295b7cfaba9793a6dc7db7e413`.
- Refreshed test blob: `1295528ccfeb439dcbd694286801ac5d89e51c5e`.
- Original pre-fix test definitions: 27/32 passed in isolated V8; five measurement-positive fixture cases were stale because they lacked explicit `natural_height` and `from_memory_cache:false` required by pre-existing validators.
- Corrected committed source + tests: **44/44 passed** in isolated V8 with Node-compatible module and URL/source-identity shims, including **12 added adversarial cases** for invalid versions, missing 61-page verification, absent/false baseline/candidate event-chain or cold-transfer flags.
- **Not yet executed:** native Node (`node --test qa/media-recovery/test_weight_claim_pair_gate_20261102.cjs`), full GitHub CI and logged-out guest Chromium. This is a static/offline gate, not a field-measurement result.

## Six P0 source records and replacement queue
[Machine-readable six-source original URL, prior external-reader result, primary archival candidate, rights and conditional 960px sizing audit](../qa/media-recovery/legacy_sitewide_v4_cold_lineage_20261115.json). These are inherited from a separately verified same-day source ledger; **no new origin/guest HTTP result was obtained in this sprint**.

| P0 image | Earlier external-reader wrapper | Primary/recovery lead | Rehosting gate |
|---|---|---|---|
| 285:5 — Three Mile Island | 404 | [Commons TMI full-frame source](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg), 819 × 614 | Full-frame scene is not identical to published 16:9 crop; verify exact file/rights |
| 285:2 — TMI technical figure | 500 | [Union of Concerned Scientists article](https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/) | Diagram/publisher permissions and moved URL unresolved |
| 287:5 — Sunshine Skyway | 404 | [Florida Memory archival scene](https://www.floridamemory.com/items/show/32083) | Alternative photo only; not exact original; item-level rights and dating |
| 418:1 — Coast Guard portrait | 403 | [USCG official accession](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) | PD catalog claim with attribution conditions; exact binary/crop dimensions unresolved |
| 418:2 — Scotch Cap wreckage | 403 | [Coast Guard Museum context](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) | Historical source/rights/crop unverified |
| 407:1 — Hebgen scarp | 400 | [USGS official item](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) | PD catalog claim, but pixel identity/native dimensions not verified |

The 404/403/400/500 values are **web-reader wrapper observations**, not actual visitor or origin HTTP status codes. All six guest HTTP statuses, decoded pixel dimensions and transferred bytes remain **null**. No automatic asset replacement. Never upscale small archival originals to 960px; use `min(960, native_width)`, proportional height only after verifying the master and visual composition.

## Performance and restoration staging
The Oct 30 frozen audit contains 61 articles, 355 image slots, 288 external origin dependencies (286 direct + 2 remote-origin Jetpack). The reported **42 broken originals** remain unconfirmed by a complete logged-out browser capture, and **76% network reduction is still unmeasured**. A more recent read-only WordPress media snapshot lists 132 attachments, 20 originals >1,500,000 decimal bytes, totaling 64,385,752 *stored-original* bytes; that is **not** visitor network transfer. Do not combine this 66-post live snapshot with frozen 61/355 savings denominator.

Next release path: Site QA #154 supplies cold full-scroll desktop/mobile CDP evidence (`currentSrc`, HTTP, decode pixels, request event chain, image transferred bytes, screenshot). For a confirmed broken image only, verify exact historical photo/scene, item reuse rights/credit and master dimensions, then draft an isolated and reversible WordPress Media + responsive `srcset/sizes` staging proposal without touching Gutenberg blocks in production. Compare images visually and cold transferred bytes before any editorial approval. Keep original URL, ALT, caption and rollback manifest.

**Release status: HOLD.** No WordPress/image binary/cache/homepage production changes, merge, deployment or subscription spend.
