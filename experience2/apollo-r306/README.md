# Apollo 1 Evidence Atlas R306 — Source Receipt Before Editorial Continuation

**Staging only / hard hold.** Stacked on independent Apollo R305; no homepage #49, Research Desk #158, WordPress, commerce, analytics, Grok queue, or production changes.

## Changed behavior

The existing single free Apollo investigation continuation now follows a **native source receipt disclosure** inside the same footer. It routes to three preexisting official NASA source catalogue entries, preserving each editorial source ID and claim key. Native `<details>/<summary>`, in-page fragment anchors and focusable catalogue destinations work with JavaScript and component CSS disabled. The receipt is closed initially to avoid additional mandatory reading before continuation. It explicitly distinguishes NASA institutional records from independent witnesses, and rejects photographic ID → claim proof / commercial image rights inference.

This is a trust/retention hypothesis, **not a demonstrated paid conversion**. The only on-site next action is the unchanged free investigation URL. No tracking, posts, merchant link or revenue event is created. Relevant commercial product/checkout are **unverified and held**.

## Reproduce

From repo root with `php`, Python Playwright, and executable Chromium installed:

`python experience2/apollo-r306/qa/source_receipt_contract.py`

The separate downloadable evidence package also includes extended `gate.py`, screenshots at 320/390/768/1440/1920, 390px CSS-free/no-JS screen, a print PDF, source SHA and a manifest. It includes two component instances to detect duplicated IDs and ambiguous native disclosure labels.

## Release blockers

Genuine axe-core (unavailable under local DNS restrictions), installed Assembler/WordPress, actual browser HTTP/CSP, independent screen-reader review, production/field LCP/CLS/INP, independently approved NASA media/rights and editorial acceptance, CI on exact head and founder release authorization. Do not deploy. NASA source links remain noncommercial references; source clicks, continuation clicks, confirmed leads, paid orders and net revenue are separate events. Business coordination: #820, charter #818; owner boundaries preserved.
