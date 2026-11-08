# Apollo Experience R202 — staging only

## Change
R201 left two public-facing development phrases in the rendered Atlas: "research prototype" in the hero and an "Unpublished research prototype / Staging QA" notice under the footer. R202 removes both **from visitor copy** and adds a free, source-linked, three-question classroom/research exercise. The exercise compares NASA Apollo 204 Review Board findings to the January 28, 1967 aftermath photograph S67-21294. Those sources do not identify the initiating spark.

The existing free "Read original investigation" link remains the **only action CTA**. No new paid offer, email form, affiliate link, tracking script, geo pin, photo download or WordPress write was added. The source comparison and source links remain visible without JavaScript.

## Reproduce locally
Requires a clean tree containing all earlier additive Apollo build scripts, Python 3, PHP, Chromium, Playwright for Python and BeautifulSoup:

```bash
python experience2/apollo-r202/build_r202.py
python experience2/apollo-r202/qa/gate_r202.py ./r202-evidence-A
python experience2/apollo-r202/qa/gate_r202.py ./r202-evidence-B
```

The builder creates a manifest, SHA-256 pinned PHP shortcode, CSS and HTML. The QA uses **actual PHP-generated output in Chromium**, verifies 320–1920px plus no-JS, touch, reduced-motion, forced-colors and CSS zoom cases, internal navigation, disclosures, source link custody and safety mutations. It records screenshot SHA-256, fixture LCP and CLS. Equal screenshot hashes across runs are expected but must be reported as measured, never assumed.

## Governance / hold
- **R201 exact parent:** `4d48cf59085efd726b9c2fe251b4c05ed3f8b8d5`. This branch does not alter PR #49 or PR #158.
- **Unresolved inherited mismatch:** The actual GitHub R198 builder has blob `57ef73d5719662a1b3647536a0eace5fb65bac4a`, but the R201 local source bundle contains a different R198 builder with blob `2e09257cbd0b32a93f2e7e034a84685d93ed93f5`. R202's newly committed executable sources have exact local/GitHub blob parity, **but a clean full inheritance rebuild from canonical GitHub history is NOT verified**. No merge until reconciled.
- Real installed WordPress, Assembler theme, CDN/CSP, axe-core, NVDA/VoiceOver, real browser zoom, exact-HEAD hosted CI and external live navigation are **not accepted** by fixture QA.
- NASA photographs are linked, not copied. Source citations do not grant advertising rights or NASA endorsement.
- No verified Apollo paid product, Grok Apollo published asset ID, checkout, order count, refunds or revenue. Commercial funnel remains hypothesis-only until independently validated.
- Release state **DRAFT / STAGING HOLD**. Founder and independent QA approval required. No automatic deployment, WordPress writes, merchant activation, email or social publishing.

Governed by Issues #150, #820 and charter #818. Grok retains creator/distribution; Praxxis independent creator QA; Claude production engineering.