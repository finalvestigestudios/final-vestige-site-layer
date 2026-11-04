# R123 — full-source variant exposure crosswalk and conversion HOLD

**Date:** 2026-11-04. Owner: Preparedness integration / source-safety lane, Issue #136. Cross-reference #820 and business charter #818. **DRAFT ONLY. Do not merge, publish, modify navigation/CMS, authorize QD, or infer emergency guidance safety.**

## Why this gate is needed

R117–R122 preserve the 35-article body/meta custody and reader-visible citations. However, the frozen source crosswalk was generated before later contributor source fragments. Those fragments can add *new same-URL provenance collisions* even when no article URL, word count, citation count or author-scoped source-use text changes.

R123 adds `preparedness/tools/r123_claim_source_coverage_gate.py` and 78 local synthetic/adversarial tests. From exact R117 baseline/candidate Git blob objects and pinned `register.json`, it constructs every base/fragment source-variant identity, checks all 35 body/meta pairs, relates every citation ID to each article's author-specific `source_use`, identifies changed per-article citation exposures and changed author reading scopes, and compares candidate shared-URL variants against the explicit unresolved source crosswalk. It preserves paths, query strings and URL fragments rather than silently merging potentially different evidence scopes. Its output stays `HOLD`, even when structural blockers are empty.

## New actual-GitHub source finding (independent read, not a full Python checkout run)

On 2026-11-04 the GitHub connector independently retrieved all **eight current candidate source-register/fragment files** at RC #584 pinned head `ddb3528ba6494dada1fa1c3a142ce746e3a67706`, plus `preparedness/sources/crosswalk.json`. The eight files contain **244 source rows**, **225 distinct exact IDs**, **202 distinct exact URLs**, and **32 same-URL groups**. The existing unresolved crosswalk declares only **30 groups**; its original count (224 source rows) is now stale against the integrated candidate.

**Two unlisted shared-URL groups:**

1. USDA FSIS emergency-food handling page: `https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keep-your-food-safe-during-emergencies`. Two distinct source identities: `food-fsis-emergencies` (food fragment) and `shelter-usda-fsis-emergencies` (shelter fragment). Both claim different reading/use scopes.
2. NWS winter vehicle safety page: `https://www.weather.gov/safety/winter-during`. Two distinct identities: `hist-field-nws-winter-during` (historical-field fragment) and `shelter-nws-winter-during` (shelter fragment); their specific readings include vehicle/CO guidance, warranting qualified review.

**Two existing crosswalk entries with changed variant rosters:**

3. USDA FSIS power-failure Q&A: `https://ask.fsis.usda.gov/article/How-do-you-keep-food-safe-during-a-power-failure`. Declared: base + food; candidate now also includes `shelter` (ID `fsis-power-failure`). All three reading scopes must remain available until adjudicated.
4. CDC outage page: `https://www.cdc.gov/natural-disasters/response/what-to-do-protect-yourself-during-a-power-outage.html`. Declared: shelter + health; candidate now also includes `start` (ID `start-cdc-power-outage`). Medication and generator CO safety claims must remain separately scoped and human-reviewed.

These are **provenance worklist defects, not findings that a cited public-health recommendation is accurate or safe**. Do not auto-deduplicate or designate a canonical source use. The source crosswalk must be regenerated/adjudicated by the owner with all 32 candidate groups and exact row positions; keep all legacy variants and R117 evidence unchanged.

## Tests and commands

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r123_claim_source_coverage_gate.py' -v
python -I preparedness/tools/r123_claim_source_coverage_gate.py \
  --repo . \
  --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json \
  --register-oid b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77 \
  --crosswalk preparedness/sources/crosswalk.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

