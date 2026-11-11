# Apollo R296 — compact NASA reconciliation / STAGING ONLY

Isolated stack on draft PR #2107 at `9f6a1879f53ff1d281ecc27e9edfce6967a24fa6`. No change to homepage PR #49, Research Desk PR #158, production WordPress, script/analytics ownership or Grok queue.

## Change and rationale
The existing three-document NASA establishment-date comparison consumes ~1,264px of additional vertical height in the 390px offline Chromium fixture, before readers opt in to compare those records. R296 uses a native `<details>` disclosure for the three longer source accounts. **The main January 27 vs January 28 discrepancy and editorial hold remain visible**, while NASA sources, their uncertainty/dependency labels, and the source URLs remain accessible to keyboard, touch and no-JS visitors. The full source accounts print in closed state. Only the existing free investigation is offered as a narrative CTA. No commercial promotion or map pins.

## Reproduce from repository root

```
php -l experience2/apollo-r281/apollo-source-experience.php
php experience2/apollo-r296/qa/compact_source_contract.php
python experience2/apollo-r296/qa/compact_browser_contract.py
python experience2/apollo-r296/qa/artifact_browser_qa.py
python experience2/apollo-r296/qa/php_cache_gate.py
```

Python Playwright and `/usr/bin/chromium` are required for browser tests; output screenshots and print are generated in `experience2/QA` by the artifact suite. A supplementary 136-assertion extended local browser suite was also executed; its source/receipt are separately preserved and are not needed to reproduce the checked-in compact tests. `php_cache_gate.py` checks CSS SHA-256 against version `r296-41ab84cba066` in both WordPress-enqueued and dynamic fallback paths. The R294 original cache suite hardcodes `r294-`, so this version-specific suite supersedes it, without changing its historical results.

## Actual local evidence / limits
Actual-PHP Chromium QA: 10/10 contexts, 136 assertions, 320–1920px, JS off/on, keyboard, touch, reduced motion, forced colors, 200% text, duplicate shortcodes, no horizontal overflow. Printed 7-page PDF retains all three NASA reconciliation records and active source links. At 390px offline fixture, collapsed height 4947px compared with 6210px on R295; this measures page compactness, **not** conversion uplift or real-user performance. Genuine axe-core unavailable; Chromium HTTP/CSP blocked by administrator, installed WordPress, independent screen reader, hosted CI and field LCP/CLS **unverified**. Founder/editorial release remains HARD HOLD.

## Historical source boundary and commerce
See NASA's original Board narrative, 1967 proceedings and the archived memorandum (https://www.nasa.gov/history/Apollo204/narr.html; https://www.nasa.gov/history/Apollo204/proceed.html; https://www.nasa.gov/history/Apollo204/15.html). The memorandum page heading supplies a date that is not separately signed in its displayed transcription. No NASA imagery or agency marks are incorporated. No NASA endorsement is implied. Business measurement under #820 must authenticate asset IDs, merchant orders/fees/refunds, and qualified sessions before reporting revenue.
