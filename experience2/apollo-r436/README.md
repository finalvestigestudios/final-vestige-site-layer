# Apollo R436 — verified source-type crosswalk (STAGING ONLY)

**Status:** BUILT and locally tested, NOT installed, NOT approved for deployment. Scope is strictly `experience2/apollo-r436/`, stacked on Apollo R435 draft PR #2897 (`8635744d2a354f765a3c9096a119f6fa6d8589c3`). No changes to homepage PR #49, Research Desk PR #158, Claude analytics, or Grok's TASK-008.

## Primary finding and actual-code defect

Read the source in PR #158, specifically `templates/ledger.html` (`403d128c57b9bc82dac7c619651689070edef86c`). Its `EVIDENCE 03` uses NASA image `S66-58038` next to an instrument chronology; `EVIDENCE 02` uses preparation photo `S67-15717` next to an oxygen-pressure finding. These photographs do NOT document those instruments or fire test readings. R435 corrected the classification into six dated photo records, but its crew-image catalog entry inherited an unverified `S67-19766` number while the linked NASA image page does not itself establish that number. R436 conservatively displays **"Crew photograph / catalogue ID not confirmed"** instead, pending specific cross-catalog proof.

R436 adds a native, expandable three-column comparison that separates (1) dated photo context (1966–67), (2) the contemporary Apollo 204 Review Board investigation (April 1967), and (3) a 2017 retrospective memorial exhibit. The official Board says an electrical arc was the **most probable** initiator; **no single original ignition source was conclusively identified**. The prior prominently positioned free article CTA remains the **only** internal next action. No new product, offer, signup, map, photograph, instrumentation, JavaScript or tracker.

## Verified sources and rights boundaries

* NASA Apollo 1 image index: https://www.nasa.gov/gallery/apollo-1/
* NASA Apollo 204 Review Board determinations: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html
* NASA 2017 exhibit announcement: https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/
* NASA Apollo 1 Crew Honored photo page (no stable ID verified from this page): https://www.nasa.gov/image-article/apollo-1-crew-honored/
* NASA commercial and attribution guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

**No NASA image is downloaded or embedded.** Source links do not constitute a commercial-use permission or NASA endorsement; image-specific and likeness rights remain to be reviewed if paid materials are proposed.

## Integration and custody

Shortcode: `[fv_apollo_source_proof_r436]`. Enable only after approved nonproduction review by defining `FV_R436_ENABLED=true` and a specific integer `FV_R436_STAGING_PAGE_ID`; WordPress must report `staging`, singular page and matching current queried object ID. No enabling code is committed and no WordPress settings are changed.

R436 refuses to render if parent R435 PHP/CSS/catalog Git blob SHA-1s do not match its pinned tuple, if a component path is symlinked or escapes the expected tree, or if R436's own CSS SHA-256 changes. The inherited R435→R429 ancestry remains independently pinned by its own gates. On missing or altered sources, the shortcode retains a usable link to the original free Apollo investigation. Native details are accessible without JavaScript; multiple instances have independently numbered IDs from the parent.

## Repeatable local tests

```bash
cd experience2/apollo-r436
php -l staging-source-proof.php
python qa/test_contract.py
python qa/browser_qa.py
python qa/staging_acceptance.py  # intentionally exits 2 / HOLD without approved staging URL, host and axe bundle
python qa/package_evidence.py
```

* 22/22 PHP/static source-gate/mutation assertions including changed upstream PHP and own CSS.
* 72/72 real Chromium **offline `page.set_content`** assertions, 14 screenshots across 320, 360, 390, 768, 1024, 1440 and 1920 plus keyboard, touch, disabled JS, forced colors, reduced motion, 200% text and print.
* Browser `page.goto` to localhost returns `ERR_BLOCKED_BY_ADMINISTRATOR`; this means navigated **LCP, CLS, axe-core and installed WordPress staging acceptance are NOT TESTED**, not passing. A fresh real HTTPS staging runner enforces an approved host and SHA-pinned authentic axe bundle before testing.
* No CI claim without exact-head GitHub status/workflow evidence. Previous R417 integrity discrepancy also remains open.

## Commercial pass/fail

Intended high-intent visitor: history educators from an approved *actually published* Grok Apollo documentary. One path: verified Grok asset/campaign → source-checked Apollo evidence → original free investigation CTA → **future independently approved, rights-cleared original educator dossier if and only if sellable**. Do not place a paid CTA without verified SKU/checkout/fulfillment. Measure net realized revenue/1,000 qualified-human sessions with approved existing instrumentation and verified merchant orders, fees and refunds. Not computable now.

Release: HARD HOLD pending real approved HTTPS staging, authentic axe, navigated LCP/CLS and CWV, independent screen-reader/QD, original R417 reconciliation, product/rights acceptance and founder approval.
