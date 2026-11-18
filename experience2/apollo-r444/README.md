# Apollo R444 — editorial signoff is not source identity

**Status:** BUILT / LOCAL PHP + Chromium TESTED / NOT INSTALLED IN WORDPRESS / NOT LIVE / NOT EDITORIALLY APPROVED. This is an isolated Experience 2.0 Apollo 1 staging-only component proposal. Issue #150; conversion governance #820 / #818. Does not edit or merge homepage PR #49, Research Desk PR #158, public WordPress page 2017, Grok/Praxxis TASK-008, Claude analytics or any merchant.

## Why this sprint

Read-only prior R443 review found that the **published**, separately implemented Apollo Evidence Atlas page (https://finalvestige.com/apollo-1-evidence-atlas/) displays two `Atlas review status: Not yet reviewed.` labels alongside separate source-crosswalk `verified` language. This does not make its historical claims false, but it leaves source identity and independent editorial signoff ambiguous. Do not silently change live content. R444's proposed standalone panel explicitly separates **NASA source identity checked** from **historical interpretation independent QD pending** and **commercial image rights not cleared**.

## Component

- Pure PHP renderer, `[fv_apollo_review_trail]` staging shortcode adapter; manifest digest-pinned `source_manifest.json`, CSS and JS; fail-open original free-investigation link when manifest/asset integrity fails.
- Five chronological source-backed findings from NASA Apollo 204 Board and 2018 retrospective, every claim with source and what it *cannot* establish. Classification distinguishes 1967 findings from a February 14, 2018 later account. No invented date of 1967 Board report publication.
- Native `<details>` SourceDrawer; optional three-state All/1967/Later filter. Without JavaScript all five findings and limitations remain readable; keyboard, tap, multi-instance isolation and reduced motion are supported. No image reproduction, geo pins, signup forms, marketing events or paid checkout.
- Only contextual next step: existing free `The Hatch Opened Inward` investigation. The suggested original educator product remains **unapproved**, not advertised.

## Run exactly

`php -l experience2/apollo-r444/review_panel.php`

`python -m unittest discover -s experience2/apollo-r444/qa -p 'test_*.py' -v`

`python experience2/apollo-r444/qa/browser_qa.py`

`python experience2/apollo-r444/qa/package_evidence.py`

Python Playwright and `/usr/bin/chromium` are required for offline browser test only. No network calls or paid tools. CSS/JS external enqueue from within shortcode is a **staging integration risk** when shortcodes render after the document head; test ordinary posts, reusable pattern, template part and dynamic block and inspect asset loading under Assembler/Jetpack before release.

## QA boundaries

Local browser navigation (including `file://` and localhost) returns `ERR_BLOCKED_BY_ADMINISTRATOR`. Accordingly Playwright's Chromium assertions use `page.set_content` with actual PHP fixture output. **This is not navigated WordPress staging** and cannot validate genuine axe-core, LCP/CLS, field CWV, browser CSP, or a screen reader. Each is **NOT RUN / HARD HOLD**, not PASS. The 320–1920 screenshots show isolated fixture behavior, not a live page. Await approved HTTPS staging URL and a reviewed exact-digest axe bundle. R417 upstream source discrepancy also remains unresolved; prior stacked PRs remain draft.

## NASA sources and rights

1. [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): most probable arc, **not conclusive** origin, oxygen/pressure conditions.
2. [NASA Feb 14, 2018 flammability history](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): later 102 deliberately initiated CM tests, not original-ignition proof.
3. [NASA advertising and media rules](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): no implied endorsement, astronaut likeness and image restrictions may apply; absence of image use here is not clearance for a future commercial product.

## Release gate

Founder-approved art direction and staging destination; independent editorial reconciliation of the two public labels; reviewer-backed source + media rights; real approved staging with Playwright, native accessibility and axe, 320–1920 and real LCP/CLS; R417 reconciliation; exact-head green CI, QD and founder approval; merchant/offer/fulfillment evidence before paid CTA. **No production write or social distribution authorized.**
