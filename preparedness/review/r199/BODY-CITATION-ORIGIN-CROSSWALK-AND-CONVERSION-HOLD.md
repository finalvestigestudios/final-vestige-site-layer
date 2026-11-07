# R199 — Article-body citations ↔ article-scoped source-origin crosswalk

**Issues:** Preparedness integration #136; conversion coordination #820; charter #818. **State:** BUILT / EXACT-CODE SYNTHETICALLY TESTED / DRAFT_HARD_HOLD. **NO release, CMS write, nav edit, checkout activation, social post, email or spending.**

## Defect and bounded fix

R194/R195 authenticates the complete old and revised article bodies and their source-use metadata; R197/R198 authenticates the source registers and checks that every article source use can resolve to its own cluster or the global base. Those two validation paths did not independently produce a **single per-citation occurrence bridge** between the complete authored body and the eligible source-origin record. Metadata-level source counts (65 frozen / 70 revised) must not be confused with **315 frozen / 334 revised article-body citation tokens**.

New read-only `preparedness/tools/r199_citation_origin_bridge.py` authenticates the exact producer Git blobs:
- R198 origin scope source: `77ca95b4140721a30370b7e851522bc0c85ef2aa`
- R195 body citation impact source: `e2dd19a5af2783817562a4928c82a9a1929ab83c`
- Original R194 seven-article docket: `05d393013a952d9d2c92a6e1d9759ca53579ae8b`

On an **authentic complete checkout containing the original Git objects**, it invokes the R198→R197 and R195 pipelines and checks, per article and version:
1. Complete old/revised body and metadata Git blob identities match the immutable seven-article R195 roster.
2. Every literal `{{cite:source-id}}` token is well formed, counted and traced to that **same article version's** explained source-use ID.
3. The source-use ID must have at least one origin in **global base or the article's own historical cluster**; foreign-only origins are rejected, and shared-ID alternatives remain explicit.
4. Every citation occurrence generates an immutable body/context digest, ordinal, source ID, source-origin alternatives, line number and **PENDING** claim adjudication. It does not select aliases or source winners.
5. The two independent upstream hard-hold packets must agree on producer schema, non-approval/sales state, article roster and citation counts. Expected old/new census is **315/334**, for only the **seven** historically changed articles.
6. Any substituted original Git object, changed version/route, malformed citation, missing relationship or false safety/QD/publication/merchant assertion fails closed. Successful structural review returns exit code **2** (`DRAFT_HARD_HOLD`), not PASS; failed custody returns **3** (`INVALID_HARD_HOLD`).

**Boundary:** This does not independently adjudicate semantic claim support, verify outbound URLs, or expand the test to every other one of the 35 articles and six tools. The seven shared source identifiers discovered in R197, and the `hist-food-nchfp-jerky` → `nchfp-jerky` discrepancy, remain UNRESOLVED; neither is silently aliased. R199 preserves original reading depth by making **zero** changes to authored bodies or metadata.

## Executed tests

- `python -I -m unittest discover -s /mnt/data/r199/preparedness/tests -p 'test_r199*.py' -q` — **76/76 PASS** in isolated synthetic fixture; 52 per-origin mutation cases plus 18 false-approval/producer/error mutations, deterministic replay, strict-census refusal and immutability checks.
- `python -m py_compile .../r199_citation_origin_bridge.py` — PASS.
- Exact **locally tested** Git blob identities, cross-checked against GitHub committed files: source `5e3fdf409a740fd22c9c858ec78aff9fb5bbef3a`; tests `e9c2ede5a04f4898eb8f99c6ba488d10461db1a4`.
- **NOT EXECUTED:** complete native repository `validate.py`, `build.py`, original 36+ test suite, R199 native CLI against 28 original versioned Git objects, original 35-article/six-tool draft WordPress export, real-browser accessibility/printing/privacy, independent citation/food/medication qualified reviews, or independent QD. The local container reproduces `github.com` DNS resolution failure on `git ls-remote`; connected GitHub source reads do not provide a complete Git checkout. Hosted CI not claimed.

