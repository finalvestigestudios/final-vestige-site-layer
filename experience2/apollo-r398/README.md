# Apollo Experience 2.0 R398 — canonical staging CSS custody

**DRAFT. NOT INSTALLED. PRODUCTION HARD HOLD.** Additive, independent candidate on top of Apollo R397 #2692. Do not enable the R395/R396/R397/R398 staging loaders together; do not edit frozen homepage #49, Research Desk #158 or Grok/Praxxis TASK-008.

## Verified historical provenance

The pinned six-record, ten-field Apollo source ledger (SHA-256 60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f) distinguishes five evidence questions backed by NASA's original 1967 Apollo 204 Review Board report from one backed by the 2018 account of later deliberate flammability tests. The later 102 ignitions are not the original fire. No NASA photos, seals, unsupported geographic pins, or speculative causation were introduced.

Primary references:
- https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
- https://www.nasa.gov/nasa-brand-center/images-and-media/

## Engineering change, limits and code

WordPress's documented plugins_url() implementation appends a supplied relative path. R397 admitted a literal /apollo-r397/../apollo-r384/ stylesheet URL. R398 requests the plugin directory only, insists on an HTTPS same-origin canonical path ending in /experience2/apollo-r398, and constructs verified sibling CSS paths without dot segments, encoding, ports, fragments, or unapproved query parameters. A native PHP witness reproduces the difference; no live exploit or failed network request is claimed.

WordPress documents the style_loader_src filter for fully-qualified enqueued CSS URLs. R398 registers a print-time guard only after passing the default-off, staging/page/ledger/CSS SHA/handle-collision prerequisites. It rejects source URL changes after enqueue, including other hosts and unauthorized query parameters. It allows only expected WordPress version queries. This is defense in depth, not a guarantee: later same-priority filters, style_loader_tag rewrites, caching, actual HTTP response bytes and CDN behavior are still outside local proof. The value returned on rejection is empty; installed staging must check that no wrong or empty-href link renders.

Official WordPress references:
- https://developer.wordpress.org/reference/functions/plugins_url/
- https://developer.wordpress.org/reference/hooks/style_loader_src/

## Executed QA; not installed staging

Native PHP stub checks: 164 PASS with loader OFF, 218 PASS with explicit staging enable, plus 4+16 source-controlled smoke assertions and a standalone R397 path-normalization witness. Real Playwright Chromium fixture checks: 195 PASS across 13 contexts (320–1920px, keyboard Enter, touch, no-JS, reduced motion, forced colors, 400% root-font, print custody, source navigation). All contexts recorded 0px horizontal overflow. Local observed LCP 72–144ms, fixture CLS 0 where observed; these are NOT hosted Core Web Vitals or native 400% browser zoom. The packaged local screenshots, inputs, tests and JSON have deterministic timestamps and a SHA-256 manifest. The packager performs a byte-identical double ZIP build.

The large local contract.php / enable.php test set and input fixture siblings are included in the downloadable QA bundle; the branch includes independent source-controlled print_gate.php, enable_print_gate.php, browser.py and the deterministic packaging code. Genuine pinned axe-core could not be obtained because dependency host DNS was unavailable. Browser page.goto navigation (including file URLs) returned ERR_BLOCKED_BY_ADMINISTRATOR. No installed WordPress, actual HTTP/CSP, axe-core, screen reader, native zoom, hosted CI, independent QD or founder release acceptance is claimed.

## Conversion-first owner plan

| Offer | Step | Blocker | Experiment and evidence | Owner |
| --- | --- | --- | --- | --- |
| Rights-cleared Apollo educator dossier (not verified) | Paid purchase | SKU, checkout, permissions and delivery unknown | Withhold purchase CTA; no verified paid sale | Founder / Claude |
| Grok Apollo documentary | Qualified session | No published approved asset ID or campaign attribution | Grok/Praxxis identify real video and source-safe landing | Grok / Praxxis |
| NASA-backed free evidence gallery | CTA to existing free Apollo investigation | Unnormalized CSS path / late style rewrite | Canonical source + print guard; local PASS, staging HOLD | Apollo QA / QD |
| Confirmed product customer | Net revenue per 1,000 human sessions | Merchant settlement, fees, refunds and 7/30-day cohorts missing | No revenue inference from clicks or views | Claude / Commerce |

Single relevant journey: Grok-approved Apollo long-form → six-record source-backed gallery → existing free investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → future separately approved educational kit only when independently sellable and rights-cleared. No unrelated commerce inside historical text.

## Release gate

Independent exact-head hosted CI, genuine axe-core and screen-reader testing, native 400% zoom, real installed WordPress/Assembler and delivered asset checks, lawful approved commercial SKU, independent QD and explicit founder authorization are outstanding. No merge, deployment, WordPress write, third-party publishing, email, tracking or spending. Coordinate Apollo #150, conversion #820 and charter #818.
