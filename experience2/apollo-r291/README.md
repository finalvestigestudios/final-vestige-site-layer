# Apollo Evidence Atlas R291 — native progressive custody disclosure and print legibility

**STAGING ONLY / DRAFT / HARD HOLD.** This R291 branch descends solely from Apollo R290 draft PR #2077 and does not edit homepage PR #49, Research Desk PR #158, production WordPress, Grok's assets, tracking, CMS settings, commerce or email. The WordPress shortcode remains `[fv_apollo_source_experience]`.

## Problem and controlled change

At 320–390px the four fully expanded Board-authority records add a long scroll journey before the NASA source gallery and the one contextual next action. The records are valuable, but imposing the entire custody ledger on every reader creates reading friction without evidence of increased qualified conversions. R291 keeps the material **available in a native `<details>` disclosure**. The January 28 EvidencePlate's direct fragment link auto-opens the closed disclosure and focuses the correct record in Chromium **without JavaScript**. Return links remain intact. The conflicting-date explanation, the two named NASA authorities and the single free investigation CTA remain visible without expanding it.

A genuine printed-PDF inspection exposed another issue: the print stylesheet set text to black while leaving the evidence-boundary background dark, harming contrast. R291 forces a white print background and black border for those boundaries. Printing from initially CLOSED details still includes all four dated Board records and clickable official source URLs; actual Chromium PDFs were extracted and checked.

Historical statements, NASA links, editorial-review flags, pin-free Atlas, and the immutable source hashes are unchanged. No NASA promotional imagery, new JS, tracking or merchant CTA.

## Source/rights custody

- [NASA original Review Board narrative](https://www.nasa.gov/history/Apollo204/narr.html): Jan 27 oral authority, Jan 28 meeting, Feb 3 written confirmation.
- [NASA original Board proceedings](https://www.nasa.gov/history/Apollo204/proceed.html): Jan 28 meeting; Jan 31 receipt of memo dated Jan 28.
- [Later NASA safety summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1): differently dates establishment. This later agency description is not independent eyewitness corroboration.
- [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): no implied endorsement and restrictions on agency identifiers and likenesses.

R291 reuses text links only, with unresolved historical reconciliation still marked pending editorial review. No invented geo pins/edges. Source links do not certify media rights.

## Execute tests from repository root

```
php -l experience2/apollo-r281/apollo-source-experience.php
php experience2/apollo-r290/qa/php_gate.php
python experience2/apollo-r290/qa/browser_gate.py /tmp/r291-inherited-browser
python experience2/apollo-r291/qa/source_controlled_gate.py /tmp/r291-source-controlled-browser
# strict HTTP+CSP+genuine axe gate intentionally fails closed on blocked environments:
python experience2/apollo-r290/qa/http_axe_gate.py /tmp/r291-http /path/to/axe.min.js
python experience2/apollo-r291/build_archive.py /tmp/Apollo_R291.zip /tmp/r291-source-controlled-browser
```

**Local results:** PHP 38/38 assertions, inherited Playwright 10/10, R291 source-controlled Chromium 10/10 over 320/390/768/1440/1920px with JS on/off, keyboard, touch emulation, reduced-motion, forced-colors at 320px, 200–400% root-text stress and no horizontal overflow or unexpected requests. Real Chromium print PDFs 2/2 preserve all four source actions, clickable NASA and investigation links, readable evidence-boundary contrast. Two independent screenshot runs matched SHA-256. The builder produces byte-identical archives from fixed input artifacts. These results are **offline browser QA**, not installed WP or field CWV.

**Release remains blocked:** genuine axe-core dependency unavailable (npm registry DNS failure); browser's actual local HTTP navigation `net::ERR_BLOCKED_BY_ADMINISTRATOR`; therefore HTTP/CSP/axe and navigation LCP/CLS probe exits 2 and records null, not a fabricated pass. Installed WordPress/Assembler/reusable-block acceptance, independent NVDA/VoiceOver, Safari/Firefox behavior, real zoom via browser UI, hosted CI exact head, independent historical/editorial/media-rights review, field p75 LCP/CLS, and founder approval are not verified.

## Conversion hypothesis / owner contract

**ONE next action in the historical narrative:** [read the free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). A shorter initial mobile reading journey **may** improve qualified investigation continuation; there is no observed conversion lift, and no paid order evidence. A later contextually suitable and disclosed Mini Museum guide remains contingent on verified merchant acceptance, buyer intent, fulfillment, affiliate terms, permitted marketing, fees and refunds. Grok owns YouTube/TikTok production and distribution, Praxxis external creator review, Claude production analytics and commerce, founder release and spending. Grok Apollo asset IDs / UTMs and realized net revenue per 1,000 qualified human sessions remain UNVERIFIED / NOT COMPUTABLE; do not invent tracking or classify clicks as paid sales. Cross-reference Issues #150, #820 and charter #818.
