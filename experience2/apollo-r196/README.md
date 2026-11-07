# Apollo Experience 2.0 — R196 Research Desk source hierarchy (DRAFT / HOLD)

Parent: Apollo R195 draft PR #1448 at `5d329e59c25da99644adf246b7750d8803b8a1ae`. Governing Issue #150 and conversion coordination #820. No change to homepage PR #49, Research Desk PR #158, WordPress, merchant or analytics.

## Source-controlled implementation
- `build_r196.py` regenerates R195 through its SHA-pinned builder, then inserts a semantic `<aside>` that separates **Review Board findings**, **recorded chronology**, and **archival photography**. A dated aftermath photo is explicitly not a picture of ignition. Includes research citations and NASA commercial-usage caution.
- Responsive 3-column/1-column glossary with forced-colors and print affordances, native no-JS content, no added JavaScript, no external embedded images, map pins, emails, tracking, or sales links.
- Generated WordPress shortcode `[fv_ex2_apollo_atlas]` remains staged only. The builder generates HTML/CSS/PHP SHA-256 integrity pins, manifest, and controlled PHP shim; JS remains optional and unchanged.
- One free editorial CTA: **Read original investigation**. Apollo educator dossier remains an unverified, not-for-sale concept.

## Rebuild and reproduce
From repository root:
```bash
python experience2/apollo-r196/build_r196.py
php -l experience2/apollo-r196/dist/fv-ex2-apollo-r196.php
python experience2/apollo-r196/qa/gate_r196.py /tmp/apollo-r196-runA
python experience2/apollo-r196/qa/gate_r196.py /tmp/apollo-r196-runB
```
Compare the screenshot SHA-256 strings in `receipt.json`. PHP shim simulates only WordPress functions; it is **not an installed WP/Gutenberg acceptance test**.

## Executed local verification (2026-11-07)
- PHP syntax and normal/printed/late-shortcode behavior: **PASS** (controlled shim).
- True Chromium/Playwright plus Chrome DevTools `Accessibility.getFullAXTree`: **10 contexts per run, 320–1920px**, named source methodology landmark and 3 accessible named source links; keyboard/touch/native details/no-JS/reduced-motion/forced-colors: **PASS**.
- Negative controls: **5/5 correctly rejected** (commerce-URL substitution, overstated ignition cause, replaced NASA photo citation, tracking pixel, duplicate ARIA ID).
- Two runs: **9/10 screenshot SHA-256 hashes reproduced**, touch screenshot visually nondeterministic. Laboratory buffered PerformanceObserver LCP/CLS collected where JavaScript enabled; neither measures production CWV. CSS zoom regression from R195 is *not* recertified in R196.
- **Not executed**: axe-core, NVDA/VoiceOver, installed WordPress staging, theme/CSP/CDN, external HTTP navigation, exact-head hosted CI or independent QD.

## Primary source and rights
- NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — no specific initiator conclusively determined; electrical arc probable.
- NASA Apollo 1 catalog: https://www.nasa.gov/gallery/apollo-1/ — S67-21294 dated January 28, 1967 depicts damaged cabin **after** the fire.
- Advertising policy: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no NASA sponsorship/endorsement implied; astronaut likeness and some imagery require additional clearance. No images are reproduced or newly certified for commercial promotion.

## Conversion gate / release hold
**OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER:** Original Apollo educator dossier → documentary audience to evidence Atlas to free investigation → no verified SKU, checkout or rights ledger → protect provenance and study a relevant *future* educator offer only after validation → local CDP/accessibility and source-custody PASS, paid attribution NOT COMPUTABLE → Apollo owner (UX), Claude/Commerce (SKU/checkout), Grok/Praxxis (published asset audit), founder (release).

No qualified-human Grok attribution, confirmed lead, merchant order, refund/fee or realized net revenue established. Do not claim a paid conversion or public launch. **STAGING HOLD; no merge or deployment authorization.**
