# Apollo R119 — source-role reconciliation / NO RELEASE

Parent: #150; revenue attribution: #820; business charter: #818. Previous isolated base: R118 draft PR #951. **Stage only. Do not merge or deploy.**

## Actual change
A new explicit source-role key is visible immediately above Apollo's six-photo source register. It separates NASA's Apollo 204 Review Board technical and instrument findings from NASA photographic context, notes that 2017 exhibit photographs are retrospective, preserves the provisional crew-portrait catalog assignment, and reiterates individual commercial-photo rights unresolved (0/6). No images, geospatial pins, forms, external scripts, affiliate or checkout links were added. The free classroom evidence worksheet remains the only primary CTA. No WordPress data, settings, themes or production code changed.

A standalone, read-only Node crosswalk compares the actual Apollo HTML with an explicitly supplied Research Desk PR #158 template. It checks all six matching NASA photograph URLs and catalog codes, quarantines source-type conflation, and fails closed on missing source roles, unresolved rights notice, unapproved commerce/collection, embedded images and invented geographic coordinates. It **never** reports publication approval—even if a future Research Desk source fixes every editorial flag.

## Read-only evidence evaluated November 4, 2026
- Apollo R118 staging source: `experience2/apollo-creator-bridge/landing-preview.html` on `qa/apollo-r118-student-print-integrity-20261104`, Git blob `02104461730050b539b5f28655142990c867a63f` prior to R119 adjustment.
- Original Research Desk template: `experience2/research-desk/templates/ledger.html` on `feature/experience-2-source-ledger-pilot-20261030` (PR #158), Git blob `403d128c57b9bc82dac7c619651689070edef86c`. **PR #158 was not edited.**
- Compared six matching photographic URLs and catalog codes. The crosswalk emitted **six editorial-review flags**, not six missing NASA URLs. Record 01 presents provisional S67-19766 as confirmed in the Desk; records 02/03 describe contextual photographs under Board/sensor record labels; records 04/06 use retrospective 2017 imagery alongside technical claims; record 05 associates a post-fire photograph with a separate ignition analysis. The underlying NASA Board findings may be sound, but the photo URLs alone do not support those claims. Independent editorial source separation is required before integrating PR #158.
- The Apollo 204 Review Board's own report is the source for pressure, timing, hatch and ignition uncertainty: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA's Apollo 1 gallery indexes the contextual images: https://www.nasa.gov/gallery/apollo-1/ .
- No media is commercially rights-cleared by this audit; all six file-specific assessments remain pending.

## Reproducible local checks
With the R119 checkout:
```sh
node --test experience2/apollo-creator-bridge/test_r119_source_roles.cjs
git show feature/experience-2-source-ledger-pilot-20261030:experience2/research-desk/templates/ledger.html > /tmp/apollo-pr158-ledger.html
node experience2/apollo-creator-bridge/qa_r119_source_roles.cjs experience2/apollo-creator-bridge/landing-preview.html /tmp/apollo-pr158-ledger.html
```
The second command intentionally produces a STAGING_HOLD JSON receipt and exits nonzero while flags remain. Run the existing R118 actual-page Playwright, axe-core, PDF print, 320–1920px, keyboard/touch/reduced-motion and LCP/CLS matrix separately. Only the read-only connected-source comparison and mutation checks were executed during R119 authoring; **not** actual-page Chromium or CI. No approval for release is implied.

## Commercial conversion contract
**OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER**
1. Proposed Apollo educator casefile → merchant-paid order → no verified relevant paid SKU, rights/fulfillment/refund proof → keep checkout disabled; validate with seller-origin receipts → **NOT VERIFIED** → Claude/Growth + founder.
2. Grok long-form Apollo video → source-led landing → free worksheet → photo-vs-primary-source ambiguity → on-page provenance key + read-only crosswalk → **BUILT; 6 editorial flags found** → Apollo engineering; Grok owns scripts/distribution, Praxxis external review.
3. Worksheet → appropriate paid offer → none approved → no commerce insertion until independently rights-cleared and approved → **BLOCKED** → Claude/founder.
4. Verified paid orders → net revenue/1,000 qualified humans → no linked campaign sessions, paid orders, fees or refunds → use existing #820 consent/privacy measurement; no duplicate scripts → **NOT COMPUTABLE** → Claude/Growth.

Release gates: reconcile six source-role flags; six photo-specific rights decisions; independent historical review; actual-page Playwright/axe and PDF/print; WordPress/Assembler acceptance; CI at exact head; existing separately published Atlas approval record; independently verified relevant merchant product; founder publication approval. Do not alter PR #49, PR #158, Grok's queue or live WordPress.