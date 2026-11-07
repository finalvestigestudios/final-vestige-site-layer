# R179 — Authored source-use → citation crosswalk (DRAFT / HARD HOLD)

## Purpose and release state
Issue #136 (Preparedness only); conversion coordination #820 and #818. R179 is a **read-only**, isolated, draft engineering addition stacked on R178 (`3d40b715b08721db04e9a3996a33febffe57c44b`). It adds no original article/source edits, editorial truncation, CMS/WordPress/navigation changes, analytics scripts, merchant integrations, emails, posts or spending. **It does not authorize any public guide, tool or commercial CTA.** Valid structural inventory returns `DRAFT_HARD_HOLD` and CLI **exit 2**, not QD PASS.

R178 binds all 35 untouched original article bodies and metadata to Git identity and R161 custody. R179 separately pins the **eight** authoritative original source inventory blobs (register + seven Claude fragments); joins each author's `source_use` relationship to the preserved `{{cite:id}}` tokens and exact literal source URL; emits a deterministic per-relationship hash and optional full JSON report. It records every source inventory alias rather than silently selecting an upgraded source, identifies shared literal URLs and trailing-slash discrepancies as human-review *groups*, rejects conflicting URLs under an identical ID, unknown source IDs, ambiguous missing source interpretations, malformed URLs, changed source inventories, false publication status and changed citation counts. Every row explicitly says `independently_reviewed_claim: false`, `modern_safety_approved: false`; HTML citation locality remains separately gated by R173/R174.

Do **not** convert an `uncited_author_source_use` to an automatic editorial defect or silently delete it: it is an investigation queue. Do **not** treat machine `verified_on` as qualified safety approval.

## Actual authenticated source/corpus inspection, 2026-11-06 PT
Reads used the connected GitHub repository at original R178 head `3d40b715b08721db04e9a3996a33febffe57c44b`, not a local clone. Eight source inventory blob SHAs are embedded in the validator and independently matched GitHub content. Source records: **244**, source IDs: **225**, distinct literal URLs: **202**, source IDs appearing in multiple inventories: **15** (zero different-URL conflicts); shared literal URL groups including repeated same-ID records: **32**, of which **17** groups involve distinct source IDs. One URL slash-variant group remains: NCHFP jerky path with and without final slash. It is **not** adjudicated as semantically equivalent. All 35 metadata records were read (one transient retrieval retried successfully), metadata blobs matched R178 baseline, and every one of the **385 authored source-use relationships** had an ID in the eight authoritative inventories; **0 unknown source IDs**. Exact source-use reconciliation by roster batches: 110 + 89 + 9 (retried medication record) + 105 + 72 = **385**. 35 original body Git identities and the **2,000** original citation occurrences remain protected by prior R161/R178 custody; full native execution of R179 on the authentic article HTML was **not** completed.

## Code and testing
New files:
- `preparedness/tools/r179_source_use_crosswalk_gate.py` (Git blob `b3007488e3ee3a095ccf394ebedb009a06a9641b`)
- `preparedness/tests/test_r179_source_use_crosswalk_gate.py` (Git blob `897fab3c1a2b479438849af83c84c5f4f70a5e8e`)
- This review record.

**165/165 Python tests PASS**, 0 fail/skip, synthetic fixtures only; includes **140 separate article-level adversarial mutations** (35 × source-substitution, citation-loss, publication-promotion, safety-label tampering), plus 25 global regression tests. Python compilation PASS. Checked GitHub's saved code blob identities against locally executed code. Missing/incomplete repository returns `INVALID_HARD_HOLD`, CLI exit 2. These results are not source-validation, medically safe advice or QD approval.

