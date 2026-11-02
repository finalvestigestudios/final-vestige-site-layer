# Oversized first-party media: seven recovered ALT values and five PNG HTML dimensions — 2026-11-02

**Lane:** Media Recovery draft PR #183, independent of homepage design and Site QA PR #154. **No production write.** This is a source-evidence correction and a P1 browser-prioritization result, not evidence that the browser already downloaded 43.52 MB, that 42 images fail, or that 76% savings occurred.

## Concrete correction

The prior 13-original ledger `qa/media-recovery/oversized_inline_proxy_corrected_20261102.json` correctly counted **10 inline references** and identified three first-party Vasa images delivered through Jetpack, but it persisted **null ALT metadata for all seven directly hosted inline originals**. That loss happened in the ledger, **not** the source census. Frozen authenticated WordPress source records in **parts/01.json** and **parts/08.json** contain substantive ALT strings for all seven. The committed ledger now copies those exact strings and records each slot's stored HTML width/height. Its Vasa items still match **parts/02.json**. All **10/10 inline oversized-original slots** have a nonempty ALT in the frozen post source.

Affected slots and their grounded source descriptions:
- `34:0`: San Francisco firefighters and horse-drawn engines during the 1906 fires.
- `35:0`: Shackleton's crew in a lifeboat during the Endurance expedition.
- `36:0`: civilians sheltering in a cave during the Siege of Vicksburg.
- `37:0`: reconstruction of Petra water channels and reservoir system.
- `38:0`: San Francisco emergency cistern use after the earthquake.
- `621:0`: surviving Malbone Street Tunnel alignment.
- `621:1`: 1903 Brooklyn Rapid Transit network map.

These descriptions paraphrase the exact source census; the updated JSON preserves the **complete original ALT strings**. Do **not** claim these posts have missing accessible ALT attributes based on the superseded ledger's nulls. Their live DOM accessibility remains an independent Chrome test.

## P1 five-PNG size and visual-integrity batch

Posts **34, 35, 36, 37, 38** each have one large first-party PNG original with **1672 × 941** source metadata and **1024 × 576** HTML image dimensions in the frozen post source. None of the five records has WordPress-generated subsize metadata. Their five originals together contain **13,267,538 storage bytes (12.65 MiB)**.

| Image key | Media ID | Original storage bytes | Page |
| --- | ---: | ---: | --- |
| 34:0 | 39 | 2,892,087 | `/2026/08/16/the-morning-san-francisco-lost-its-water/` |
| 35:0 | 40 | 2,552,136 | `/2026/08/16/the-boat-that-refused-to-die/` |
| 36:0 | 41 | 2,498,247 | `/2026/08/16/the-city-that-went-underground/` |
| 37:0 | 42 | 2,488,823 | `/2026/08/16/how-petra-made-water-flow-through-stone/` |
| 38:0 | 43 | 2,836,245 | `/2026/08/16/the-cisterns-beneath-san-francisco/` |

The source-to-HTML width difference **does not prove** that visitors transfer the full originals. An HTML `width` attribute is not a confirmed `currentSrc`, natural decoded width, or network encoded size. It is a focused **P1 measurement hypothesis**, behind P0 potential missing external photographs.

Conditional derivative geometry from source 1672×941 is **960×540** without upscaling; measured candidate binary dimensions, bytes, codec choice and visual/rights clearance are **not yet available**. WordPress image ownership by itself does not establish independent rights to alter/rehost artwork. Do not silently transform illustrated scenes or overwrite the originals.

## Evidence and safety checks

- Source census Git blob SHA-1: parts/01 `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`; parts/02 `48e1ebf07207e948ba5802e714eb39659d2e1c1d`; parts/08 `5659ec243c188928be3f89c0f96354b660608ca2`.
- Updated machine ledger commit: `8bdf6e871af80a2368105fa0854099cf57c4331c`.
- Defensive ALT/geometry/source validator commit: `a95b7511338bcd3c59e07b54d04ff1e2ed1235a5`.
- Extended regression test commit: `6c6f035b76b372a2b4f997c02dc2d5ea7bb529fa`.
- **35/35 tests passed** against the exact committed validator, snapshot parts and regression sources using isolated V8 Node API shims. **Native Node CI not executed** in this run. Tamper tests reject null/altered source ALT, falsified HTML dimensions, changed source snapshots, imaginary HTTP/byte-savings evidence, bogus rights and WordPress write approvals.
- Browser HTTP status, MIME, redirect chain, `currentSrc`, decoded dimensions, actual encoded transferred bytes, and LCP/CLS remain **unverified**. Five image URLs independently checked with the web retriever on November 2 were **inaccessible to that tool without numeric origin HTTP responses**; that is not a proof of site outage.

## Nonduplicating Site QA handoff

Site QA PR #154 owns the existing logged-out Chromium/CDP image audit. Keep its P0 targets **285:5, 287:5, 418:1–2, 407:1** first. When P1 capacity permits, inspect posts 34–38 in mobile and desktop cold-cache conditions using that *existing* browser code: recorded DOM ALT, `currentSrc`, CDP image request/final response, actual transferred bytes, naturalWidth and screenshots. Compare same post/source/viewport before/after only after rights and staging review. A claimed **76% sitewide reduction must not be computed from file-library original storage**.

**Unchanged baseline:** 61 published posts, 355 stored inline image references, 288 external-origin references, 13 originals >1.5 MiB (43,522,829 original storage bytes), 0 production images repaired. The reported 42 broken and 76% reduction are not verified browser measurements. Zero media downloads, paid services, Gutenberg rewrites, WordPress production changes or homepage design edits.
