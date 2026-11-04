# Experience 2.0 — HOLD: anonymous mobile primary navigation, no-JS + Focus preservation

**2026-11-04 PT — source-controlled candidate only; no WordPress or production writes.**

## Source-based finding
The actual flagship `index.html` includes three header destinations (Investigations, Public Record, Library), but `flagship.css` applies `.fv-hf__nav{display:none}` at <=920px without a mobile replacement. Readers on narrow screens cannot reach those three primary destinations from the masthead. Footer routes are not a first-screen substitute.

## Actual design change
- Introduced **one** closed native `<details><summary>Explore</summary><nav>…</nav></details>` immediately beside the existing header navigation, containing the **same three unchanged URLs**.
- Only show it <=920px; retain original desktop navigation >920px.
- 44px native summary/route targets, keyboard Enter/Tab support without JavaScript, automatic platform semantics, forced-colors border and existing antique-gold focus ring. No motion or third-party resources.
- Retain free `/focus/` masthead CTA, all seven chapters, existing editorial/image sources, 72 published Margins integration, Jetpack signup and every original evidence link. No affiliate URLs, analytics, paywall, popup or new content chapters.
- Dropdown uses the **masthead as its positioned ancestor**, opening beneath the full header rather than underneath the Explore button. This prevents the menu from covering the revenue-critical Focus CTA when the masthead wraps.

## Executed controlled Chromium study — NOT full source or WordPress
In a source-derived isolated masthead DOM/CSS reconstruction, JS disabled, reduced motion, at widths **320/360/390/420/600/768/920/921/1440**: **9/9 final viewport assertions passed**. The 3 original primary header links were invisible at <=920; the new disclosure exposes 3/3 in its appropriate breakpoint. Native keyboard Enter opens; Tab focuses the first route; route hit targets >=44px; no horizontal overflow detected in the *controlled masthead*.

A regression was caught during the first local test: the dropdown initially covered the Focus CTA in **4 of 7 mobile widths (320/360/390/420)** when open. The CSS was corrected to anchor below the full header, then **0 of 7** tested mobile widths covered the CTA, while all nine width conditions passed. Before/after controlled PNGs and JSON receipts are retained as founder review artifacts **outside GitHub**; these are not full-home or WordPress screenshots.

## Source-controlled exact candidate gate — BUILT, not executed
`tests/verify_mobile_explore_browser.py` loads the checkout's actual `index.html` and **all six actual stylesheets**, inlines them to avoid forbidden file:// navigation, disables JS/outbound network, validates source routes/chapter count, runs nine widths, native keyboard open/close, at-least-44px target bounds, horizontal overflow, and asserts the opened menu does **not** obstruct the Focus CTA. Results and screenshots go only to a disposable local directory. The existing isolated Assembler workflow is updated to run it after its pinned Python Playwright installation. Do not claim the full exact-source test passes until it actually runs.

## Required release gates
1. Execute the new exact-source browser gate on its exact branch HEAD; diagnose any failures. GitHub Actions currently often fails before starting runner steps.
2. Render anonymous visitors with actual isolated WordPress/Assembler and all 72 **published** Margins, without backend/production/database imports. Confirm native navigation, card image bytes, keyboard/no-JS/touch/200% physical zoom and complete-document axe WCAG 2.2 AA.
3. Measure Lighthouse/CWV rather than infer from isolated source. Confirm rights/provenance of Apollo/Franklin/NYPL images and full first-party image transfers.
4. Independent QD/CI on exact head, founder visual/release approval. WordPress.com Personal plan does not provide a second native staging clone. Free Playground ≠ WordPress.com hosting parity.
5. Distinguish confirmation of Focus subscriptions from actual paid orders/refunds/net revenue; leave campaign asset IDs and attribution to Grok/Praxxis/Claude and issue #820.

**OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER:**
Existing free 52-page Focus Fieldbook → homepage first-screen reader exploration → mobile primary navigation missing and its initial repair overlapped the Focus CTA → accessible no-JS Explore in source and dropdown below masthead → 9/9 controlled viewports + 12/12 exact-blob source assertions, full-source/WordPress pending → interim homepage engineering; Claude measurement/commerce; Grok/Praxxis acquisition.

**Release decision: HOLD.** No merges, deployments, WordPress content/theme/navigation/settings writes, plugin activation, emails, posts or spending. Frozen PR #49 and Apollo #158 untouched.
