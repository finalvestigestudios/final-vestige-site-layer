# Apollo R340 — evidence gallery and scoped WordPress asset bridge

Scope: Experience 2.0 #150, conversion #820/#818. Draft staging only, never production-authorized. Stacks on R339 draft PR #2367. Does not edit homepage PR #49, Research Desk #158, Grok TASK-008 or any WordPress/merchant settings.

## Actual implementation
- apollo-accession-gallery.php: WordPress-compatible [fv_apollo_gallery_r340] shortcode plus [fv_apollo_experience_r340] composite shortcode. The composite renders prior R339 six-event NASA chronology and the four-record NASA accession gallery. **One** existing free investigation CTA (inside chronology) and **zero** gallery commerce CTAs.
- assets/accession-gallery.css: responsive 320–1920px gallery, native no-JS source drawers, 44px keyboard/touch targets, forced colors, reduced motion and print styling; zero embedded archival photographs, logos or tracking scripts.
- Conditional WP enqueue bridge: on ordinary singular posts containing the exact composite or gallery shortcode, enqueues R340 CSS and the adjacent R339 CSS where applicable. Simulated WordPress-function unit proof only; nested reusable blocks and Assembler delivery require installed-site review. If styles fail, content remains complete HTML.
- qa/browser_acceptance.py: real PHP CLI renders with WordPress function stubs, two simultaneous component instances, 14 Playwright Chromium scenarios across widths, zoom/text, no-JS, keyboard, touch and forced-colors. Seven adversarial source/rights/geo/commerce controls. Screenshots and JSON evidence. Not independent axe-core or live-site acceptance.

## NASA source custody
Verified public NASA URLs on 2026-11-13:
- S67-15717 https://www.nasa.gov/image-detail/amf-s67-15717/
- S66-58038 https://www.nasa.gov/image-detail/amf-s66-58038/
- S67-21294 https://www.nasa.gov/image-detail/amf-s67-21294/
- KSC-20170124-PH_KLS01_0090 https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/

These are contextual photo accession links, **not** photographs licensed for FV commerce or independent proof of the ignition point. NASA's 1967 Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ found a probable electrical-arc initiator but not a conclusively identified exact ignition source. Rights/endorsement guidance: https://www.nasa.gov/nasa-brand-center/ . No map pins or edges fabricated.

## Reproduce locally
1. PHP lint: php -l experience2/apollo-r340/apollo-accession-gallery.php
2. Browser: FV_R340_OUT=/tmp/apollo-r340 python experience2/apollo-r340/qa/browser_acceptance.py
Prerequisites: PHP 7.4+, Python 3, playwright, beautifulsoup4, installed Chromium and R339 adjacent source. No network service needed to run tests.

## Conversion hypothesis and release gate
Audience: qualified history-documentary viewers and educators researching Apollo 1. Path: verified Grok Apollo campaign [UNAUTHENTICATED] → staged NASA chronology + source gallery → published free investigation → separately validated, rights-cleared and payable educator kit [BLOCKED]. Hypothesis only: explicit limits on photographs promote trust and qualified continuation. No asserted paid impact. Reconcile qualified-human asset_id/UTM sessions, original CTA, confirmed leads, actual settled merchant orders, refunds/fees and realized net revenue per 1,000 sessions in #820. No new measurement scripts.

**HARD HOLD:** Research Desk source-custody owner reconciliation; real installed WordPress/Assembler including nested blocks, HTTP/CSP, genuine axe-core, screen readers, Firefox and WebKit; hosted exact-head CI and production LCP/CLS; editorial/rights review; real published Grok asset and payable offer; founder/QD release approval. No deployments, posting, merchant writes, analytics changes, emails or spending.
