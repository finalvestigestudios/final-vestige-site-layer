# Apollo Experience 2.0 — R402 request-integrity acceptance

**DRAFT / HARD HOLD / not installed.** Isolated source-controlled QA change stacked exclusively on R401 PR #2715. Frozen homepage PR #49, Research Desk PR #158, Grok/Praxxis TASK-008 and Claude's commerce/analytics lane remain untouched.

## Reproduced gap and correction

R400's read-only browser intercept admitted arbitrary same-origin GET/HEAD paths. A denied request was aborted, but the presence of a denied request did not itself guarantee a failing acceptance verdict. Consequently an unreviewed endpoint, script, tracking pixel or absent asset could be hidden by a superficially passing gallery.

R402 narrows admission to exactly one canonical HTTPS Apollo staging document plus two reviewed versioned gallery stylesheets in the WordPress plugin's experience2 subtree. Its audit converts *every* denied request into a staging HOLD. The upstream R400 CSS SHA-256, CSP, genuine axe-core and R401 six-record NASA semantic/chronology/visibility protections remain required. Future legitimate theme resources must be reviewed individually; this deliberately strict rule may HOLD an ordinary WordPress staging render until that review.

No NASA photo, logo, unsupported geography, new merchant CTA, marketing pixel or JavaScript tracker is introduced. Nothing is installed or deployed, and release_allowed remains false.

## Test commands and limits

- python -m unittest discover -s experience2/apollo-r402/qa -p 'test_*.py' -v
- python experience2/apollo-r402/qa/network_custody.py --fixture experience2/apollo-r384/QA/local-php-fixture.html --out /tmp/apollo-r402-qa
- python experience2/apollo-r402/qa/pack_evidence.py

For a separately authorized installed staging check, supply a canonical URL, an exact --host, genuine independently pinned axe-core asset with its SHA-256, and an exact GitHub HEAD checkout. Never test against production.

**Executed evidence:** seven local unittest methods PASS using an archived shadow R400 runner, including five real Chromium resource-interception contexts (320, 390, 768, 1440 and 1920px), with two unauthorized resources blocked and flagged in each. The older gallery fixture also passed seven shadow-source contexts including keyboard, touch, no-JS, reduced motion, NASA source custody and zero horizontal overflow. The locally available R392 and R400 files are NOT byte-identical to their reviewed GitHub parents: label all results PASS_LOCAL_FIXTURE_SHADOW_DEPENDENCY_ONLY, not exact-head staging. No staging navigation, actual HTTP/CSP/CSS delivery, genuine axe-core, independent screen reader, native browser 400% zoom, hosted CI or production CWV was tested. The deterministic archive contains source, tests, receipt and screenshots, with no private visitor data.

## Source and conversion custody

NASA's 1967 [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) and [2018 later flammability testing retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) remain distinct: 102 deliberate tests occurred after the original fire, not during it. NASA's [image and media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) remains applicable; no images are reproduced.

Proposed only: Grok-approved Apollo documentary with genuine asset_id and approved UTMs → NASA Evidence Gallery → one nonintrusive [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) CTA → a future independently rights-cleared educator product *only after merchant SKU, fulfillment and founder authorization are verified*. Grok owns production/distribution; Praxxis creator review; Claude commerce/attribution. No confirmed qualified sessions, merchant orders, refunds or fees are available, so net revenue per 1,000 qualified human sessions is NOT COMPUTABLE.

Coordinate [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Production release is blocked pending exact-head CI, installed staging, real axe and screen-reader QA, QD and founder approval. No WordPress writes, merge, social post, merchant activation, tracking installation, email or spending.
