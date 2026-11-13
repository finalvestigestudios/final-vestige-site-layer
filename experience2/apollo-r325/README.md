# Apollo Evidence Atlas R325 — touch-ready NASA source navigation

**Staging-only / not installed / not live / production HARD HOLD.** Stacked only on R324 draft #2280 (head `d09451e4c4f191145bdcbe5bf264a2fe8d083842`). No edits to frozen homepage #49, Research Desk #158, creator queue, WordPress, analytics or merchant accounts.

## Defect and bounded implementation

Genuine Chromium measurement of the R324 CSS found eight cited NASA links with 19–22px high clickable boxes in the 1440px fully expanded research view. These long, inline links have narrow touch targets and are difficult to activate precisely; WCAG 2.2 does include exceptions for links within running text, so this is a verified *usability defect*, **not** a claim of a certified WCAG violation. A screen-media-only, `.fv-r281`-scoped rule increases `a[data-fv-link-purpose]` target heights to 44px, preserves natural wrapping and native keyboard navigation, and leaves printed source URLs unaffected. The CSS version in the PHP loader was updated to match reviewed CSS bytes; no historical statements, NASA destination, commercial CTA, JS, media or geo pin was changed.

## Reproduction and status

From the repository root, with PHP, Node, Python Playwright and local Chromium:

```
python experience2/apollo-r325/qa/touch_source_links.py
python experience2/apollo-r324/qa/release_readiness.py
```

The new test uses 14 actual Chromium width/JavaScript contexts at 320, 360, 390, 768, 1024, 1440 and 1920px. Each checks every documented NASA link's rendered target dimensions after expanding native disclosures, center-point hit testing, keyboard focus outline, no horizontal overflow, single free investigation CTA, image-rights metadata and no invented location/media. It also exercises forced colors and 200%-type configurations. A source-controlled negative control verifies the *exact* R324 stylesheet Git blob and reproduces the short link boxes before checking the correction. The inherited R324 14-context regression tests (source URLs, print-PDF link neutrality, source AX names and four deliberate bad mutations) also pass after updating its exact source pins.

Local result: **14/14 R325 Chromium contexts passed; 8 old short-target witnesses; 2 additional accessibility profiles passed; 14/14 inherited R324 contexts and 4 negative mutations passed.** These are offline fixtures, not an installed WordPress/Assembler/CDN or native HTTP/CSP acceptance. Genuine axe-core, NVDA/VoiceOver, Safari/Firefox, field LCP/CLS and hosted CI are **not verified**. No sales or paid product performance has been measured.

## Revenue-first release contract

One future path only: Grok-published Apollo documentary (URL and asset ID still unverified) → verified NASA source Atlas → original *free* Apollo investigation → only after founder/rights/merchant approval, a separate relevant educational evidence product. The screen-media improvement reduces source inspection friction, not a verified increase in paid conversion. No monetization in accident chronology. No net revenue/1,000 qualified humans can be computed without independently reconciled sessions, paid orders, fees and refunds.

**HARD HOLD:** actual axe-core, screen readers, native HTTP/CSP, real WordPress/Assembler/CDN, CI green at exact head, independent NASA/media-rights and QD review, authenticated SKU/checkout, campaign ID and founder approval. Issue #150 is engineering custody; #820/#818 are the conversion contract.
