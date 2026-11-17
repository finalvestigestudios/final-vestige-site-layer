# Apollo R440 — Original educator preview and commercial proof HOLD

**Status: BUILT / LOCALLY TESTED / NOT INSTALLED / NOT LIVE / NOT APPROVED.** Independent staging-only WordPress shortcode `[fv_apollo_educator_preview_r440]`. This directory adds no changes to homepage PR #49, Research Desk PR #158, or R439; the user may place the R440 shortcode **after** the existing R439 Research Desk content on a separately approved staging page. Do not append a second article CTA: the R439 source path already provides it.

## Purpose and commercial truth

For the high-intent educator audience, R440 previews **one original source-analysis learning task**, an original instructor rubric, and a user-initiated text-only activity export. It directs readers to the **existing** R439 free investigation link and NASA sources. The proposal is an original classroom-ready Apollo 1 evidence dossier, not a currently purchasable SKU. The `product_evidence.json` proof ledger is SHA-256 pinned in PHP; all eight merchant/rights/distribution acceptance booleans are false and the paid URL/order/net fields remain `null`. Any unexpected change to it (or two own assets) fails open to a free article rather than displaying misleading commerce. A later actual paid CTA would require a separate reviewed PR and founder-approved rights/merchant proof; simply changing JSON cannot activate one.

The component neither submits data nor claims any sales, subscribers or attribution. It does not copy or sell NASA media. Direct sources: [1967 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [later flammability tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/), [NASA advertising and media conditions](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). Primary Board: probable electrical arc **not** one conclusively established spark; tests after the fire do not reconstruct its initial ignition.

## Installation gate (no current authorization)

The plugin is inert unless all of these hold: `FV_R440_ENABLED===true`, positive integer `FV_R440_STAGING_PAGE_ID`, WordPress `wp_get_environment_type()==='staging'`, singular query and exact queried page ID. `fv_r440_verify()` requires pinned SHA-256 of the manifest and both assets, rejects symlinks/path escapes; `fv_r440_offer_hold()` refuses changed/approved-looking merchant fields. It renders self-contained; it does not require or edit any R439 file. The companion R439 remains the source Atlas and one CTA. This is a **candidate**, not approval to edit a WP page or staging installation.

## Reproduce

From the repository root:

```sh
php -l experience2/apollo-r440/staging-educator-intent.php
python3 experience2/apollo-r440/qa/test_contract.py
python3 experience2/apollo-r440/qa/browser_qa.py
python3 experience2/apollo-r440/qa/staging_acceptance.py # expect HOLD exit 2 absent approved HTTPS staging and actual SHA-verified axe-core
python3 experience2/apollo-r440/qa/package_evidence.py
python3 experience2/apollo-r440/qa/package_evidence.py # same archive SHA if inputs unchanged
```

**Local QA evidence (2026-11-17 PT):** 27/27 actual PHP integrity, gating and corruption assertions; 105/105 actual Chromium assertions using PHP-rendered HTML via `set_content`, 14 screenshots at widths 320–1920 and accessible states, true browser `.txt` exports. `ERR_BLOCKED_BY_ADMINISTRATOR` blocks real navigated WordPress staging even on localhost; genuine axe-core unavailable; **LCP/CLS, axe WCAG, installed WP staging and field p75 are NOT TESTED**. Do not treat the browser assertions as genuine axe or a real staging visit. The navigated-staging runner returns exit 2 HOLD until explicit inputs are provided, and does not write to WordPress.

No deployed service, payment integration, email, analytics script, affiliate, social post, NASA media file, speculative map edge or third-party contact. R417 source reconciliation, real staging and QD review, product rights/seller/fulfillment proof, founder release approval and exact-head CI remain BLOCKED.
