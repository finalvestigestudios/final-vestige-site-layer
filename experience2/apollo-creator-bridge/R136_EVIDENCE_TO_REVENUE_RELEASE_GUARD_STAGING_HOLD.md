# Apollo Experience 2.0 — R136 evidence → conversion contract
**STAGING HOLD. No homepage changes, no WordPress writes, no paid activation, no posted social content, no merchant proof.**
Governing work: [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [Revenue Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## One high-intent journey, not an attention loop
Audience: grades 6–9 teachers and homeschool instructors considering classroom-ready primary-source materials.

1. **Grok YouTube long-form or Short** (asset link, immutable ID, rights and actual public URL still to be supplied/verified by Grok and independently reviewed by Praxxis). No Grok video claimed live.
2. **Apollo 1: Fourteen Seconds, More Than One Failure** isolated source-backed editorial landing: technical chronology derives from the NASA Apollo 204 Review Board, with six NASA photographs used **only as outbound visual-context sources**, never as telemetry or commercial media. The 2017 exhibits are retrospective; the portrait's proposed S67-19766 association and January day remain unconfirmed.
3. **One nonintrusive, already implemented next action:** `href="#classroom-preview"` → free source-analysis worksheet. Works without JavaScript; no signup, no purchase, no gated information.
4. **Prospective paid teacher casefile** would package *original* differentiated lesson materials, answer key, rubric, and a provenance/rights register. **No matching Payhip listing, fulfillment test, license, rights signoff, institutional approval, or merchant settlement has been independently demonstrated.** Do not add an offer link.
5. **Actual conversion measurement**, once approved by Claude and founder: qualified-human campaign sessions by Grok asset `utm_content`, correct landing, CTA clicks, separately confirmed leads, independently verified paid orders, refunds/fees and realized net revenue. Never mistake referral clicks or unconfirmed checkouts for purchases. 7- and 30-day cohorts, small sample flags, and `net revenue / 1,000 qualified-human sessions` ONLY with validated denominator and settled merchant receipts.

## New exact-source implementation
- `r136_conversion_evidence_gate.cjs` — pure conservative conversion-integrity gate. Explicitly distinguishes source audits, supplied campaign/merchant *candidates*, independent external proof, revenue reconciliation and founder release. Outputs no visitor identifiers or submitted order details.
- `r136_run_evidence_receipt.cjs` — deterministic native-Node CLI, reading **actual** `landing-preview.html`, `r130_nasa_media_custody.json`, `r132_research_desk_source_role_review.html`; invokes existing route/media/Research Desk audits and records SHA-256 inputs and staging-only evidence receipt. Does not contact any domain.
- `r127_source_role_crosswalk.cjs` — integrates a closed conversion gate with the independent PR #158 original-source review. Unresolved Research Desk editorial flags disqualify any spurious source-ready assertion.
- `test_r136_conversion_evidence_gate.cjs` — fifteen adversarial regression cases; `test_r136_run_evidence_receipt.cjs` — four complete-checkout integration tests.

Reproduce in a **complete local checkout**, using already-installed Node; do not spend GitHub Actions budget:
```sh
node --test experience2/apollo-creator-bridge/test_r136_conversion_evidence_gate.cjs
node --test experience2/apollo-creator-bridge/test_r136_run_evidence_receipt.cjs
node experience2/apollo-creator-bridge/r136_run_evidence_receipt.cjs --out /tmp/apollo-r136-a
node experience2/apollo-creator-bridge/r136_run_evidence_receipt.cjs --out /tmp/apollo-r136-b
sha256sum /tmp/apollo-r136-{a,b}/r136-evidence-to-offer-receipt.json
node --test experience2/apollo-creator-bridge/test_r135_artifact_and_acceptance.cjs
node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r136-browser
```
Browser command needs a navigation-permitting Linux/Chromium environment plus locally installed Playwright and axe-core; it MUST NOT substitute `page.setContent` for real navigation. Both actual Research Desk and the full Apollo landing will need independent 320–1920 viewport QA before WordPress integration. Current environment returns `ERR_BLOCKED_BY_ADMINISTRATOR` for HTTP, file and data navigations. No Playwright/axe/LCP/CLS screenshot pass is claimed.

## Prioritized OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
| Priority | Offer → funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Proposed Apollo educator kit → paid order | **NO verified active SKU, checkout, fulfillment, rights signoff, refunds or buyer intent** | Claude/Growth audits actual merchant listing; founder approves any terms; independently test checkout and delivery without live payment until authorized | **COMMERCIAL HOLD; no paid CTA** | Claude / founder |
| P1 | Grok video → Apollo evidence → free worksheet | Need actual asset ID/permalink and real browser acceptance | Keep one linked worksheet action; R136 route/rights/offer gate and existing R134/135 viewport/axe runner | **BUILT source gate; 15/15 V8 regression checks; native/browser pending** | Apollo; Grok asset inventory; Praxxis independent review |
| P2 | Worksheet → future paid resource | No audience demand or approved matching offer | Interview 5 educator/institution buyers with founder-approved outreach; prototype only after rights/source signoff | **HYPOTHESIS, not traffic or orders** | Growth / founder |
| P3 | Paid orders → net per 1,000 qualified humans | No verified campaign-bound merchant order/fee/refund reconciliation | Use existing approved analytics only, consent and Issue #820 schema; independent paid conversion proof | **NOT COMPUTABLE** | Claude/Analytics |

## QA, rights and release hold
Source custody is not image licensing. Public NASA image-detail links do not authorize NASA branding/endorsement, unrestricted promotional reuse or identifiable-person publicity. Six photo-specific commercial reviews remain open (0/6 cleared). The primary Review Board source is https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; media rules https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

**Not completed:** full native Node suite in full checkout; real full-page Playwright/axe; human reviewed screenshots at 320/360/390/768/1440/1920; genuine LCP/CLS; WordPress/Assembler shortcode verification; photograph reuse permissions; independently reconciled merchant/asset proofs; founder production authorization. No source or CI gate may be treated as proof of live traffic or revenue.

**Ownership:** Grok owns videos/creative/distribution; Praxxis owns creator research/QA; Claude owns website production/analytics and homepage; Apollo owner only isolated source experience; founder retains release/spending/posting approval. Frozen homepage PR #49 and Research Desk PR #158 remain untouched.
