# R348 — actual citation occurrence ↔ authored claim-region crosswalk

**2026-11-13 PT · Issue #136 · DRAFT / HARD HOLD · Unmerged / unapproved.**

## Why this matters

R345 identified 12 **metadata declarations** for four disputed source IDs across ten manuscripts; a metadata declaration is not itself an in-body citation. R348 identifies each literal **in-body citation occurrence**, its ordinal, semantic region tag, full-region SHA-256 and redacted per-occurrence SHA-256. Claim text is never returned. Distinct mentions of the same source in the same paragraph remain distinct review obligations. It rejects citation tokens in attributes, comments, scripts, malformed/partial tokens, missing declared source IDs, missing/extra body–metadata pairs, symlinks, and changed original draft/safety states.

The synthetic test suite explicitly recognizes an original **ungated historical** "not-required" safety-review state *only* on \`track=lost-ways\` articles. That state is not QD approval. Other original private advice stays pending.

## Independent original-Git readback at R347 SHA

**Source:** GitHub \`finalvestigestudios/final-vestige-site-layer\` at exact parent \`88da4cc5eeece4e6fdcbdeeec4479e76d4b4c135\`. Ten corresponding authentic body+metadata pairs were read as GitHub blobs, separately from synthetic tests. All ten were \`status.publish=draft\`. Eight reported \`safety_review.state=pending\`; two ungated lost-ways historical articles reported \`not-required\`.

| Original held document | Disputed literal citation occurrences |
| --- | ---: |
| articles/food-safety-power-outage | 3 × fsis-power-failure |
| articles/outage-heat-cold-generators | 1 × fsis-power-failure |
| tools/power-outage-planner | 1 × fsis-power-failure |
| articles/pickling-fermentation-old-recipes | 2 × nchfp-home |
| articles/pressure-canning-low-acid | 1 × nchfp-home |
| articles/navigation-before-gps | 2 × loc-prairie-traveler |
| articles/pemmican-and-dried-meats | 1 × loc-prairie-traveler |
| articles/pioneer-supply-chains-failed | 2 × loc-prairie-traveler + 1 × loc-pioneer-diaries |
| articles/pioneer-travel-rations | 1 × loc-prairie-traveler + 1 × loc-pioneer-diaries |
| articles/ships-biscuit-and-hardtack | 1 × loc-prairie-traveler |

**Seventeen literal disputed citation occurrences** across ten held documents: **five** \`fsis-power-failure\`, **three** \`nchfp-home\`, **seven** \`loc-prairie-traveler\`, **two** \`loc-pioneer-diaries\`. These observations narrow the review queue; they are *not* independently validated agency URLs or verified claim support. Do not confuse with 12 metadata declarations.

## Tests, custody, and limits

- New synthetic R348: **63/63 local Python tests passed**. Reconstructed local R344–R348: **393/393 passed**. Python compilation passed. Committed implementation and test blobs are byte-identical to those locally executed (separately verified via GitHub SHA readback).
- Fixture tests create only temporary synthetic data. Never write an authentic source file.
- Native \`python -I preparedness/tools/validate.py\`, \`python -I preparedness/tools/build.py\`, and the genuine complete repository suite **NOT RUN**: local full native checkout unavailable due GitHub DNS. The explicit incomplete-checkout invocation returns \`INVALID_HARD_HOLD\` exit 2.
- R348 pins R347 predecessor implementation Git blob \`744f5b4d905241532fabd19bc0dab2ac8dd16bd8\`, then requires R347's prior source-custody audit. A source-content presence test cannot upgrade this to evidence of safety, link verification, QD acceptance, WordPress release, merchant checkout or paid revenue.
- **Review and release HOLD unchanged:** original 15 editorial conflicts; original 17 Article #15/Tool #104 high-risk safety/child-privacy claim reviews; four disputed source identities; independent QA #157/#169 and dependent #2205 still draft; 50 WordPress + 50 private preview native exports unverified.
- Seven Claude and two Shelter contributor refs were read from GitHub and still equal their R341 frozen SHAs. Homepage lead #1689 remains a separate untouched draft. No merge or public release.

## Conversion-first decision (#820 / #818)

One possible high-intent topic is **family emergency contacts**, but a genuinely published Grok \`asset_id\` and permitted link remain unauthenticated. The only candidate public destination is the existing free, official-agency resources Archive \`https://finalvestige.com/preparedness/\`; original Article #15 and Tool #104 remain **private**. No FV-owned, payable, rights-cleared, deliverable Preparedness pack was authenticated, so **no paid CTA**. Proposed free CTA, not deployed: **Start With Trusted Preparedness Resources**.

**Priority OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → EVIDENCE → OWNER:**

1. Actual FV-owned Preparedness pack → purchase → rights/SKU/checkout/delivery/refund unverified → authenticated merchant and fulfillment evidence before CTA → HOLD / no sale claimed → Founder/Commerce.
2. Archive → original free guide and optional wallet card → disputed source IDs and child/privacy/emergency claims → human adjudication + keyboard/mobile/print checks → HARD HOLD → Preparedness/QD.
3. Grok family-contact asset → Archive → published asset and platform-permitted route not authenticated → TASK-008 read-only asset ID/post URL/destination match → UNVERIFIED → Grok/Praxxis.
4. Qualified human traffic → consented CTA → confirmed lead → paid orders → refunds/fees/net revenue → no independent merchant or 7/30-day cohort evidence → audit existing reports, no new scripts → NOT COMPUTABLE → Claude/Commerce.

No publication, CMS/nav write, social posting, emails, affiliate/merchant activation, spending, QD PASS, or live conversion/revenue claim authorized.
