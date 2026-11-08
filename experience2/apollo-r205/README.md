# Apollo R205 — chronology-to-original-source custody (STAGING HOLD)

**Scope:** additive Apollo Evidence Atlas prototype, based on R204 draft PR #1519, independently of homepage PR #49 and Research Desk PR #158. Refs #150 / #820 / #818. Not for production activation.

Each of the four chronology dates now has its own original NASA record link, accessible label and a programmatically connected explanatory caption. The existing internal evidence navigation, eight source disclosures, gallery, Research Desk, and **single free “Read original investigation” CTA** remain unchanged. The new labels distinguish contemporaneous preparation photography, the Review Board's accident findings, and the following-day aftermath photography. No JavaScript, photographs, geolocation, new scripts, commercial promotions or paid services are added.

## Source custody verified 2026-11-07
- 1966-10-18: NASA **S66-58038** training photo: https://www.nasa.gov/image-detail/amf-s66-58038/
- 1967-01-03: NASA **S67-15717** spacecraft processing: https://www.nasa.gov/image-detail/amf-s67-15717/
- 1967-01-27: NASA **Apollo 204 Review Board**, no conclusively identified source of ignition: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- 1967-01-28: NASA **S67-21294** post-fire damage photograph: https://www.nasa.gov/image-detail/amf-s67-21294/
- Rights and endorsement rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

Historical citation is **not** independent commercial advertising/media/astronaut-likeness permission. No images embedded or copied in R205. No speculative geographic pins or relationships.

## Build and QA
Requires the historical additive R191–R204 builder scripts available in their distinct directories. Command examples:

```sh
python experience2/apollo-r205/build_r205.py
php -l experience2/apollo-r205/dist/fv-ex2-apollo-r205.php
python experience2/apollo-r205/qa/gate_r205.py ./r205-QA-A
python experience2/apollo-r205/qa/gate_r205.py ./r205-QA-B
```

Local fixture results (2026-11-07): Chromium 144, two independent runs of ten contexts from 320px to 1920px, no-JS, keyboard, touch, reduced-motion, forced-colors, simulated 200% CSS zoom, native disclosures, accessible source link names/descriptions, no horizontal overflow, eight deliberate custody/commercial mutants rejected and 10/10 byte-identical screenshot hashes between runs. Local fixture LCP 76–312 ms where observable; CLS 0. **Not production Core Web Vitals.** The QA harness renders a PHP shortcode through a WordPress-function shim; it does not constitute genuine installed WordPress acceptance, actual browser zoom, screen-reader testing, or **axe-core**.

Outputs are deterministically hashed in `dist/manifest.json`; a separate `source-records.json` retains NASA URLs and limitations. `commercial-offer-gate.json` is **disabled**. No verified rights-cleared Apollo educator product, live checkout, Grok campaign asset_id, confirmed orders/leads or net-revenue data exists here. Affiliate outbound ≠ affiliate sale; a checkout start ≠ a sale.

## BLOCKED: inherited R198 builder mismatch
Canonical GitHub R198 builder Git blob: `57ef73d5719662a1b3647536a0eace5fb65bac4a`. Supplied local ancestor R198 builder Git blob: `2e09257cbd0b32a93f2e7e034a84685d93ed93f5`. R205 uses the *local* ancestry and records `source_chain_verified=false`; exact canonical ancestry rebuild still required. Do **not** merge a green-looking fixture without resolving the mismatch.

**Release hold:** canonical source ancestry, exact-head hosted CI, installed WordPress/Assembler theme/shortcode/real links/CSP/CDN validation, genuine axe-core, NVDA/VoiceOver, actual 200% zoom, independent site QA, relevant sellable product and founder release approval. No WP, email, social, paid checkout, or production writes.

**Offer → Funnel step → Blocker → Change/experiment → Evidence → Owner:** Apollo educator dossier → paid purchase → no proven seller/rights/checkout → validate commerce before paid link → BLOCKED → Commerce/Claude; Grok Apollo documentary → Atlas → no published attributable asset_id → TASK-008 reconciliation → UNVERIFIED → Grok/Praxxis; Atlas → original investigation → chronology citations not individually navigable → R205 links → LOCAL PASS → Apollo; original investigation → purchase → no approved relevant SKU → preserve free CTA → HOLD → Founder; paid order → realized revenue → no merchant receipts/refunds/qualified-human denominator → 7/30-day cohorts → NOT COMPUTABLE → Analytics.
