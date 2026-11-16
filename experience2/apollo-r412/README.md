# Apollo Experience 2.0 R412 — real loopback HTTP acceptance lane

**DRAFT / STAGING-ONLY RESEARCH / NO PRODUCTION AUTHORIZATION.** Builds exclusively upon the source-controlled R411 SourceDrawer; does not change any WordPress content/settings, deployed scripts, homepage PR #49, Research Desk PR #158, Grok's assets or Praxxis' TASK-008 queue.

## Why this sprint exists

R411's Chromium QA used `page.set_content`, proving markup and CSS under a synthetic document, **not** actual browser resource fetching. R412 uses **real Playwright `page.goto` navigation** against an ephemeral `127.0.0.1` HTTP origin that serves **real PHP-generated SourceDrawer markup** and its separately fetched source-controlled CSS. The server is read-only, loopback-only and allowlist-only, and sends a restrictive CSP, nosniff, no-cache and no-referrer headers. HTTP and CSS delivery become independently observable.

Exact reviewed R411 Git blob dependencies (failed hash => immediate abort):

- `experience2/apollo-r411/staging-source-drawer.php`: `efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`
- `experience2/apollo-r411/qa/render_fixture.php`: `bbcea951ad755e62959aa86d48b735c620053162`
- `experience2/apollo-r411/assets/source-drawer.css`: `2ed53b254dd9cfd4b27e56a2ace2c68bf05a8118`

## Run locally on a checkout of the R411 parent + R412

```bash
python3 -m unittest discover -s experience2/apollo-r412/qa -p 'test_*.py' -v 2>&1 | tee /tmp/r412-tests.log
python3 experience2/apollo-r412/qa/release_gate.py  # expected exit 2 until all gates cleared
python3 experience2/apollo-r412/qa/package_evidence.py
```

Prereqs: `php`, Python 3.10+, `playwright`, and locally installed Chromium at `/usr/bin/chromium`. The `test_http_acceptance.py` uses Playwright with no paid/browser cloud services. It records screenshots at 320/360/390/768/1024/1440/1920px plus no-JS, touch/reduced-motion and enlarged-text forced-colors. Native `<details>` is keyboard/touch accessible. No JavaScript is served by the fixture. Browser `PerformanceObserver` is injected from the **test harness only**, before navigation, to collect actual Chromium `largest-contentful-paint` and layout-shift samples; these are isolated fixture samples, **not** field Core Web Vitals or production p75, and not proof of real-origin HTTPS performance.

### Genuine axe-core execution gate

The harness does not claim CDP role checks or a custom linter are axe-core. Set `FV_AXE_CORE_PATH` to a **verified, license-compliant local axe-core JS distribution** to run `axe.run` against the navigated document. Without it, the resulting `axe_core.status` is `BLOCKED_NOT_INSTALLED_OR_VERIFIED`; never equate this with a pass. Independently test screen readers and native browser zoom on staging. CSP in this fixture deliberately blocks site scripts; Playwright injection is QA-only.

### Meaning, copyright and conversion

R412 embeds no images, insignia, speculative geolocations, affiliate code, lead forms or instrumentation. Historical claims are unchanged from R411. NASA's 1967 Apollo 204 Review Board did not conclusively identify the initiating ignition source; its later flammability tests took place after January 1967. Source URL alone is not a media rights license or NASA endorsement. See official https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/nasa-brand-center/images-and-media/.

Only the existing free Apollo investigation is offered: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . Proposed educator dossier is **not** a verified sellable SKU, so no purchase CTA. Hypothesis: successful external-source/CTA navigation and good legibility lower evidence-to-article friction for qualified educator audiences; no conversion or revenue data are present. Grok retains creator distribution, Praxxis independent creator QA, Claude merchant and analytics, founder release approval.

### PASS vs HOLD

Local navigation, HTTP/CSS transport and performance observer evidence can be **TESTED**; installed WordPress/Assembler, actual HTTPS/CDN/CSP, independent axe, screen reader, 400% native browser zoom, proper real-user performance p75, QD review, exact-head CI, rights clearance and founder authorization remain **HOLD**. This is NOT LIVE. Never promote an offline fixture performance number as website performance.

## 2026-11-16 execution receipt (this environment)

This runtime allowed a real Python `urllib` fetch of the loopback HTML and CSS with restrictive CSP (three source/server guard tests passed), **but Chromium `page.goto()` returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`** for the same loopback address. The suite now probes and explicitly skips eight Chromium-HTTP assertions rather than falsifying network/LCP/CLS results. All Chromium-navigated metrics remain `null` / unavailable, not zero. Genuine axe-core JS could not be sourced/verified and is recorded BLOCKED. Inherited R411 in-memory Chromium QA and native PHP assertions were run separately and passed (10 methods and 46 assertions), but they do not replace HTTP QA. See `QA/http_report.json`, logs and `QA/release_gate.json`. Three screenshots and the inherited browser report from the unmodified R411 in-memory suite are included with an `R411-inherited-` prefix; these are **not** R412 navigated HTTP screenshots. The release gate intentionally exits **2 (HOLD)**.