Trusted *complete checkout* runbook, explicitly not completed in this environment:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300
python -I preparedness/tools/r178_safety_state_admission_gate.py --repo .
python -I preparedness/tools/r179_source_use_crosswalk_gate.py --repo . --summary
# Both safety/citation gates ALWAYS exit 2; inspect JSON state and errors, never "|| true" as evidence of PASS.
```

Local `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` failed `Could not resolve host: github.com`. Native build, full original test suite, authentic crosswalk execution, WordPress draft rendering, staged 360/390/768/1440 browser, privacy and printing QA are **not verified**. The connected GitHub reads are narrower evidence, not a substitute for the native build.

## Contributor/independent QA coordination
Fresh exact comparison against pinned heads returned `identical`, **0 ahead/0 behind** for Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`, Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`, Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. Independent safety PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (followup #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`) inspected as patches, left separate. Homepage lead PR #1300 head `b03ced998272a8dec5a70c5f6a48b31d54fe6599` observed, not touched.

Unreviewed safety/citation claims remain blocked: existing **75** source decisions, **32** shared literal URL groups, **10** jerky claim anchors, **11** Family Card decisions (overlap, do not sum), historical two `approved` labels with ambiguous scope and four `not-required` labels, NCHFP/FSIS differences, and independence of food, medical, QD and source reviewers. PR #157 suggests a safer main-breaker drill rewrite and medicine-specific advice; R179 does not silently merge it.

## ONE intent / ONE free draft / optional commercial path — conversion-first
**Verified content scope, not verified social traffic:** caregivers worried about school pickup, out-of-area contacts and family reunification. Draft **ungated free** Household Emergency Plan `/preparedness/start-here/household-emergency-plan/`; optional **free draft** Family Reunification Card, pending source/privacy/print QA. Proposed non-live contextual CTA: “Make a plan for how your household will reconnect. Read the free Household Emergency Plan.” Do not make access to safety steps contingent on an email or purchase. Existing /focus/ Fieldbook remains the sole approved email lead magnet; old water freebie remains retired.

**Matching purchasable Preparedness pack = UNVERIFIED / PAID CTA DISABLED** until Commerce/Claude independently document a real owned rights-cleared SKU, live seller-approved listing, price, terms, checkout, usable original-file delivery, fees, refunds and independently confirmed paid order (no test sale charged without approval). This work introduces **no** new offer or affiliate activation. Mini Museum-first creator strategy outside this lane remains untouched.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (draft only) | PASS / FAIL evidence | OWNER |
| --- | --- | --- | --- | --- |
| Existing owned practical pack → actual paid order | No verified matched Preparedness SKU, rights, payment/delivery/refund evidence | Verify merchant listing and fulfillment before *any* purchase CTA | HARD HOLD; no paid product or sale verified | Commerce / Claude |
| Free Household Plan → resource CTA | Human citation/safety gate and authentic native build missing | Qualified source audit + full native/staging checks; preserve ungated instructions | DRAFT/HOLD; 165 synthetic tests do not approve content | Preparedness / independent QA |
| Free guide → optional Family Card | 11 source decisions, printability, accessibility and data-on-device assurances unverified | Test with synthetic family data at 360/390/768/1440, read-only privacy/print check | HARD HOLD | Site QA |
| Grok caregiver video `asset_id` → destination | No matching published creator asset/allowable CTA placement confirmed in TASK-008 and dated handoff | Grok/Praxxis supply immutable asset ID, actual published URL, approved destination and UTM; no script changes | UNVERIFIED | Grok / Praxxis |
| Human sessions → paid orders → realized net | No authenticated qualified-session denominator, actual merchant-paid orders, fee/refund settlements or valid attribution | Reconcile 7/30-day cohorts using existing #820 contract, no new script | NOT COMPUTABLE | Claude / Commerce / Analytics |

Proposed after creator/source authorization only: `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11`, `utm_content=<verified_asset_id>`, source/platform from actual published asset. Never count clicks/confirmed leads as sales. Key KPI `1000 * realized_net_revenue / qualified_human_sessions` requires both verified numerator and nonzero qualified denominator; cohort and small-n warning mandatory.

**Release governance:** founder decides public release. No merge, WordPress/CMS edits, public nav, social posts, marketing emails, measurement script, merchant changes, affiliate launch, or spend from this PR. See #136 and #820.
