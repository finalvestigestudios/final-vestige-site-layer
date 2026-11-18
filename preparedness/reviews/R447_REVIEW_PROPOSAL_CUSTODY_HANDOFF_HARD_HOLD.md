# R447 — Authenticated original review-proposal custody (DRAFT / HARD HOLD)

**Scope:** Preparedness Integration #136; conversion dependencies #820 / charter #818. No merges, WordPress, navigation, social, email, tracking, commerce, affiliate, spending, or public publishing changes.

## What changed

- This draft stacks on exact R446 HEAD `7ddd51b7fdec7fe2a0cb04ecb059434b669f73cb`; all original 35 article bodies, metadata, original source IDs/URLs, and manuscript variations remain untouched.
- The review template was generated directly from exact original R446 evidence blob `0e655316ced77212abeff77459898253a1e768fd`, itself anchored to authentic R397 docket blob `86d22a1d504c93db7689b914e2202a7845b648e2`.
- Exactly **five** named source-scope disputes, **nine** original manuscript/metadata/fragment forks, and **17** shared-URL review groups get distinct **unselected** review slots. The source IDs remain distinct even when sharing a URL; repeated manuscript blob appearances retain their original identities.
- A read-only validator checks candidate SHA-256 digest against **the entire original source or fork variant object** (including original reading scope/claim text), nine pinned contributor heads, reviewer evidence URLs, non-empty qualified-review narratives, and false approval flags. The results are **proposals, not selections**. URL-ID merging is never automatically authorized.
- The deterministic output includes candidates, unresolved counts, structural error codes and constant `DRAFT_HARD_HOLD`. It does not verify reviewers' identities, source scientific validity, published pages, offers or merchant transactions.

## Exact reviewer queues

**Qualified food reviewer:** `fsis-power-failure` (time/context/temperature boundaries), `nchfp-home` (a hub is not a tested procedure), and `nchfp-jerky` (species/parasites/heating and regulator applicability).

**Qualified historical-source reviewer:** `loc-pioneer-diaries` (catalogue vs first-hand passages) and `loc-prairie-traveler` (page-level scan/OCR reading depth).

**Manuscript and citation reviewers:** `family-communication-plan` body + metadata, `home-fire-escape-plan` body + metadata, `outage-heat-cold-generators` body + metadata, `shelter-or-evacuate` body + metadata, and Shelter fragment JSON. Nine competing original paths remain unselected.

**Citation reviewer:** 17 exact shared URLs need independent source-ID scope and URL-multiplicity assessment; do not merge just because a literal URL repeats.

## Native offline validation instructions

From an authenticated full checkout run:
```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r447_adjudication_proposal_guard.py \
  --packet preparedness/reviews/R446_AUTHENTIC_R397_CONFLICT_REVIEW_QUEUE.json \
  --proposals preparedness/reviews/R447_ORIGINAL_31_CASE_REVIEW_TEMPLATE_HARD_HOLD.json \
  --observed-heads /path/to/independently-observed-current-nine-heads.json
```

The last command deliberately returns exit status **2 on all outcomes**, including structurally correct proposals, and only the first three native commands could establish the site's technical build status. They **cannot** establish medical, water, food, emergency, privacy or editorial safety approval. The full original 35-article build, authentic WordPress/private-preview exports, browser checks and qualified review are **NOT VERIFIED** in this run.

## Conversion-first, one-offer acceptance

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| One existing FV-owned Preparedness digital pack (no new invented SKU) | Actual purchase/fulfillment | Rights, active payable checkout, verified delivery, refunds/fees and settlement not authenticated | Read-only verify product rights, permitted seller checkout and delivery; THEN consider one contextual paid CTA | **HOLD**, no merchant-confirmed sales | Founder/Commerce |
| Existing authentic emergency family-contact Grok clip | Published asset to existing free Preparedness Archive | Real immutable `asset_id`, original post, rights and mobile destination unverified | Praxxis independently check TASK-008; no creator queue changes | **UNMATCHED**, no attributable human sessions | Grok/Praxxis |
| Official family checklist | Free content to optional practical Tool #104 | Article #15 emergency/child privacy, accessible printing and Tool #102/#104 distinction still QD HOLD | Draft-only contextual text link; never gate essential safety information | **HARD HOLD**, no public CTA | Preparedness/QD |
| Verified sessions to paid orders | Qualified `asset_id`/UTM visit → CTA → confirmed lead (where applicable) → merchant-confirmed paid order less fees/refunds | No consented joined attribution or merchant settlement records | Claude maintains existing instrumentation only, define 7/30-day confidence-tagged cohort | **NOT COMPUTABLE** net revenue per 1,000 qualified humans | Claude/Commerce |

**Unpublished free-only CTA candidate:** “Review the official household emergency checklist.” No water-freebie resurrection, invented product, paid upsell, affiliate activation or fake sales claims.

## Release custody

Local synthetic tests may pass while **qualified source and safety review remains unapproved**. This branch and all underlying Preparedness drafts are not publication permission. Founder retains all live and commercial release decisions.
