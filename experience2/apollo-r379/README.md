# Apollo Experience 2.0 · R379 — resolved template-part source custody

**BUILT / PHP API-STUB TESTED / REAL CHROMIUM LOCAL FIXTURE TESTED / INSTALLED WORDPRESS NOT VERIFIED / DRAFT RELEASE HOLD.**

## Evidenced gap / change

R377 Apollo source-role Research Desk and R378 reusable-block asset guard enqueue CSS from queried post content and published reusable-block references. Neither inspects the page's **resolved block theme template** or its template-part references. A Research Desk rendered from such a template can therefore be unstyled at first paint. This is code-path analysis and a local API-stub proof, **not a production observation**.

R379 adds an optional staging-only pre-head WordPress companion. It reads **only the current resolved wp_template**, its active-theme wp_template_part references, and published core/block references. Uses WordPress's documented template IDs, prevents duplicate CSS enqueues and accepts CSS only when the already-reviewed R378 stylesheet SHA-256 guard and R377 source seal succeed. Bounds: 7 levels, 200 parsed nodes, 1 MiB aggregate; no searching every template or unrelated posts. Rejects foreign/malformed identities and slugs, draft parts, wrong themes, cycles, pre-owned shortcode handlers, production and unapproved hosts. A shortcode-looking literal in block attributes or code samples does not activate a stylesheet.

WordPress contracts: https://developer.wordpress.org/reference/functions/get_block_template/ and https://developer.wordpress.org/block-editor/reference-guides/core-blocks/core-blocks-theme/core-block-template-part/ .

No new shortcodes, JavaScript, NASA photographs/logos, speculative geospatial edges, tracking tags, merchant links, WordPress database writes, publishing, or paid services. Homepage #49, lead homepage lane, Research Desk #158 and Grok/Praxxis TASK-008 remain untouched.

## Source and media-rights custody

- Original 1967 Review Board (NASA): https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — probable electrical arc, but no conclusive exact initiating source.
- John Uri, NASA, February 14, 2018: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — 102 deliberate Command Module boilerplate ignitions in December 1967–February 1968, **not** ignitions during the January 1967 disaster.
- NASA Brand Center: https://www.nasa.gov/nasa-brand-center/ — source linking does not establish NASA endorsement, commercial photograph rights or permission to use protected marks. No external media reproduced.

## Reproduce local QA

Requires PHP 7.4+, Python, Playwright/Chromium, with sibling R377/R378 files at repository root. Commands:

    php -l experience2/apollo-r379/prehead-template-parts.php
    php -l experience2/apollo-r379/qa/wp_stub.php
    python experience2/apollo-r379/qa/browser_qa.py
    python experience2/apollo-r379/qa/package.py
    python experience2/apollo-r379/qa/package.py

API simulation covers 19 scenarios including nested/reusable theme parts, cycles, wrong/foreign templates, drafts, malformed slugs, hidden shortcode text, missing/oversized content, shortcode ownership and disabled/production/wrong hosts. Actual Chromium **local set_content fixture** uses PHP-generated R377 DOM and the exact bundled R377 CSS at 320, 390, 768, 1440 and 1920px, plus no-JS, keyboard, touch, reduced motion, forced colors, 4× root-font, overflow and print-CSS checks. QA/results.json and screenshots are reproducible. Performance-observer LCP and CLS from those fixtures are **not p75 production Core Web Vitals**.

A missing genuine axe-core distribution, independent screen readers, native 400% browser zoom and blocked loopback browser HTTP prevent claims of axe, real staging HTTPS/CSP, first-paint CSS waterfall or installed WordPress/Assembler acceptance. Hosted CI on exact PR HEAD, production LCP/CLS/INP and supported theme identity/lifecycle remain release blockers. No staging site installed or WordPress admin action performed.

## One audience-to-offer pathway, conversion-first

**Grok-owned, actually published Apollo documentary with approved asset_id and UTM (unverified) → source-custody Research Desk → one existing free Apollo investigation** https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ **→ separately approved educator evidence kit (not verified payable)**. The hypothesis is that consistent source styling protects educator trust and qualified continuation, **not proven purchases or revenue**.

| Offer → funnel step | Blocker → change / pass-fail evidence | Owner |
|---|---|---|
| Apollo educator dossier → paid order | No approved rights-cleared SKU or real checkout; **purchase CTA withheld** | Founder / Claude |
| Grok documentary → qualified landing | Published Apollo asset and first-party qualified human sessions not proven; attribution unobservable | Grok / Praxxis / Claude |
| Evidence trail → free investigation | Template-part CSS guard built; local PHP/Chromium PASS, installed WordPress acceptance blocked | Apollo QA |
| Verified order → realized net revenue | Merchant settlements, fees, refunds, 7/30-day attributable cohorts unavailable; KPI not computable | Claude / Commerce |

Release requires installed WordPress/Assembler staging, real HTTP/CSP, independent accessibility and exact-HEAD CI, verified commercial product and founder/QD approval. **Do not deploy/merge, publish, send email, install analytics, activate affiliates or spend.**
