# Apollo Experience 2.0 — R386 printable source custody

**Staging-only draft; not installed, merged, deployed or founder-approved.** Isolated Apollo change stacked on R385 PR #2626. Homepage PR #49, Research Desk PR #158, Grok and Praxxis TASK-008 are untouched.

## Reproduced defect and source-controlled fix

R384 renders the six reviewed NASA source roles and photographic limitations inside native HTML `details` drawers. In a Chromium PDF print with all drawers closed, their contents disappear: baseline **0/6 printed source roles and 0/6 printed photographic limits**. This materially weakens a printed educator/research dossier.

R386 adds a print-only duplicate of the existing, source-verified `evidence_role` and `catalog_note` fields for each card, hidden from screen and ordinary speech output. Print styles show all six fields without needing to open drawers, and display the full original NASA source URLs taken from existing links. No JavaScript or extra tracking, checkout, visual media, NASA logos, coordinates, or geographic connection edges are introduced. Existing three phases, six questions, native interactions and the single free investigation CTA are unchanged.

Changed only: `experience2/apollo-r384/document-gallery.php` and `experience2/apollo-r384/assets/gallery.css`, including the CSS integrity checksum. R386 adds local PHP stub and Chromium Playwright regression tests and a deterministic evidence packager.

## Local reproduction

```sh
php experience2/apollo-r386/qa/contract.php
python experience2/apollo-r386/qa/browser.py
python experience2/apollo-r386/qa/package.py
```

Requires the reviewed `experience2/apollo-r377/custody.json`, PHP, PyMuPDF, Playwright and Chromium at `/usr/bin/chromium`. Contract checks **38/38** passed; real local Chromium fixture checks **179/179** across ten 320–1920px contexts (keyboard, touch, no-JS, reduced motion, forced colors and 4× root-font stress); printable PDF preserves **6/6** exact source roles, **6/6** exact photographic limits, five printed Board URLs and one later-testing URL. Source records are checked against the sealed reviewed JSON and checksum. Local fixture LCP/CLS observations are **not** hosted Core Web Vitals.

A before/after regression is preserved in QA artifacts: unmodified R384 with drawers closed = 0/6 and 0/6; changed R386 = 6/6 and 6/6. The fixed PDF includes source URLs as visible text for offline print.

## Historical records / rights

- Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — the exact ignition source was not conclusively identified.
- NASA 2018 testing account: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — later flammability ignitions must not be conflated with January 1967.
- NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — no NASA photographs or logos are reproduced; linking is not media licensing or endorsement.

## Release and commerce HARD HOLD

This was offline browser QA on PHP-generated local fixtures, **not installed WordPress/Assembler**. Chromium localhost HTTP navigation is administratively blocked in the execution environment, and genuine axe-core is unavailable here. Browser-enforced HTTPS/CSP, native 400% browser zoom, independent screen-reader review, installed staging, exact-head hosted CI and independent Quality Director/founder approval remain mandatory. No analytics, WordPress, merchant, social or production writes.

Conversion hypothesis: a portable, accurately cited source dossier improves trust for history educators following Grok's Apollo documentary to the free Apollo investigation, then potentially a future rights-cleared educational kit. **No payable Apollo SKU or checkout has been independently verified; no purchase CTA is offered, and no uplift, paid orders, net revenue or qualified attributed sessions are claimed.** Founder and Claude own offer validation and production; Grok/Praxxis retain creator ownership.
