# R173 — Claim-local citation checks and human safety docket

**Scope:** Issue #136 only. Coordination with #820 and charter #818. Stacked strictly on R172 PR #1283 head \`54b2c5fbc170d10b1e4906df02eff587aaadef97\`. This is a **DRAFT / HARD HOLD** review packet, not merge, WordPress, QD or food-safety authority.

## Actual finding and what's new

The three R172-identified jerky-related drafts contain claims that require **source-specific, block-local checks**: \`safe-jerky-dehydration\`, \`pemmican-and-dried-meats\`, and \`pioneer-travel-rations\`.

Original HTML and metadata for these three drafts were independently read through authenticated GitHub at the pinned R172 head on **2026-11-06**. The ten selected claim anchors, citations, and metadata relationships were checked against those actual files in a read-only JavaScript preflight: **10/10 source-locality matches after stripping inline markup**. One bare-string test initially failed because the word **After** was enclosed in a \`<strong>\` tag; normalizing inline HTML found the correct same-cell citation pair. **This is not a complete native Python execution on authentic files.**

The current NCHFP guidance describes more than one processing order; the USDA FSIS Hotline page explicitly recommends a sequence **before** dehydration; FSIS also discusses resistance after drying. Do not collapse them into a single source or declare either technique independently safe for publication. The disputed trailing-slash NCHFP source still requires qualified review, as do hazard- and article-specific sentences.

Authoritative primary source observations, inspected 2026-11-06:
- NCHFP/UGA, *Jerky* (2014 source): https://nchfp.uga.edu/how/dry/recipes/jerky
- USDA FSIS, *How can I make meat or poultry jerky at home?* (last updated **2025-02-04**): https://ask.fsis.usda.gov/article/How-do-I-dry-jerky
- USDA FSIS, *Why is temperature important when making jerky?* (last updated **2024-11-18**): https://ask.fsis.usda.gov/article/Why-is-temperature-important-when-making-jerky

## Added components

1. \`preparedness/tools/r173_claim_scope_gate.py\` checks **ten** claim anchors within their original HTML \`p/li/th/td\` blocks, insists that the cited source IDs occur in that same block *and* in original per-article \`source_use\`, protects the historical "not a recipe" warning and the explicit official-source disagreement, and writes a deterministic SHA-256 claim-evidence receipt. It pins all **three HTML and metadata Git blobs** and this round's human docket. It invokes R172, which itself invokes R161's original **35-body / 2,000-citation / 385-source-edge** custody check. No original content, metadata, register, route or source crosswalk is modified.
2. \`preparedness/review/r173/claim-scope-human-docket.json\` holds **ten pending human review records**: article/claim/source IDs, unresolved scope, independent food-safety and QD fields. It retains the literal NCHFP variants and prior count baselines. A populated reviewer or a supposed "approved" state is rejected; a legitimate eventual review needs a new explicit audited gate/version.
3. \`preparedness/tests/test_r173_claim_scope_gate.py\` provides **97 unittest cases, 95 passed / 2 skipped**, including missing or adjacent-only citations, removed claim anchors, duplicate paragraphs, invalid metadata, altered safety states, forged reviewers, substituted sources and bogus paid sales.

**Development verification:** \`python -I -m unittest discover -s /mnt/data/r173/preparedness/tests -p 'test_r173*' -q\` → **97 tests run: 95 pass, 2 skipped** (synthetic); Python compilation PASS; committed Python Git blob SHAs match locally tested files. The two skips correspond to mutation tests that require a cited source for the explicitly uncited, non-instructional "not a recipe" warning.

**Run when a trusted full checkout is available:**
\`\`\`sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r173_claim_scope_gate.py --repo .
\`\`\`
The R173 gate deliberately exits **2 even when the structural checks succeed**, because neither synthetic tests nor cited sources establish expert safety/QD approval. Invalid/missing repository inputs give \`INVALID_HARD_HOLD\`.

## Scope of the HOLD

- All 35 original articles retain their original draft/release status. Ten claim-local tests are **not** a substitute for the 75 earlier source decisions, 32 shared-URL reading scopes, qualified food-safety adjudication, or R157 independent safety fixes.
- Full native 35-article validation/build, full authentic tests, real WordPress/browser/print privacy, and independent QD **NOT RUN**. This runtime still cannot resolve GitHub for cloning (\`git ls-remote\` DNS failure). R157, R169, R973 and homepage PRs #49/#604 are separate/unmodified.
- The seven contributor branches were checked against exact checkpoint SHAs on Nov 6; all identical with **0 ahead / 0 behind**. Start \`2122d856\`, Food \`f911ff7a\`, Shelter \`5daeaf2d\`, Health \`d5ef5baf\`, Historical Field \`4e5caf81\`, Historical Food \`67e116e5\`, Historical Home \`7504a5f0\`.
- No CMS, navigation, WordPress, analytics, merchant, social, email, purchase, tracking or spending changes.

## Conversion-first decision and friction map — DRAFT ONLY

**One audience/topic:** Parents/caregivers searching for emergency school pickup and reunification arrangements. **Authentic existing free guide:** *Household Emergency Plan*, still **unpublished** and intended to remain **ungated**. **Optional free practical tool:** Family Reunification Card, quarantined with source, print and privacy HOLD. **Existing paid offer:** no verified, rights-cleared, genuinely purchasable Preparedness SKU; do **not** create an invented paid pack or purchase CTA.

| Offer → Funnel | Blocker | Change / experiment | Acceptance evidence | Owner |
|---|---|---|---|---|
| Existing owned Preparedness product → paid transaction | No authenticated matched SKU/rights/checkout/delivery/refund evidence | Commerce inventory and sandbox purchase/fulfillment/refund proof, then decide whether the product actually fits | **HOLD; no paid CTA** | Commerce / Claude |
| Household Plan → reader | Qualified source/safety/QD + native build pending | Independent claims audit and original 35-article validation | **Draft only, not live** | Preparedness / Site QA |
| Free guide → optional Family Card | Eleven source decisions, privacy/print/a11y checks outstanding | Staged 360/390/768/1440 tests and qualified review | **HOLD**, no download offered yet | Preparedness / Site QA |
| Grok social asset → guide | Verified Preparedness \`asset_id\`, published post URL and destination not supplied in TASK-008 | Coordinate read-only; Grok retains production and publishing | **UNVERIFIED**, no UTMs invented | Grok / Praxxis |
| Confirmed orders → net revenue | Missing qualified-human sessions and independently confirmed paid orders/fees/refunds | 7/30-day merchant reconciliation, consent-appropriate attribution | **NOT COMPUTABLE** | Commerce / Analytics |

**Draft future CTA copy (not published):** "Plan how your household will reconnect after an emergency. Read the free Household Emergency Plan." Optional card CTA only after source, accessibility and privacy/printing approval: "Use the free printable Family Reunification Card." No checkout prompt until one real existing Prepareness offer passes commerce acceptance. Any verified purchase must be separate from clicks, email registrations and affiliate outbound.

**Landing acceptance checks:** Social asset topic must match the free guide, canonical target path must be reviewed and live only after approval, no gate on safety instructions, semantic accessible CTA/link labels, responsive display and printable output, clear optionality and no false scarcity, native privacy-safe UTM handling without duplicate scripts, confirmed signup only via the existing \`/focus/\` flow where appropriate, and real merchant-confirmed purchases net of non-double-counted fees/refunds. Key KPI \`1000 × verified realized net revenue / qualified human sessions\` is presently **not computable**.

All release and product decisions remain with their established owners.
