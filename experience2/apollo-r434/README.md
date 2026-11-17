# Apollo R434 — compact evidence-first research route (draft only)

**Governance:** Isolated additive staging candidate stacked on R433 (commit `d9d2ddc1f49c3d3d318d73cbd270df3796bee2c0`), no homepage PR #49 or Research Desk #158 changes. Source charter: #150; conversion charter: #820/#818. No production authority, no WordPress write, affiliate/merchant activation, paid services, or Grok/Praxxis queue edits.

## Actual improvement

The R433 source Notebook buried the one free-investigation article link below long repeated source records and questions. R434 creates a **three-row scan-first evidence and chronology summary** from the actual upstream R433 source data and relocates, rather than duplicates, the original R429 allowlisted-UTM free-investigation CTA *above* a native disclosure containing the entire unchanged R433 provenance + R431 private classroom notebook. This is an editorial UX/conversion hypothesis, **not** evidence of any user conversion. Reading source limitations is never gated behind JavaScript or purchase. Sources inside the disclosure remain available via keyboard, touch and no-JS. No new map pins, NASA photos/logos, forms, scripts or paid controls. The only destination for the relocated CTA is the same verified original article. All NASA sources linked, no media copied.

## Pinning and fail-open

- R433 PHP exact blob `e48e577d0d14964ba77a86f5fc66db6f2c37a830`
- R433 CSS exact blob `548c3b479e5003a925babbdebbb43712443675a9`
- R433 delegates to R432's seven-object R429/R430/R431 inherited chain; reject symlinked/modified source, unexpected preloaded parent functions, out-of-range instances or changed CTA markup/URL.
- On gate failure serve the unchanged free investigation link. Local fixture may render only because the exact upstream files are present. Isolated shortcode `[fv_apollo_research_route_r434]` requires `FV_R434_ENABLED===true`, a positive integer `FV_R434_STAGING_PAGE_ID`, singular page match and `wp_get_environment_type()==='staging'`. Explicitly enable on **one approved staging page only**; do not install without the release decision.

## Reproduction

From the repo's `experience2/apollo-r434` folder:

```
php -l staging-research-route.php
python qa/test_contract.py
python qa/browser_qa.py
python qa/staging_acceptance.py  # EXPECTS exit 2 / HOLD without staging approval and reviewed axe
python qa/package_evidence.py
```

`qa/browser_qa.py` loads actual PHP-produced R429–R434 markup through `set_content` and checks 320, 360, 390, 768, 1024, 1440, 1920, focus/keyboard, touch, no JS, reduced motion, forced colors, enlarged text, exact article UTM, private TXT export, duplicate IDs, screen overflow, print and nonmerchant links. This is **offline Chromium**, not navigated WordPress QA. A separate approved-staging runner requires explicit HTTPS host, a locally reviewed pinned real axe bundle and successful `page.goto`, and records lab LCP/CLS. It fails closed rather than report synthetic performance. p75 field CWV, screen-reader QD, green exact-head CI, merchant custody and founder authorization are separate gates.

## Evidence and rights

NASA primary review: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (no conclusively identified spark; arc most probable). Later NASA account: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ (2018 narrative about later deliberate tests). Media guidance: https://www.nasa.gov/nasa-brand-center/ (no NASA endorsement; specific third-party and media rights require review). R158's six NASA photo identifiers remain **unreproduced** and have no approved commercial-media rights manifest. No geographic plot is warranted by this evidence presentation.
