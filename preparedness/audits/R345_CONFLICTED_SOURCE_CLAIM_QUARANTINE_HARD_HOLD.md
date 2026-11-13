# R345 — Competing Source Claims: Deterministic Quarantine and Affected-Article Docket

**Status:** DRAFT / HARD HOLD / READ ONLY. Owner: Issue #136; commercial coordination #820 and charter #818. Stacked on R344 draft #2363 at frozen commit `17ebbdd5c875a4326d8b2758f0996e7cc3f24f4f`. No original source, article, tool, taxonomy, CMS, site navigation or production edits.

## Engineering defect addressed

R343’s source loader rejects duplicate *research-verified* source IDs; R344 likewise rejects four competing fragment definitions. Their strict rejection is appropriate for release, but an early invalid result can obscure **which source-linked paragraphs need human review**. R345 creates a **quarantined human-review packet** from the two pinned variants of each conflicting ID, and binds already-unreviewed R343 citation tickets by original source identity. It does **not** select the first variant as authoritative and never downgrades the release hold.

The eight source JSON objects remain Git-pinned by R344, and R345 also pins the actual R343 and R344 validator Git blobs. Four source records require reviewer decisions, distinct from the original 15 editorial conflicts and 17 Article #15 / Tool #104 safety/privacy reviews:

| Source ID | Research-fetched variants to inspect | Why |
|---|---|---|
| `fsis-power-failure` | `fragments/food.json` and `fragments/shelter.json` | Different support summaries and fetch dates; source may appear beside consequential food-safety claims |
| `nchfp-home` | `fragments/food.json` and `fragments/hist-home.json` | Different research support scope; landing-page reference must not be treated as method-specific validation |
| `loc-prairie-traveler` | `fragments/hist-field.json` and `fragments/hist-food.json` | Different source interpretations, including historical context |
| `loc-pioneer-diaries` | `fragments/hist-field.json` and `fragments/hist-food.json` | Different summaries and verification dates |

All four conflicting groups happen to reuse a source URL, **not** an independently adjudicated claim. All original 244 source rows have `human_link_check` unset or false. The R345 reviewer output shows only hashed source variants, cited-document IDs and claim fingerprints, not private full text or a preferred URL.

## Independently checked corpus impact (metadata, not proof of visible citation)

At R344 head, all **41 original metadata files** were inspected through authenticated GitHub reads: 35 article and six tool metadata records, all `status.publish=draft`. Exactly **12 source-use declarations across 10 distinct draft entries** reference one or more of the four disputed IDs.

| Source identity | Draft entries declaring the source |
|---|---|
| `fsis-power-failure` | `articles/food-safety-power-outage`; `articles/outage-heat-cold-generators`; `tools/power-outage-planner` |
| `nchfp-home` | `articles/pickling-fermentation-old-recipes`; `articles/pressure-canning-low-acid` |
| `loc-prairie-traveler` | `articles/navigation-before-gps`; `articles/pemmican-and-dried-meats`; `articles/pioneer-supply-chains-failed`; `articles/pioneer-travel-rations`; `articles/ships-biscuit-and-hardtack` |
| `loc-pioneer-diaries` | `articles/pioneer-supply-chains-failed`; `articles/pioneer-travel-rations` |

The metadata references are a **triage impact estimate**, not a count of actual visible citation tokens or validated paragraph claims. Only an authenticated native R343 review-ticket run can establish the latter. Never mark these source claims correct or medically safe by default. The complete 35/6 corpus, 14 shared Git-object differences and 15 separate editorial conflicts remain frozen for review.

## Code and test contract

- Pure `make_packets` rejects unexpected conflict IDs, variant provenance drift, different URLs, duplicate records in one source file, duplicate/invalid ticket IDs, forged review states and mismatched document/claim fingerprints.
- Native `native_audit` pins R343/R344 code bytes and R344's original eight source JSON blobs, invokes R343's original 41-entry/R337 witness, and permits **only the four known duplicate-ID errors to pass through to the quarantine docket**, never through to QD/release certification. Other validation errors fail closed.
- Output state `KNOWN_CONFLICT_HARD_HOLD` or `INVALID_HARD_HOLD` only, with every commerce, CMS, safety and approval flag false. The CLI returns nonzero even for the known-conflict docket.
- Locally executed **68/68 new adversarial Python tests PASS**; **164/164 R344+R345 isolated tests PASS** and Python compilation PASS. Exact R345 committed Python module and tests checked by Git blob ID after last modifications. **NOT EXECUTED:** full authenticated native checkout, 35+6 validation/build, actual 50 WordPress + 50 preview outputs, hosted CI and qualified human claim review. Offline reconstruction is not release evidence.

## Independent QA and coordination boundaries

2026-11-13 live exact heads: #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (draft); #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (draft; one remaining canonical source fixture write); dependent #2205 `bbcf1859768624c611df4abadc564c18247cf32a` (draft, no merge); home lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` (draft, untouched). All original seven Claude cluster and two Shelter branch refs equal their pinned R334 manifest commits (nine exact matches). No changes to other owners' branches.

## OFFER → FUNNEL → BLOCKER → TEST → EVIDENCE → OWNER

| Offer | Funnel step | Blocker / next test | Evidence | Owner |
|---|---|---|---|---|
| One **existing**, FV-owned payable Preparedness digital pack | Actual settled order, delivery and refunds | No authenticated rights-cleared SKU, checkout/fulfillment or refund rules: verify *real existing* merchant listing, seller ownership, receipt and delivery before proposing any paid CTA | **NO VERIFIED SKU / NO SALE** | Founder/Commerce |
| Existing free official-agency Archive | Matching free guide and optional held practical card | Four competing source claims, 15 editorial conflicts, 17 original high-risk claims: claim-by-claim qualified review, private mobile/print/links QA | **HARD HOLD** | Preparedness/QD |
| Genuine already-published family-contact/reunification Grok asset | Social link → existing free `/preparedness/` | Original matching `asset_id`, published date, mobile-permitted link and actual campaign tagging not authenticated | **UNVERIFIED** | Grok creates; Praxxis QA |
| Qualified human session → consented lead → merchant-paid order | Net revenue/1,000 qualified humans, 7/30-day cohorts | No verified sessions, confirmable leads, receipts, fees, refunds, matching campaign attribution | **NOT COMPUTABLE** | Claude analytics / Commerce |

Only potential public destination is the **already existing** free official-resource `https://finalvestige.com/preparedness/`. Original Article #15, Tool #104, Tool #102 and other authored drafts remain private. No retired water offer, speculative product, QD PASS, false conversion, paid vendor, social queue rewrite, WordPress/CMS/nav publish, affiliate/merchant activation, analytics scripts, email, spending or production change. **Founder retains release/commerce approvals.**
