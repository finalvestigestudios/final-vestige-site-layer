# Apollo Experience 2.0 — R219: real viewport + no-JS acceptance (STAGING HOLD)

**Scope:** isolated Apollo Evidence Atlas QA, related to #150, #820 and business charter #818. **Base:** R218 exact-source recovery commit `dbe95c617d1e86da08ce0c30c7d2d964b6f93181`. **Never touch** homepage PR #49, homepage lead branches or the standalone Research Desk PR #158. **Nothing in this PR deploys or edits WordPress.**

## Why this matters — visual regression in R218 evidence

The R218 screenshots came from PHP *fragments* placed in Chromium with `page.set_content(fragment)` and no hosting-document `<meta name="viewport">`. On mobile Chromium, such a test may use a wide virtual layout viewport and scale the content, rather than exercising actual 360px and 390px wrapping. Indeed the earlier R218 screenshot receipts recorded **identical hashes at 360 and 390px**. That does **not** establish a layout defect in the component itself, but it invalidates those screenshots as evidence of distinct mobile layouts.

R219 supplies a full, deterministic HTML test shell with `<meta name="viewport" content="width=device-width, initial-scale=1">`, actual R217 PHP-rendered HTML, its *SHA-pinned* generated stylesheet, and two explicitly different JavaScript settings per width. This directly fixes the test-harness defect without altering evidence/source data or adding unrelated commercial UI.

## Source and exact reproduction

- New source-controlled gate: `experience2/apollo-r219/qa/mobile_gate.py` (Git blob `99e4ee33e69ddeee011b33b25ab6c54fef8c8e89`).
- Exact upstream committed builder source blob: `769b574c14a37220d522e37ceaea01044630e3e7` (R217 commit `5d40d61149838eb3c36d0c8a5a15ba22e31c71da`).
- Required independently pinned R216 staging manifest SHA-256: `a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128`.
- Expected exact-source R217 output manifest SHA-256: `90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72`.
- From a staging workspace with sibling `apollo-r216/dist/` and `apollo-r217/build_r217.py`: `python experience2/apollo-r219/qa/mobile_gate.py --workspace /path/to/staging-workspace --output /path/to/evidence`.
- Prerequisites: Python 3, Playwright Python, PHP CLI, system Chromium at `/usr/bin/chromium`. No network or paid service needed. Captures 16 PNGs + JSON receipt, excludes timestamps from deterministic artifact content. The upstream R216 dist is an **explicit local fixture**; it has not been reconstructed to canonical R198 ancestry.

## Executed local gate, not an installed website claim

The **byte-identical source code committed to GitHub** was executed locally twice. Each run: 8 widths **320, 360, 390, 600, 768, 1024, 1440, 1920**, each in true viewport **JS-enabled and JS-disabled** Chromium (16 contexts per run), PHP lint/render/print/late fallback, SHA-pinned source and manifest checks, no active scripts/forms, no speculative geographical overlay, one free investigation CTA with >=44px native tap target, duplicate ID / missing ARIA reference checks, native keyboard and touch/pointer disclosure operation, printed source-based answer-guide visibility, no horizontal overflow, and full-page screenshots.

**Result: PASS 16/16 contexts in both runs.** Their screenshot SHA-256 values matched **16/16** across runs. Unlike R218, 360px and 390px now have different reproducible screenshots. JavaScript-disabled contexts genuinely use `java_script_enabled=False`. In a supplemental *non-committed* local probe, four widths (320/390/768/1440), forced-colors normal/active and simulated CSS zoom to 200% did not overflow; this is **not** a claim of actual browser/UI zoom acceptance.

LCP collected using Chromium PerformanceObserver on the **eight JS-enabled offline fixtures**: approximately 88–104ms; CLS = 0 in those fixture measurements. These values are **NOT production CWV**, are not real network performance, and are not p75 field traffic. Genuine axe-core, screen-reader AT, real browser zoom, installed WordPress, cross-origin link navigation, hosted CI and independent QD remain **NOT EXECUTED/NOT ACCEPTED**. Browser fixture tests also do not independently certify NASA image/likeness rights.

## Source and commerce separation

Flagship: **Apollo 1 / The Hatch Opened Inward**. NASA's [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) reports an electrical arc as the most probable initiator; the exact ignition source was not conclusively identified. NASA's [advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) does not grant commercial endorsement or automatic astronaut-likeness permission. No new photographs, marketing rights or speculative historical claims were added.

One audience path only: **Grok Apollo long-form (published asset and asset_id UNVERIFIED) → source-led Evidence Atlas → free original investigation → possible teacher-ready educator dossier**. Dossier is a **product hypothesis**, not a sellable/approved SKU. The editorial CTA remains the only commercial-adjacent next step; NO unrelated Mini Museum promotion is inserted into the accident narrative.

| Offer → funnel step | Blocker | Change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Future educator dossier → paid sale | No approved SKU, rights-cleared media, checkout, fulfillment | Validate product/customer demand before a paid CTA | NOT VERIFIED — commercial HOLD | Founder / Claude Commerce |
| Grok video → Atlas | Published asset ID/post URL not independently verified | TASK-008 reconciliation with Grok and Praxxis; no queue edits | UNOBSERVABLE | Grok / Praxxis |
| Atlas evidence → free investigation | Mobile fixture screenshots lacked viewport meta | R219 true mobile and genuine no-JS gate | 16/16 LOCAL PASS; 16/16 hash parity | Apollo |
| Verified order → realized net revenue | No attributable merchant order/qualified cohort evidence | 7/30-day order/refund/fee reconciliation via existing #820 tracking plan | NOT COMPUTABLE | Claude Analytics |

**Release:** HARD STAGING HOLD. Missing: inherited R198 canonical source chain, genuine axe-core + AT, installed WP staging acceptance, actual HTTP/navigation, CI on exact R219 head, independent QD and founder release authorization. No production CMS, website, analytics, paid offer, merchant, email, creator or social posting writes.
