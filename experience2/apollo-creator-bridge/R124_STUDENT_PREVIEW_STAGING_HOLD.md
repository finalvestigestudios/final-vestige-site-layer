# Apollo R124 — inspect before printing / browser QA expansion
**November 4, 2026 — DRAFT / STAGING HOLD.** Owner: Apollo Evidence Studio. Issues: #150 and #820; commercial charter #818.
Parent: R123 PR #982 (base branch qa/apollo-r123-chronology-primary-source-custody-20261104). Do not alter homepage PR #49, Research Desk PR #158, or production.

## Visitor friction and change
Secondary educators arriving from a Grok Apollo long-form investigation previously had no screen inspection of the actual printable student-only handout. The handout was display:none outside print, so instructors had to open print preview to evaluate the three questions, response space, rights notice and six NASA source references.
R124 adds a low-friction secondary **Preview the student worksheet** utility inside the existing free classroom callout. The handout itself remains unchanged, hidden until user opt-in; it includes a close control, Escape handling, focus management and an explicit aria-expanded control relationship. The original primary CTA is still free, no email gate. Preview UI never appears on printed handouts. Without JavaScript, the worksheet remains accessible through native Print. No NASA image binaries, coordinates or geospatial claims are introduced.

## Evidence and test honesty
- 20/20 isolated V8 exact-source preflight assertions and HTML inline script syntax compilation PASS during implementation, before committed writes.
- 18 native Node regression tests are **authored** and require execution on an actual Node host: `node --test experience2/apollo-creator-bridge/test_r124_worksheet_preview.cjs`.
- Existing actual-source browser runner `qa_r113_print.py` extended to assert full-page 320–1920px JS on/off screen preview availability, focus return, Escape, all six source links and print/no-JS parity. It still requires exact Git HEAD, installed Chromium/Playwright, a local approved axe-core bundle and reproducible screenshots/PDF/performance receipts.
- **NOT RUN**: exact-page Chromium Playwright matrix, axe-core, actual-page LCP/CLS, screenshots, WP Assembler and native Node CI. Source checks alone are not release acceptance. Run: `python experience2/apollo-creator-bridge/qa_r113_print.py --axe /local/approved/axe.min.js --out /tmp/fv-apollo-r124` from checked-out exact branch.
- Rights remain unresolved for all six photographs; proposed S67-19766 catalog association provisional. Primary technical chronology: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; general NASA imagery guidance not proof of individual permission.
- No third-party tracking, posting, paid service, WordPress content/settings write or production release.

## Conversion-first gate
| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Proposed teacher casefile | Verified paid order | No matched rights-cleared, merchant-verified live SKU | Inspect inventory, price, delivery/refunds before considering a paid CTA | BLOCKED / no sale verified | Claude/Growth + founder |
| Free Apollo source worksheet | Grok long-form → Apollo → utility | Handout couldn't be examined on screen without printing | R124 preview, then user may print | BUILT; source preflight only; browser acceptance pending | Apollo |
| Relevant commercial offering | Worksheet → merchant checkout | No approved offer/product mapping | Keep paid CTA disabled; ensure editorial fit | NOT ACTIVATED | Founder + Claude |
| Paid order → net revenue | attributed cohort | No verified orders and qualified-session linkage | Reuse #820 unique asset_id/UTM events and merchant reconciliation | NOT COMPUTABLE | Claude/Growth/Praxxis |

## Release blockers
Full actual-source Playwright/axe, browser PDF/print proofs and device performance, native CI, WordPress/Assembler acceptance, photo-specific rights 0/6, PR #158 source-role editorial reconciliation, approved offer and independent historical QA, founder release approval. **DO NOT MERGE/DEPLOY**. Grok owns script and social posts, Praxxis owns external review.
