# November 3, 2026 — Frozen-source and CDP request identity guard (Media Recovery PR #183)

**Scope:** Separate from the interim homepage art director and Site QA #154. Zero production CMS actions, media downloads, license assumptions, spend, or photo substitutions.

## Material defect closed

The sitewide 76% CDP byte evaluator formerly checked decoded image responses and the 61/355 slot census, but a request associated with a slot could describe an unrelated tiny photograph. That made a favorable byte reduction **insufficient to demonstrate historical-image integrity**. A plausible but unrelated placeholder can load perfectly and still destroy the original documentary value.

The new `claim_source_identity_gate_20261103.cjs` compares every before/after mapped slot against its **exact immutable stored source URL**, then ties DOM `currentSrc` to the CDP `request_url`. Missing/extra mappings, unrelated originals collapsed into a single request, source substitution, wrong post, and partial repetition fail closed. The evaluator now issues `sitewide_76_percent_verified: true` **only if this separate binding gate passes**, in addition to its pooled-byte calculation, cache/response checks, complete 61/355 inventory, and repeat thresholds.

The CLI reads all eight frozen census part files and checks each raw file's Git SHA1 blob identity against the pinned manifest before calculating the claim. Any previously collected benchmark lacking the new binding fields downgrades to limited-sample, not a sitewide savings badge.

New per-request fields: `dom_stored_sources: {"287:5":"<exact Gutenberg stored URL>"}` and `dom_current_sources: {"287:5":"<actual img.currentSrc>"}`. Keys must match `slot_keys` exactly. CurrentSrc must equal the CDP request URL. DOM evidence itself is still a supplied assertion, **not independent proof of a browser run**. A legitimate historical-image replacement requires separate provenance, rights, same-scene/crop and manual release approval; this fast-path deliberately refuses silent source changes.

**Additional fail-closed hardening:** A complete frozen 61/355 capture that omits DOM/source bindings or substitutes an original now returns `INSUFFICIENT_DATA`, with `measured_reduction_percent:null`, rather than exposing even a potentially misleading limited-sample percentage. Code commit `a31179264e603b8fe7bdbe0678b3c56aed8f6a0b`, test commit `739c32fde00a3740f4cb8e191915dddbd62f0e72`; existing 38/38 V8 regression suite remains green. Native Node/CDP remain pending.

## Verification

**50/50 synthetic checks passed** against exact committed GitHub blobs in isolated V8 CommonJS compatibility execution: 12 source binding cases and 38 wire-byte evaluator cases. The 355-slot positive fixture and decoy/missing-binding mutations ran successfully. This is not native Node CI. There are no actual guest Chromium network recordings or measured before/after wire bytes. Consequently **42 alleged broken images are not established** and **76% achieved savings cannot be claimed**. Stored originals (13 over 1.5 MiB) are not visitor page-transfer measurements.

Commits:
- `093bf9f9fba51e16a508e7a11ae89f8d2b2559ce` source binding
- `41479cba534631cad1745cfeaf759704e4b23024` 12 tests
- `fb02f5b7d9c82c6a4c0b7e3828c91282d932f278` evaluator integration
- `0026c2bd9b35eb0875c9ecb5b54613925dc6ca74` 38 case suite
- `7db385b7428aa0f9eefc154e0ff6c94bc5322e72` SHA1 object NUL fix

## Preserve highest-priority visual repair

**Sunshine Skyway 287:5:** frozen published image is `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` (retriever wrapper 404; guest browser status unknown). The publisher's current [original April 10, 2020 article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/) links to `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`, independently displayed November 3. Existing PR research already identified that migration; this sprint rechecked the link.

**Visual-integrity risk:** The migrated publisher image depicts Summit Venture against broken original Skyway piers; it does **not** depict the later new cable-stayed bridge, despite the frozen article's ALT description. The publisher credits University Press of Florida. The similarly themed Florida Memory 1987 alternative is **not** proven identical. No copying/rehosting or URL/ALT editing without browser verification, publisher rights review, historical visual confirmation, and explicit publication approval. Original intrinsic dimensions remain unknown; maximum 960px width and no upscaling if a licensed rendition is later authorized.

## Hand-off to Site QA #154

Continue independent logged-out **390px and 1440px** Chromium tests, prioritizing 285:5/285:2, 287:5, 418:1-2 and 407:1. Capture `currentSrc`, raw `getAttribute('src')`, CDP requestId, HTTP/MIME, image `naturalWidth`, screenshot/visible load, cold `Network.loadingFinished.encodedDataLength`. Compare exact source identity and check each historical caption. No duplicate edits to Site QA PR #154.

All releases remain **HOLD** pending rights-cleared, visually verified archival candidates and measured visitor-borne performance. The old 61/355/288/13 source baseline remains unchanged.
