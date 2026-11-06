# R157 — Preparedness source-bound draft campaign admission (HARD HOLD)

**Issue:** #136 (Preparedness); conversion coordination #820 and business charter #818.  
**Base:** frozen R156 source reconciliation PR #1181, exact `f7c00c2a120f9a28caa209cad85de9e39b8016cb`.  
**Status:** draft-only engineering. This does **not** authorize any website, navigation, publishing, email, paid offer, affiliate, social post, or analytics write.

## Why this exists

The source review pipeline holds **75 review tasks**, including 11 Family Reunification Card relationships / 16 citation occurrences, 2 contested interpretations, 6 inaccessible automated source retrievals, and 3 limited text matches. Meanwhile, TASK-008's creator inventory does not identify a confirmed published Preparedness-specific asset or its exact permitted destination, and a **matching rights-cleared, presently purchasable FV Preparedness SKU has not been authenticated**. Those unknowns must not silently turn into landing-page claims, verified sales, or active checkout links.

R157 gives the proposed, narrowly relevant journey a checkable draft contract:

**School pickup / family reunification creator topic → free Household Emergency Plan → optional free Family Reunification Card → optional verified existing paid toolkit (currently absent, so NOT DISPLAYED).**

The two destinations are **proposed canonical WordPress draft routes**, not statements that the pages are live:

- `https://finalvestige.com/preparedness/start-here/household-emergency-plan/`
- `https://finalvestige.com/preparedness/field-tools/family-reunification-card/`

No retired water freebie, speculative product, personal contact list, email gate for essential guidance, or conversion-tracking script is included.

## What the gate enforces

- Invokes the exact Git blob of the R156 validator (`050bbf14761c12a666250a4da633c19b979f3c81`), its frozen source chain and the original review docket. Missing, changed, or incomplete custody **fails closed**.
- Requires the source report to stay `DRAFT_HARD_HOLD` (11 Family sources / 16 citations / 64 other review tasks). Reads the exact guide and card metadata and verifies both still have draft publish states and body files.
- Requires the free guide to stay available without registration or payment; makes the optional card explicitly unreviewed in internal draft materials. The current article/tool and their citations stay untouched.
- Validates exact host/path for proposed draft destinations and rejects encoded-path ambiguity, query-string data leaks, fragments, path deviations, and lookalike origins.
- Rejects partial creator attribution, forbidden spoken-script CTA placement, wrong platform host, invented purchase order or refund metrics, unapproved merchant SKU/checkout, approval forgery and speculative offer claims.
- Even when a complete creator reference is **supplied**, its authenticity is **not verified by this script**. `creator_asset_fields_complete` may be true; `creator_asset_verified` is always false. A submitted post URL is **not** social-platform evidence.
- A valid structural assessment always returns `DRAFT_HARD_HOLD` with unknown sales and revenue. The CLI always exits **2**, including on an internally consistent draft. It never claims QD PASS or that unreviewed advice is medically safe.

## Reproduction

From a **trusted complete repository checkout**, run:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r157_preparedness_funnel_gate.py --repo .
```

**Expected R157 CLI code is 2, not 0**. Its JSON output must say `DRAFT_HARD_HOLD` or `INVALID_HARD_HOLD` with `public_release_allowed: false`. No WordPress changes occur. A separate `--manifest /path/to/proposal.json` is supported for local, read-only drafts. Omission uses the explicit unknowns baked into `proposed_contract()` and creates no output file.

### Local test evidence

At the committed source and test Git blob identities, 45 isolated Python unit tests passed, including malicious URL, merchant-approval forgery, fabricated metrics, and cross-platform post-host spoofing. Python compilation passed. These tests use synthetic data only and cannot prove the authentic 35-article build, WordPress renders, independent human safety review, creator publishing, merchant delivery, or live attribution.

The complete authenticated repository is **not** available to the local Python runner: container GitHub DNS resolution fails. GitHub connector provides read/write source access but is not a mounted checkout, so **native validation/build/full-suite are NOT EXECUTED** here.

## Conversion prioritization / acceptance

| Offer → funnel step | Blocker | Draft change / acceptance evidence | Owner |
| --- | --- | --- | --- |
| Existing FV-owned Preparedness toolkit → verified purchase | No approved matching actual SKU/rights/merchant acceptance | Obtain actual listing + price, source/asset rights, guest/mobile checkout, file delivery, refund/fees; independent merchant-confirmed paid order only. **HOLD** | Commerce / Claude / founder |
| Household Emergency Plan → free reader | Original source/safety and QD reviews incomplete | Human adjudication, full narrative preserved, visible source-specific disclosures, native validator and WordPress draft browser checks. **HOLD** | Preparedness / independent QA |
| Free guide → Family Reunification Card | 2 source-scope disputes, 6 blocked retrievals; privacy/print untested | R156 workorders; verify offline/local storage, no family contacts transmitted, legible print and keyboard use at 360/390/768/1440. **HOLD** | Preparedness / Site QA |
| Grok post → same-intent draft destination | Actual Published Preparedness media ID/URL and permitted CTA location absent | Praxxis/Grok TASK-008: actual asset_id, published URL, license/source QA and compliant caption/pinned sources/profile placement, approved exact destination/UTMs. **UNKNOWN** | Grok / Praxxis |
| Qualified sessions → CTA → lead → verified purchase → realized net | No reconciled human session/order/fee/refund evidence | Reuse #820 privacy-preserving contract; paid conversion only from settled merchant records; 7/30-day cohorts, small samples flagged, net revenue / 1000 qualified-human sessions null until measurable. **NOT COMPUTABLE** | Claude / Commerce / analytics |

Suggested internal copy (NOT PUBLIC APPROVAL): **“Plan who to contact and how your household will reunite — free household guide.”** Secondary internal draft: **“Optional family reunification card — free printable, under source and privacy review.”** Do not append a paid call-to-action until the genuine offer passes commercial and release gates. Never hide essential safety content behind a purchase or email signup.

## Contributor / neighboring QA boundaries

Verified contributor branch heads in this engineering round:

- Start Here `claude/prep-start-bbfeb8`: `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `claude/prep-shelter-5e1e0e`: `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Food `claude/prep-food-ccdc55`: `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Health `claude/prep-health-837444`: `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical Food `claude/prep-hist-food-b81f19`: `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `claude/prep-hist-home-0e0e38`: `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- Historical Field `claude/prep-hist-field-9db767`: `4e5caf812727953aa45e3bda2d382f2c67b6a09c`

Independent safety **draft PR #157** (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and synthetic fixture **draft PRs #169** (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) / **#973** (`4d40996a559b0124d74a9bb3bdcd481ad1992aa8`) stay separate and unmerged. Homepage PRs #49 (`10495883299d53596992c26a8987f629b2904670`) and #604 (`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`) remain outside this lane. No competitor branch or article/source record was modified.

All 35 instructional articles remain **DRAFT / HOLD**. This run has added only a read-only, isolated admission guard and adversarial tests; human source/medical safety and independent QD are still outstanding.
