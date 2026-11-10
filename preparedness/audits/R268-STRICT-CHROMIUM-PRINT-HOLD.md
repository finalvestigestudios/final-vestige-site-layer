# R268 — Strict offline Chromium print-evidence acceptance (DRAFT / HARD HOLD)

**2026-11-10 • owner: Preparedness Integration, #136.** Business coordination #820 / charter #818. This is a *review-only* correction to R267's **manual offline test harness**, not a revision of original Tool #104, Article #15, 35 manuscripts, 2,000 citation occurrences, source crosswalk, public site or product.

## Problem and change

Independent Praxxis review of exact R267 PR #1922 head `0388f2cedbb77f8689e8f30605e3c5b03006fc2c` correctly identified that `front_and_back_visible` was *recorded but not required* by the browser reproduction's final success predicate. That older predicate also never required the asserted 672×206px print dimensions, two 335px faces, 8pt print notices, a one-page PDF, the specific privacy warnings, the five contact/review field labels or JavaScript-on/off text and geometry parity.

R268 adds `r268_wallet_print_parity_acceptance_hold.py` and modifies only the manual `r267_reproduce_browser_observation_REVIEW_ONLY.py` to call it. The gate checks 5 viewport widths for each original/preview source, both warnings visibly rendered in screen captures, 4 print PDFs (original/preview × JS on/off), expected dimensions and notice font, exact printed warning and field content, exact one-page PDF count, and printed-content and geometry parity across both comparisons. PDF binary SHA-256 may differ because of non-content metadata; hashes are recorded, NOT treated as a visual or safety approval. Any mismatch fails the offline reproduction and emits a **failed** external evidence JSON, never an approval.

The script verifies the gate's Git blob before invoking it. R220 independently pins the revised manual reproduction script and gate before the held draft export and rechecks identities after the audit. Full native R220 pipeline was **NOT executed**. The previous R267 observation receipt is immutable and continues to describe a *bounded* original experiment.

**R268 matching committed Git blob identities:**
- New acceptance gate: `5207b20954c1b6d93b88f430843d4bafb2e8df88`.
- New 79-case regression suite: `67fec360ae113a6f756450c604c1b0693d93fd19`.
- Revised manual reproduction: `6ed7552d9b9c210e7fd4b7d67771a154c3b7a590`.
- R220 custody: `b34ffd2d060eb8df276cdff3849009d782366ad6`.
- Original R264 HTML **unchanged**: `40782ef142edfd348fec53eb6d8a0dc673244dea`.
- R267 screen candidate **unchanged**: `5ae643302faf6bce47e8c507fbcfff9c099eaf00`.
- Original Tool #104 remains `be8698ac5d020476ff649d85813810e2000c6f98`.

## Tests actually executed vs not executed

- **79/79 PASS** local Python unittests of the new R268 gate and test module, compiled successfully, including 77 independent negative mutations. Both local modules were byte-identical to GitHub blob IDs listed above.
- **Actual independent browser rerun** in local Chromium 144.0.7559.96/Playwright with network requests aborted, JS ON/OFF print, original/preview source bytes authenticated to the two unchanged Git blob IDs above. Original widths [680,680,680,768,1440] → preview [320,360,390,768,1440], with exact configured CSS viewports [320,360,390,768,1440]. The strict gate returned `DRAFT_HARD_HOLD` with both warnings and five labels in one-page, 672×206 CSS px PDF captures, 335px halves and 10.6667px (8pt) caution. Four PDFs/ten screenshots, and machine observation file were generated locally for audit. **This was an independent local verification invoking the committed gate's matching bytes, NOT execution of the revised committed R267 reproduction script.**
- Python syntax compilation of the revised R267 script and complete original-data `validate.py`, `build.py`, inherited 36+ tests, original 41 WordPress draft exports: **NOT EXECUTED** due to full repository checkout DNS failure in local runtime.
- Browser zoom, keyboard, assistive technology, physical printing/cutting, readable detached card and child-privacy review: **NOT APPROVED**.

## Why this remains a hard hold

The sheet-level **UNAPPROVED REVIEW CONCEPT** warning is outside the wallet cutout. The two *privacy* notes are on the individual faces, but detached prototypes do not carry an unambiguous review-only/publication label. Original Tool #104 remains unchanged, has 13 original fields and separate privacy problems. The slim adult contact cue is **not** a full family plan, school/child card, authorization, medical record or vetted emergency tool. Never distribute it.

Article #7's chemical-contamination instructions require qualified review. All 32 shared-source groups, two disputed CDC occurrence references in A7, and one disputed Ready.gov occurrence in A20 remain unresolved. Independent QA #157, synthetic-fixture #169 and homepage lead #1689 remain unmerged and untouched.

## Fresh coordination snapshot (2026-11-10)

Current seven original Claude branch heads, independently read (no changes made):
- `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`

QA #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (DRAFT/OPEN); fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (DRAFT/OPEN); homepage #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` (DRAFT/OPEN). No merging or other-lane edits.

## Conversion-first acceptance — all review-only

**Single proposed audience:** adults organizing emergency contacts. Existing public free destination: `https://finalvestige.com/preparedness/` and its linked official public resource, NOT unreleased tools. **Provisional paid candidate:** already listed Legacy Triage $19 PDF, rights/content/privacy/fulfillment and founder suitability NOT verified, therefore **no Preparedness sales CTA approved**.

1. **OFFER → social → free guide:** Unverified matching *already published* Grok emergency-contacts/reunification asset and usable clickable destination. **BLOCKER:** no authenticated asset ID, rights/copy, click surface or attribution. **CHANGE:** Grok/Praxxis TASK-008 verify existing post and signed-out mobile path; reject if no match. **EVIDENCE:** NO VERIFIED MATCH. **OWNER:** Grok/Praxxis.
2. **OFFER → free guide → optional free contact reminder:** Released Tool #104 still held; responsive preview was offline only. **BLOCKER:** detached review warning, original child-privacy and 8pt print legibility. **CHANGE:** independently assess true cutout, accessibility/privacy and editorial source signoff. **EVIDENCE:** Chromium bounded PASS / release FAIL-HOLD. **OWNER:** Preparedness + independent QA/editorial.
3. **OFFER → free guide → optional Legacy Triage:** **BLOCKER:** product suitability, rights and handling of credentials/privacy not independently verified. **CHANGE:** audit full exact deliverable and founder approve only if fit. **EVIDENCE:** NOT APPROVED. **OWNER:** Founder/Commerce.
4. **OFFER → paid checkout/fulfillment:** **BLOCKER:** authentic merchant payment, refunds/fees/delivery not independently checked. **CHANGE:** permitted merchant-side acceptance test. **EVIDENCE:** NOT TESTED. **OWNER:** Commerce.
5. **OFFER → realized net revenue:** **BLOCKER:** qualified-human sessions joined to verified merchant orders/refunds absent. **CHANGE:** 7/30-day consent-safe funnel cohorts using confirmed orders and fee/refund reconciliation, with tiny-sample warnings. **EVIDENCE:** net revenue per 1,000 qualified-human sessions NOT COMPUTABLE. **OWNER:** Analytics/Commerce.

No public publication, navigation, CMS writes, social posting, creator queue changes, new measurements, affiliate activation, email, paid service, or spending. QD PASS remains FALSE. Follow #136 for engineering and #820 for commercial coordination.
