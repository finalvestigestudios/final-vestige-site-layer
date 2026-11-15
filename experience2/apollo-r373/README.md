# Apollo R373 — actual WordPress staging acceptance gate (DRAFT)

**Scope:** independent, read-only browser QA for R372 Evidence Path. This is a *gate*, not a WordPress deployment or product listing. Parent: #150, commercial program: #820/#818. Stacked on R372. Do not change homepage PR #49, Research Desk PR #158, Grok production or TASK-008. Never use this script against production.

## Why
Prior R365–R372 browser tests used PHP fixture HTML via Playwright `page.set_content`. The R366 PHP HTTP contract and R370–R372 pre-head loaders have **not** been tested inside an installed WordPress/Assembler page. This gate never promotes those local tests to staging acceptance. It refuses a production host, non-HTTPS URL, credentials, query strings, administrative paths, or a missing *locally supplied* real axe-core library. It never follows the external editorial CTA or submits anything. It prevents third-party tracking/merchant requests by aborting them in Chromium, recording consequences as request failures. It does not rewrite WordPress content/settings or activate analytics.

## Execute locally (real PHP fixture smoke, NOT staging)

From the repository root, with Python Playwright, Chromium (`/usr/bin/chromium`) and PHP available:

```sh
python3 experience2/apollo-r373/qa/preflight_test.py
python3 experience2/apollo-r373/qa/staging_acceptance.py --mode fixture --out /tmp/apollo-r373-fixture
```

The fixture generates ten separate real Chromium contexts with screenshots, native keyboard and touch source-drawer tests, 320–1920px and 4× root-font checks. `results.json` says `FIXTURE_SMOKE_PASS_NOT_STAGING` and `axe_fixture_not_run=true`. This **cannot** fulfill installed WordPress, HTTP/CSP, or axe acceptance.

## Approved staging ONLY — after founder/QD authorizes an isolated WordPress/Assembler route

```sh
python3 experience2/apollo-r373/qa/staging_acceptance.py --mode staging \
  --url https://APPROVED_STAGING_HOST.example/apollo-evidence/ \
  --host APPROVED_STAGING_HOST.example \
  --axe-js /verified/local/axe-core/axe.min.js \
  --out /private/qa/apollo-r373
```

Use a locally verified/pinned genuine `axe-core` distribution; no CDN injection or purchased service. Browser-enforced HTTP CSP might legitimately block injection and must be reported as a **failure**, not bypassed. Run with the staging shortcode and all required CSS linked in `<head>` by WordPress/Assembler. The `--host` must match the URL exactly; the public `finalvestige.com` hosts are hard-refused. Report genuine `STAGING_PASS` only after all ten contexts, HTTP/CSP, stylesheet response and axe WCAG 2.2 AA tagged checks complete without violations. Native screen-reader acceptance (NVDA/VoiceOver) and Firefox/WebKit remain manual independent gates.

## Acceptance/evidence boundaries

Screenshots are reproducible captures of a specified browser/runtime; **pixel-identical results across environments are not promised**. This runner records a screenshot and structured checks for each context, first-party network responses and failures, relevant CSP header presence, axe version/violations and lab PerformanceObserver measurements when available. Those observations are **not real-user 75th percentile LCP, CLS or INP**. The JS-disabled context cannot run axe; that is not a pass or a skip of the JS-enabled axe checks. Source-custody negative mutation tests remain in R372, and real source rights must be reviewed separately. Commercial CTA stays the existing free investigation; no Apollo paid SKU has been verified.

**Release:** HARD HOLD until actual authorized WordPress/Assembler acceptance, true independent axe + screen readers, HTTP CSP, hosted exact-HEAD CI, commercial rights/checkout verification and founder/QD approval. No WordPress/plugin writes, publishing, analytics, paid services or merge in this PR.
