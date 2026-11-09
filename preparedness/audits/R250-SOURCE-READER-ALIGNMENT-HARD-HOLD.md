# R250 — Preparedness reader disclosure and original-source parity (UNAPPROVED)

2026-11-09 PT · Issues #136, #820, charter #818. DRAFT_HARD_HOLD / no merge / no release.

## Gap closed

R248 independently authenticates the five original Article #15 / Tool #104 sources and proves that the shorter printed card includes six user-entered fields (household name, household phone, out-of-area contact and phone, first meeting place, review date), while the full card includes thirteen. R249 independently checks an unsigned HTML reader disclosure. Previously, the *two receipts were never directly compared*. A future phrase swap could pass a mere count-based inspection.

New R250 independent gate verifies all 13 field identities, frozen print order, six true shorter-mode fields, seven omitted fields, all UNREVIEWED statuses, and exact *visible* six-field disclosure. It rejects changed, missing, reordered, duplicate, or euphemistic entries, plus a changed preview digest, false human approval flags, missing paper-loss or no-JavaScript warnings, and accidental commerce activation.

R220 now authenticates the gate's exact Git blob SHA **c8149e31b44b6b37ce930dfc8a140560270f1f73**, runs the comparison *after* the pinned R248/R249 inspections and *before* export, and rechecks the gate after the audit. Receipt: OBSERVED_NOT_APPROVED. This does **not** repair the original Tool #104, claim privacy safety, approve medical advice, select editorial Option A/B, or clear QD.

## Tests and limits

Executed locally against the R250 exact-committed-identity Python module, test cases, and byte-identical **R249 unsigned preview** (HTML Git blob **ce5c363786deb0296f78598818af1fd7abefae65**): Python compilation PASS, **64/64 R250 unittest methods PASS**, including more than 50 independent adversarial mutation tests. The original five-source receipt was *synthetically modeled* in the local tests; this is not a native source-backed full audit.

GitHub blobs: new module **c8149e31b44b6b37ce930dfc8a140560270f1f73**, tests **ca30654cd9fcc016ac0e867a426c8adb2971eb49**. Native repository validation/build, 36+ inherited tests, 35-manuscript corpus / six tools / 41 WordPress exports, and genuine original Tool #104 browser/print/storage/network QA were **NOT EXECUTED**; container cannot resolve github.com. Integrated R220 wiring inspected but not native executed.

Original seven contributor heads checked live against frozen R200: start 2122d856fce9f64887c16df3d52e64be9f59a55b; shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; food f911ff7a655de8d81535ea86ec3d65a49ee76648; health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; historical field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; historical food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; historical home 7504a5f099594d635e3dd7332a33a2e1346c43a2. All seven unchanged. Independent QA #157 head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa and fixture #169 head e9cd7766dac59d47ab467d8945269b9146c2aef5 remain open drafts. Homepage lead #1689 f55c36b6598eec558dd8bb24e4c8988becc51be0 untouched.

32 shared-source groups and three original disputed citation occurrences (two CDC Article #7; one Ready.gov Article #20) remain unresolved. The prior 35-article / 2,000-citation audit is an inherited baseline, not re-performed in this run. No qualified source-safety or independent QD approval.

## Conversion-first acceptance | OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / step | Blocker | Required acceptance experiment | Evidence | Owner |
|---|---|---|---|---|
| Existing free Preparedness Archive → Grok traffic | No authenticated already-published matching asset ID, platform URL/date/hook/rights and signed-out mobile path | Praxxis independently verify TASK-008 current inventory; leave Grok queue untouched | UNVERIFIED | Grok / Praxxis |
| Free guide → held Article #15 / Tool #104 | Six-field printed disclosure, noJS, home-plan, privacy wording conflict | R250 source/copy parity then independent editorial choice and actual WP/mobile/print/storage review | Isolated 64 PASS, release HARD HOLD | Preparedness / independent QA |
| Free guide → optional **Legacy Triage** owned pack | Commercial rights, product fit and secure handling unverified | Founder/Commerce audit actual existing file and authorized SKU; no retired water freebies | NOT APPROVED | Founder / Commerce |
| Optional paid pack → settled order | Checkout, delivery, refund/fee data unknown | Authorized merchant-side verification | NOT TESTED | Commerce |
| Attributed qualified-human session → CTA → lead → settled paid sale | No authenticated creator asset or merchant ledger | Reconcile 7/30-day unique human UTM cohorts, provider confirmed leads, paid orders, fees, refunds | Net revenue per 1,000 qualified humans NOT COMPUTABLE | Praxxis / Claude analytics / Commerce |

No publishing, WordPress/CMS/nav, social, email, merchant or affiliate activation, duplicate tracking scripts, live experiments, spending, or merge. Human/editorial and founder authorization still required.
