# Apollo R122 — cancelled-print recovery + exact-source browser evidence guard

**2026-11-04 / DRAFT ONLY / STAGING HOLD.** Additive Apollo lane; parent Issue #150, source-role reconciliation in Research Desk draft PR #158, business prioritization #818/#820. Parent branch R121 at `f2305dbfb9e60e9401ef313c40854b0a24eca247`. No edits to homepage PR #49, Research Desk #158, active production branches, Grok scripts or Praxxis shared task queue. No deployment, merchant, email, analytics or WordPress writes.

## User-visible defect
R120–R121 set `fv-worksheet-only` before invoking native printing and reset it **only** when the browser emits `afterprint`. If a browser/OS print sheet is dismissed without that event, the in-memory `pending` guard ignores subsequent student-print clicks, and later ordinary printing can unintentionally omit the full investigation/source register. That would violate Apollo's historical source-custody promise.

## Actual staging implementation
- The existing standalone student worksheet remains one optional utility; main free classroom exercise is the single primary destination. No new primary CTA, external checkout, signup or third-party script.
- `landing-preview.html` resets print state idempotently on `afterprint`, `pagehide`, return from print media, delayed refocus after canceled print, and a native Ctrl/Cmd+P keyboard shortcut. An explicit second print-button click always retries after a missed exit event; `window.print()` exception also restores.
- Explanatory button uses `aria-describedby` with unique guidance text. Print-only six NASA source links, 2017 retrospective status and 0/6 media clearances remain unchanged. The no-JS full packet still works.
- `qa_r113_print.py` now refuses to declare *actual-source release acceptance* unless the canonical Apollo HTML bytes exactly match `git show HEAD:experience2/apollo-creator-bridge/landing-preview.html`. A renamed fixture, missing Git metadata or dirty/nonmatching source fails **UNVERIFIED_SOURCE_IDENTITY** before running.
- QA now asserts retry without `afterprint`, native Ctrl+P recovery, `pagehide` and refocus. Fixed a genuine QA false-positive: `page.evaluate('window.print=()=>{...}')` returns the function, which Playwright's evaluation helper may invoke; appending `;null` prevents premature invocation and makes the print-count assertion meaningful.
- `test_r122_print_recovery.cjs` adds 17 dependency-free Node `node:test` cases by extracting the **actual** HTML's lifecycle controller, including explicit failure/no-JS, errors, keyboard, media, focus and omission-of-afterprint scenarios.

## Evidence received this sprint
- Exact R122 GitHub landing/source read and its real controller executed directly with a V8 mock-DOM harness: **18/18 assertions passed** (NOT native Node CI or browser). Browser runner source updated separately and re-fetched.
- **Actual Chromium 144.0.7559.96** on an **identified representative R121-derived R122 fixture**, not the complete Apollo staging HTML: **14/14** viewport/JS configurations (320, 360, 390, 768, 1024, 1440, 1920 × JS on/off), two print screenshots, one student-only PDF checked using `pdftotext`. This is component-fixture validation **ONLY**. The browser fixture exposed the Playwright function-return issue above and the counter stub was corrected.
- Deterministic fixture QA ZIP (twice byte-identical): SHA-256 `28020d2d74097a3878e03441b33b4028f1a3672ad433f4e3f734ce1d4f2f67ba`. Local `Apollo_R122_Print_Recovery_Fixture_QA_STAGING_HOLD.zip`, not a production deployable.
- New 17 Node tests are source-controlled but **native Node execution on exact GitHub R122 HEAD not completed**. Actual R122 full-page Playwright, axe-core acceptance, actual-page LCP/CLS trials, Apple/Safari/VoiceOver/NVDA, and WordPress/Assembler remain **NOT EXECUTED**.
- No qualified-human Grok Apollo asset-session denominator, verified subscriber cohort, merchant-confirmed Apollo purchase, revenue, refunds or fees was established.

## Commercial offer → step → blocker → experiment → evidence → owner
| Priority | Offer / funnel step | Blocker | Change or experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Proposed secondary-educator Apollo casefile → paid order | **No independently verified, sellable, rights-cleared Apollo SKU** with Payhip acceptance/price/delivery/refund evidence | Claude/Growth audits existing Products 001–015 and only proposes a matching product if verified; no live checkout link | **BLOCKED; no sale claimed** | Claude/Growth/founder |
| P1 | Grok evidence-rich Apollo video → Apollo landing → free classroom handout | Abandoned print session can silently alter source packet and prevent retry | R122 recoverable native print + source-of-truth QA | **BUILT; V8 unit-executed / fixture-browser-tested; actual-page QA HOLD** | Apollo |
| P2 | Free handout → relevant paid educator casefile | No approved verified offer; avoid interruptive unrelated commerce | Specify a single quiet casefile CTA *after* seller, rights, terms and founder approval, never activate prematurely | **NOT ACTIVATED** | Claude/founder |
| P3 | Paid orders → net revenue per 1,000 qualified sessions | Grok `asset_id/utm_content` and merchant records absent / no validated human denominator | Reuse Issue #820 privacy-reviewed UTM → landing → relevant CTA → verified merchant order → fees/refunds contract; 7/30-day cohorts | **NOT COMPUTABLE**, tiny-sample caution | Claude/Growth, Praxxis/Grok asset evidence |

**Proposed single flagship:** *Apollo 1: Fourteen Seconds, More Than One Failure* for interested educators. This is an editorial/education offer **hypothesis**, not evidence of Grok approval, social publication, product-market fit or sales. Grok alone owns creation/distribution; Praxxis owns external creator/rights QA. No new social task queued.

## Explicit remaining release gate
1. Exact-HEAD full Apollo R122 Playwright (320–1920, JavaScript on/off, keyboard/touch, print/cancel/retry, screen-reader and reduced motion) **PASS** with approved local axe bundle and screenshots/PDF.
2. Genuine LCP/CLS trials on actual Apollo candidate plus independent WordPress/Assembler and responsive layout QA.
3. Editorial crosswalk with Research Desk PR #158; provisional crew-photo `S67-19766` unchanged; six individual NASA photograph-use rights assessments still **0/6**; independent historicist review and published Atlas release-record reconciliation.
4. Hosted CI exact HEAD, QD, founder visual, publication and separate commercial release approval. No branch merge, WordPress write, external mail/post or paid spend.
