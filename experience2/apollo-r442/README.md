# Apollo R442 — origin-locked release evidence, not another story layer

**BUILT + OFFLINE TESTED. NOT INSTALLED, NOT LIVE, NO PAID PRODUCT APPROVAL.**

Independent Apollo Evidence Studio staging acceptance, layered after R441 draft PR #2931. This sprint repairs two gaps in the former test runner: (1) a local file merely over 25KB was accepted as axe-core without a reviewer-pinned checksum; (2) navigation could redirect or fetch off-origin materials without an explicit fail. It also makes paid-checkout absence, the exact free investigation link, five NASA evidence cards, the original educator preview and lab LCP/CLS explicit release assertions.

**Critical safety:** Only manually approved HTTPS staging origin; real source links are inspected but never visited. Browser network requests to all other origins abort and produce a HOLD. No login, consent popups, merchant interactions, staging installation, WordPress change, email or social posting.

## Local test and reproducible artifacts

```bash
python3 -m unittest discover -s experience2/apollo-r442/qa -p 'test_*.py' -v
python3 experience2/apollo-r442/qa/offline_regression.py
python3 experience2/apollo-r442/qa/staging_acceptance.py  # expected HOLD_NOT_RUN without approval
python3 experience2/apollo-r442/qa/package_evidence.py
```

Offline regression runs the **actual R440 PHP fixture** in Chromium at 320, 360, 390, 768, 1024, 1440 and 1920 pixels, with JS enabled/disabled, showing the original educator exercise and multiple independent instances. It is *not* full staging, axe or CWV evidence.

## Authorized navigated staging command (not run until approvals)

```bash
FV_APOLLO_STAGING_URL='https://approved-staging.example/apollo-review/' \
FV_APOLLO_APPROVED_ORIGIN='https://approved-staging.example' \
FV_AXE_CORE_JS='/reviewed/local/axe.min.js' \
FV_AXE_SHA256='<independently-reviewed-64-character-sha256>' \
python3 experience2/apollo-r442/qa/staging_acceptance.py --out experience2/apollo-r442/QA/staging
```

Must produce actual HTTP 200 with no redirect; one free CTA to the original investigation; five NASA-linked evidence records; one educator preview; zero payment links; no horizontal overflow or attempted off-origin load; **genuine, pinned axe-core WCAG 2.2 AA checks**; measured lab LCP <=2500ms, CLS <=0.1; no-JS meaning across seven sizes. Any missing test is HOLD, not PASS. Field p75 CWV, screen reader and QD review remain separate release gates.

## Editorial and business boundaries

Apollo 204 Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (probable electrical arc, no confirmed ignition source).
NASA brand/advertising: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ (no implied endorsement, distinguish linking from commercial image use).

Founder-approved Grok Apollo asset (NOT verified) → source-backed Research Desk/Atlas → original free educator preview → single free investigation → **possible** paid original teaching resource **only after** licensed deliverable, a functioning approved SKU/checkout and founder authorization. No unverified merchant conversion, tracking scripts, invented geography, NASA images or new CTAs. Exact purchased orders, settlements, refunds, fees, per-asset qualified sessions, 7/30-day cohorts: unavailable. Main KPI therefore NOT COMPUTABLE.

**Release HOLD:** R417 reconciliation, authentic staging with vetted axe, no-JS/keyboard/touch/screen-reader acceptance, field CWV, merchant and rights proof, independent QA/QD, exact-head CI and founder release signoff.
