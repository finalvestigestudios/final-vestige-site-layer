# Apollo Experience R303 — source-integrity failure is not a conversion (STAGING)

**Isolated draft / HARD HOLD / NOT LIVE**. Parent: R302 draft PR #2150, HEAD `2485bafd28bd7ad041fa3e607810e5aa321b91eb`. Engineering #150; business coordination #820 / charter #818. Never merge into or modify frozen homepage PR #49 or independent Research Desk PR #158. No WordPress writes, live scripts, publishing, spending or commercial activation.

## Actual change

A failure in **any** of the three existing source-custody validation gates (main event digest / allowlist, date reconciliation digest, Board authority ledger digest) now renders a visible, distinctive, CSS/JS-independent **source-integrity-failed** recovery rather than the previous generic unclassified fallback. The recovery withholds unverified historical evidence and offers only the pinned NASA Board report and the existing free investigation. Explicit passive machine-readable classifications distinguish an official noncommercial source from an editorial continuation. It does not record clicks, payments, leads or identities. Repeated recoveries get unique accessible landmark names. Historical event text and all NASA source URLs/digests, Atlas CSS, images and commerce destinations were not modified.

## Exact QA / reproduce

From the repository checkout with PHP 8+, Python Playwright, and Chromium `/usr/bin/chromium`:

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r301/qa/source_controlled_browser_gate.py
python experience2/apollo-r302/qa/source_controlled_browser_gate.py
python experience2/apollo-r303/qa/test_integrity_recovery.py
python experience2/apollo-r302/qa/verify_source_egress.py
python experience2/apollo-r303/build_archive.py
```

R303 test executes four adversarial temporary PHP mutations, including forged source URL, event text, date reconciliation and authority ledger. Each is forced through **actual PHP rendering** and **40 real offline Chromium contexts** (4 mutation types × 5 widths 320–1920px × JS on/off), including keyboard Tab, touch environment, reduced motion, no stylesheet, focus, no overflow, two repeated component instances, 160 source/editorial link-contract checks and 80 keyboard checks. Screenshots are of this **deliberately degraded source-failure state**, not a styled WordPress install. The inherited healthy source/print gate ensures an unmodified canonical record still renders full NASA chronology and a 13-page printed source appendix. No network access or third-party browser JS.

`build_archive.py` bundles actual tested PHP/CSS, runnable tests, healthy and degraded screenshots, print PDF, receipts and a SHA-256 manifest in a stable-entry ZIP. Run it twice to verify byte identity; do not assert deterministic screenshots on other OS/browser/font versions without an environment lock.

## Primary source and image/rights boundary

Board history: https://www.nasa.gov/history/Apollo204/narr.html . Proceedings: https://www.nasa.gov/history/Apollo204/proceed.html . Archival memo: https://www.nasa.gov/history/Apollo204/15.html . The original Board narrative dates oral authority January 27 and convening January 28; a January 28 memo is recorded as received January 31; February 3 confirms in writing. These are different documented acts, not independent eyewitness accounts. NASA permits factual linking without implying endorsement; separate approval restrictions apply to insignia, promotional use, and images: https://www.nasa.gov/nasa-brand-center/ . No images, logos, astronaut likenesses, speculative pins or map edges were added.

## Funnel / release

Grok/Praxxis authentic published Apollo asset_id and actual approved mobile landing → viewer inspects independently linked NASA custody → existing **free editorial** investigation → *only if separately approved and independently verified* a buyer-relevant owned or affiliate SKU. No currently approved Apollo-paid offer is established. CTA/source clicks are not sales; no revenue per 1,000 qualified human sessions can be calculated without validated 7/30-day cohorts, provider-confirmed orders, fees and refunds. Claude retains production analytics/checkout; founder retains commercial and release approvals.

**HARD HOLD:** genuine axe-core **NOT EXECUTED** (package unavailable in runner), native Chromium HTTP/CSP blocked, independent NVDA/VoiceOver and installed WordPress/Assembler acceptance **NOT VERIFIED**, field LCP/CLS/INP **NOT VERIFIED**, hosted CI statuses, NASA editorial rights, independent QD and founder release approval all required. Offline Chromium is not a substitute for these gates.