- **BUILT:** independent read-only R123 gate and test file on a stacked private draft branch; no source/article/metadata or safety-status mutation.
- **TESTED LOCALLY:** 78/78 synthetic and adversarial tests passed; Python compilation passed. The Git object identities of the committed files match the locally tested bytes. Source checker simulates 35 paired articles and 30 shared-URL groups, including 35 independent missing-author-source-use mutations. No live safety, commerce, or browsing assertions.
- **INDEPENDENTLY READ FROM GITHUB:** real 244-row source census and four specific crosswalk omissions/drifts above.
- **NOT EXECUTED:** exact Git checkout audit against all 35 actual historical/candidate body+meta pairs, native repository validate/build/full regression, WordPress/browser or print QA, mandatory integrity, independent QD and qualified medical/emergency review. Container cannot access the private GitHub clone and no trusted checkout is mounted. GitHub Action runner dispatch has historically failed before runner execution; do not claim code failure or success from runner failures.

## Governance and coordination

Seven live contributor refs checked on November 4: food `f911ff7a`, health `d5ef5baf`, historical-field `4e5caf81`, historical-food `67e116e5`, historical-home `7504a5f0`, shelter `5daeaf2d`, start-here `2122d856`. Release candidate #584 `ddb3528b`; homepage #49 `10495883`; flagship #604 `bdf01b4a`. Independent QA #157 `7d1ae6b8` and synthetic-fixture PR #169 `e9cd7766` remain isolated drafts; PR #169 still has a shared-directory temporary fixture in one test. No branches were merged; all publication and safety holds retained.

## Conversion-first Preparedness path (no unapproved sale)

**One chosen audience/topic:** households wanting emergency-contact, school pickup and reunification planning. **Authentic editorial free guide candidate:** source-backed `household-emergency-plan` (draft, still safety HOLD). Proposed route `/preparedness/household-emergency-plan/` is **not a verified live destination**. Draft noncommercial CTA: *“Build a family communication and reunification plan you can actually practice. Explore the source-linked household guide and adapt it to your needs.”* Never gate the essential instructions behind a form.

**Optional paid practical tool: BLOCKED.** No live FV-owned, purchasable, rights-cleared preparedness SKU/price, usable downloadable delivery, refund policy, or merchant sale record was authenticated. Do not introduce a mock purchase link or imply the Focus Fieldbook is a preparedness pack. Retired water freebies remain excluded.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing Preparedness pack → purchase | No confirmed SKU or delivery rights | Validate merchant listing, price, rights, fulfillment file, refund terms and test purchase when authorized | **UNVERIFIED / HOLD** | Growth + Claude |
| Free household guide → reader | 32 candidate source groups, safety/claim adjudication | Human reconcile four discovered crosswalk defects; qualified safety review + full build QA | **FAIL: 2 unlisted, 2 stale rosters** | Preparedness + QD |
| Grok social asset → guide | No verified Preparedness asset_id or published destination | Coordinate with Praxxis/Grok TASK-008; specify source=platform, medium=organic_social, campaign=preparedness_pilot_2026_11, content=unique asset_id; test profile/bio routing | **NOT TESTED** | Grok/Praxxis |
| Guide → optional CTA → checkout | Paid offer and checkout unverified | Staged mobile 360/390/768/1440, label/disclosure, clear free vs optional, checkout accessibility and usable file delivery | **NOT TESTED** | Claude / Site QA |
| Paid order → net revenue | No order/refund/fee attribution or qualified-human denominator | Record qualified unique sessions and verified merchant orders only; 7/30-day cohorts, tiny-sample flags, net revenue per 1,000 | **N/A (no verified transactions)** | Growth |

Track qualified human landing sessions by immutable `asset_id` → guide CTA click → independently confirmed lead (where relevant) → paid merchant-confirmed order → refunds/fees → realized net revenue. **Do not equate views, visits, clicks, checkout starts or email form submission with a sale.** No duplicate tracking scripts, new public URLs, sending/posting, affiliate activation, spending or CMS writes.

**Release: HOLD.** R123 is structural evidence tooling, not approval of a source, URL, historical method, emergency recommendation, QD status, product, or publication.
