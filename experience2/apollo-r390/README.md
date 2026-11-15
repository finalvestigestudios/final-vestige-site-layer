# Apollo Experience R390 — fail-closed staging-origin and stylesheet custody

**Draft-only source. BUILT and locally TESTED. NOT installed, LIVE, merged, CI-green, axe-audited or release-approved. HARD HOLD.**

Base: isolated R389 draft PR #2648, exact parent commit `2a376b0926dfba86c6f4e2864acddc3c401fb592`. This patch modifies only `experience2/apollo-r389/qa/staging_smoke.py` and adds `experience2/apollo-r390/` QA/docs. It does **not** edit frozen homepage PR #49, Research Desk PR #158, Grok's production queue, WordPress pages/settings, paid services or tracking.

## Why this is a blocker, not polish

R389's installed-staging smoke checked only the *initial* URL, and used `page.goto()` after its HTTPS staging-host precheck. That accepts a staging URL that HTTP-redirects to the live production origin, and it does not detect production-host stylesheets or browser-fetched third-party assets before the request. It also inferred CSS integrity from a computed background instead of verifying the actual bytes delivered over HTTP. These are release-evidence integrity failures.

## R390 changes

- Every intended document/subresource GET (JS and no-JS) is restricted to the exact approved HTTPS staging hostname; production and other origins fail closed before network. Service workers are blocked for inspection consistency.
- Redirects are rejected at the **first response** using `route.fetch(max_redirects=0)`; routing only the first URL in a redirect chain would otherwise miss the subsequent hop. For now, **even same-origin 3xx redirects are a HOLD**, requiring separately reviewed handling rather than silently following.
- The staging runner compares the browser-delivered `/assets/gallery.css` HTTP response bytes with the reviewed SHA-256 `4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9` and requires exactly one successful matching response. A computed color is no longer sufficient proof.
- Blocked request/redirect details, final browser URLs and CSS response digests become part of structured output. Redirect/navigation failures are recorded as blockers, not reported as false acceptance. The script still requires a separately reviewed, pinned axe-core bundle for actual staging execution.
- The 23-check adversarial unit suite verifies denied origins, blocked redirect hops, mixed content, exact stylesheet byte identity, duplicates, missing/404 CSS and allowed same-origin 200 responses.

**Conservative behavior:** existing staging frontends that redirect canonically, source remote fonts or optimize/rewrite gallery.css will HOLD, not PASS. Approving such behavior requires an independently reviewed explicit change, not automatic network access. No network isolation code is installed on visitor pages; this is only a QA harness.

## Execute from repository checkout

    php experience2/apollo-r389/qa/contract.php
    python3 experience2/apollo-r389/qa/browser.py
    python3 experience2/apollo-r389/qa/test_staging_guard.py
    python3 experience2/apollo-r390/qa/test_network_boundary.py
    python3 experience2/apollo-r390/qa/package.py

The R389 browser suite uses `page.set_content()` with a locally PHP-generated fixture and produces ten responsive screenshots, Chromium accessibility-tree checks, one print dossier, fixture LCP/CLS. R390's network tests use pure fake HTTP routes: **they do not establish real route interception**. Chromium navigation is administrator-blocked even for local HTTPS in this runner. Genuine axe-core, installed WP/Assembler, actual browser HTTPS/CSP/redirect chains, independent screen readers, native 400% zoom, and hosted exact-head CI all remain untested.

## Source and conversion custody

The exhibit still has **six evidence questions supported by only two NASA publications**, with distinct 1967 investigation vs later controlled 1967–68 flammability tests. Primary sources: [NASA Apollo 204 Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) and [NASA 2018 retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/). No NASA media are reproduced or implied licensed; [NASA image/media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/).

Only proposed path: Grok-approved Apollo long-form/Shorts asset with genuine immutable `asset_id` + permitted UTM -> source-backed Apollo gallery -> [existing free investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) -> future rights-cleared educator kit **only after** SKU, checkout, delivery and founder approval are verified. **No paid CTA now.** Educator source-trust is a hypothesis, not a demonstrated conversion lift. The KPI is realized net revenue per 1,000 qualified human sessions; missing confirmed sessions/orders/settlements/refunds/fees and 7/30-day cohorts make it uncomputable.

Release gate: approved installed staging (real HTTPS and axe-core), independent WCAG/AT and zoom review, exact-head hosted CI, QD and founder release authorization. No production/site/Grok/merchant/email writes or spending.
