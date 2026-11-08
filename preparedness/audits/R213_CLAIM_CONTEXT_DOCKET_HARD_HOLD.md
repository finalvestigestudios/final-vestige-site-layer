# R213 — immutable claim-context docket and test-integrity repair
**Scope:** Issue #136 exclusively; cross-reference conversion #820 and charter #818. **DRAFT / HARD HOLD**. No WordPress, navigation, homepage, merchant, social, email, analytics, spending, merge or release change.

## Problem and substantive repair
R212 safely pinned six original Start Here files and identified exactly **three unexplained citation occurrences** in two of the 35 original Preparedness articles, but its receipt-only record did not carry a short readable source-claim context for independent reviewers. Worse, `test_rewording_held_citation_requires_new_adjudication` compared synthetic data to authentic production Git blob pins *after* mutation, so it passed even if the intended mutation were absent. That was a false-positive test design, not proof of production source drift.

R213 adds an **offline, read-only, source-bound claim-context docket** and fixes that false-positive test. It reuses R212's authenticated source reader and frozen hash check, then outputs exactly three distinct SHA-256-receipted review items, their UTF-8 byte-accurate citation spans, a non-executable text excerpt, and an independent excerpt digest. All fields remain **PENDING** and **HUMAN_SOURCE_CLAIM_ADJUDICATION_REQUIRED**; source-link verification, editorial approval, medical-safety approval, QD and publication remain false. CLI only prints JSON and exits **2** for held admissible originals or **3** for invalid input; it cannot write files, mutate articles or return PASS. The `synthetic_pins` injection point exists only for in-memory testing, not CLI.

## Frozen source and QA custody checked on 2026-11-08
Seven original Claude contributor heads (read-only Git refs):
- Start Here `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Independent QA PR #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture isolation PR #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and follow-up PR #973 head `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`: no branch edits, direct merges or older article overwrites. Homepage EX2 PR #1555 and Mind #1560 inspected without modification. Seven historical shared-source conflicts, QA test parity and full 35/41 authentic release-candidate checks remain outstanding.

**Held source occurrences unchanged:**
- Article #7, Homemade Water Filters: two `cdc-find-clean-water` references without article-level `source_use` explanations. CDC distinctions concerning drinking-water heater vs space-heating tank, previously uncontaminated melted ice, and suspected fuel/chemical contamination require qualified contextual review, not silent copy editing.
- Article #20, Preparedness for Real Households: one `start-ready-plan` reference without article-level explanation. Ready.gov source support has not been independently adjudicated; a prior request was HTTP 403.
- Source-register human link check remains false for both; URLs/source equivalence not approved.

## Executed local tests and identity
- Local Python `python -I -m unittest discover -s preparedness/tests -p 'test_r213*.py'`: **90/90 PASS** against an isolated local R212 module with exact original Git blob `5de67ebe4db2f7a77671d4916679dba2507657b2`.
- Of 90 tests, **70** individual mutation replays (35 synthetically positioned citations and 35 nearby claim-text changes) first assert the original synthetic snapshot gives `DRAFT_HARD_HOLD` with *matching synthetic pins*, then hold those exact pins constant and verify mutation produces `INVALID_HARD_HOLD` with **source blob drift**. **These are 35 synthetic slots in one mock article, not 35 original articles tested.**
- Other tests cover all three unique receipts, exact byte spans, Unicode offsets, deterministic context/excerpt SHA, source URL substitution, broken citations, attempted publication-state promotion, source-use edits, duplicate JSON keys and untrusted input fail-closed behavior.
- `python -m py_compile` on R212, R213 and R213 tests **PASS**.
- Reconstructed exact inherited R212 test file locally and verified its Git blob identity **`139f6572921cc5cd8967121245f86190c7ec3c70`** matches committed corrected file. R212+R213 isolated subset run `python -I -m unittest discover -s preparedness/tests -p 'test_r2*.py' -q` = **153/153 PASS** (63 corrected inherited R212 tests + 90 R213 tests). This is NOT the original full repository test suite. No original contributor bodies/meta changed.
- Exact committed new tool Git blob: `53aaf772d354a32aff97321ad1494e8d02a91cac`; exact new test Git blob: `f88ca7093669f58f48027e8f7a4587be6e5cad8b`. Local executable content identities matched remote bytes through Git object SHA-1.
- **NOT RUN:** full native repo `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete original repository-wide suite beyond the isolated 153-test subset, original six-file authenticated R213 CLI, full 35-article citation audit on this R213 head, 41 rendered WordPress outputs, browser/WCAG, qualified safety and QD. Reason: local GitHub DNS cannot resolve, and trusted full repository/source checkout not available. Connected GitHub read API was used for exact head/PR/source identities, not a replacement for executable originals.

## Review order / release gate
1. Qualified human independently compare three immutable receipt/context pairs to official source content, explain support *in context* including all caveats; preserve any resulting proposed edit as separate review evidence.
2. Human reconcile seven historical conflicting source identities and negative-safety-test parity from PRs #157/#169/#973 without overwriting newer authored articles.
3. With an authenticated full checkout, run native validate, build, existing Python tests and all 35 article/41 output parity/citation/URL/reading-depth checks; run staged mobile/accessibility source and browser checks.
4. Independent QD and founder release authorization are required. Do not mark `human_link_check`, safety, QD or publication passed by a script.

## Commercial conversion lane — DRAFT ONLY (#820)
**ONE audience**: households organizing emergency contact details, insurance/records locations and fallback decision-maker instructions. **ONE free destination**: already-live, ungated https://finalvestige.com/preparedness/ and authentic official-source resources. **ONE optional candidate**: already-listed Legacy Triage PDF https://payhip.com/b/n1RhV, a family records organizer, **not** emergency-treatment advice; paid offer activation forbidden until seller rights, product-currentness, checkout, PDF fulfillment, accessible mobile journey, refund/support and founder approval are verified.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Actual Grok preparedness media → existing free archive | Immutable published asset ID, post URL, hook, UTM and destination not reconciled | Read-only TASK-008 matching; Grok retains all creative and posting | UNVERIFIED | Grok / Praxxis |
| Free archive → detailed original FV guide | Source/citation safety and native rendering incomplete | Finish three human claim reviews and independent QD; never gate essential free guidance | DRAFT/HARD HOLD | Preparedness / independent QA |
| Free guide → optional records organizer | Intent mismatch and $19 SKU rights/terms/delivery unverified | Founder-approved accessible disclosure and no-purchase route, stage only | UNVERIFIED / NO CTA | Commerce / Preparedness QA |
| Checkout → authenticated customer and delivered PDF | Authorized end-to-end purchase, support and refunds evidence absent | Merchant-controlled acceptance and delivery test with approval | HARD HOLD | Founder / Commerce |
| Attributed qualified-human sessions → realized net revenue | No linked merchant-confirmed paid orders, fees/refunds or 7/30-day denominators | Privacy-safe existing-system reconciliation, no new analytics scripts | NOT COMPUTABLE, NOT ZERO | Claude / Analytics + Commerce |

No conversion counts, sales or successful deliveries are claimed. No currently unpublished FV article, Reunification Card or retired water freebie is linked as live. Grok/Praxxis TASK-008 was inspected read-only; no asset ID was invented or queue edited.
