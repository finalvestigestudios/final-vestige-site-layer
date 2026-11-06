# Focus Fieldbook — no-JavaScript fragment navigation repair (review only)

**Date:** 2026-11-05. **Source:** connected WordPress.com production Page 1579 read at **modified 2026-11-03T14:36:15** in both `context=edit` and `context=view`. **Status:** PROPOSED / NOT TESTED ON ANONYMOUS LIVE SITE / NOT PUBLISHED.

## Reproducible source finding

The current editor-source Gutenberg body (31,683 characters) contains precisely one `<!-- wp:jetpack/subscriptions ... /-->` block and five subsequent `href="#subscribe-blog"` CTA anchors. It contains **zero literal `id="subscribe-blog"` targets**. Its existing inline script `fvf-signup-anchor-v1` installs the missing span at runtime. The REST view serialization (31,331 characters) likewise contains five fragment links and zero static targets; it renders the subscription action as a link to `?post_type=page&p=1579`, not a literal email form.

This means **the five fragment links have no static HTML target when JavaScript is off**. It does **not** prove that those links, the Jetpack button/modal or subscription confirmations fail for normal anonymous visitors. JavaScript may create the target and Jetpack may render a distinct public experience. Do not report a production lead failure without a browser check.

## Proposed bounded change

Run `node focus_1579_nojs_anchor_proposal.cjs --self-test` (expected positive 1, negative 6); use a privately held **public-only** Page 1579 Gutenberg edit-content export as input to the optional `--input INPUT --output NEWFILE` command. The tool refuses to overwrite the input, refuses unknown content, requires exactly one native Jetpack subscription block, and writes **only** a new local candidate. It inserts a single 134-character native Gutenberg HTML block immediately **before** the existing Jetpack block:

```html
<!-- wp:html -->
<span id="subscribe-blog" style="display:block;scroll-margin-top:5rem" aria-hidden="true"></span>
<!-- /wp:html -->
```

The existing JavaScript anchor installer already returns when `document.getElementById('subscribe-blog')` is present, preventing a duplicate. The five CTA links, subscription block settings, download link and other editorial copy remain byte-for-byte identical. Source transformation checked against the connected WordPress editor representation: original 1 Jetpack block → proposed 1; 5 fragment links → 5; static targets 0 → 1. The current published page is unchanged.

**This repair is small but consequential to keyboard and no-JS navigation**; it does not repair or validate the Jetpack form itself and does not assert improved lead conversion or revenue.

## Integrating with flagship staging without diluting governance

The present seven-chapter imported Playground Blueprint uses a local `fv-ex2-review` page with a direct `[fv_ex2_playground]` shortcode. Earlier #250/#637 private-preview harnesses expect a **different** `fv-ex2-playground-review` route and a nonce-protected iframe renderer. **They are not interchangeable release evidence.** The exact new Blueprint's five-step WordPress admission check is source-validated, but actual WordPress/Assembler execution, real image responses, Chromium visual reviews, complete axe, true zoom and measured Lighthouse remain outstanding. Do not mark the old harness PASS against the newer shortcode without a tested adapter.

The Blueprint also does **not** contain production Page 6 or its 72 Margins items or Jetpack. It cannot demonstrate the combined live subscriber journey.

## Browser acceptance before any release decision

1. On a network-capable **anonymous** browser, inspect actual `/focus/` at 320/390/1440px, with JS enabled **and** disabled, keyboard Tab and Enter, and screen-reader-meaningful focus. The five repeated CTAs must land at the real subscription control; the usable Jetpack UI must be observed, not inferred from REST markup. Never submit a real email without consent.
2. In a disposable WordPress/Assembler review using **public content only**, import the proposed block safely and verify that no duplicate `subscribe-blog` IDs appear in either mode and that the link target is not behind sticky chrome.
3. Independently verify direct PDF access and privacy/consent, then reconcile Jetpack confirmation/delivery with authorized records. These are not equivalent to a sale.
4. Return to the **full seven-chapter flagship** current-source staging admission. Do not take the page-level fix as a homepage acceptance substitute.

**Owner:** Claude/Jetpack content engineering for eventual block insertion after founder release approval; independent Site QA for visitor rendering; homepage lead engineer for proposal and chapter continuity; Grok/Praxxis remain social acquisition owners. **Release:** HOLD. No CMS writes, merges, affiliate activation, email sends, scripts or spending.

**Commercial contract:** OFFER: free 52-page Focus Fieldbook → STEP: five repeated in-page signup CTAs → BLOCKER: no static fragment target under JS-off → EXPERIMENT: one reviewed Gutenberg target block → EVIDENCE: source-level mutation + negative tests only → OWNER: Claude/Jetpack + Site QA. Verified paid orders, refunds and net revenue **not measured**.