To reproduce on a trusted complete checkout:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r199_citation_origin_bridge.py --repo . --report /tmp/fv-r199-citation-origin.json
```

Structural correctness still yields only `DRAFT_HARD_HOLD`. A qualified reviewer must individually reconcile body claims, changed historic sources, medically consequential food/medication safety and child-data privacy before any publication decision.

## Contributor and QA coexistence

Fresh source heads on 2026-11-07 PT:
- Start `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Food `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Health `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Shelter `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Historical Field `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- Historical Food `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Independent QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its follow-up PR #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` all remain separate drafts. #157/#169 touch shared original `preparedness/tests/test_preparedness.py`; DO NOT blind merge. Homepage Focus conversion PRs #1443 (`4c2a1fabd4ae01ee8b6a90ce810cba9c029db494`) and #1451 (`b3830356fe00871da4bb54ab1a0e5a213ca4aab7`) are untouched. Historical crosswalk and current cluster heads may differ; no cherry-pick, reset, rebase, source change, QD claim or public merge.

## Conversion-first, one audience, one candidate — NO PAID CTA LIVE

**Audience intent:** households protecting identity, insurance, financial and emergency-contact records before displacement.

**Free information:** existing public Preparedness gateway; detailed original Household Emergency Plan is an **unpublished** source-review candidate, not a public campaign destination. Optional Family Reunification Card is a **free** held printable, not a paid offer. The approved Seven Day Focus Fieldbook remains the **only** active signup gift; do not revive retired water freebies.

**Single paid candidate:** existing *Legacy Triage* listing, **UNAUTHENTICATED** for original ownership/rights, SKU/content, current live price, relevance, merchant checkout, PDF fulfillment, refunds/support and independent purchase evidence. Do not put it in a CTA or claim it is currently purchasable until each field is verified by founder/commerce.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Legacy Triage → confirmed paid order | Rights, actual active SKU and payment/delivery/refund unknown | Read-only verified commerce inventory, followed by founder-approved, non-financial staged checkout/fulfillment acceptance | **HARD HOLD**; no order or merchant proof | Founder / Commerce / Claude |
| Grok records-continuity post → free gateway | Exact posted creator asset_id, URL, approved link placement and landing URL not supplied in TASK-008 | Praxxis reconciles existing TASK-008; Grok retains creative/distribution; do not generate a phantom UTM | **UNVERIFIED**; no attributed qualified visits | Grok / Praxxis |
| Public gateway → Household Emergency Plan | Original 35-article native validation, human citation and qualified safety review pending | Re-run native validate/build + independent claim/citation reviews, 360/390/768/1440 staged checks | **DRAFT_HARD_HOLD** | Preparedness / Independent QA |
| Free plan → optional Family Card | Child-data privacy, local-only/browser-offline/print access/source adjudication | Real staged synthetic-data testing, keyboard and print checks without retaining private contacts | **HARD HOLD** | Preparedness / Site QA |
| Verified paid orders → net revenue per 1,000 qualified-human sessions | No confirmed Payhip/order attribution, refunds, fees, customer count or QHS denominator | Report 7-day and 30-day cohorts only when first-party confirmed, separate clicks/leads from paid sales | **NOT COMPUTABLE** | Commerce / Analytics |

**Unpublished sample free-resource CTA:** “Keep essential household contacts and documents organized before an interruption. Explore the free emergency-planning resources.” No fear-based urgency, unsupported medical/financial claim, email gate on safety guidance, or unapproved paid product.

**Campaign acceptance, to be tested only after approval:** correct published Grok asset ID → platform bio/caption link and permitted UTM → correct public free landing intent → accessible mobile CTA and readable safety disclosures → confirmed lead only with valid consent/record → verified merchant order/affiliate report → fees/refunds → realized net revenue. Capture only privacy-appropriate events through approved existing measurement, without a duplicate script or unsupported attribution.

**Release remains HARD HOLD.**