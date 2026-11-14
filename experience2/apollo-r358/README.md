# Apollo Experience 2.0 — R358: exact assigned-template pre-head staging bridge

**DRAFT / RESEARCH ONLY / NOT LIVE.** Stacked on R357, not on homepage PR #49 or Research Desk PR #158. No WordPress writes, deployment, settings updates, analytics, tracking, checkout, social posts, merchant changes, or expenses.

## Concrete defect and bounded fix

R357 discovers shortcodes in singular `post_content`, saved `core/block` and explicitly referenced `core/template-part`, but misses a `core/template-part` that exists **only in the theme-level template that WordPress renders**, not in the post body. This produces missing CSS/JS in staging for an Apollo shortcode inside an assigned template. R358 adds a new **companion** `wp_enqueue_scripts` pre-head hook (priority 17), looking up **only the post's explicit custom template** via `get_page_template_slug($post)` and `get_block_template("$theme//$slug", 'wp_template')`. It then delegates bounded nested scanning to R357 and enqueues the exact same seven CSS/one optional JS for composite Atlas or two CSS/zero JS for post-fire note. Existing R357 markup and WordPress enqueue handles remain unchanged (WordPress deduplicates handles).

This is *not* an automatic default page/single hierarchy resolver. `get_page_template_slug()` returns an empty string for default templates, so default theme template parts are a **hard coverage gap**, rather than speculative assets. Exact template ID, slug and theme identity are guarded where supplied. Any missing, malformed, foreign, unassigned or unsuitable template fails closed for asset discovery, not by hiding reader-facing source content. Source URLs and the single free investigation CTA remain unchanged. No Atlas geo pin or commercial CTA is introduced.

## Reproduce from repository

```sh
php -l experience2/apollo-r358/explicit-template-prehead.php
php experience2/apollo-r358/qa/wp_contract.php
python experience2/apollo-r358/qa/browser_gate.py
python experience2/apollo-r358/qa/build_evidence.py
```

The standalone PHP WordPress-API model executes 24 cases including custom-template IDs and `templates/*.html`, nested parts/reusable blocks, absent/default templates, foreign/altered template IDs, unsafe paths, cycles, oversized content, missing objects and non-singular requests. The local Chromium inheritance fixture exercises real PHP-rendered evidence UI across 320/390/768/1440/1920px, with 400% text, keyboard, touch, reduced motion, forced colors, JS on/off, native browser PDF, source annotations, and synthetic LCP/CLS diagnostics. These tests **DO NOT** establish installed WordPress/Assembler correctness, live HTTP/CSP enforcement, genuine axe-core or NVDA/VoiceOver, Firefox/WebKit or production CWV. The QA archive is deterministic, with file checksums, screenshots and test receipts.

## Source rights and commercial bridge

The flagship remains the original Apollo 1 fire and the 1967 Board record; a separately classified later NASA retrospective [February 14, 2018](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) documents **102 CM flammability test ignitions, December 1967–February 1968**. That number must **not** be conflated with the original Board's fire investigation. NASA source links are not third-party photo, trademark, endorsement, or product-licensing clearance. No images have been imported in this sprint.

High-intent audience: history and science educators examining failures, evidence and engineering response. Proposed controlled journey: approved Grok Apollo long-form asset with validated `asset_id` / standard UTMs → readable NASA evidence Atlas → the one existing free Apollo 1 investigation link → a **separately approved, actually payable, rights-cleared educator kit**. Candidate kit is an unvalidated offer, not a purchasable product or conversion. The hypothesis that better provenance and accessibility improve trust is untested commercially.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Future rights-cleared educator kit | paid order | No authenticated live SKU or checkout | Hold sales CTA, require payment/rights/fees receipt | BLOCKED | Founder/Claude |
| Grok Apollo long-form | validated qualified landing | No confirmed published `asset_id` | Praxxis independently verifies via existing TASK-008; no queue edits | UNKNOWN | Grok/Praxxis |
| NASA Atlas | free investigation click | Theme-only explicit custom template assets missed | Exact assigned-template pre-head scan, existing editorial link only | Local stub + Chromium PASS; WP install UNKNOWN | Apollo |
| Net revenue per 1k qualified humans | reconciled 7/30-day cohort | No attributed qualified sessions or paid settlements/refunds | No new scripts; use governed merchant/analytics records | NOT COMPUTABLE | Claude/Commerce |

**Release HARD HOLD:** actual installed WordPress/Assembler QA, default-template hierarchy coverage, genuine axe + independent screen readers, Firefox/WebKit, native HTTP/CSP, hosted CI on exact HEAD, media-rights/claim review, approved payable offer, founder/QD permission. Cross-reference #150, #820 and #818. Never modify frozen homepage #49 or Research Desk #158.
