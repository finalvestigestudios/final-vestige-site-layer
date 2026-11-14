# Apollo R349 — shared source-page quarantine across the full evidence experience

**DRAFT / research staging / NOT live.** Stacked on R348; no homepage PR #49, Research Desk PR #158, Grok queue, production WordPress, merchant, analytics or email changes.

## Defect and engineering decision

R348 correctly withheld unreviewed URLs **in its Source Custody Drawer**, but R339 ChronologyRail, R340 accession gallery, R345 EvidencePlates and R347 index could independently render the same changed/unapproved URL as a clickable source. This was a cross-component source-laundering loophole. R349 installs one exact-address policy in `source-policy.php` and uses it across all five rendered evidence surfaces (including print copies). The R348 crosswalk now derives its eight source-page identities from the same policy. A new NASA path, query, fragment, hostname lookalike, executable URL or a missing policy cannot acquire an outbound evidence link accidentally. Textual evidence and limitations remain visible, and the existing single editorial continuation survives.

This is **not NASA rights clearance** and is not approval to reuse photographs, marks or third-party material. The eight addresses are historically reviewed source-page identities, not eight independent reports. Link destination redirects and later NASA page changes still require fresh editorial inspection.

## Reproduce, offline

From the repository root (PHP 7.4+, Python 3, Playwright with Chromium, PyMuPDF, BeautifulSoup):

```sh
php -l experience2/apollo-r349/source-policy.php
php experience2/apollo-r349/qa/preflight.php
python experience2/apollo-r349/qa/browser.py
python experience2/apollo-r348/qa/acceptance.py
```

`qa/preflight.php` rejects unsafe identities, while `qa/browser.py` runs eight genuine Chromium screen/print contexts from 320 to 1920px. A larger temporary-filesystem mutation suite is included in the external reproducibility archive, not this draft PR. Artifacts under untracked `QA/` include screenshots, native PDF and JSON receipts. Does not contact NASA or any commerce service. Local LCP/CLS are fixture observations, not production metrics.

## Release gates outstanding

Real installed WordPress/Assembler/reusable-block acceptance, genuine axe-core (not installed in this offline runtime), independent screen readers, Firefox/WebKit, native HTTP/CSP, exact-head CI, source/media-rights editorial approval, verified Grok source/asset ID and a legitimately payable rights-cleared product, and founder/QD release authorization. **No deploy, merge or new purchase CTA.**

Conversion pathway remains Grok-produced Apollo long-form → source-backed landing → existing free Apollo investigation → an approved, separately verified educational offer. CTA clicks, leads and affiliate outbound clicks are not paid orders. Net revenue per 1,000 qualified human sessions cannot be computed without verified sessions, settlement, fees and refunds.
