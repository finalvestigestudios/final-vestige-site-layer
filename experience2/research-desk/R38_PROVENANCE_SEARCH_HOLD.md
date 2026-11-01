# Apollo R38 — searchable photograph provenance (DRAFT / HOLD)

Stacked on R37 draft PR #418, **not** homepage PR #49, Research Desk foundation PR #158, or the homepage lead. No WordPress, main, live-site, or paid-service writes.

## Integrated improvement
- Search indexes both the reviewed original card metadata and its human-readable photograph provenance/rights drawer. “Kim Shiflett” now returns source records 04 and 06; the previous index returned zero.
- Provide a visible, minimum 44px-high **Clear search** action, responsive touch sizing, keyboard Escape-to-clear, and focus restoration. The button and all search controls stay hidden without JavaScript.
- Navigation still restores a hidden evidence record before following its anchor. On malformed search metadata, the whole ledger becomes readable and registered listeners are removed; no stranded evidence.
- No source-card prose, historical claim, NASA destination, media-rights status, map coordinate/edge, or embedded image changed.

## Exact reviewed Git blob SHA-1
- `templates/ledger.html`: `4842afb84b4c993cfc4861ce7f5a7a4d7b451871`
- `assets/source-ledger.css`: `7b0972fc3a920ded08f9783fddcfc9c609c7ff06`
- `assets/source-ledger.js`: `57f4a639d4c37fc4355b10fe7dec085bf87c6eb7`

The actual NASA HTML differs from R37 only by the clear button. The original six article records are preserved verbatim. CSS is append-only; all six photo rights remain `INDIVIDUAL_REVIEW_REQUIRED`, with photographs linked externally.

## Reproduce against a full checkout
```bash
python -m unittest discover -s experience2/research-desk/tests -p 'test_r38*.py' -v
python experience2/research-desk/tests/browser_r38_provenance_search.py --output /tmp/fv-apollo-r38
```
The Playwright gate defaults to actual `templates/ledger.html` and CSS/JS. It captures 7 widths × JS/no-JS, checks keyboard/touch/escape/clear/provenance/fail-open/no overflow, and optionally runs an **existing, approved pinned** axe-core bundle with `--axe PATH`. Synthetic `--fixture` mode cannot approve release. The test explicitly marks hosted LCP/CLS/INP and HTTP CSP **NOT MEASURED**.

## Evidence this run
- GitHub private-source contract check: six NASA cards, drawers and chronology links, six rights holds, zero embedded photos or speculative geographic records; actual prose search matched records 04 and 06.
- **14/14 local Chromium Playwright cases PASS on a labeled synthetic fixture** (320/360/390/768/1024/1440/1920 × JS/no-JS); keyboard, touch, clear, Escape, no-JS and malformed metadata fail-open passed. **14/14 screenshot bytes matched** on repeated runs after normalizing persistent mobile `:hover` state. Local QA archive SHA-256 `ef13e3ae46a3651da0c05d6a0cb5454b51553b0d5c3cf7127ec8ae5a2c9456d1` (two byte-identical builds).
- **Not executed**: full-checkout Playwright/Python suite, axe-core (not installed), isolated WordPress/Assembler, hosted performance, header CSP, Safari/screen readers, CI and independent QA.

## Release blockers
Actual WordPress staging/shortcode and singular asset performance, authorized pinned axe-core, screen readers/Safari, hosted LCP/CLS/INP, individual NASA photo reuse decisions, independent editorial/QD, founder approval and green exact-head CI. Retain HOLD. NASA media guidance: https://www.nasa.gov/nasa-brand-center/ . NASA Apollo report: https://www.nasa.gov/apollo-1-resources/ . No speculation, deployments or WordPress settings changes.
