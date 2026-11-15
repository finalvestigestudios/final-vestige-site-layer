# Apollo Experience 2.0 R387 — print-state invariant source custody

**BUILT and locally browser TESTED; staging installation NOT TESTED; NOT LIVE, merged or release-approved.** Independent Apollo staging sprint stacked only on R386 draft PR #2632. Do not merge R387 without its ancestors and their independent review. Frozen homepage PR #49, existing Research Desk #158, Grok creator work and Praxxis TASK-008 are untouched.

## Reproduced bug

R386 correctly mirrored six NASA source roles and six photographic-evidence limitations into printable source cards when all HTML `details` disclosures were closed. However, opening disclosures before printing caused their regular contents *and* the print mirror to render. Actual Chromium PDFs for **0, 3 and 6 disclosures open** contained **6, 9 and 12** copies respectively of each labeled custody field. A printout could therefore mislead educators about the number of independent records.

## Change

R387 adds one print-only `.fv-r384__drawer {display:none!important}` rule in the existing scoped CSS, leaving the six reviewed `.fv-r384__print-custody` mirrors visible. A new CSS hash is recorded in the existing R384 PHP seal, so tampering prevents staging style enablement. There is no change to NASA claims, source links, WordPress database, JSX, JavaScript, offer activation, copyright/media or geographic pins. The accessible on-screen native disclosures remain fully usable with keyboard, touch or no JavaScript. Printed source custody now comes from exactly one reviewed representation independent of disclosure state.

## Reproduction (local fixtures, **not** WordPress staging)

```sh
php experience2/apollo-r386/qa/contract.php
python experience2/apollo-r386/qa/browser.py
python experience2/apollo-r387/qa/print_states.py
python experience2/apollo-r387/qa/package.py
```

Prerequisites: PHP, Python `playwright`, PyMuPDF `fitz`, and Chromium at `/usr/bin/chromium`. R386 baseline retained; 38 PHP contract assertions and 179 original Chromium fixture assertions pass. R387 adds 126 Chromium assertions (five responsive widths, keyboard, touch, no-JS, closed/1/3/6-open print invariance), four independently generated real Chromium PDFs, source content comparison to sealed six-record NASA custody data, and deterministic QA screenshots. Print page count and all extracted text are identical across all four open states, with **six source roles and six limitations** in every state.

No real `axe-core` execution: genuine package is unavailable here. Browser a11y tree spot checks are not a substitute for axe or manual screen readers. No browser-over-HTTPS WordPress staging, CSP, paid merchant checkout, exact-HEAD hosted CI, real 400% native zoom or field LCP/CLS/INP has been tested. Old fixture LCP/CLS timings must not be represented as hosted CWV. **RELEASE HARD HOLD.**

## Sources and limited rights

- [Apollo 204 Review Board (NASA)](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): no single ignition source conclusively identified; electrical arc probable, not exact cause proven.
- [NASA's February 14, 2018 retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): the later 102 deliberate Command Module test ignitions occurred December 1967–February 1968, not in the original January 1967 incident.
- [NASA media-use conditions](https://www.nasa.gov/nasa-brand-center/images-and-media/): no NASA photos/logos copied; links do not confer commercial media licensing or endorsement.

## Acquisition to revenue, one controlled pathway

**Grok-owned approved Apollo documentary → NASA-backed Evidence Gallery → existing free Apollo 1 investigation → separately approved, independently verified educational kit.** No spoken commercial CTA, tracking changes or new signup. Future educational product, fulfillment, merchant approval and photo rights remain unverified; therefore no paid CTA is offered. Grok/Praxxis control creator asset IDs/UTMs under TASK-008. Claude/Commerce own checkout verification, 7/30-day cohorts, refunds and **realized net revenue per 1,000 qualified human sessions**. An outbound link is not a sale.

### Release governance

No merge, deployment, WP content/settings modification, analytics script, email, social post, merchant activation or spending. Installed WordPress/Assembler acceptance, genuine axe, screen reader and WCAG 2.2 AA review, real network/CSP and CI, independent QD and founder approval remain outstanding. Record exact GitHub HEAD and tested file identities in Issue #150 and cross-reference conversion charter #820.
