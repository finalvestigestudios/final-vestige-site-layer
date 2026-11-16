# Apollo Experience 2.0 — R413 EvidencePlate (isolated draft, staging OFF)

Founder Issue [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), business gate [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Independent of frozen homepage PR #49, source PR #158, and Grok/Praxxis creator task queue. No WordPress, analytics, merchant or publishing writes.

## Built

`staging-evidence-plate.php` exposes only `[fv_ex2_evidence_plate_r413]` when `FV_R413_ENABLED === true`, the WordPress environment is `staging`, and `FV_R413_STAGING_PAGE_ID` matches the current singular page. The component displays six documented questions with adjacent **what the record supports** and **what it cannot prove** passages. It uses the **exact original six-source R411 catalog** without copies, and pins the R411 adapter's Git blob SHA `efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`. The scoped `assets/evidence-plate.css` is pinned to Git blob `95aa879a118f15de35b7fd82d3f1e182fead002c`. A mismatch returns one plain public-article fallback. No JavaScript, local storage, vendor script, media, new email form, purchase button, geography, or tracking is used.

Each of the six plates has two independent same-origin NASA source links (research text + archive citation), user-visible uncertainty, unique fragment target and an accessible jump navigation. Native DOM is fully readable without JS, prints cleanly and retains source links. Exactly one **free Apollo investigation** next action appears in each component instance. The EvidencePlate can coexist with the R411 SourceDrawer; it does **not** overwrite either the earlier sources or original PR #158.

## Source and rights boundary

Original Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — the ignition initiator was not conclusively determined. Subsequent NASA Command Module boilerplate flammability tests: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — 102 ignitions occurred **December 1967 through February 1968**, after the January 1967 accident. NASA rights and non-endorsement: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . The component reproduces **no photographs, insignia or astronaut likenesses**, and does not imply NASA approval of FV or a future product. An image gallery remains excluded pending a per-asset permissions/credit manifest and independent review. No speculative Atlas pins or links.

## Executed local tests

From a checkout containing the exact R411 and R413 paths:

```sh
php experience2/apollo-r413/qa/test_contract.php
python experience2/apollo-r413/qa/test_browser.py
python experience2/apollo-r413/qa/package_evidence.py
```

Native PHP assertions: **25/25 passed**. Real Playwright Chromium: **7/7 methods passed** against actual PHP-rendered HTML using `page.set_content`, covering 320, 360, 390, 768, 1024, 1440, 1920px; keyboard anchor activation, touch, no JS, 400% root type, reduced motion, forced colors, print, source link restrictions and multi-instance IDs. **Eleven fresh screenshots** (seven widths + four conditions); zero horizontal overflow in each captured fixture. This is not installed WordPress staging. Browser `page.goto` remains administratively blocked even for data/file URLs, so **real navigated LCP/CLS, HTTP/CSP and axe-core remain NOT TESTED**, not pass. Screen readers, 400% browser zoom, and original PR #158 template integration remain pending. Local fixture has no paid checkout; attribution, leads and sales are unverified.

## Explicit release HOLD

Requires a fully authorized WordPress/Assembler staging installation, media rights review before any gallery, genuine axe and 320–1920px browser/device QA, actual HTTP navigated CWV measurements with 7/30-day traffic cohorts, exact-head CI, independent QD and founder approval. Do not merge, activate, deploy or modify WordPress, analytics, Grok/Praxxis queue, or money flows based on this branch.

Conversion hypothesis (UNTESTED): adult educators arriving from a genuinely published Grok Apollo source-led long-form asset will trust an evidence/uncertainty comparison enough to continue to the existing free Apollo investigation and later express qualified demand for a **separately verified** original teacher-ready evidence dossier. There is **no verified Apollo paid SKU**, no attributable qualified-human sessions, paid orders, refunds or net realized revenue; thus net revenue per 1,000 qualified sessions cannot be computed. Claude owns measurement/checkout, Grok creator distribution, Praxxis external review, founder release and spending approval.
