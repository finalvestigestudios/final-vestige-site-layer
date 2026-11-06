# EX2 Focus destination — source-grounded no-JS conversion continuity gate
2026-11-06. Read-only, review-only. RELEASE HOLD.

## Exact source comparison
Authenticated WordPress.com `pages_get(slug=focus, context=view)`, site 256784396, page **1579**; modified **2026-11-05 17:44:02** (API timestamp). Public rendered **page-content fragment** contains 31,491 characters. This is not whole-document browser HTML.

* The hero promises a **free 52-page Focus Fieldbook**.
* It contains one `wp-block-jetpack-subscriptions` block.
* Its "Send me the fieldbook" anchor is `https://finalvestige.com/?post_type=page&#038;p=1579`, i.e., the same page by query URL.
* The rendered page-content fragment has **zero** `<form>` elements and **zero** `<noscript>` blocks.
* A PDF link appears under `<div id="fvf-gift" hidden role="status">`; that content is initially hidden.
* Browser-side Jetpack or theme code **might** enhance the link to a working subscription flow. This audit cannot rule that out. Equally, an anchor pointing back to the same page **does not** establish a usable no-JS conversion path.

## New executable source gate
`node --test experience2/home-flagship/qa/test_verify_focus_nojs_funnel.cjs` runs nine native Node tests, including same-page links, a hidden PDF, a no-JS fallback in a hidden ancestor, `noscript` content, HTML form, missing merchant promises and missing subscription block. The analyzer accepts a **locally supplied public rendered content fragment** and emits only source-level flags. It never sends email, uses network, changes WordPress or invents conversion events.

`node experience2/home-flagship/qa/verify_focus_nojs_funnel.cjs focus-rendered.html` exits **2 (HOLD)** for a self-link with no accessible no-JS form/PDF fallback in the content fragment. Even with a passing source result, `qualified_for_release` is always false; browser, accessibility and real Jetpack tests remain mandatory.

## Required staging checks / ownership
**Offer →** 52-page Focus Fieldbook. **Step →** high-intent homepage → `/focus/` → actual signup → verified confirmed lead → separate independently verified paid purchase. **Source-level blocker →** Jetpack-rendered subscribe link is self-referential with no form in the page-content fragment. **Experiment →** compare JS on/off by keyboard and touch on isolated WordPress/Assembler and then read-only public endpoint. If the JS-off experience loops, propose an accessible genuine fallback that does not require an unsafe test subscriber. **Pass/Fail →** actual focus transfer and signup/confirmation behavior are **NOT MEASURED**; source gate flags a potential dead end. **Owner →** Claude/Focus lead capture for production code and attribution; EX2 homepage and QA for destination/admission; founder for release approval. No sales claims.

Do not treat PDF clicks, outbound CTA clicks, simulated form submissions or unconfirmed email attempts as verified paid conversions. No new instrumentation. No subscriber creation. No live change. This PR is stacked on #1258, not on frozen #49.
