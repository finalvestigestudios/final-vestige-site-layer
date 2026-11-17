# Apollo R437 — dated source-custody chronology / independent staging prototype

**Status:** BUILT, contract-tested, browser-tested offline only; NOT installed or approved for WordPress staging/production. Parent: R436 draft PR #2902 at commit `c0f7ce81dc6311eb43af9e1510064373bcb4f1d5` and Issue #150. All source changes are isolated in `experience2/apollo-r437/`. Homepage PR #49 and Research Desk PR #158 are untouched. No WP, email, traffic, merchant or social writes.

## Verified documentary distinction

Actual PR #158 HTML was read, as were the original R436 PHP/CSS and full inherited component chain. Historical presentations currently risk conflating **event date**, **report findings**, **later exhibit date** and **retrospective publication date**. R437 inserts a four-entry `<ol>` ChronologyRail directly into the independently source-pinned R436 evidence experience, before its original Source-Type Comparison, with each record identifying the type of date, a directly linked NASA source and an explicit evidence boundary. The 1967 Review Board entry uses **1967 only**, not an asserted precise release date, because the historical report signature/publication dates are easily conflated. The January 27, 2017 tribute and February 14, 2018 retrospective are expressly *later records*. No invented coordinates, relationship edges or archival media are included.

Primary research: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); [NASA Safety Office Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1); [NASA 2017 tribute](https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/); [NASA Feb 14 2018 flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/). [NASA advertising/media guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) precludes any inferred NASA endorsement or presumed clearance of astronaut likeness rights. We link, do not republish.

## Activation safety

Staging shortcode: `[fv_apollo_chronology_audit_r437]`. Requires `FV_R437_ENABLED === true`, a positive integer `FV_R437_STAGING_PAGE_ID`, `wp_get_environment_type() === 'staging'`, and the exact singular queried page. Verify Git SHA-1 blob identities of R436 PHP/CSS and SHA-256 of local R437 CSS/JS **before render or enqueue**; all path components reject symlinks, and the inherited R436→R429 verification chain remains authoritative. A missing, altered or unexpectedly loaded parent falls back to the free investigation. The original **one** full-investigation CTA and allowlisted public Grok UTM context remain untouched. Zero cookies, storage, new analytics, email capture, checkout code, or paid offer.

The small filter buttons are created **only by JavaScript**, with independent state per instance; absent JS, the full chronology, all source limits, citations and the free investigation are still visible. Native `<details>` remains keyboard/touch accessible; closed limitations remain visible in print via duplicate print-only text. CSS scopes styles locally, includes reduced-motion, forced colors, focus visibility, text scaling and 320–1920px layouts.

## Evidence, reproducibility and honest limits

Run from an adjacent checkout containing R429–R436 files at the Git identities pinned by those components:

```
python3 experience2/apollo-r437/qa/test_contract.py
python3 experience2/apollo-r437/qa/browser_qa.py
python3 experience2/apollo-r437/qa/staging_acceptance.py  # HOLD exit 2 until approved live staging URL and authentic axe bundle
python3 experience2/apollo-r437/qa/package_evidence.py
```

The local PHP server accepts HTTP 200 from Python `urllib`, **but Chromium `page.goto` is prohibited even for localhost** (`ERR_BLOCKED_BY_ADMINISTRATOR`). Playwright therefore renders the actual PHP output with `page.set_content`, exercises controls/keyboard/touch/no-JS/print/forced-colors, and produces screenshots. This is **not navigated browser acceptance**. We do not claim real LCP/CLS values or axe results. The separate `staging_acceptance.py` enforces actual HTTPS HTTP navigation, pinned **authentic** axe-core bundle and local lab LCP<=2500ms / CLS<=0.1 at seven widths; it deliberately holds without credentials and approval. Independent screen-reader acceptance, actual field p75 CWV, full installed WordPress theme/plugin interactions and QD review remain blocked.

## Commercial conversion hypothesis and experiment

**High-intent audience:** teachers preparing a primary-source history/safety lesson. **Offer:** original rights-cleared Apollo educator evidence dossier, not an authenticated paid SKU. **One allowed current action:** the free Apollo investigation. Potential funnel: Grok-approved Apollo long-form → four-step evidence trail → existing free investigation CTA → future approved educator dossier. Hypothesis: clearer source dates increase qualified teacher trust and subsequent purchase interest. Validation prerequisites: founder/Claude authenticate a currently payable SKU, rights/licensing, checkout, fulfillment and settlement, confirm published Grok `asset_id` and campaign URL, and use existing approved privacy-preserving measurement (no duplicate script). Track qualified humans → relevant CTA → confirmed lead where applicable → merchant-confirmed paid orders, refunds/fees, realized net per 1,000 human sessions, 7/30-day cohort uncertainty. Neither an outbound click nor a subscription equals revenue.

**HARD HOLD:** unresolved R417 identity discrepancy, actual WordPress staging, genuine axe and navigated LCP/CLS, field performance, screen-reader/independent QD, approved Grok asset, merchant readiness and founder release. Do not merge, deploy, edit WP, alter homepage branches or post externally.
