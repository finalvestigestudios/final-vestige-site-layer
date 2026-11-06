# R172 — Jerky source identity / article-impact gate (DRAFT / HARD HOLD)

**Issue:** #136 | **Conversion coordination:** #820, business charter #818. **Parent:** R171 PR #1277 at `77df5c0ec20058faea163f04ca0d09b1dd3d4997`. This draft does not authorize publication, source-link approval, a recommended food-preservation method, paid sales, or QD PASS.

## Concrete impact, authenticated on 2026-11-06

I read all **35 original pinned article metadata files** against R151 Git blob identities from the existing protected repository head; all **35/35 match their pins**, all are **draft**, and they contain **385 source-use edges (208 in the first 18, 177 in the remaining 17)**. Only **three original articles** use either of the two literal NCHFP jerky IDs:

| Draft article | Pinned original metadata SHA | Source ID | Review |
|---|---|---|---|
| `pemmican-and-dried-meats` | `03d3824e07fe51931671d0ddc7aa8c85eda58435` | `hist-food-nchfp-jerky` | HUMAN HOLD |
| `pioneer-travel-rations` | `7191acba55d63dc405ad9c2003d66193276da89f` | `hist-food-nchfp-jerky` | HUMAN HOLD |
| `safe-jerky-dehydration` | `50b365e8109c14bdb9ce1a9365db88215a678ec5` | `nchfp-jerky` | HUMAN HOLD |

The original crosswalk records **three variants** at the literal slashless NCHFP URL: `base:20 nchfp-jerky`, `food:3 nchfp-jerky`, and `hist-food:14 hist-food-nchfp-jerky`. But the actual historical-food source record ends with a slash. **Do not silently normalize either variant or delete IDs.** A 200/redirect alone is insufficient to establish source-scope identity.

## Separate material content issue — authoritative agencies describe different approaches

NCHFP's published UGA *So Easy to Preserve* jerky guidance (6th ed., 2014) describes both pre-drying and post-drying heat approaches: https://nchfp.uga.edu/how/dry/recipes/jerky . The USDA FSIS Meat and Poultry Hotline's page, **last updated February 4, 2025**, advises heating meat/poultry to appropriate temperatures *before dehydrating*: https://ask.fsis.usda.gov/article/How-do-I-dry-jerky . FSIS separately discusses why bacteria can become harder to destroy after drying (last updated November 18, 2024): https://ask.fsis.usda.gov/article/Why-is-temperature-important-when-making-jerky . **These are official-source differences, not an invitation to mix methods, improvise recipes, declare after-drying heating safe, or tell readers either procedure has been independently approved by FV.** A qualified reviewer must inspect each of the **three affected article passages** alongside the cited full source and applicable current food-safety advice, record a claim-by-claim disposition, then request independent QD. The URLs' current equivalence remains unapproved.

## R172 engineering and testing

- Read-only `preparedness/tools/r172_jerky_alias_claim_gate.py` checks exact R151/R161 custody and Git blob pins for the original crosswalk, the original historical food source, R171's quarantine and all 35 metadata; runs R161's authentic complete-body 35/2000/385 custody proof first; then checks the original alias's three source variants, row indices, IDs, source-level human checks and 32-group HOLD status. Produces deterministic three-article impact and SHA-256 receipt, **never an approval**.
- `preparedness/tests/test_r172_jerky_alias_claim_gate.py`: **57/57 Python unit tests PASS locally**, including source-identity and forged-review adversarial mutations; Python compilation PASS. Tests use **synthetic fixtures**, and an incomplete checkout returns `INVALID_HARD_HOLD` with process exit 2.
- `preparedness/review/r172/jerky-source-impact.json` records exactly three authentic impacted drafts and the source-scope concern. Original bodies, metadata, source registries, crosswalk, taxonomy, routes, output and WordPress were **not modified**.
- Full authentic `python -I preparedness/tools/validate.py`, `build.py`, complete test suite, R172 authentic gate and actual WordPress/Chromium print/privacy/A11y checks are **NOT EXECUTED**; local `github.com` DNS still blocks private git cloning. The upstream R171 crosswalk discrepancy remains an independent invalid hard hold. Human source/safety and QD remain **PENDING**.

## Read-only collaborators / non-interference

Seven Claude clusters remain at exact original R151 checkpoint: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`, Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`, Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. GitHub compares on Nov 6: all seven **identical, ahead/behind 0**. PRs #157 (safety), #169 and #973 (synthetic fixture isolation), #49/#604 (homepage) inspected **read-only**. Pending **75 source decisions** and **32 URL interpretation groups** are not automatically cleared.

## Conversion-first, strictly draft-only

High-intent audience: family caregivers planning school pickup and reunification. Creator topic / immutable asset ID / post URL: **not authenticated in Grok/Praxxis TASK-008**; no creator queue edits. Existing original ungated `Household Emergency Plan` (**DRAFT**) → optional free `Family Reunification Card` (**DRAFT / source and browser HOLD**) → only after commerce verification of an **existing, rights-cleared, actually purchasable FV Preparedness pack** would an optional relevant paid practical pack be eligible for founder-reviewed CTA. No matching SKU, rights/fulfillment/refund and checkout evidence yet; **no paid CTA or merchant link**. Do not redirect to retired water freebies or disturb `/focus/`.

**Draft CTA for future qualified review only:** “Put your household contact and school pickup plan on paper — a free guide, no signup required.” Link only after authentic safety/QD/WordPress testing and founder release approval.

**Pre-release landing acceptance:** correctly matched actual Grok asset ID and platform-permitted URL/UTMs; honest guide scope and safety dates; free ungated access; optional card with privacy and 360/390/768/1440 print tests; no accidental lead capture; clear optional product disclosures and correct merchant checkout only after SKU/rights validation; no duplicate analytics and consent respected.

**Offer → funnel → blocker → change → pass/fail evidence → owner:** existing paid Preparedness pack → purchase → no authenticated rights-cleared SKU or delivery → merchant/commerce evidence inspection → **HOLD** → Claude/Commerce. Free Emergency Plan → guide read → pending source/safety/QD and native build → source adjudication and native tests → **R172 57 fixture tests only; authentic HOLD** → Preparedness/QA. Free guide → optional Card → 11 source decisions and real browser/print/privacy pending → independent QA → **HOLD** → Preparedness/Site QA. Grok social asset → landing → missing published Preparedness asset ID/destination → TASK-008 reconciliation → **UNVERIFIED** → Grok/Praxxis. Sale → realized net revenue/1,000 qualified humans → missing merchant settlements, fees/refunds and verified traffic denominator → reconcile 7/30-day cohorts → **NOT COMPUTABLE** → Commerce/Analytics.

No publishing, nav, CMS, merchant, affiliate, email, social posts/queue, analytics activation, spending or merging. **DRAFT / HARD HOLD.**
