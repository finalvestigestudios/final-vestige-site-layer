# Image weight: version-4 cold-wire proof gate and six original P0 sources
**2026-11-15 Pacific | Draft-only engineering | Existing media PR #183; separate Site QA #154**

## What actually changed

The standalone `compare_cold_image_wire_v1.cjs` previously emitted `LAB_PAIR_MEASURED` for two otherwise plausible synthetic snapshots even if their `probe_version` was absent, fractional, a string, or pre-version-4, **and even if a bound Image network request lacked `cold_event_chain_complete` or `cold_network_transfer_proven`**. All four cache flags could be forged as `false` with no verified CDP transfer. This allows a false-positive **76%** comparison (1000 B baseline versus 240 B candidate), not evidence of real site traffic. Independent P0 adjudication already rejects these records; the performance comparator had fallen behind that safety policy.

Changed **only** media-recovery comparator and its two existing fixture/test files, plus this isolated ledger and documentation; none of Site QA #154's four files or homepage components were touched.

* A completed browser result now requires integer `probe_version >= 4`.
* Every **bound** Image request must have `cold_event_chain_complete === true` and `cold_network_transfer_proven === true`, in addition to all four cache flags being exactly `false`, exact request ID and final URL, image MIME, status 200 and positive `encoded_data_length`.
* Unmatched independent theme/logo requests are still outside article-photo bytes; additional transfers from the same historical image continue to force `HOLD`.
* Both baseline and candidate must qualify. The original per-slot published source must remain identical; the script refuses to misrepresent a different historical image as compression.
* Even a valid `LAB_PAIR_MEASURED` is **not** 76% site-wide proof, field CWV, rights approval or a restoration deployment.

## Reproduction and tests

Previous exact comparator Git blob: `fc7c662f72fbba99b6078cdc7ba18c6cf21110c1`. New source blob: `9c5e7e74a4ca2437a806489f1e4804537c527fb0`. Added nine version/cold-event tests, updating fixtures in two preexisting regression files.

Using the exact committed code in isolated V8 with explicit Node assertion, URL and conservative source-equivalence shims:

- Prior comparator: **1/8** selected regression controls passed and **7/8** failed (seven reproducible false-positive cases).
- Patched comparator: **72/72** tests across the main and source-family suites passed.
- These are *not* native Node executions, browser observations or CI. The URI shim was test-only; the real implementation continues to import the existing `browser_probe_core.cjs` source-equivalence policy. Actual CI and real CDP captures are pending.

## P0 source queue: real URLs, not fabricated visitor errors

The [machine-readable six-source ledger](../qa/media-recovery/cold_wire_pair_v4_integrity_20261115.json) retains every exact original published URL, prior external-reader wrapper code, official archival candidate, identity gap, rights constraints, unknown master dimensions, and `null` guest-browser status/bytes.

This sprint independently reopened two originals via an external web retriever: [Sunshine Skyway old publisher URL](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg) returned wrapper **404** and [USCG Scotch Cap debris JPG](https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg) wrapper **403**. These are **not** HTTP status captured from a real user/browser. Historical same-day wrapper outcomes for the other four P0 references were 285:5 **404**, 285:2 **500/inaccessible redirect**, 418:1 **403**, and 407:1 **400/unsupported binary**; the provenance and date are preserved in the ledger. **No source is yet confirmed broken to visitors.**

Archive-rights observations: [USCG Anthony Pettit portrait, VIRIN 210330-G-DE713-0002](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) says public-domain release with photographer credit and separate DoD limitations; [USGS 1959 Hebgen fault scarp](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) lists photographer J. R. Stacy and public-domain usage. Catalog rights do not verify that a candidate binary is the same photograph/crop, nor the actual source URL HTTP outcome. The 1980 Skyway alternatives at Florida Memory differ in chronology or image composition; the 2010 TMI Commons aerial must not be presented as a 1979 photograph. All prospective sources remain on **rights/identity HOLD**.

**Sizing:** calculate derivatives only from verified native master dimensions and conditional maximum width `min(960, nativeWidth)`. Preserve aspect ratio, never upscale, and check text legibility, crops, old/new bridge chronology, archival photo identity and attribution. When master dimensions are unknown, output geometry remains `null` and derivative creation is held.

**Proposed future staging after approval:** existing first-party WordPress Media Library or licensed cached copy, physical 960px-max derivatives and responsive srcset/sizes, item-level license and archive credits, visual before/after at mobile/desktop, exact slot mapping, original source retained for rollback. No blanket external mirroring or Gutenberg block replacement.

## Cohort and release math

The *frozen* Oct 30 source census is **61 posts / 355 stored inline images**, which differs from a later expanded **66 posts / 361 stored image references**. Do not pool unmatched cohorts. The reported **42 broken images** are not guest-CDP confirmed; the proposed **76% network-byte reduction** has no verified paired browser measurement. The last verified media inventory was **16 WordPress originals strictly above 1.5 decimal MB, totaling 49,107,665 stored bytes**; storage is not transfer. Compare the *same complete cohort* on desktop/mobile separately with cold version-4 evidence and provenance/visual review before reporting any lab delta.

## Operational boundaries

Site QA #154 owns its existing full-scroll guest Chrome collector; Media Recovery owns only the offline consumption/measurement policy, archival triage and reversible proposals. No duplicate collector, third-party image download/rehost, production WordPress write, home page visual change, paid subscription or merge/deploy occurred. **Next action:** capture cold guest failures and actual transferred bytes for the six P0 slots; do not restore an image on retriever status alone.
