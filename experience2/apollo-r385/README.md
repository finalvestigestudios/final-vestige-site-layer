# Apollo Experience 2.0 — R385 gallery CSS custody in reusable blocks

**BUILT / locally TESTED only. NOT installed on WordPress, NOT LIVE, NOT production-verified, NOT revenue evidence.** Independent opt-in, staging-only companion to R384 document gallery. Draft stack is PR #2620 (R384), itself stacked on R383/R382 curated Atlas; frozen homepage PR #49 and original Research Desk PR #158 are unchanged.

## Evidence-backed defect and change

R384's `fv_r384_enqueue()` scans only the queried `post_content` for a literal `[fv_apollo_source_gallery_r384]`. If a published reusable `wp_block` contains the shortcode and the post embeds `<!-- wp:block {"ref":7} /-->`, its content can render without R384 gallery CSS. The local WordPress API-stub test first reproduces this exact absence. This new read-only `gallery-asset-guard.php` is a separate pre-head CSS loader for **published reusable blocks in singular posts**. It reuses the existing handle; it does not alter or replace the shortcode and does not touch the R384 component itself.

- Only enters after R377 approved staging environment, R384 exact canonical NASA source/citation check, and R384 stylesheet SHA-256 verification.
- Checks that the current shortcode callback is exactly `fv_r384_shortcode`, never a foreign owner.
- Traverses a complete, bounded graph (7 levels / 200 nodes / 1 MiB); rejects circular/missing/draft/foreign/malformed references, including an invalid sibling encountered after an earlier positive match. Reused valid blocks are permitted. Code, preformatted and HTML examples cannot trigger asset loading.
- Loads R384 CSS only for relevant singular content, at most once; no JavaScript, additional analytics, map coordinates, affiliate links, commerce or NASA media.
- **Out of scope:** block themes' resolved template/template-part graphs, builder render callbacks not represented in `post_content`, and unapproved WP installations. These require separately governed acceptance, not speculation.

## Actual local proof and reproduction

The test checkout must have R377 `custody.json` and R384 `document-gallery.php`, `assets/gallery.css`, and `qa/contract.php` in their review paths. Executed:

```sh
php -l experience2/apollo-r385/gallery-asset-guard.php
php experience2/apollo-r385/qa/contract.php
python experience2/apollo-r385/qa/browser.py
python experience2/apollo-r385/qa/package.py
python experience2/apollo-r385/qa/package.py # deterministic repeat
```

PHP uses explicit WordPress function doubles, **not** installed WordPress. Browser uses actual Playwright Chromium against an R384 PHP-rendered local fixture, 10 viewports/interaction contexts 320–1920 px; real source disclosures, keyboard, touch, no-JavaScript, reduced-motion, forced-color, fourfold root-font stress, screenshots and PDF clickable NASA citations. A Python `urllib` loopback server fetch checks true HTTP bytes/CSP response headers; Chromium navigation to the loopback host is blocked by this execution environment (`ERR_BLOCKED_BY_ADMINISTRATOR`), so **browser HTTP stylesheet loading and browser-enforced CSP are NOT verified**. Browser runs an inline reviewed CSS fixture. LCP/CLS are fixture-only observed values; never production Core Web Vitals. Genuine axe-core is unavailable; only Chromium native accessibility-tree semantics checked. Real native 400% browser zoom / VoiceOver / NVDA / Safari and installed staging remain untested.

`QA/Apollo_R385_Evidence.zip` has reproducible source, tests, screenshots, PDF, results and manifest (zero ZIP timestamps). The `MANIFEST.json` hashes test outputs, and records required R377/R384 dependency hashes; archive excludes inherited component source so that the PR change is isolated.

## Historical and commercial boundaries

NASA original Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA later testing account: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ ; NASA media-use guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/ . Six questions rely on only two NASA publications; no photos, insignia, unverified rights or implied endorsement. The Board did not conclusively identify an exact initiating ignition source. Later deliberate tests were not contemporaneous observations of the 1967 event.

Single possible audience path, **hypothesis only**: Grok-approved, actually published Apollo documentary (asset ID and landing URL pending Grok/Praxxis independent QA) → the source-inspectable gallery → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → only after separate verified approval, a rights-cleared educator kit. No paid CTA until an authenticated payable SKU, merchant acceptance, lawful media rights and fulfillment are verified by Founder/Claude. No presumed traffic, subscribers, paid orders, refunds, fee deductions or revenue-per-1,000-session values.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Rights-cleared Apollo educator kit | Buyer purchase | SKU, checkout, rights, payment and fulfillment not verified | No paid CTA until source-of-truth merchant audit | HOLD; no sale verified | Founder / Claude |
| Grok Apollo documentary | Qualified landing | Posted asset_id, permitted UTMs and human-session attribution missing | Grok/Praxxis review one exact asset and destination | UNOBSERVABLE | Grok / Praxxis |
| NASA gallery | Source trust → free investigation click | Nested reusable CSS missing | Review staging-only gallery asset guard | PHP/Chromium local PASS; WP NOT TESTED | Apollo QA |
| Confirmed orders | Realized net / 1k qualified sessions | Settlements, fees, refunds, 7/30 day cohorts missing | Match paid orders to approved campaigns when consent and evidence allow | KPI NOT COMPUTABLE | Claude / Commerce |

## Hard release hold

No merge or install until full approved WordPress/Assembler staging, actual HTTP/CSP asset waterfall, genuine axe-core and screen-reader review, native zoom, CI at exact SHA, independent QD, founder visual/commercial/production approvals. Never touch homepage PR #49, PR #158, Grok/Praxxis Drive queue, WordPress settings/posts or live analytics, nor activate any merchant/affiliate functionality.
