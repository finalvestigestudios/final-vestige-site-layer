# Apollo R445 — preserve creator campaign context without manufacturing a sale

**BUILT and LOCAL TESTED; NOT INSTALLED; NOT LIVE; STAGING QA / AXE / NAVIGATED LCP + CLS / SCREEN READER / REAL CUSTOMER OUTCOMES: NOT RUN.** Isolated additive draft stacked on R444. Source of truth: [Apollo Experience #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and [qualified revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), governed by [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Do **not** touch frozen homepage PR #49, source Research Desk PR #158, Grok/Praxxis TASK-008, WordPress, analytics, checkout or merchant settings.

## Why

A creator video may send a visitor to Apollo source evidence with four privacy-conscious campaign identifiers. The original Research Desk/Atlas preview links to the free complete investigation, but navigating without an approved safe continuity mechanism drops the campaign context. This is only a **hypothesis about attribution continuity**, not proof of qualified human visits, any email subscriber, a merchant purchase or net revenue. We preserve one contextual research CTA **without adding any tracking, cookies, redirect, third-party service, sign-up or checkout**. We do not pretend the example asset ID is a published Grok video.

## What it does

- PHP adapter `bridge.php` uses **exact SHA-256 source custody** over prior R444 renderer, CSS and JS. It renders R444's five NASA-linked, chronologically labelled source records, native disclosure drawers and optional filter without editing its files.
- Strictly accepts **all four or none** of `utm_source=youtube|tiktok`, `utm_medium=organic_social`, `utm_campaign=apollo_pilot_YYYY_MM` (calendar month 01–12), and `utm_content=<6–80 safe alphanumeric/_/- characters>`. This only validates syntax, **not** existence of the post or campaign. Query order canonicalized. Duplicate/partial/invalid/too-long tokens drop all campaign tags. Extra visitor params, emails and click identifiers are never copied.
- Keeps the original fixed internal investigation URL and **one** R444 free-investigation CTA per rendered instance. Never inserts links to an unapproved product. Unverified offer=HOLD.
- Staging WordPress shortcode `[fv_apollo_campaign_bridge]` registers **only** when `wp_get_environment_type() === 'staging'` and the explicit `FV_APOLLO_R445_ENABLE_STAGING` constant is true. It never registers under `production` and does not write WordPress content/settings. Pre-head `wp_enqueue_scripts` handles ordinary singular-post shortcode content; nested/reusable/dynamic template cases require separate real staging QA (do not claim passed).
- On source/asset corruption, outputs only the original untagged free article link. No JavaScript: all evidence is visible. No location pins, NASA photographs or insignia are introduced.

## Source, rights, editorial boundaries

- [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): an electrical arc was the most probable initiator, **not** a conclusively identified single ignition source.
- [NASA, Feb 14, 2018 later flammability account](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): later tests do **not** identify the original spark.
- [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): no NASA endorsement and image/likeness/insignia restrictions may apply. R445 reproduces no NASA media.
- Public Atlas review-status discrepancy, historical interpretation/QD signoff, commercial photo rights and earlier R417 source discrepancy remain HOLD. R445 is a transport-only conversion-support enhancement, not a new historical approval.

## Reproduce locally

```bash
php -l experience2/apollo-r445/bridge.php
python -m unittest discover -s experience2/apollo-r445/qa -p 'test_*.py' -v
python experience2/apollo-r445/qa/browser_qa.py
python experience2/apollo-r445/qa/package_evidence.py
```

Must execute from repo directory containing unchanged `experience2/apollo-r444/`. Requires PHP 7.4+, Python, Python Playwright, BeautifulSoup and Chromium at `/usr/bin/chromium`. All test queries use **synthetic** asset IDs; no network or published social post. `page.set_content` tests real PHP-rendered markup in Chromium at 320/360/390/768/1024/1440/1920, both JS/no-JS, keyboard/touch and supplementary forced-colors/HiDPI/print captures. Do not label this navigated WordPress testing. This environment blocks `page.goto` with `ERR_BLOCKED_BY_ADMINISTRATOR`, and does not have a reviewed genuine axe-core file. Thus real staging, real axe, navigated LCP/CLS, field CWV and screen-reader QA remain **HOLD/NOT RUN**.

## Release sequence (not authorization)

(1) Grok/Praxxis provide real publicly verifiable immutable asset_id, platform, asset URL and allowed caption/pin/bio destination, (2) Claude validates first-party privacy-safe attribution without duplicate trackers and verifies merchant product/rights/checkout/fulfillment if a commercial offer is later proposed, (3) run exact-head CI and authentic independent WordPress staging QA with reviewed axe bundle and navigated CWV, (4) QD editorial/source rights reconciled, (5) explicit founder release approval. No merge, deployment, post, email or spending authorized by this draft.
