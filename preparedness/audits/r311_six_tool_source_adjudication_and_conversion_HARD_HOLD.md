# R311 — authentic six-tool citation-to-source crosswalk (read-only HARD HOLD)

Date: 2026-11-12. Scope: Issues #136 and #820. Source commit `b6dafd5c49cfeb74770b03ff211733e4dd1a45cc`; parent draft PR #2159. **This is source-custody and identifier consistency, not claim-level medical, safety, privacy or QD approval.**

The pinned six-tool snapshot contains **67 metadata source-use claims mapping to 58 distinct citation IDs**. All 6 tool body citation ID sets agree with corresponding metadata entries in the inspected Git revision. Across the five pinned source register/fragment JSON files, every cited ID has at least one recorded fetched source. **This proves source-record presence, not factual support or live URL status.**

## Hard-hold finding: verified source identity collision

`fsis-power-failure` is fetched-verified in BOTH `sources/fragments/food.json` (verified_on 2026-10-29) and `sources/fragments/shelter.json` (verified_on 2026-11-01). The URLs match, but the `supports` evidence wording and explanatory notes differ. Its older top-level register entry is an unverified placeholder. This citation is used by `power-outage-planner`. Do not automatically choose the newer or shorter record, deduplicate, or represent source parity as release authorization. Require source-editor adjudication and a native `build.Library`/validation result.

## Additional holds

- Number 102 labels BOTH `home-fire-escape-worksheet` and `reunification-plan`; number 103 labels BOTH `kit-builder` and `power-outage-planner`. Slugs remain distinct; no renumbering/alias/public route changes approved.
- 58 distinct cited IDs lack a human-click verification witness in the source records inspected. Recorded machine fetch is not independent review.
- Tool #104 emergency-messaging/child privacy/no-JavaScript and Article #7 hazards remain independently held. QA PRs #157 and #169 are draft; PR #169 still contains a separate source-directory fixture write in `test_register_fragments_cannot_duplicate_ids`.
- No authenticated native 41-draft WordPress build, no independent QD PASS, no paid Preparedness SKU approval, no matching published Grok family-contact asset ID, and no verified net revenue proof.

## Conversion-first acceptance (no public action)

| Offer | Funnel step | Blocker | Change / experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| Existing free family-contact guide | Social → free official references | No verified published asset ID/mobile destination | Match Grok TASK-008 ID to an authentic free guide; check mobile link | NOT VERIFIED; no CTA deployment | Grok/Praxxis |
| Free guide + free Tool #104 | Guide → optional printable | Emergency claims, child privacy, JS-disabled and print review | Independent source/privacy/browser review | HARD HOLD | Preparedness/QD |
| Existing eligible FV-owned Preparedness SKU only | Free guide → optional paid pack | No verified currently purchasable, rights-cleared, deliverable fit | Founder/Commerce verify actual SKU, license, checkout, refund, delivery | NO APPROVED SKU | Founder/Commerce |
| Confirmed paid purchase | Qualified session → verified net revenue | Orders, attribution, fees, refunds missing | Read-only merchant/analytics reconciliation, 7/30 day cohorts | NOT COMPUTABLE | Claude/Commerce |

No public, CMS, navigation, paid-offer, social, email or analytics changes in this evidence operation. Machine-readable manifest: `preparedness/audits/r311_authentic_six_tool_citation_source_crosswalk_HARD_HOLD.json`.
