# R442 — Original claim-to-source-variant binding custody (DRAFT / HARD HOLD)

**Ownership:** Preparedness Archive integration + source/citation safety gates, Issue #136. Business coordination only in #820, source-of-truth charter #818. **No release authority.**

## Defect class addressed
An article can preserve its citation count and each valid source ID while reassigning a source to a materially different paragraph, changing claim order, replacing the original URL/source Git object, removing source-reading scope, or placing a marker in script/attribute text rather than readable copy. An article-level ID count is insufficient evidence that the right source substantiates the right visible claim.

The read-only R442 gate binds each citation occurrence to (article slug, immutable body Git blob, visible block index, citation occurrence ordinal, SHA-256 of normalized block copy, exact original source ID, one exact original contributor/source-blob/URL triple, and an explicit reading-scope note). The independent frozen annotation file is a prerequisite, **not** created or approved by the gate. A variant match means custody only; it does not certify support, trustworthiness, emergency accuracy or current validity.

## Hard gates and limitations
- Exactly 35 original article identities and 203 source IDs; preserve five unresolved source disputes, nine forks and 17 shared-URL review groups.
- Detect mismatch of authentic body bytes, citation block/context, source occurrence, variant provenance, reading scope, HTML-hidden citation markers and accidental review-state promotion.
- A structural clean fixture is **not QD PASS**. Outputs always set eligible, publication_approved, qd_pass and merchant_offer_verified to false, and command-line invocation returns code 2.
- Real R397 35 article bytes, independently approved frozen citation annotations, native validate/build, 70 authenticated WordPress/private-preview export files, no-JS/print/mobile acceptance, and qualified emergency/food/medical/privacy reviews were **not available/executed** in this run. Do not substitute test fixture results.
- The HTML text parser is intentionally strict: complicated nested layouts or legitimate WordPress template content may trigger a conservative review hold. It does not constitute a browser accessibility audit.

## Locally executed evidence
- Exact locally executed new Python source and test bytes read back from GitHub by Git blob SHA: source 8817354b8d9762a6218408e5ac47ee18dc9e117e; tests e05337107cbbce86a97687d99adb2e3d780afb12.
- Python compilation PASS, R442 new tests **73/73 PASS**, local cumulative R430–R442 equivalent test suite **841/841 PASS**. R441 inherited modules derive from previously supplied local equivalent bundle, with the same previously disclosed provenance limitation.
- Repository-hosted CI and native release pipeline remain **NOT VERIFIED**, and **no CI PASS** is claimed.

## Read-only invocation contract
\`python preparedness/tools/r442_claim_source_binding_gate.py --docket PATH_TO_AUTHENTIC_R397_DOCKET.json --repo-root PATH_TO_AUTHENTIC_FROZEN_CHECKOUT --frozen-citation-baseline PATH_TO_INDEPENDENT_REVIEWER_CITATION_INDEX.json\`

The baseline format has schema=1, release_state=DRAFT_HARD_HOLD, articles keyed by original slug, a body_git_blob for each, and ordered citations with source_id, block_index, occurrence, context_sha256, source_variant {branch, source_blob, url}, reading_scope_exact and review_state=HUMAN_REVIEW_REQUIRED. **Absent independent baseline = hard hold**, not authority to self-generate acceptance. This gate augments rather than replaces R440/R441 provenance, export parity gates, and human QD review.

## Conversion-first acceptance, no implementation outside lane
| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Authenticated existing FV Preparedness pack | Optional paid purchase after free guide | No authenticated payable rights-cleared SKU, delivery, refunds | Commerce owner independently authenticates a single actual pack; no speculative checkout URL | HOLD / no merchant records | Founder/Commerce |
| Verified family-contact Grok asset | Published asset → free official Archive resource | Exact immutable asset_id, post/hook/rights/mobile route unmatched | Research-only matching via TASK-008; no posting or creator task reassignment | UNMATCHED | Grok/Praxxis |
| Free official checklist + optional clearly labeled practical printable | Page CTA/download | Tool #102/#104 identity, Article #15 accuracy, child privacy, print QA | Qualified review and accessible preview, no protected info capture | HARD HOLD | Preparedness/QD |
| Qualified human sessions → verified paid orders | Attribution and net revenue/1000 sessions | No merchant-confirmed paid conversions, fees/refunds or 7/30-day cohorts | Read-only reconciliation by Claude/Commerce with consent and no duplicate script | NOT COMPUTABLE | Claude/Commerce |

Draft free CTA only: "Review the official household emergency checklist." Keep core safety resources free. No paid CTA or offer activated. The legacy retired water funnel remains retired.

**No branch merge, production write, CMS/navigation/social/email/analytics edit, affiliate activation, expense, source adjudication or live release.**
