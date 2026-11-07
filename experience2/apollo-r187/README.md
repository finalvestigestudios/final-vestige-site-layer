# Apollo R187 — Gutenberg synced-pattern early-style preflight

**STAGING-ONLY DRAFT. NOT LIVE.** Isolated follow-up to R186; parent Apollo issue #150 and revenue issue #820. No homepage PR #49 or Research Desk PR #158 edits; no CMS writes, tracking, merchant activation, NASA embeds or paid services.

## Problem and change

R186 detects the shortcode only in the queried post_content. If the Atlas shortcode is instead in a synced Gutenberg pattern (core/block with a ref to a wp_block record), the stylesheet is not queued before wp_head and the visitor receives the free-investigation fallback. This was reproduced with a read-only mock of WordPress functions. R187 adds cycle-safe, bounded, read-only discovery of core/block refs, with max 96 nodes and max depth 12. Direct shortcode detection stays fast. Missing, malformed, excessively complex and wrong-type references fail open to the free investigation. The source-pinned R186 HTML/CSS, all NASA source links, source limitations, four chronology entries, four finding plates, eight disclosures and sole reading CTA are unchanged.

**Build:** python experience2/apollo-r187/build_r187.py (from a checkout with the complete R186 parent chain). The generator also accepts --reuse-r186-dist for independently SHA-verified archived inputs. Outputs are local dist assets and a JSON manifest, NOT deployed content. Use only one Atlas shortcode registration on an isolated staging site.

**Regression tests:** python -m unittest discover -s experience2/apollo-r187/qa -p test_*.py -v; php -l experience2/apollo-r187/dist/fv-ex2-apollo-r187.php; php experience2/apollo-r187/qa/wp_function_harness.php. Optional Chromium: python experience2/apollo-r187/qa/browser_acceptance.py --out /tmp/apollo-r187-A; repeat to /tmp/apollo-r187-B and compare screenshots.

## Truthful QA outcomes — 2026-11-07

- Parent R186 PHP SHA-256: 25f7acfe36a4e81c44e3b91cd594706539e76506b3abc44d8e0e50d082f45cd5.
- Generated R187 PHP SHA-256: 8bf0264087d00dc80aa05927bf0cffc6c2855e6d2d99fbd6faaffd94ca741fa0.
- Unchanged HTML SHA-256: f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315.
- Unchanged CSS SHA-256: dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6.
- **10/10** Python unit tests, PHP lint, **17/17** WordPress-function mock checks PASS, including synced/nested/chained refs, cycle, missing/wrong-type refs, admin/archive, duplicate fallback and bounded-work negative controls.
- **148/148** real Chromium assertions in each of two complete 12-context runs, widths 320–1920px, keyboard, touch, reduced motion, no-JS/no-CSS, forced colors and 200% zoom; **12/12 screenshots reproducible**. Lab LCP 104–364ms and CLS 0, not real WordPress Core Web Vitals.
- Genuine axe-core NOT executed (package registry DNS error); NVDA/VoiceOver, installed WP, exact-head CI, real CSP/cache, NASAs image delivery and commercial rights NOT verified.

## Conversion-first release plan

| Offer / funnel | Blocker | Proposed experiment/change | Evidence / owner |
|---|---|---|---|
| Future original educator Apollo dossier → purchase | No verified SKU, rights, checkout or delivery | Validate current catalog and buyer demand first | COMMERCIAL HOLD / Founder, Claude |
| Grok Apollo long-form → Atlas | No verified published Apollo asset_id or tagged destination | Reconcile TASK-008; use standard UTMs only for actual posts | UNVERIFIED / Grok, Praxxis |
| Atlas → free investigation | Synced-pattern stylesheet preflight failed | R187 read-only Gutenberg ref scan | PHP MOCK + CHROMIUM PASS; WP HOLD / Apollo |
| Investigation → appropriate product | No approved relevant paid offer | Keep one nonintrusive reading CTA, defer purchase action | BLOCKED / Founder, Commerce |
| Verified purchases → net revenue | Merchant/fees/refunds and qualified-human sessions absent | 7/30-day cohorts; net revenue per 1,000 qualified human sessions | NOT COMPUTABLE / Analytics |

Intended pathway: Grok-approved Apollo long-form or Shorts → historically verified Atlas → sole **Read original investigation** CTA → optional later rights-cleared educator dossier after offer validation. No unrelated Mini Museum promotion inside the Apollo 1 investigation; no affiliate clicks or leads counted as orders.

## Release gate

Approved isolated installed WordPress staging must prove real Gutenberg core/block reuse and theme enqueue timing; genuine axe-core and independent assistive-tech QA; NASA media/rights, real asset delivery, CSP, cache and production-like CWV; exact-head CI and founder approval. R187 is an isolated draft, never production-authorized.
