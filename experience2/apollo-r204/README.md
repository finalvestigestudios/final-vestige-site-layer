# Apollo R204 — independent Research Desk crosswalk (STAGING HOLD)

Issue #150; conversion issue #820; charter #818. Draft chain based on R203 SHA `c1966b75330c04e4a2e853be39519691c3d7ae38`. No homepage, Research Desk PR #158, WordPress, social, commerce, or production changes.

## Defect and fix

The inherited local R198 builder nests the four NASA technical finding/source crosswalk within the Research Desk methodology `<aside>`. Canonical GitHub R198 builder places the crosswalk outside that aside. R204 restores the crosswalk as a sibling section in the main Apollo evidence content, immediately after methodology and before chronology, preserving DOM navigation and accessible naming. The R198 history is *not* repaired by this forward fix: **GitHub blob `57ef73d5719662a1b3647536a0eace5fb65bac4a` differs from supplied ancestor blob `2e09257cbd0b32a93f2e7e034a84685d93ed93f5`.** Full exact-source build remains blocked.

## Reproduce local fixture (requires parent additive scripts R191–R203)

```sh
python experience2/apollo-r204/build_r204.py
python experience2/apollo-r204/qa/gate_r204.py ./apollo-r204-A
python experience2/apollo-r204/qa/gate_r204.py ./apollo-r204-B
```

Both executable Git blob IDs match their locally executed files: builder `f9370c6bac9aaaadf16b2e4082227266185cb597`; Playwright QA `68d19edae3df1fe195f25489a33367a6ae57bf1c`.

Chromium 144, two runs of ten contexts each, 320/390/768/1440/1920px plus no-JS, touch, forced-colors, reduced-motion and 200% CSS zoom simulation. PHP lint and normal/print/late-fallback harness PASS; four negative mutations caught (missing CTA, synthetic sale, missing crosswalk, wrong-parent regression); keyboard focus and native details PASS. 10/10 screenshot SHA-256 pairs match. Local LCP measurements 84–184ms, CLS 0 where measured. These are **offline fixtures, not production web vitals**. Genuine axe-core **not executed**.

Four NASA Review Board crosswalk records, four chronology events, eight native source disclosures, source-comparison exercise and single free investigation CTA retained. No new JS, imagery, external tracking, map pins, affiliate or checkout. NASA report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; image S67-21294: https://www.nasa.gov/gallery/apollo-1/ ; advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Citation does not clear advertising or identifiable-person rights.

## Conversion requirement

Grok's verified Apollo long-form asset (asset_id not established) -> evidence-led Atlas -> free investigation -> proposed original educator evidence dossier **only after** founder-approved SKU, verified rights, delivery and merchant checkout. No Apollo merchant-confirmed orders or qualified human sessions available; net revenue per thousand qualified sessions cannot be calculated. Preserve single relevant free CTA. Grok script/distribution, Praxxis creator QA, Claude production engineering; no new measurement scripts.

## Release hold

Full exact-HEAD ancestor reconstruction, genuine installed WordPress/Assembler staging, real zoom, axe-core/NVDA/VoiceOver, URL/CDN/CSP acceptance, green hosted CI, independent QA and founder go-live approval. A paid CTA also requires verified actual sale availability, rights and attribution. No merge/deploy without approvals.
