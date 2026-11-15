# Apollo Experience 2.0 R391 — read-only staging boundary and no-JS custody

**DRAFT / PRODUCTION HARD HOLD.** Stacked only on Apollo R390 PR #2653, exact parent `1b47f0c1c2c9fcea4ce8ea2de894b46a0d94b2ab`. This changes QA tooling, not visitor-facing content, WordPress settings, Grok's production, homepage PR #49, Research Desk PR #158, analytics, sales or paid services.

**Reproduced gap:** R390's staging runner said read-only but permitted same-origin POST/PUT/PATCH/DELETE, nonstandard TLS ports and WebSockets. Denied URL and exception logs could include query credentials. Its no-JavaScript smoke only counted six cards/disclosures without verifying delivered CSS or both NASA publisher links.

**R391 fix:** Reject every HTTP method except GET/HEAD *before request*, exact approved HTTPS host on port 443 only; fail closed against all WebSocket connections using Playwright's pre-connection `route_web_socket`; keep the no-redirect and no-service-worker policy. Strip query strings, userinfo and fragments from QA logs; never log exception messages. Require the no-JS response to deliver exactly one SHA-256-matching gallery CSS and render six questions, six native disclosures, six direct NASA question source links, two underlying publisher links, and one free investigation CTA. Existing JS-context exact CSS and axe checks are preserved.

**Executed November 15, 2026:** 59/59 PHP API-stub, 399/399 actual Chromium local fixture assertions across ten contexts 320–1920px; 7/7 staging URL checks, 23/23 inherited mocked network checks and 50/50 source-controlled R391 adversarial checks. Re-run `python3 experience2/apollo-r391/qa/test_readonly_boundary.py` and `python3 experience2/apollo-r391/qa/package.py` after the R389/R390 baseline commands below. Ten fixture screenshots, five-page print custody and LCP/CLS fixture readings are not installed staging or real-user metrics. No actual browser network navigation, genuine axe-core, independent AT, native browser zoom, hosted exact-head CI or installed WordPress testing occurred; this environment blocks `page.goto` even for local/data URLs. A GET may still create staging logs or side effects on a badly designed endpoint, so this is a method-level guard, not an absolute zero-write guarantee.

**Conversion gate:** One proposed educator/librarian journey: Grok-owned approved Apollo long-form with genuine asset ID/UTMs → verified two-publication NASA gallery → [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → *future* independently rights-cleared classroom evidence kit (no payable SKU/checkout/delivery verified; **purchase CTA withheld**) → merchant-confirmed paid order minus refunds/fees. Qualified-human visits, 7/30-day cohorts and realized net revenue per 1,000 sessions remain unmeasurable. **Owner:** Grok/Praxxis acquisition review, Apollo QA evidence and accessibility, Claude commerce/analytics, founder release authorization. No unrelated sales pitch inserted into the tragedy.

**HARD HOLD** until isolated installed WP/Assembler staging, live HTTP/CSP/axe and no-JS CSS verification, independent screen readers/native zoom, hosted exact-head CI, QD and founder approval. No merge/deployment/WordPress write/social post/email/spending.

---

## Prior R390 baseline (retained)

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
