# Apollo 1 Evidence Atlas — R234 navigational/touch repair (staging only)

**Release status:** built and locally tested, **NOT LIVE**. Based on R233 draft PR #1713 (`93324d10f8d6831fa2b9616b2845705675736284`) and the SHA-256-pinned R228 generated Atlas manifest `28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413`. This standalone repair does not alter PR #49, #158, main, the Research Desk, the founder's publisher settings, or any live page. No new sources, photos, map edges, commerce, data collection or services.

## Defect and fix

R228 repaired 14 trace-specific links, but independent browser inspection found additional undersized **standalone** actions in the main navigation, four chronology route controls, expanded evidence cards and the footer return route. At 320px, 14 of 27 selected navigational actions were below 44px tall; at 390px 18/27 were below 44px; at 768px 19/27; at 1440px and 1920px 20/27. Some in-text NASA citations (which are subject to inline-link spacing exceptions under WCAG 2.2) are deliberately untouched. R234 adds only a scoped, no-JS CSS patch: min-height 44px, readable focus indicator, forced-colors focus and normal responsive wrapping. No click overlay or geometry fake.

**Browser result:** 0/27 below 44px in six tested widths (320, 390, 768, 1440, 1920, and 256px reflow proxy). 256px is **not** real browser 400% zoom. No x overflow; native Enter and mobile touch interaction preserved. No code was inserted into the historical narrative.

## Reproduce

Use the previously pinned generated R228 artifact directory. From this repository:

```sh
python experience2/apollo-r234/qa/r234_targets.py \
  --dist /path/to/verified/generated-r228 \
  --patch experience2/apollo-r234/assets/r234-action-targets.css \
  --out /tmp/apollo-r234-generated \
  --qa /tmp/apollo-r234-QA-A
php -l /tmp/apollo-r234-generated/fv-ex2-apollo-r224.php
php experience2/apollo-r234/qa/r234_php_pin.php /tmp/apollo-r234-generated
```

The builder verifies every parent manifest file hash, makes a new isolated output copy, appends the CSS, updates both the PHP adapter's CSS hash and cache token, rehashes the new manifest, and checks actual Chromium rendered actions (Playwright, no external requests). Run twice in separate dirs; `receipt.json` and screenshots should reproduce byte-for-byte. For independent QA, verify the exact GitHub file blobs match the executables before accepting the receipt.

## Commercial gate

Visitor pathway: a **verified, actually published** Grok Apollo long-form/Shorts asset → the free Evidence Atlas → source-proven NASA records and chronology → exactly **one** original Apollo investigation CTA → optional educator dossier **only if** separately rights-cleared, buyer-validated, check-outable and founder-approved. Grok owns creation/distribution, Praxxis reviews creators, Claude owns production analytics and checkout engineering. No asset ID has been authenticated here. No educator dossier SKU, checkout or paid order is asserted. Tracking remains the existing #820 standard UTM convention and native event plan, without duplicating scripts. Record qualified-human sessions → CTA clicks → consented leads if observable → independently confirmed merchant orders/refunds/fees → net revenue per 1,000 qualified sessions (7/30 days); this is currently **not computable**.

| Offer | Funnel step | Blocker | Change | Evidence | Owner |
|---|---|---|---|---|---|
| Educator dossier (hypothetical) | Paid checkout | No verified SKU/rights/fulfillment | Validate existing offers and classroom buyer demand before enabling | COMMERCIAL HOLD | Founder / Claude |
| Grok Apollo asset (unverified) | Social → Atlas | No authenticated published URL/asset ID | Reconcile TASK-008 in existing Drive, without queue edits | UNVERIFIED | Grok / Praxxis |
| Free original Apollo investigation | Atlas navigation → investigation | Additional standalone targets <44px | R234 scoped CSS repair | LOCAL PASS, 27/27 action targets | Apollo |
| Actual paid orders | 7/30 day net realized revenue | No authenticated session/merchant reconciliation | Maintain read-only source-of-truth joins | NOT COMPUTABLE | Commerce / Analytics |

## Unresolved release gates

Inherited R198 canonical-source ancestry discrepancy, installed WordPress/Assembler acceptance, axe-core, actual browser UI zoom, screen reader, independent site QA, hosted exact-head CI, rights/endorsement approval, social asset and sellable SKU verification, founder production authorization. **Do not merge, install, deploy, send, publish, spend or activate any commerce.** This tests the complete generated Atlas fixture in local Chromium, not WordPress or field LCP/CLS.
