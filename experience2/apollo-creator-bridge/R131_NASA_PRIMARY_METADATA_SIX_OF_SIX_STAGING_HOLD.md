# Apollo R131 — NASA #04 primary-source metadata reconciliation (STAGING HOLD)

Date: 2026-11-04 PT. Scope: Apollo 1 / Experience 2.0 isolated evidence lane, stacked on R130 draft PR #1028. Sources: Issue #150; commercial attribution #820 and charter #818. **No homepage PR #49, Research Desk PR #158, WordPress, analytics, Grok queue, checkout, email or production edits.**

## Independent primary-source finding — record 04
- Official NASA image-detail page: https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/
- NASA's rendered image-detail metadata explicitly states **Taken January 24, 2017**, **Producer KSC**, **Image Credit NASA/Kim Shiflett**, **PIA Number KSC-20170124-PH_KLS01_0164**. Page title: *Apollo 1 Tribute*.
- Readable direct metadata independently retrieved on November 4, 2026. Earlier R130 classified this image as secondary-only because its NASA page did not return readable metadata then. **R131 resolves only that evidence-source limitation.**
- Historical interpretation remains **RETROSPECTIVE_DISPLAY**, not a photo of the January 27, 1967 fire. Do not infer any 1967 event timing, exact ignition source, map position, or other photographic fact from this 2017 item.
- This check does **not** clear image republication, advertising/endorsement, identified-person likeness, third-party rights or an FV paid educator product. **Commercial image clearance = 0/6.** NASA media guidance: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

## Implementation
1. `r130_nasa_media_custody.json`: source 04 now PRIMARY_PAGE_VERIFIED with NASA official metadata support. All six NASA image-page records have direct-source verification; crew portrait catalog `S67-19766` is **still provisional**.
2. `r130_nasa_media_custody_gate.cjs`: six strict primary-page provenance expectations. A credit, catalog, image role or cited support URL alteration now fails; NASA-domain substitutions no longer pass provenance support. Exit status remains **STAGING_HOLD** regardless of source audit pass.
3. `test_r130_nasa_media_custody_gate.cjs`: 21 tests, including the four new adversarial tests for source #04 credit, catalog, provenance and source #02 evidence-role drift.
4. `landing-preview.html`: user-visible native `<details>` SourceDrawer explains NASA 04's newly verified metadata and 2017 status. No new external link, primary CTA, image, map coordinate, analytics script or checkout.
5. `r131_source_evidence_manifest.json`: exact tested file blobs and evidence classification, independent of PR-head self-reference.

## Checks / limit of proof
- Four changed source files re-fetched from the actual GitHub R131 branch after committing.
- A V8 Node-compatible test harness executed **21/21 authored source custody tests** successfully against those exact branch files, including negative mutations; separate in-memory contract assertions **12/12** passed before the branch writes. These are **not native Node CI, real page navigation, actual Chromium/Playwright, axe-core, LCP/CLS, or production evidence**.
- The prior Chromium environment returned `ERR_BLOCKED_BY_ADMINISTRATOR` for HTTP, file, and data URL navigation. Do not re-label an injected document/fixture as full-page QA. A browser that permits actual navigation must still execute 320/360/390/768/1440/1920px, no-JS, keyboard, touch, zoom and reduced-motion checks with reproducible screenshots and actual-page performance.
- Research Desk PR #158 remains frozen/unmodified with six outstanding source-role/editorial findings. WordPress/Assembler integration and historical review remain open. **No release without independent QA and founder approval.**

## Conversion-first gate (the commercial priority)
**OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER**

- Existing but unverified FV paid educator item → merchant-confirmed paid order → no matching, rights-cleared SKU, verified price/checkout/delivery/refunds → **withhold commerce CTA; merchant inventory read-only verification** → FAIL/BLOCKED → Claude/Growth/founder.
- Grok future Apollo long-form asset → evidence-backed landing → free printable classroom source exercise → image #04 was not directly corroborated → **R131 primary metadata custody and accessible disclosure** → BUILT + SOURCE-TESTED, no live traffic claim → Apollo.
- Paid purchase → net revenue per 1,000 qualified-human sessions (7d/30d) → no approved purchase journey or linked merchant orders and platform asset IDs → **reuse Issue #820's approved privacy-safe attribution**, no duplicate tracking → N/A/UNOBSERVABLE → Claude/Growth.

**One on-page next action** remains the free classroom exercise (without a signup). Hypothetical future teacher casefile is neither sellable nor a confirmed conversion. Grok owns script/distribution; Praxxis owns creator review through shared TASK-008. **STAGING HOLD / NO DEPLOYMENT.**
