# Apollo Experience 2.0 — R389: direct NASA publisher custody + read-only staging acceptance

**BUILT; local PHP and Chromium fixture TESTED. Not installed on WordPress staging; not LIVE, merged, QD-approved, or founder-approved. HARD HOLD.**

Isolated Apollo gallery feature stacked on [R388 draft PR #2643](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2643). Homepage PR #49, independent Research Desk PR #158 and Grok/Praxxis TASK-008 stay untouched. Do not infer this prototype is installed on the **separate, already published** WordPress Apollo Evidence Atlas page (page ID 2017; read-only verification November 15, 2026).

## Defect and implementation

R388 distinguishes six evidence questions from **two NASA publications** but supplied only six in-page question jumps from the custody index. Readers could not open the original publication directly from that index; printed copies also lacked direct publisher URLs at that point. R389 adds exactly two direct source links and explicit type/date labels:

- **Publication A: original 1967 Apollo 204 Review Board investigation** — five distinct evidence questions based on a single investigation. [NASA original](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/).
- **Publication B: NASA Johnson Space Center retrospective of February 14, 2018** — the 102 deliberate Command Module ignitions from December 1967 to February 1968, which took place after the disaster and are not eyewitness records of the January 27, 1967 fire. [NASA retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/).

Links work without JavaScript, are native keyboard/touch links, use safe rel attributes, retain accessible text, and are exposed as full URLs in print. Original six card-level source anchors, six limitations, all three phases, and one free investigation CTA remain. Updated gallery CSS SHA-256 is sealed in PHP. No NASA photograph, logo, tracking script, speculative map pin, new email form or commercial product link is introduced. External links do not imply media licensing or NASA endorsement: [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/).

## Exact local QA reproduction

Run these from the GitHub checkout root (PHP, Python Playwright, PyMuPDF and Chromium required):

    php -l experience2/apollo-r384/document-gallery.php
    php experience2/apollo-r389/qa/contract.php
    python3 experience2/apollo-r389/qa/browser.py
    python3 experience2/apollo-r389/qa/test_staging_guard.py
    python3 experience2/apollo-r389/qa/package.py

- PHP source-custody and WordPress API stubs: **59/59 PASS**, including modified-source and forbidden-environment rejection.
- Playwright Chromium local fixture: **399/399 PASS** in 10 contexts covering 320–1920px, keyboard, touch, no JS, forced colors, reduced motion, fourfold root-font stress, original source deep links, full printed publisher URLs, and no horizontal overflow.
- Browser-generated print dossier: 5 pages, 6 source roles, 6 photographic limitations and two publication-level URLs retained.
- Production URL guard test: **7/7 PASS** (6 rejected unsafe URLs, 1 approved HTTPS staging example), zero network.
- Fixture PerformanceObserver LCP and CLS in QA/browser-results.json; **not hosted CWV**.
- QA/package.py creates reproducible screenshots, manifest with file hashes and byte-identical ZIP in QA. Binary artifacts are **not source-committed**.

## Installed staging acceptance — script exists, execution blocked

The new read-only qa/staging_smoke.py accepts an explicitly approved HTTPS staging hostname, refuses production finalvestige.com, mismatched hosts and credentials, and requires a separately obtained genuine axe-core JavaScript bundle with its reviewed SHA-256. The staged browser will collect HTTP/CSP, loaded stylesheets, computed CSS, LCP/CLS observations, real axe.run findings, five-width desktop/mobile screenshots, native no-JS evidence counts and a print PDF. No WordPress writes or outbound marketing clicks.

**NOT EXECUTED:** no approved installed WordPress/Assembler staging URL, no pinned axe-core asset available in this local execution environment, no independent screen-reader/native 400% zoom audit, no verified real browser network stylesheet delivery/HTTPS CSP, no hosted exact-HEAD CI, no independent QD or founder release authorization. Native 4x root-font simulation is **not** browser zoom.

## One conversion bridge, no invented sales

**High-intent audience:** educators and school librarians needing source-traceable Apollo 1 classroom investigations. **Future offer hypothesis:** original pedagogy and rights-cleared classroom case kit; payable SKU, delivery, licensing, checkout and approval are **unverified**, so no purchase CTA was added.

Proposed creator-to-customer route: Grok-approved Apollo long-form/Shorts asset with its *real* immutable ID and permitted organic-social UTM → Apollo source gallery → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → future verified educator offer → independently confirmed paid order → fees/refunds → realized net revenue. Praxxis independently reviews Grok attribution; Claude/Founder approve technical and merchant changes. Unrelated published affiliate pages are not appropriate Apollo tragedy CTAs.

**No confirmed Apollo-qualified-human session count, attributable paid checkout, lead, paid order, refund, fee or net revenue report exists for this test lane.** Net revenue per 1,000 qualified human sessions and 7/30-day cohorts therefore remain uncomputable. Conversion hypothesis (source clarity improves educator trust) is untested. Do not claim clicks or subscribers as sales.

**HARD HOLD:** no merge, deployment, WordPress content/settings change, media post, subscriber email, affiliate activation, analytics addition, paid service or production release until approved installed staging, accessibility QA, exact-head CI, QD and founder authorization. Post exact SHAs/tests/blockers to [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and cross-link [revenue control #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
