# R158 — Family Reunification Card claim-scope corrections (DRAFT / HARD HOLD)

Parent: R157 PR #1188 at `7684f5b1141795dc2eb838f0f07978f5d9288168`. Governing Preparedness Issue #136; revenue-coordination Issue #820 and charter #818.

This is a **read-only, source-pinned correction proposal**, not an edit to the 35-article slate, Family Card, metadata, source register, source crosswalk, WordPress, or merchant configuration. The Python CLI does **not** save rewritten content, and exits 2 even for a structurally valid draft. No QD PASS or medical/safety approval is implied.

## Five concrete claim / UX defects in the current draft

1. **Privacy certainty unsupported:** the body says entries are never sent/saved and closing the tab clears them; the metadata says "Nothing is stored" and "local-only." The reviewed inline JS renders via DOM text nodes and prints via window.print(), but full WordPress/browser/third-party-script/network, restoration, extensions and print-service privacy have not been independently tested. Do not promise zero retention.
2. **SMS overgeneralization:** blanket "use text messages rather than calls for everything else" is broader than a source inaccessible to automated retrieval demonstrates; text delivery also is not guaranteed.
3. **Misdescribed no-JS features:** the no-script copy mentions automatic reminders and text download, neither visible in the reviewed interactive controls. The blank printed fallback exists; print quality is untested.
4. **Unverified Ready.gov privacy attribution:** the original cites a form and asserts the government does not store/share typed information. Source retrieval was blocked; do not repeat an unreviewed privacy assurance.
5. **Colorado source-scope mismatch:** the current article attributes photo-ID guidance to the Colorado page. The previously retrieved page did not establish this detail; advise verification with each child's school.

The proposed candidate narrows five text anchors and two metadata phrases only. **Exact original blob identities required:** body `be8698ac5d020476ff649d85813810e2000c6f98`; metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`. Source IDs/order (16 citations, 11 source relationships), HTML elements, JS/CSS and safety/publication states must be conserved; any drift fails closed.

## Validation / release gates

Test command from a trusted checkout: `python -I -m unittest preparedness.tests.test_r158_family_card_candidate -v`; structural proposal: `python -I preparedness/tools/r158_family_card_candidate.py --repo .` (expected exit **2** and DRAFT_HARD_HOLD). Then execute native `validate.py`, `build.py`, 35-article full test suite and independent QA.

In the isolated local prototype, **57 Python tests passed**, including 48 separate mutated-anchor tests plus source-ID rejection, forged review states, link/fixture custody and unchanged HTML+CSS+JS checks. Python compilation passed. GitHub committed blob identities must be compared to tested files. The authentic checkout was not available locally (GitHub DNS failure), so the native validator/build, complete suite and browser testing **were not run**. Do not mistake synthetic results for release clearance.

Review required: 11 Family Card relationships/16 citations (2 disputed source scopes, 6 blocked automated retrievals), plus 64 other source tasks. Independent safety PR #157 and fixture PRs #169/#973 remain separate. Nothing may be automatically approved from this candidate.

## Conversion-first, inactive funnel

One matching audience only: parents/caregivers coordinating school pickup and reunification. Draft social topic (Grok owner) → existing free Household Emergency Plan draft → optional Family Card draft → paid item **NOT AVAILABLE** until commerce independently identifies one rights-cleared, genuinely purchasable FV Preparedness SKU and verifies checkout, delivery, refunds and acceptable claims. Grok/Praxxis TASK-008 has no confirmed Preparedness asset ID or approved live destination in the material reviewed.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Existing paid Preparedness pack | Purchase | No authenticated SKU, rights, fulfillment | Read-only Payhip verification before CTA | HOLD, no merchant evidence | Commerce / Claude |
| Household Emergency Plan | Free reader | Source, safety and QD pending | Qualified review and native build | DRAFT, no clearance | Preparedness / independent QA |
| Family Reunification Card | Optional printable | Privacy overclaims, 11 sources, print/browser unknown | Proposed five-anchor correction plus staged browser/print/privacy QA | 57 synthetic tests; authentic QA NOT VERIFIED | Preparedness / Site QA |
| Grok creator topic | Qualified landing | No verified asset ID and approved destination | Reconcile existing TASK-008; no queue writes | UNVERIFIED | Grok / Praxxis |
| Confirmed order → net revenue | 7/30-day cohort | No qualified-session denominator / paid orders | Merchant evidence, fees, refunds; small-sample caution | N/A, not zero | Commerce / Analytics |

Do not claim email subscribers, clicks or pageviews are paid sales. KPI net realized revenue per 1,000 qualified human sessions remains unavailable. No retired water freebie, speculative checkout, affiliate activation, marketing post, CMS write or spend.

**No publishing or navigation authorization. All 35 instructional articles remain DRAFT / HOLD.**
