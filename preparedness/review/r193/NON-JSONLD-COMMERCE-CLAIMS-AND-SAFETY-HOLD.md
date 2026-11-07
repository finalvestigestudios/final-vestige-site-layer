# R193 — Non-JSON-LD commerce-claim custody; source/safety and conversion HOLD

**Scope:** Preparedness Archive #136; creator-to-customer governance #820, founder charter #818.  
**Release state:** DRAFT_HARD_HOLD. This is a review-only change on an isolated branch, not WordPress, merchant, analytics, email, social or publication authorization.

## Finding and patch

R191/R192 checked unapproved `Product`, `Offer` and purchase assertions in JSON-LD, as well as external CSS/SVG resources, duplicate HTML attributes and comment-obfuscated CSS. Their HTML scanner did **not** reject equivalent assertions expressed through **Microdata, RDFa or OpenGraph product/price meta tags**, and the original JSON-LD type parsing missed trailing-slash schema URLs.

R193 extends that *existing* fail-closed six-tool scanner to recognize commercial `itemtype` / `typeof` types, `itemprop` / `property` / `rel` properties, product/price `meta` declarations, and trailing-slash or percent-encoded JSON-LD types. It preserves neutral article, citation and accessibility metadata. These are static, negative controls: catching a declaration cannot establish merchant authenticity or a sale.

**Producer source pin:** patched `preparedness/tools/r191_static_resource_offer_gate.py` Git blob `26f3067379148161f3404355c52454c4139372ce`. The native wrapper `preparedness/tools/r191_full_integrated_preflight.py` pins that exact blob, and does not emit a successful release exit. The original 35 article bodies, six companion-tool bodies, review records, source registers, 2,000 article citations, 173 tool citations, 385 article source-use and 67 tool source-use relationships are not edited here.

## Validation contract and current evidence

- New `preparedness/tests/test_r193_microdata_rdfa_commerce.py` has **77 generated unittest methods**: 55 unapproved markup examples, 15 permitted examples, six mutations of a tool's synthetic WordPress draft, and one six-tool structural HOLD case.
- A **locally reproduced R191/R193 parsing subset**, not the exact private repository module, executed **77/77 PASS, 0 skipped**, with Python isolated-mode compilation also passing (2026-11-07). This provides targeted algorithm evidence, not a claim that committed tests ran in a complete exact checkout.
- The full authentic `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v` and all 41 actual WP draft exports are **NOT EXECUTED** here. GitHub DNS resolution failed from the container (`Could not resolve host: github.com`). No external browser, customer-data, privacy, source adjudication or safety/QD pass exists.
- GitHub readback confirms the updated parser blob and its exact pin in R191 native preflight. A clean structural result remains `DRAFT_HARD_HOLD` with exit code 2, never live/published.

**Independent review:** QA PR #157 corrects a dangerous home-breaker drill statement, cautions on medicine-specific storage/continued treatment and correctly identifies the Red Cross; its original patch is separate and unmerged. Fixture PR #169 isolates food-source tests; stacked PR #973 isolates the last shared-tree source fixture; both remain separate and unmerged. None proves independent food, medication, child-data, privacy, or clinical safety review.

## Seven upstream Claude branches — fresh GitHub heads (2026-11-07)

| Cluster | Current head | Compared with frozen source crosswalk |
| --- | --- | --- |
| Start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | Identical (0/0) |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | Identical (0/0) |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | Diverged (1 ahead/1 behind; docs/tests only in comparison) |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | Ahead 1 (cluster document) |
| Historical field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | Ahead 1 (article/source edits) |
| Historical food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | Ahead 1 (article/source/tests edits) |
| Historical home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | Ahead 2 (article/source edits) |

The comparison is to the historical `preparedness/sources/crosswalk.json` source-head pins, **not evidence of unexpected changes during this round**. No blind merge, repointing, or reset of these branches. Reconciling their article and citation deltas against the full candidate requires an authenticated complete checkout and independent review.

## Offer → funnel → blocker → experiment → evidence → owner

| Offer | Funnel step | Blocker | Draft-only change / acceptance check | Evidence and owner |
| --- | --- | --- | --- | --- |
| **Legacy Triage** (candidate only) | Actual checkout → paid order | Seller ownership, resale rights, exact PDF contents, checkout, delivery, fees/refunds and audience fit not authenticated | Commerce to independently verify a real purchasable rights-cleared SKU, accessible mobile checkout, real download delivery, refund policy and seller order ledger before a sales CTA | **HARD HOLD** — Founder/Commerce/Claude |
| **Household Emergency Plan** | Social household-documents interest → free ungated guide | Original article still unpublished and source/safety/QD held | Keep public /preparedness/ official-resource gateway as any provisional destination; verify guide citation accuracy and visible warnings before proposal to publish | **DRAFT / HELD** — Preparedness, independent QA |
| **Family Reunification Card** | Free guide → optional printable | Eleven source decisions, child/contact privacy, print and keyboard checks unresolved | On synthetic identities: ensure no exfiltration/storage, complete printable fields, legibility/contrast at 360/390/768/1440, no checkout or email gate | **HARD HOLD** — Site QA |
| **Grok social asset** | Organic video → landing | Actual published immutable asset_id, post URL, rights, CTA placement and approved landing absent from TASK-008 | Grok/Praxxis maintain their queue; stage `utm_source=platform`, `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11`, `utm_content=verified_asset_id` only if approved and observable | **UNVERIFIED** — Grok/Praxxis |
| Existing Focus signup (optional, not replacement) | Landing → confirmed lead | No Preparedness-specific confirmed consent or delivery evidence | Preserve sole Seven Day Focus Fieldbook and existing signup; never gate emergency instructions, compare source-confirmed counts only | **UNKNOWN** — Claude/Dispatch |
| Merchant order | Paid customer → realized net revenue | Source-confirmed paid orders, refunds, fees and qualified-human sessions not available | Report 7/30-day cohorts and realized net revenue per 1,000 qualified-human sessions **only** after payment source confirmation and valid denominators; tiny sample warning | **NOT COMPUTABLE** — Commerce/Analytics |

**Audience/topic fit (research-only):** “Which essential identity, insurance and family contact records could you actually locate if you had to leave tonight?” Grok owns creative and posting; no new TASK-008 asset is claimed, no speculative paid offer is activated. Legacy Triage relates to records continuity rather than emergency child reunification, so no mismatched upsell. No retired water freebie, no email campaign, no added paid services or duplicate scripts.

## Exit criteria

1. Execute exact committed Python scripts/test suite and complete 35+6 native build in a trusted pinned checkout, with source/citation comparison to seven contributor heads.
2. Human adjudicate open source/claim/food/medication/reunification decisions, plus independent QD and browser privacy/print/accessibility.
3. Authenticate merchant SKU, rights, fulfillment, fees/refunds, and Grok asset IDs/destination before considering any conversion experiment.
4. Obtain founder's separate release approval. This document authorizes **nothing live**.
