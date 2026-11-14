# Apollo Experience 2.0 R357 — template-part-aware staging asset discovery

**RESEARCH ONLY · DRAFT · NOT LIVE.** Based on isolated R356 HEAD `f7cd78ed035dda6c15126176e41e867f98bb6713`. No changes to frozen homepage PR #49, Research Desk PR #158, Grok/TASK-008, WordPress content/settings, analytics, commerce or site deployment.

## Why this exists

R356 only discovers the Apollo shortcodes when they appear directly in a singular post or through a saved `core/block` reusable block. WordPress can render an Apollo shortcode inside a **`core/template-part` block** while the actual post content contains only a template-part reference. That misses pre-head asset discovery and risks unstyled evidence content. This sprint adds `core/template-part` traversal for **same-theme, explicit references present in scanned content** with WordPress's documented `get_block_template( "$theme//$slug", 'wp_template_part' )` contract. It does not attempt to search every installed theme template, alter live settings, or enqueue assets globally.

Opt-in shortcodes: `[fv_apollo_experience_r357]` (seven local CSS files and one optional filter JS); `[fv_apollo_postfire_r357]` (two local CSS, no JS). Existing source content and one free editorial continuation are inherited unchanged. The 2018 NASA source notes **102 post-fire deliberate ignitions** across three CM test series; it is a later institutional retrospective, not the 1967 accident Board's finding. Source: [NASA, 14 February 2018](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/). No photograph or commercial media license is asserted.

## Guardrails and status

- Traverse only same-theme `core/template-part` slugs of up to 80 safe characters, and `core/block` numeric saved references. Foreign-theme IDs and path traversal do not authorize loading any assets.
- Prevent unbounded recursion via visited reference keys, maximum depth, bytes and node counts; return a separate completeness flag for uncertain scans. No network, CMS or payment writes.
- Explicitly **not covered**: template parts that exist only in theme-level layout and are absent from scanned singular `post_content`; dynamic render-time shortcodes, WP Query templates, cached revisions, malformed `parse_blocks`, actual Assembler/plugin interactions, or late script enqueue. Those require installed WordPress QA. Bounded-size exhaustion may leave unstyled but still readable HTML; do not present this as production-ready fail-open integration.
- No client tracking, commerce, new editorial CTA, unsourced map pin, external image, or new NASA claim.

## Reproducible local QA

```sh
php -l experience2/apollo-r357/template-asset-bridge.php
php experience2/apollo-r357/qa/wp_contract.php
python experience2/apollo-r357/qa/browser_gate.py
APOLLO_R357_HEAD_SHA=<exact-GitHub-HEAD> python experience2/apollo-r357/qa/build_evidence.py
```

Tests: **19 WordPress API-stub scenarios** (including direct/reusable/template-part/nested/cyclic/foreign theme/path traversal/oversized/non-singular), **seven actual local Chromium contexts** at 320–1920px with no-JS, keyboard, touch, 400% font stress, reduced motion, forced colors, CDP accessibility-tree named-link checks, native 14-page PDF and source-link annotation. PDF preserves the later NASA source even after JS filters activate. Local synthetic fixture LCP and CLS are diagnostic only, not CWV at p75. Tests use a model of WordPress APIs rather than a full WordPress install. Genuine axe-core and independent screen reader acceptance were NOT executed.

## Conversion-first hypothesis and release gate

**High-intent audience:** educators/home-school researchers teaching historical evidence and engineering failures. **Candidate offer:** a rights-cleared Apollo 1 classroom evidence kit with chronology, inquiry worksheets, source-citation tasks and teacher guide (hypothetical; not a currently verified payable SKU). **Intended path:** Grok-produced Apollo documentary (asset_id + approved UTM after validation) → free NASA Evidence Atlas → one existing free Apollo investigation link → *only after verified checkout/rights approval*, a contextual educator offer outside the narrative. Hypothesis: uninterrupted accessible evidence builds trust and qualified educator interest, but no payment lift is measured.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → EVIDENCE → OWNER**

| Offer / step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Apollo educator kit → paid purchase | No authenticated payable/rights-cleared Apollo SKU | Hold commerce CTA and validate actual merchant, fulfillment, rights and fees | BLOCKED / no sale evidence | Founder / Claude |
| Grok Apollo film → qualified landing | No verified published asset_id or destination | Request QA handoff through existing TASK-008; do not edit production queue | NOT OBSERVABLE | Grok / Praxxis |
| NASA evidence → free investigation | Template-part asset lifecycle uncertain | Add bounded same-theme `core/template-part` discovery and seven-context browser tests | Local model / Chromium PASS; WP install unverified | Apollo |
| Paid order → net revenue per 1,000 qualified humans | No reconciled sessions, orders, refunds or fees | Await source-of-truth 7/30-day merchant and privacy-safe attribution data | NOT COMPUTABLE | Claude / Commerce |

Hard hold: installed WordPress/Assembler and dynamic template-part acceptance; genuine axe-core, NVDA/VoiceOver, Firefox/WebKit, browser-enforced HTTP/CSP, hosted exact-HEAD CI, reviewed media rights, verified product/checkout, founder and QD approval. No merge or deployment from this PR. Coordinate Issue #150 and #820; founder charter #818.
