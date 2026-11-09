# Apollo R241 — NASA source-role / commercial-rights release gate

**STAGING HOLD. No production deployment, WordPress edits, affiliate activation, social publishing, consent bypass, or spending.**

This branch adds an isolated independent QA executable. It stacks on **R240 draft PR #1764**, never edits frozen homepage PR #49 or independent Research Desk PR #158. Source of truth: #150; business measurement/release coordination: #820 / #818.

## Evidence identities and limits (reviewed 2026-11-09)

- **Apollo 204 Review Board:** https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — primary technical conclusions and recorded chronology; probable electric arc **not** a conclusively identified single ignition source.
- **S66-58038:** https://www.nasa.gov/image-detail/amf-s66-58038/ — October 18, 1966 pre-accident crew preparation, **not** a fire recording.
- **S67-15717:** https://www.nasa.gov/image-detail/amf-s67-15717/ — January 1967 spacecraft preparation; not physical evidence of the ignition event.
- **S67-21294:** https://www.nasa.gov/image-detail/amf-s67-21294/ — January 28, 1967 aftermath/damage; not an ignition photograph.
- **NASA media/identity policy:** https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — research links are not commercial endorsement or clearance of image reproductions and astronaut likenesses.
- **NASA Apollo 1 collection:** https://www.nasa.gov/gallery/apollo-1/ — published photographic context.

**Rights decision:** No NASA imagery is newly embedded. Source-link verification only; publication or commercial use of any sourced image or person likeness still requires independent rights/endorsement review.

## Reproduce exact local QA

Unpack the R240 artifact `Apollo_R240_Real_AX_Print_LCP_CLS_STAGING_HOLD.zip` and use its `generated-r238-A/` directory. Install Python Playwright, BeautifulSoup and Chromium, with PHP CLI available. Do **not** fetch external websites in the test.

```bash
python experience2/apollo-r241/qa/r241_source_rights_gate.py \
  --atlas generated-r238-A --out QA-A
python experience2/apollo-r241/qa/r241_source_rights_gate.py \
  --atlas generated-r238-A --out QA-B
sha256sum QA-{A,B}/receipt.json
```

The runner verifies the **exact R238 manifest SHA-256** `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`, all protected-file hashes, and calls the **actual R224 PHP shim**. It tests source roles and limitations, disallows unauthorized paid order/affiliate/analytics claims, checks only one original-investigation CTA, and rejects seven intentionally unsafe mutations. Native Chromium checks run at 320, 390, 768, 1440, 1920px with JS on/off, native source disclosure, CDP accessible link names, no overflow, no network requests, and deterministic screenshots.

**Local result, 2026-11-09:** two independent executions, 10 Chromium contexts each, 7/7 mutations rejected per run, 10/10 screenshot pairs identical, receipt SHA-256 `91e04d7489acee8bd3c07c45ebc46a3e5d9b5850f7db0127f7838c799afd0642`. Exact tested Python Git blob: `98faacff1314bd542b6474c939a615505f233161`.

**Not claimed:** axe-core, screen readers, actual browser zoom, installed WordPress/Assembler, live HTTP (Chromium ERR_BLOCKED_BY_ADMINISTRATOR), hosted CI, field LCP/CLS, rights clearance, sales, or live campaign attribution. Staging acceptance is not production release authorization.

## Business fit / single action

Proposed Grok long-form Apollo 1 asset (actual post ID/URL still **UNKNOWN**) → verified Apollo Evidence Atlas → **one free read-the-original-investigation CTA**. The suggested educator dossier is a hypothesis, **not** an approved/rights-cleared purchasable SKU. Do not add a paid CTA. Grok owns production/distribution; Praxxis independent review via TASK-008; Claude owns analytics/merchant engineering; founder approves releases.

| Offer | Funnel step | Blocker | Change | Evidence | Owner |
|---|---|---|---|---|---|
| Future educator dossier | Payment | No verified SKU/rights/merchant fulfillment | Hold paid CTA | Not commercially verified | Founder / Claude |
| Grok Apollo film | Creator to landing | No verified published asset ID or mapped URL | Require TASK-008 handoff | Unknown | Grok / Praxxis |
| Free investigation | Evidence to next action | False source/rights/sales claims could erode trust | R241 gate | Local Chromium PASS | Apollo |
| Realized net sales | 7/30d attribution | No verified qualified-human sessions, orders, fees/refunds | Native measurement QA under #820 | NOT COMPUTABLE | Claude / Commerce |

**Release gate:** inherited R198 source ancestry, actual WP/Assembler, independent accessibility + media-rights review, CI, founder written authorization; all pending. No live changes made.
