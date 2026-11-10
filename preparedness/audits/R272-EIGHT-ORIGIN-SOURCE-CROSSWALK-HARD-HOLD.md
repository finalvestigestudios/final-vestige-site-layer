# R272 — Eight-origin source crosswalk identity gate (REVIEW ONLY / HARD HOLD)

**2026-11-10 | Owner:** Preparedness integration, Issue #136; conversion liaison #820 / #818.  
**Scope:** Existing 35 article slate, six original tools, exact historical source-reading identities.  
**Release:** `DRAFT_HARD_HOLD`; no WordPress, publishing, navigation, source overwrite, email, merchant, affiliate, analytics, social or spend action.

## New source-integrity engineering

The existing `sources/crosswalk.json` (Git blob `d62e493a67dedd23e04cfdf3cce762ef933c6bf9`) references eight original source-file snapshots from the seven frozen Claude clusters plus the base register. R272 independently binds all eight exact Git source blobs and rejects unexpected changes. It distinguishes **exact source URLs** from **conservative terminal-slash review aliases**, without rewriting an exact URL or claiming two reading scopes equivalent.

Connector-based independent inspection on the actual Git blob identities:
- 244 complete original source rows, across eight snapshots: 34 + 30 + 21 + 28 + 28 + 29 + 45 + 29.
- **202 distinct exact URLs**; **201 distinct terminal-path-slash review aliases**. The one alias exception is NCHFP jerky: the historical `hist-food` source has a terminal slash, while `base` and `food` read the no-slash URL.
- **32 pending shared-URL review groups**, including the three-reading NCHFP group when using the conservative review alias. **15 duplicate source-ID groups** remain separate origin-scoped identities, not permitted for implicit merge.
- All group variants, original row indices, complete source dictionaries and group member source IDs matched the eight authenticated blobs under terminal-slash review equivalence; group reviewer/reviewed_on fields are null and every review_status is pending.
- `source_head_commits` records historical source snapshots and must **not** be equated with the later frozen R200 contributor heads. R200 manifest SHA `5822f9dfde21d1f3bdfc26658769d852c639438c` instead freezes the seven independent contributor branches.
- Exact `crosswalk.json` and eight source blobs at R271 draft HEAD were independently authenticated through GitHub. The new R272 gate adds independent read-only audit logic and is SHA-pinned into the pre/post custody of R220.

A naive exact-URL group check falsely reported one missing row in the NCHFP group. R272 explicitly prevents that class of mistaken reconciliation by retaining **both** exact and conservative-alias counts and asserting the exact source-to-review-group roster. A historical crosswalk URL count of 202 must **not** be silently replaced by the 201 review-alias count.

## Independent contributor and QA controls

As of this review, the seven `claude/prep-*` contributor branches each compared `identical` (ahead=0, behind=0) to R200's frozen SHA. PR #157 (independent Start Here safety QA) remains open/draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. PR #169 (food synthetic-fixture tests) remains open/draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`. PR #169's remaining direct test-fixture write to `preparedness/sources/fragments/_dup_test.json` is an **inspection-only isolation risk**, not an executed failure, and needs the QA owner's separate fix. Homepage lead PR #1689 is a separate owner's open draft and must not be modified here.

## Test/evidence receipt (scope is critical)

- **Executed local prototype:** 68/68 synthetic Python tests PASS, Python compilation PASS, on a standalone prototype under `/mnt/data/prep_r272/`. The prototype is **not identical to the committed GitHub R272 module**; do not count its PASS as a committed-suite run.
- **Committed GitHub R272:** new source-bound Python gate, 61 declared synthetic cases (8 baseline/behavior and 53 mutation cases), R220 pre/post source-custody binding. The **committed Python tests are NOT EXECUTED** in this environment; GitHub DNS blocks exact repository checkout.
- **Authenticated source reconciliation:** independently executed through the GitHub connector on the exact crosswalk and eight source blob identities, with zero variant-roster mismatches under correct conservative alias rules.
- **Not executed:** full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, inherited 36+ regression suite and authentic 41 WordPress draft exports. No hosted QD, physical card or paper privacy approval.

The new gate deliberately returns `DRAFT_HARD_HOLD` on structurally consistent inputs and `INVALID_HARD_HOLD` on drift. **Neither output grants a QD PASS, emergency/medical-safety certification, product clearance or publishing permission.**

## Unresolved source and safety holds

All 32 groups and 15 duplicate-ID sets remain awaiting human review. The three previously disputed claims (two CDC Article #7 and one Ready.gov Article #20) remain unadjudicated. Article #7 chemical-contamination guidance requires qualified assessment. Article #15 and original Tool #104 require independent child-information privacy and accessibility review; unpublished R271 9pt alternative remains unapproved pending actual paper cut/fold/readability.

## Conversion-first plan — no new live offer

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing public Preparedness Archive (official free guide destination) | Authenticated Grok asset → visit | Matching published family-contact/reunification asset ID and actual mobile link are not verified | Existing Grok/Praxxis TASK-008 owners verify source/rights/asset ID and tagged clickable link; otherwise NO VERIFIED MATCH | UNVERIFIED | Grok / Praxxis |
| Unreleased article #15 and original Tool #104 | Free guide → optional practical resource | Privacy, safety, real-paper use and accessibility unresolved | Independent privacy and print audit; do not link the draft | HARD HOLD | Preparedness / QA |
| Existing Legacy Triage digital PDF (provisional candidate, not approved Preparedness upsell) | Optional free-to-paid handoff | Full rights, product fit, sensitive records, delivery/merchant acceptance and founder approval missing | Audit entire PDF, disclose product terms, then authorized checkout/fulfillment test | NOT APPROVED / NOT TESTED | Founder / Commerce |
| Existing owned customer attribution | Qualified social → CTA → verified order → refunds/fees | No authenticated post ID / merchant-confirmed orders available | 7/30-day reconciliation of unique source IDs and confirmed net orders, no duplicate measurement scripts | NET REVENUE PER 1,000 QUALIFIED SESSIONS NOT COMPUTABLE | Analytics / Commerce |

No paid CTA, live page, creator task queue, public product, CMS record, tracker or email changed.

## Blockers and owner requests

1. Perform exact checkout of stacked R220–R272 branch and run native build/validate/inherited tests, audit 41 intended WordPress drafts, preserving original 35/6 and no duplicate routes.
2. Independently adjudicate 32 shared reading-scope groups, 15 duplicated IDs, three contested citations and Article #7 advice; retain no hidden safety PASS.
3. QA owner to sandbox PR #169's remaining `_dup_test.json` fixture; do not make a silent change to their branch.
4. Founder/Commerce to decide Legacy Triage suitability after whole-PDF rights and fulfillment verification; Grok/Praxxis remain responsible for existing asset IDs.

**Decision: DRAFT / HARD HOLD. No merge/publication release requested or authorized.**
