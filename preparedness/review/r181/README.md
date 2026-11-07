# R181 — Seven-branch + independent-QA patch-intake contract (DRAFT / HARD HOLD)

**Owner:** Final Vestige Studios Preparedness Archive, Issue #136. Conversion coordination #820; business charter #818. **Stacked on R180** at exact commit `532198896128e612e88b3bee36c6368cb825e58b`. No production publishing authorization.

## What this changes

Three newly added artifacts: a read-only Python validator, 38-case synthetic/adversarial regression test suite, and a dated GitHub-connector-observed contributor/independent QA evidence receipt. Four files including this README. No original authored article, source register, metadata, citation, taxonomy, home, WordPress, navigation, merchant, tracking, email, or Grok task-board file is modified.

Unlike a verbal claim that "the branches are still the same," this pins each of the **seven Claude cluster branch names and exact SHAs**, requires zero ahead/behind drift, and checks the **three independent QA/fixture PR heads, bases, draft state, merge status and changed-file lists**. As of the evidence receipt, all seven Claude branch comparisons are **identical / 0 ahead / 0 behind**. PR #157 remains draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its direct fixture follow-up PR #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. We inspected the actual #157/#169/#973 patches, not merely their titles.

### Integration hazard made explicit

**All three independent PR diffs touch `preparedness/tests/test_preparedness.py`**. PR #157 also changes `household-emergency-plan.body.html`, `three-day-kit.body.html`, `preparedness/sources/fragments/start.json`, and `preparedness/taxonomy.json`. PR #169 is a source-test fixture isolation patch; #973 is stacked on #169 and completes remaining isolation. These are not interchangeable merges. A blindly applied patch series could overwrite the Start Here safety regression, revert synthetic fixture isolation, or lose a seven-cluster taxonomy change.

**Correct integration sequence for an authorized maintainer (not performed):** obtain a trusted full checkout; compare pinned blobs with each PR base/head; stage #157 safety fixes in a dedicated candidate with a qualified reviewer (not by silently editing the original); stage #169 plus #973 as an ancestry-preserving fixture series; manually resolve the shared test-file changes without losing any assertions; rerun native validation/build/full test suite plus R176–R181 custodial gates; independently adjudicate medical, food preservation, source and QD decisions before any release consideration.

The R181 receipt confirms **35 matched original metadata/body file paths** from the exact R180 Git tree. The original 385 authored source relationships and 2,000 citation occurrences are carried forward from R179/R180's pinned review records, **not recounted by a complete native Python build in this run**. All 35 originals remain release-held draft according to that prior evidence; the structural preflight cannot grant human safety or QD approval.

## Local verification executed

- `python -m py_compile /mnt/data/r181/*.py` — PASS (exact locally created files).
- `python -I -m unittest discover -s /mnt/data/r181 -p 'test_*.py' -v` — **38 tests PASS**, plus additional negative subtests across seven branch SHAs, ahead/behind counters and the three independent PR signatures.
- GitHub-content APIs independently returned the committed validator Git blob `ee0982ef0a50e401d218acee9c7c4814c8aa56d8` and test blob `2b697ca3830d79c29debbb9a000228194d17191c`, both **byte-identical to the locally tested files**.
- The test suite uses **synthetic data**; the separately captured `contributor-evidence.json` reflects connected GitHub branch/PR metadata and Git-tree inspection. This is a provenance/structural guard, **not** a verified safety review or a full repository run.
- A complete local repository checkout remains blocked by `Could not resolve host: github.com`. Original `validate.py`, `build.py`, the full `preparedness/tests`, R176's native runner, and authentic WordPress export/print/mobile acceptance checks were **not executed**. Incomplete execution must not be labeled PASS.

From a complete trusted checkout (use actual contributor PR refs; no publishing):
```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r181*.py' -v
python -I preparedness/tools/r181_contributor_intake_gate.py \
  --observed preparedness/review/r181/contributor-evidence.json \
  --output /tmp/fv-r181-intake.json
# Expect exit 2 + DRAFT_HARD_HOLD, even when the evidence is structurally valid.
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300
```

## Conversion-first gate — one audience, no speculative offer

Target is **caregivers preparing school pickup, emergency contacts and family reunification**. Source-backed free guide candidate: **Household Emergency Plan**; optional free practical **Family Reunification Card** is an existing held draft and must pass eleven source decisions, data minimization/privacy, printing and mobile acceptance before activation. The creator asset ID, Grok destination URL and published landing are **unverified** in TASK-008; never invent either or overwrite the Grok/Praxxis queue.

**No authenticated rights-cleared, checkout-ready paid Preparedness SKU has been identified.** Therefore no purchase CTA, upsell URL, affiliate activation, fabricated merchant checkout, launch urgency or revenue claim is approved. Keep this audience/guide/tool mapping as a proposed nonpublic flow until a genuine seller listing, permitted rights, delivery, terms, test checkout and refund evidence can be cross-checked by Commerce/Claude.

Draft **onsite free-guide CTA** for later editorial/QA review (do not place live): “Make the plan before the emergency. Read our household planning guide — free, with sources and review dates.” Companion tool mention must say “Printable Family Reunification Card — coming after source, privacy and print review,” never implying a working download. No download form or school/child contact details should be ingested for measurement.

Acceptance checklist before any future release: exact Grok `asset_id` and `utm_content` resolved; actual source link/profile path confirmed; matching social message/landing intent; real mobile destination; clear free-vs-paid separation; intact source citations and safety labels; usable accessible buttons and printable tool; private household information kept local; rights and affiliate disclosure reviewed; confirmed purchase only from merchant records; fees and refunds subtracted. No duplicate analytics instrumentation.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Actual rights-cleared Preparedness pack → checkout | No authentic matching SKU/terms/delivery | Independently verify existing inventory and a real order path before adding an offer | **HOLD / unverified** | Commerce / Claude |
| Free Household Emergency Plan → relevant reader | Citation and qualified safety/QD review incomplete; native build blocked | Source-review decisions + native validation/build + staged mobile checking | **DRAFT / 38 synthetic R181 tests PASS only** | Preparedness / QA |
| Free guide → optional Family Card | Eleven source decisions, privacy/print QA incomplete | Validate safe local printing with synthetic contacts and no collection | **HARD HOLD** | Site QA |
| Grok social asset → guide landing | Real published asset ID and destination not supplied | Coordinate through existing TASK-008, no new task queue | **UNVERIFIED** | Grok / Praxxis |
| Verified paid orders → net revenue per 1,000 qualified sessions | Merchant orders, refund/fee amounts, qualified session denominator unknown | Reconcile 7/30-day cohort evidence before calculating net revenue | **NOT COMPUTABLE** | Commerce / Analytics |

Even a clean R181 structural result is **DRAFT_HARD_HOLD, exit code 2**. Never interpret historic “approved” or “not required” metadata labels as current release authorization; the two historically marked approved articles remain independently unverified, and food-safety/medical advice remains subject to qualified review.

**No existing article, citation, source, route, CMS, email, affiliate, measurement, merchant, social or public website change is made.**
