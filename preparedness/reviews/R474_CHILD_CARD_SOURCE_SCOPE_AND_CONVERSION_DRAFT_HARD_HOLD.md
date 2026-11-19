# R474 — Child-card context and source-depth custody

**2026-11-18 PT | Issue #136, commerce #820/#818 | DRAFT / HARD HOLD | reviewer evidence only.** No public or CMS edits.

## New integration conflict, NOT a medical or privacy approval
Original Article #15 and Tool #104 are both still `draft` and `safety_review.pending`. Their four original Git blob pins are recorded in `r474_child_card_scope_manifest.json`; the original Tool #104 says not to put a child's full name or diagnosis on **a printed card**. The original Article #15 says that its separate caution is its own editorial judgment, not agency advice.

Independent editorial E466, [review PR #2789](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2789), exact memo blob `c83330dbc53625be81e30c681aa6df35308ab52e`, identifies a **purpose/custodian distinction**: a minimal adult public-carry wallet card is not a school-managed child backpack emergency-information card. A categorical rule for one should not silently be represented as CDC guidance for the other. No new child-sensitive fields, local-data security certification, medical instructions, or school-pickup authorization have been implemented.

## Source/version crosswalk — not registered as original article citations
- [CDC children: keeping safe](https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html), 2025-12-16, reviewer reports full page read, not yet registered in original article source-use.
- [CDC before/during/after an emergency](https://www.cdc.gov/children-and-school-preparedness/before-during-after/index.html), 2025-12-24, reviewer reports full page read, not yet registered.
- [CDC Backpack Emergency Card](https://stacks.cdc.gov/view/cdc/139829), 2020, **catalog record only**; do not claim the linked PDF was read.
- FEMA's PDF cited in the independent memo is originally July 2017; a `2025-06` URL directory is not a publication-date witness; second page unverified.

Retain the original `shelter-cdc-reunification`, `shelter-ready-plan-form`, and state-specific `shelter-co-oss-reunification` citations and their original limited reading scopes. These are not interchangeable with later CDC guidance. Source registration, specific text changes, privacy advice, child consent/access, and school pickup procedures require qualified human review.

## Engineering and release boundary
Additive only: R474 strict manifest, four original Git-blob pins, provenance date/source crosswalk, eight separate unadjudicated decisions, fail-closed Python gate and 134 isolated regression tests (118 adversarial mutation cases). Code/test/manifest blobs must match the actually run local files. The native gate returns exit 2 on missing authenticated originals **and even on successful structural examination**: there is no QD PASS path. Native 35-article `validate.py`/`build.py`, actual WordPress/private-export parity, production JS privacy/security, mobile/print/assistive-technology tests and qualified review remain NOT EXECUTED / NOT APPROVED.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER
1. Existing genuinely payable FV-owned Preparedness pack → confirmed checkout → no authenticated rights-cleared SKU/delivery/refunds/settlement → privately verify merchant/fulfillment before drafting any paid CTA → **HOLD**, zero verified paid orders → Founder/Commerce.
2. Already-posted Grok family-contact asset → free existing [Preparedness Archive](https://finalvestige.com/preparedness/) → no authenticated intent-matched asset ID/hook/rights/mobile link → Praxxis verify an actual published post before any UTM → **UNMATCHED** → Grok/Praxxis.
3. Original Article #15 → optional **free** Tool #104 → unadjudicated CDC child-backpack vs adult-wallet purpose and child privacy → qualified review of source scopes, accessible printable and local-only claims, school authority → **HARD HOLD**, original drafts unchanged → Preparedness/QD.
4. Qualified human sessions → verified paid order → realized net revenue per 1,000 sessions → no merchant-confirmed orders, attribution, fees/refunds or 7/30-day cohort → no false conversion inference or duplicate tracker → **NOT COMPUTABLE** → Claude/Commerce.

Potential private CTA draft: **“Make a family contact plan using verified emergency resources”** → current free Archive landing only after actual media match. Never advertise held Tool #104 as public or present a future pack as purchasable. No retired water freebie, production release, WordPress/nav writes, Grok queue edit, paid activation or email.
