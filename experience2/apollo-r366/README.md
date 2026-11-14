# Apollo R366 · Local HTTP security and source-custody acceptance (DRAFT)

Parent: R365 [#2507](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2507), Issue #150; conversion contract #820. **Staging QA fixture only, not a WordPress plugin, deployed route, or production security policy.** No homepage PR #49, Research Desk #158, creator handoff, merchant, email, WordPress or analytics changes.

R365 was previously tested through Chromium `set_content`, which cannot test actual HTTP response headers. R366 creates a **local PHP HTTP-only** fixture serving the R365 PHP-produced ChronologyRail and exact R365 CSS, plus a CSP negative-control route. `qa/verify_http.py` checks actual HTTP status/content types; a deliberately strict CSP response header; click-safe/no-remote media markup, source drawers, original NASA links and one free Apollo investigation continuation; stylesheet byte identity; 404 handling and no unexpected server state. This is an additional QA layer, not a replacement for installed WordPress acceptance.

Run from repository root:

```sh
php -l experience2/apollo-r366/qa/http_fixture.php
python experience2/apollo-r366/qa/verify_http.py
```

**Environment limitation:** Chromium direct navigation to localhost and intercepted HTTP responses returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`, so **browser-enforced HTTP CSP is NOT VERIFIED**. The independent R365 Chromium fixture QA (7/7 in R365) remains applicable, but do not conflate it with this HTTP-only test. Genuine axe-core, actual WordPress/Assembler, production HTTP/CSP, field LCP/CLS, Firefox/WebKit, hosted exact-HEAD CI and paid checkout remain blocked. The only next action remains the already-live free Apollo investigation; a paid educator product has not been merchant-verified. No new media, maps, product CTAs, analytics scripts or licensing claims.
