# Apollo R361 — Embedded NASA rights-annex asset custody

Research-only, staging-only. Source: Issue #150; conversion governance: Issue #820; Research Desk PR #158. Stacked on R360, not on frozen homepage PR #49.

## Implementation

R360 styles only a singular post whose literal content has its rights-audit shortcode. Reusable blocks, same-theme template parts, explicitly assigned templates and R359-attested resolved default block templates could therefore render the nine-source audit without its CSS. The R361 adapter adds bounded, read-only detection for those cases. It accepts both R360 and R361 audit shortcodes, reuses the R360 stylesheet handle, adds zero JavaScript, and does not modify nine NASA links or their NOT_CLEARED_LINK_ONLY boundaries.

Missing or foreign theme records, altered template identities, recursive references and exceeded 500,000-byte/128-node/48-reference budgets do not authorize the stylesheet. Both aliases render the same documentary annex. This is asset discovery, not installed WordPress acceptance or media clearance.

## Reproduce

Run in repository root:

1. php -l experience2/apollo-r361/rights-asset-bridge.php
2. php experience2/apollo-r361/qa/wp_contract.php
3. python experience2/apollo-r361/qa/browser_gate.py
4. php experience2/apollo-r360/qa/contract.php
5. php experience2/apollo-r359/qa/wp_contract.php

The new PHP suite has 28 WordPress API-stub cases; the Playwright test uses real system Chromium at 320, 390, 768, 1440 and 1920 CSS pixels, covering keyboard, touch, no-JavaScript, 400% root text, forced colors, reduced motion, accessible names and printed NASA source URLs. LCP and CLS observations are synthetic page-set-content fixtures, NOT production Core Web Vitals. Genuine axe-core and independently installed WordPress/Assembler are NOT verified.

## Conversion-first spec (no publication)

Audience: source-critical history educators watching a Grok-produced Apollo 1 documentary. Proposed path: Grok long-form / Shorts → NASA Evidence Atlas with 1967 Board versus post-fire source classification → one nonintrusive CTA to FV's existing free investigation, The Hatch Opened Inward → separately approved Apollo educator evidence kit. The kit is only a candidate: no verified payable rights-cleared SKU or checkout. There is no purchase CTA, fabricated source claim, invented map geometry, or social publication.

Conversion hypothesis, not an observed result: independently inspectable source limitations reduce educator trust friction. Claude owns the existing consent/analytics stack and merchant verification; Grok owns asset_id and campaign distribution; Praxxis owns independent creator QA. If approved, record utm_source=(platform), utm_medium=organic_social, utm_campaign=history_pilot_2026_11, utm_content=(Grok asset_id), then qualified human landing sessions → free-investigation click → separately confirmed lead → verified paid order → fees/refunds → realized net revenue. Score 7/30-day cohorts and net revenue per 1,000 qualified-human sessions; never count clicks or signups as sales.

## HARD HOLD

Actual installed WordPress/Assembler, genuine axe/screen-reader, browser-enforced HTTP/CSP, hosted exact-SHA CI, NASA/media rights review, a verified commercial offer, and QD/founder approval remain mandatory. No merge, deploy, WordPress content/settings write, social posting, analytics install, merchant action or spending.
