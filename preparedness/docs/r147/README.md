# R147 — Preparedness draft-route and citation delivery safety gate

**Scope:** Preparedness Archive only (Issue #136); cross-reference #820, charter #818. Stacked upon R146 draft PR #1109, exact parent 0f09bcf4d6107831b8a84c955714e8ecf15b695f. **DRAFT/HOLD. No merge or public publishing authority.**

## Real evidence discovery: six tools built, not nine

The immutable R146 source tree contains **35 article HTML/metadata pairs**, **six implemented tool HTML/metadata pairs**, **eight named section hubs**, and the landing page. Taxonomy lists NINE possible tool names but only SIX have content/body files. Three are planned, not ready. Expected unique draft destinations: **50** (35+6+8+1). The previously locked article citation baseline is 2,000 article citations, not a tally of tools. Six authentic tool metadata source-use key sets were independently compared to their actual citation tokens with no key-set mismatch; no claim of medical/source approval.

## Scope of this isolated R147 check

Read-only Python verifier:
- Crosswalk the exact 35 article names and six actual tool names to the taxonomy, metadata/body pairings and author-specific source_use keys, while retaining original article citation counts and DRAFT states.
- Fail on duplicate canonical URLs OR duplicate WordPress draft HTML filenames, including collisions against landing/hubs.
- Normalize case, trailing slashes and percent encoding for collision detection only; reject foreign hosts, unsafe encodings, queries, fragments, and traversal. Never rewrite public URLs.
- When native draft build exists: verify build-report article/tool canonicals and counts, eight hubs, all 50 nonempty draft WordPress and preview files, zero published articles and explicit independent-QA/publication HOLD.
- Optionally inspect supplied read-only WordPress URLs, fail on overlap; even a clean user-supplied snapshot is UNVERIFIED pending owner browser/CMS confirmation.

The gate does NOT establish claim safety, source-link validity, browser/cross-device rendering, private input storage, checkout acceptance or real WordPress state. A structural pass always retains publication=false, medical_safety_verified=false, merchant_offer_verified=false and independent_qd=NOT_APPROVED.

## Trusted checkout commands, NEVER production writes

First R146 exact-current-HEAD ancestry/custody and its isolated native runner must pass in a trusted checkout. Then execute:

    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/r147_route_delivery_gate.py --preparedness preparedness
    python -I -m unittest discover -s preparedness/tests -p 'test_r147_route_delivery_gate.py' -v

For a *route-only diagnostic*, use --skip-build; this never asserts the WordPress-ready draft output exists. An optional --wp-inventory path accepts a scoped JSON object of URLs for read-only collision review, NOT an independently certified CMS export.

## Evidence and blockers

**BUILT:** Three additive files in this PR: route/citation/export verifier, synthetic adversarial tests, runbook. No pre-existing article, metadata, source register, taxonomy, URL, QD, safety, homepage, CMS, analytics or merchant state is edited.

**TESTED LOCALLY:** 84 synthetic/adversarial cases and Python compilation on corresponding locally authored code. Tests include 35 independent citation-removal probes, 35 independent draft-to-published forgeries, bad URL aliases, lost draft outputs, corrupted canonicals, forged QD and real route overlap. These are fabricated fixtures; do not treat them as native 35-article validation or claim hosted CI PASS.

**READ FROM AUTHENTIC GITHUB:** immutable R146 taxonomy, article/tool filenames, selected actual meta/source-use relationships; seven Claude contributor branches re-compared exactly to frozen commits (identical, 0 ahead/behind).

**NOT VERIFIED:** real full checkout, all authentic 2,000 article-token R147 checks, native validation/build/regression, external WordPress URL inventory, staged mobile/print/browser behavior, 32 human shared-source groups, qualified medical/food/fire safety/source approval, independent QD, merchant sales.

**Seven unchanged branch pins:** Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Food f911ff7a655de8d81535ea86ec3d65a49ee76648; Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Hist Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Hist Home 7504a5f099594d635e3dd7332a33a2e1346c43a2; Hist Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c. Independent QA #157, fixture #169 and correction #973 remain open isolated draft changes. Eight jerky source-ID retargets, CDC outage citation disappearance, high-rise-fire source loss and medication wording still require specialist review. Homepage #49/#604 belong to others and are unchanged.

## ONE conversion-first, safety-gated journey

Parents/caregivers preparing school pickup and family reunification → free *Household Emergency Plan* (authentic article but safety/source/QD DRAFT/HOLD) → optional free existing *Family Reunification Card* (authentic draft, mobile/privacy/print NOT TESTED) → optional paid Preparedness practical pack ONLY if Growth verifies a specifically purchasable FV-owned SKU, rights, checkout, download and refunds. No verified matching SKU currently; **do not add a paid CTA, price or fictional product**. Emergency safety guidance must not be email gated; do not reinstate retired water freebies.

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing FV-owned paid Preparedness offer → purchase | Matching SKU/rights/price/fulfillment/refunds not authenticated | Read-only merchant audit before any CTA | HOLD | Growth / Claude |
| Free household plan → reader | Qualified source/safety/QD review and native build pending | Exact R133–R147 native and staged source/citation QA | DRAFT | Preparedness / QA |
| Reader → family contact printable | Local-data privacy, mobile, keyboard and printing unverified | 360/390px and offline print/download test | NOT TESTED | Site QA |
| Grok video asset → approved guide route | TASK-008 has no verified Preparedness asset_id/live permalink/UTM placement | Grok/Praxxis reconcile with existing inventory, no queue changes | UNVERIFIED | Grok / Praxxis |
| Human sessions → confirmed order → net revenue | Missing sessions, merchant-paid order, fees/refunds | 7/30-day consent-safe ledger under #820; no duplicate tracking | NOT COMPUTABLE | Growth / Analytics |

**Draft-only CTA (not for publishing):** “Make a family contact and school-pickup plan. Read the free Household Emergency Plan, then optionally print a Family Reunification Card and keep the details privately.”

Acceptance requires a real published Grok asset_id/allowed destination, qualifying sessions, relevant CTA, verified lead only when observable, merchant-confirmed paid orders separate from clicks, net of fees/refunds and tiny-sample 7/30-day cohorts. **Net revenue per 1,000 qualified-human sessions is not computable.**

All 35 instructional articles remain DRAFT/HOLD. No WordPress/CMS, navigation, homepage, analytics, merchant, affiliate, email, social post or spending action.