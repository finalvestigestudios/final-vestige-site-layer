# Apollo R468 — archival source identity and provenance custody (2026-11-18 PT)

**Scope:** staging-only additive successor to Apollo R467 PR #3072; this branch is not for direct production activation. Homepage PR #49, independent Research Desk PR #158, Claude commerce/analytics work and Grok/Praxxis TASK-008 are outside scope.

## Finding / change
The old `fv457_valid()` accepted any apparently valid NASA hostname and counted the right number of accepted and held records, but could still accept a *different* valid NASA image URL paired with an unrelated archive ID, or a swapped date/Atlas placement. R468 requires exact editorially-reviewed (record ID, verification state, machine date, precision, displayed date, source URL, Atlas placement, homepage confirmation) tuples for the six existing entries. Any source correction must update the separate contract deliberately and be reviewed; this is not remote authentication or license evidence.

## Tested (offline)
- PHP lint for gallery and EvidencePlate module: PASS.
- `python qa/r468_custody_gate.py`: 13 deliberately broken ID/date/URL/status/placement cases REJECTED; valid six-record source set renders with three EvidencePlates, three chronology entries, visible source holds and one original free investigation CTA.
- `python qa/r467_contract_gate.py`: 26 source/accessibility/integrity assertions PASS.
- `python qa/r468_browser_gate.py`: 14 local Chromium/Playwright contexts PASS (320, 360, 390, 768, 1024, 1440, 1920; JS enabled/disabled; keyboard, 390px tap, reduced motion, no horizontal overflow). Screenshots at 390 and 1920px.
- Previously established printed PDF custody: a local 390px Chromium print export had nine unique NASA URL destinations and one original FV investigation destination; no new commerce link.
- `python qa/r468_archive_gate.py`: creates deterministic offline archive from exact source, QA scripts, screenshots and manifest. Same input produced identical zip SHA-256 across two consecutive builds: `7e2f1d8beecf2c0bf45825a8eb0d669befce0eac1bc73e06b37006dda49fcfd1`. ZIP is delivered in the assistant's automation report, not committed to the repository.

**Explicit HOLD_NOT_RUN:** Chromium page navigation on hosted WordPress; validated axe-core; navigated LCP/CLS, INP and field p75 Core Web Vitals; real screen-reader and independent QD review; exact-head green CI. The browser gate uses `page.set_content` and MUST NOT be described as navigated CWV evidence.

## Sources / rights
Source identity and image-use permission are separate. NASA primary archive: https://www.nasa.gov/gallery/apollo-1/ . NASA media and commercial rules: https://www.nasa.gov/nasa-brand-center/images-and-media/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . `S67-19766` image-ID mapping and `KSC-20170124-PH_KLS01_0129` candidate catalogue lookup remain editorial HOLD. No images embedded, no invented geo pins, and no NASA endorsement or commercial license claimed.

## Commercial pathway: OFFER → FUNNEL → BLOCKER → TEST → OWNER
1. **Original source-led Apollo educator dossier → real paid checkout:** no verified rights-cleared payable SKU, checkout, fulfillment or refund ledger → no paid CTA; Founder + Claude; HOLD.
2. **Grok long-form / Shorts asset → attributable qualified Apollo landing:** no verified published asset ID, destination, consent-safe human sessions → Grok owns creative/distribution, Praxxis creator QA, Claude attribution; UNKNOWN.
3. **Atlas source records → the free Apollo investigation:** source identity acceptance tightened; retain single nonintrusive contextual CTA; local source/browser PASS, hosted HOLD; Apollo / independent QD.
4. **Confirmed order → realized net revenue per 1,000 qualified sessions:** absent merchant-verified orders, fees/refunds and 7/30-day cohorts → not computable; Claude commerce.

**Production HARD HOLD:** no merge, deployment, WordPress post/settings write, publication, mailing, merchant/affiliate activation, new analytics scripts, or spending. Requires independently cleared NASA media rights where applicable, approved true staging, exact-head CI, QD, genuine offer/checkout verification and founder release authorization.
