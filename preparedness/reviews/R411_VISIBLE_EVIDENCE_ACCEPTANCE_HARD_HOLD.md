# R411: visible citation / reading-depth custody — DRAFT / HARD HOLD

Scope: **Preparedness Archive Issue #136 only**, with commercial cross-reference #820 and charter #818. Stacked on R410 draft PR #2726 HEAD `1ab0eba84d891480d76b3e347c9d4b4e6e3e78c6`. No merge, WordPress/CMS/navigation write, publication, tracking, social assignment, email, affiliate/product activation or spend.

## Concrete adversarial finding
Four **synthetic** paired 35-article export cases were structurally accepted by R410: (1) an entire article enclosed in `<div hidden>`, (2) an article inside `<template>`, (3) a bidirectional override inside the reader copy, and (4) misnested closing HTML. R410 still returned DRAFT/HARD HOLD in every case; no live content was tested or exposed.

R411 introduces a read-only overlay atop the original R409/R410 source graph and exact-URL parity: 50+ reader-visible words, visible headings/source links, strict nested HTML closure, rejection of concealed/inert/template/noscript/closed-details content and Unicode bidirectional/zero-width controls, and paired visible citation/order/text parity. Original R410 URL, source-ID, article coverage, manifest and Git pin checks remain mandatory.

**Local verification:** R411 new synthetic 89/89; inherited R409+R410 143/143; combined 232/232 Python PASS. Python `compileall` PASS. These are exact-code **local** tests, not CI, genuine manuscript, baseline reading-depth, computed-CSS/browser, WordPress preview or safety review evidence. CLI returns code 2/HARD HOLD on missing authentic input even if structural checks could otherwise pass.

## Source preservation and independent QA
- Original pinned inventory: **35 articles**, **203 source IDs**, **280 occurrences**, **17 distinct-ID shared exact-URL groups**, five unresolved source-scope disputes, nine unselected Shelter manuscript forks.
- Current branch comparisons: seven Claude and two Shelter successors were identical (0 ahead/behind) to original R397 pins on 2026-11-16.
- Independent QA #157 (source-language/safety-approval revisions) and synthetic-fixture #169 were inspected and remain separate open drafts. Dependent fixture fix #2205 is open/unmerged. Protected homepage #1689 remains open/draft.
- Editorial E403 consolidated Article #11 candidate reported in Issue #136; authentic private E395–E403 manuscript/printable bytes have not been independently received here. No version selection or food-safety approval.
- Authenticated full repository checkout unavailable locally (GitHub DNS resolution failure). Therefore native `validate.py`, `build.py`, full 35-article exports and signed-out browser checks are **NOT RUN**. Hosted CI status must be checked separately; local test PASS does not predict it.

## Conversion-first acceptance / owners
| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (unpublished) | PASS / FAIL evidence | OWNER |
| --- | --- | --- | --- | --- | --- |
| ONE existing FV-owned/licensed Preparedness digital pack | verified payable checkout → usable fulfillment | no authenticated rights-cleared deliverable current SKU or merchant settlement/refund proof | founder/commerce privately verify genuine listing, purchase route, delivery, rights, fees and refunds before any paid CTA | HOLD; no accepted SKU or verified order | Founder/Commerce |
| Household family-contact/reunification source-led free guide | already-published Grok social asset → free Archive landing | no independently authenticated matching `asset_id`, hook, rights or mobile link | Grok/Praxxis review existing TASK-008 assets; if matched, test signed-out 360/390px landing and approved UTM (without changing creator queue) | UNVERIFIED; source-led Archive URL is candidate only | Grok/Praxxis |
| Existing free Archive → optional Tool #104 | relevant free guide → voluntary resource | child privacy, emergency guidance and print accessibility not independently approved | draft only: “Start With Trusted Preparedness Resources” → existing `https://finalvestige.com/preparedness/`; do not promote Tool #104 until qualified review | HARD HOLD | Preparedness/QD |
| Qualified humans → CTA → confirmed lead → merchant-confirmed purchase → net revenue | 7/30-day attributable funnel | verified session denominator, merchant orders, fees/refunds and consented attribution unavailable | apply native, privacy-preserving measurement only after Claude/founder approvals; distinguish outbound clicks from sales | NOT COMPUTABLE: net revenue / 1,000 qualified sessions | Claude/Commerce |

Do not resurrect retired water freebies, ship speculative products, claim citations prove procedures medically safe, auto-select source conflicts, or treat test-fixture integrity as QD PASS. This PR is solely a guarded integration reviewer artifact.
