# Apollo R148 — offline browser QA with source provenance and truthful axe gate

**2026-11-05 | BUILT / FIXTURE-TESTED / STAGING HOLD.** Isolated from frozen homepage PR #49 and Research Desk PR #158. Governing issues: #150 (Apollo), #820 (commercial conversion), charter #818.

## What changed
- Added `r148_acceptance_gate.py`, which accepts only a locally provided, R147-repaired, SHA-256-pinned WordPress raw Gutenberg snapshot plus the R147 source-custody receipt. A change to the image/CTA content or receipt is rejected before browser testing.
- Reuses the existing R146 Playwright offline document tests and adds six-width (**320/360/390/768/1440/1920**) two-mode (JS on/off) Chromium checks for all three archival figures, the ordinary **Read the full investigation** link, exact link target, focusability, no-JS visibility, overflow and reduced-motion preference.
- Records screenshot hashes for each mode and verifies screenshot bytes before recording results.
- **Crucial:** the R146 runner previously emitted `OFFLINE_TEST_PASS` without axe-core being supplied. R148 explicitly returns `OFFLINE_QA_INCOMPLETE` until a vetted local axe-core source is provided and runs without violations. An offline-green result still cannot certify actual WordPress-theme accessibility, live production, LCP, CLS or paid conversion.
- Added 12 native Python adversarial tests. No analytics code, merchant links, email, tracking, map pins, photo-rights assertions or WordPress writes.

## Reproducible local commands
Use the existing R147 node gate to produce `review/apollo-r147-offline-review.html` and `review/r147_source_receipt.json` **from an independent authorized read of WordPress page 2017**. R148 refuses other content, including its own synthetic fixture, at the CLI boundary.

```sh
python -m unittest experience2/apollo-creator-bridge/test_r148_acceptance_gate.py -v
python experience2/apollo-creator-bridge/r148_acceptance_gate.py \
  --input review/apollo-r147-offline-review.html \
  --r147-receipt review/r147_source_receipt.json \
  --axe-js /preapproved/local/axe.min.js \
  --out new-empty-r148-evidence-dir
```

The script uses installed Python Playwright and local Chromium; it neither navigates the public site nor fetches external assets. The raw Gutenberg HTML does not include actual WordPress theme/styles or live image delivery. **Browser fixture evidence is not live-page acceptance.**

## This sprint's actual evidence
- Native Python 3.13: **12/12 unit tests PASS** (including same-length tampering, source drift, fake release approval and false browser claims).
- Local Chromium: **142/142 browser+source checks PASS on the synthetic R146 fixture; 1 expected FAIL** for missing local axe-core. Final status `OFFLINE_QA_INCOMPLETE`; 19 screenshot files with hashes. The fixture is explicitly **SYNTHETIC**, not the published WordPress page.
- Exact tested Git blob SHA: `r148_acceptance_gate.py` `c50f0c2129f4a82ca676aaf21db83a0d9dacf525`; `test_r148_acceptance_gate.py` `d6f98b1280fe752f10fd9251012007d90f1e0287`.
- Read-only WordPress page 2017 metadata: last modified `2026-11-04T17:09:24`, 96,274 raw characters; the original incorrect gallery selector is still present. **No live repair**.
- No actual WordPress export was transferred into the offline Chromium environment for this sprint; no actual-page axe, p75 LCP/CLS, production screenshots or verified source-linked revenue.

## Commercial bridge: one relevant, nonintrusive action
Candidate Grok long-form/Shorts: **Apollo 1: Fourteen Seconds, More Than One Failure**, historical source trail and NASA Board primary reference. Proposed high-intent buyer: grades 6–9 history/science educators. Existing LIVE landing URL: `https://finalvestige.com/apollo-1-evidence-atlas/` and its single published static **Read the full investigation** action (not a purchase). Potential educator evidence dossier is **not a verified sellable product**; verify rights, seller inventory and fulfillment before suggesting a paid link. No Grok Apollo asset, qualified visits, confirmed buyer, merchant order, fees/refunds or attributable net revenue have been verified.

**Offer → Funnel → Blocker → Change → Evidence → Owner:** educator dossier → investigation-to-purchase → no verified SKU → audit Payhip product, rights and checkout → BLOCKED, Claude/Growth; Grok Apollo → Atlas → asset & UTM unknown → reconcile TASK-008 → NOT VERIFIED, Grok/Praxxis; Atlas → investigation → wrong gallery selector in published source → R143 repair + R148 QA gate → source-checked and synthetic-browser-tested, Apollo; verified order → net revenue/1,000 qualified sessions → no reconciled orders → use #820 7/30-day cohorts, Claude/Analytics.

## Release gate
**STAGING HOLD.** Actual fixed WordPress content needs browser evidence (320–1920, keyboard/touch/no-JS), axe-core, theme integration, real asset delivery, p75 LCP/CLS, photograph-specific rights review, independent historical review, sellable product verification, QD review, exact-head CI and founder production authorization. This PR is draft and stacked only on the Apollo R147 branch. No WordPress, social, email, payment, analytics or homepage modifications.
