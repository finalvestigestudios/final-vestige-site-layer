# Apollo Experience 2.0 — R15 source-year lens and authenticated context export

**Date** 2026-10-31 PT | **Status** DRAFT / HOLD | **Issue** #150 | **Base** R14 PR #268 exact `9bd42395edcb82a32b3d2c2e3046faeb48bc892c` | **Source pin** PR #215 `74375657f2cdaac0710f94c6de6c24534ee06858`.

## Implementation

- Native radio CSS-only source-year context filter: 6 all, 1 from 1966, 3 from 1967, 2 from 2017. JS not required. Unsupported `:has()` browsers show all records and hide nonfunctional filter controls (fail-open).
- The filter changes source visibility, never a historical finding or evidence provenance. 1966 training and 2017 retrospective exhibits remain explicitly differentiated from the 1967 accident.
- New deterministic six-record `source-context.json` export from canonical NASA catalog witness rows, preserving catalog identifiers, dates, source credit, limitations, NASA URLs, chronology and source-drawer anchors, link-only media restrictions and `geometry=not_assigned`.
- Context JSON packed as additional hash-checked asset into editor/nonce-only staging PHP. Secure download route now permits five explicit research exports; new `X-FV-EX2-Apollo-Context-SHA256` is independently checked by read-only staging admission.
- Zero NASA photo embeds, zero speculative pins or relationships, zero WordPress changes, zero paid services. All changes isolated to `experience2/apollo-wp-bridge/sealed`.

## Executed exact-authored-source QA

- **68/68 Python/PHP integration and adversarial tests passed** (14 new vs R14 56): date reclassification, non-NASA domain, rights escalation, missing source drawer, export integrity/header tampering, PHP HTTP auth and nonce denials.
- **7/7 actual Chromium/Playwright viewport passes** 320 / 360 / 390 / 768 / 1024 / 1440 / 1920. Four radio controls, 6/1/3/2 counts, native keyboard ArrowRight, touch taps, no-JS filter, SourceDrawer disclosures, 44px link targets, reduced motion and 200%-equivalent zoom; no root overflow, 14 screenshot SHA receipts.
- Local synthetic LCP where observed 148–324 ms; 1440px LCP unavailable. Local synthetic CLS 0 in all seven runs. NOT production/field CWV or Lighthouse.
- Two deterministic plugin packages match. ZIP SHA-256 `5fc93112e5561e208674290a091558c6577640789bd141f4a393406bef77915b`. Derived source context index SHA-256 `d48d13c5102ff3fa2920f744b7e55a3d8c8ef804eb5215a9e09f6db783c3975e`.

## Blockers

Verified axe-core bundle unavailable, so **axe certification NOT RUN** and `--require-axe` remains fail-closed. Chromium navigation to HTTP, intercepted, file and data origins blocked by execution-environment policy; actual browser-enforced CSP and cookies not verified. PHP socket tests use synthetic WordPress shim, NOT WordPress staging. No Assembler/Jetpack render, Safari/VoiceOver/NVDA, hosted metrics, independent QA, successful hosted CI, individual NASA media reuse clearance or founder visual approval. DO NOT MERGE OR DEPLOY.

## Reproduce

From `experience2/apollo-wp-bridge/sealed/`: `python -m unittest discover -s qa -p 'test_*.py' -q`, `python qa/browser_exact.py`, `python qa/browser_exact.py --require-axe` (expected hold), `python build_sealed.py --out R15-review.zip`.

## Sources rechecked 2026-10-31

- NASA image record S66-58038 (18 Oct 1966): https://www.nasa.gov/image-detail/amf-s66-58038/
- NASA KSC-20170124-PH_KLS01_0164 (24 Jan 2017 tribute): https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/
- NASA images/media guidelines, attribution, no implied endorsement, third-party material and commercial/identifiable-person restrictions: https://www.nasa.gov/nasa-brand-center/images-and-media/
