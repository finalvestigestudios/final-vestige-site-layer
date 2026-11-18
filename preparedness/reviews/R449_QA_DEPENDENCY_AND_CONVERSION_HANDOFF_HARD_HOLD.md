# R449 — Preparedness independent-QA dependency / source custody release hold (DRAFT ONLY)

**Issue #136; commercial coordination #820 / charter #818. Parent:** R448 PR #2939, exact `cbb981d47a75bea417768026258d7b6fe54b5865`. No original manuscript, source fragment, URL, existing safety state, WordPress file, CMS, navigation or analytics file changed.

## Critical independently observed dependency hazard

As of **2026-11-18 02:56:30 UTC**, the original QA branch PR #157, food fixture PR #169 and its dependent remediation PR #2205 all modify exactly the same test path: `preparedness/tests/test_preparedness.py`.

- #157 open/draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, base `claude/prep-start-bbfeb8`.
- #169 open/draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`, base `claude/prep-food-ccdc55`.
- #2205 open/draft HEAD `bbcf1859768624c611df4abadc564c18247cf32a`, base EXACTLY #169 head.
- Therefore #2205 may be integrated after its parent, but **does not resolve the independently diverging #157 test-file overlap**. Do not auto-cherry-pick or drop fixture protections. Require a human-reviewed merged test file and exact post-integration native test run, with no writes to canonical fragments by synthetic fixtures.
- Home lead #2931 `c43980270e3e9d31c03fcb70e0f1126914c58604` and Preparedness Article #11 editorial #2789 `4e1ef2fb82f5888901e1e2ead87601880efad1af` were also read-only checked, with no changes.

## Preservation and tests

- R448 frozen docket retains 35 articles; 203 distinct original source IDs; 280 occurrences; 181 literal URLs; 17 separately reviewed shared URLs; 5 unresolved source-scope disputes; 9 unselected forks; 9 contributor branch pins.
- All 9 original Claude/Shelter branch names compared via GitHub `compare_commits` against frozen SHAs: **0 ahead, 0 behind** on all nine at this observation. This does **not** mean the unpublished 35-body integration has been built or source claims qualified.
- New draft-only `r449_qa_dependency_gate.py` and `test_r449_qa_dependency_gate.py` plus this full PR and original-branch snapshot are additive; no false QD PASS conditions.
- Local independent **companion/prototype** gate: Python compilation PASS and **72/72 adversarial synthetic tests PASS**. The smaller committed GitHub test module contains **68 discoverable methods**, **NOT executed** from exact final GitHub bytes in an authenticated checkout. Explicitly do not present 72 as execution of the committed module.
- Native 35-article validation/build, genuine WordPress/private-preview exports, real browser/mobile behavior, human source-link checks, qualified food/emergency/medical/child-privacy and QD verdicts: **NOT EXECUTED / NOT APPROVED**. No release or deployment permission follows from structural preflight.

## ONE high-intent acquisition-to-revenue candidate (no active offer)

**Audience:** published Grok household emergency contact/reunification viewer, *only if Praxxis establishes real immutable asset_id, public post date/URL, topic match, usage rights and permitted destination*.

**Free existing source:** independently referenced Ready.gov `https://www.ready.gov/plan` (original source docket ID, live page and mobile check still required). Candidate free CTA copy only: **“Review the official household emergency checklist.”** Do not link to unpublished Article #15 or Tool #104. The separate Tool #102 remains unchanged. No retired water freebie.

**Optional practical tool:** Tool #104 remains private/not safety-approved; consent/child privacy, emergency accuracy, printable/no-JS accessibility and qualified review HARD HOLD.

**Paid pack:** no authenticated existing FV-owned, rights-cleared, genuinely payable and deliverable Preparedness SKU with verified mobile checkout, merchant acceptance/refunds and actual orders. **No paid CTA is authorized.** Reject other sellers' products as FV-owned packs without ownership/license evidence.

## Conversion-priority acceptance plan

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One authenticated FV Preparedness pack | paid checkout → settlement | SKU, selling rights, delivery/refund/fees unknown | Independently confirm existing owned product and real purchase path before any CTA | FAIL / no payable SKU or merchant settlement established | Founder/Commerce |
| Existing source-backed agency free plan | asset_id + UTM → human landing | no matched published Grok family-contact post | Praxxis validates ONE real post and destination without content/post creation | UNMATCHED / no immutable ID | Grok (creator), Praxxis (QA) |
| Article #15 → optional Tool #104 | free guide → optional download | 2 original article/meta forks, child privacy and QD unknown | qualified source and print/no-JS evidence review before linking | HARD HOLD / not safety-approved | Preparedness/QD |
| Verified FV pack | relevant CTA → verified paid order | permission, mobile checkout, refunds, actual merchant reporting absent | receipt-verified purchase/delivery/refund test only with founder approval | NOT TESTED | Founder/Commerce |
| Qualified human sessions | 7/30d cohort net revenue per 1,000 | no independently verified qualified sessions/attribution/settlements | existing native consented reports; no duplicate scripts | NOT COMPUTABLE | Claude/Commerce |

Measurement is `grok asset_id/utm_campaign → qualified human landing → relevant CTA → confirmed lead (if applicable) → merchant-confirmed paid order → fees/refunds → realized net revenue`. **Outbound clicks, signup, attributed visits, checkout starts and affiliate clicks are not paid orders.** Tiny sample cohorts require explicit warnings.

**Release:** DRAFT / HARD HOLD. No merge, public publishing, WordPress, navigation, analytics, social posts, emails, affiliate/merchant activation, spending or safety PASS claims. Founder retains all release and spending decisions.