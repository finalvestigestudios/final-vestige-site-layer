# Apollo Experience 2.0 / R313 — cache-safe click-only campaign continuity

**DRAFT STAGING ONLY / HARD HOLD / NOT LIVE.** Stacked after R312 PR #2210, not on homepage PR #49 or Research Desk PR #158. Issue #150; commercial charter #818 and implementation #820.

## Actual implementation

- The server-rendered Apollo 1 HTML remains *byte-identical across visitor query strings*, preserving R311's shared-cache safety rule.
- An isolated first-party progressive enhancement (`apollo-cache-continuation.js`) runs only on a **trusted activation** of the existing **free** Apollo investigation link. It validates exactly one each of four UTM values, a source-matched Apollo-only asset ID, a bounded campaign date/format and `organic_social`, then updates that one first-party link. Extra parameters—including identifiers, advertising click IDs or email-like values—are never copied.
- The script registers no analytics, storage, cookies, beacons, cross-origin fetches, checkout links, commercial events or extra CTA. Missing or blocked JS leaves the original free editorial link intact. Repeated instance links are independent. A history change before a later click clears stale labels.
- The PHP shortcode enqueues the script only during the existing WordPress preflight for a discovered shortcode; dynamically rendered shortcodes without preflight remain plain, untagged links. This behavior is safe but yields incomplete attribution and must not be mistaken for validated funnel coverage.
- The allowed Grok `utm_content` format is a **synthetic proposed format**, not a verified published asset ID. Grok/Praxxis must reconcile existing asset IDs and destinations before approval. No existing creator queue was modified.

## Executed evidence and reproducibility

- PHP syntax and Node syntax PASS. Source-controlled R313 QA: **12** actual offline Chromium 320–1920px contexts with JS on/off, six valid trusted activations, five rejected invalid values, two visitors receiving the same PHP body. Keyboard/touch, reduced motion, forced colors, no-JS fallback and HTML source/photograph custody are checked.
- Independent extended local fixture: **12** additional Chromium cases, two simulated cache-identity visitors, three history-change activations, invalid/PII-style inputs, link-purpose and source-gallery integrity, and a PHP-shaped WordPress script-enqueue stub PASS. It does not constitute an installed WordPress test.
- Inherited R311 cache-isolation, R311 source-controlled, R312 source-controlled and R312 link-purpose executable gates PASS on the changed source. Original NASA source destinations and historical evidence hashes remain unchanged.
- Both browser test suites use `about:blank`-query documents because the hosted Chromium environment forbids navigation to HTTP(S), file or data URLs with `ERR_BLOCKED_BY_ADMINISTRATOR`. **Therefore browser response HTTP/CSP, installed WordPress, actual shared CDN, axe-core, independent screen readers, actual LCP/CLS/INP and merchant outcomes are NOT VERIFIED.** No pass is claimed for any of these.

## Release and business decisions

Only after founder approval and Claude production engineering, verify exact real WordPress enqueue, dynamic shortcode fallback, CDN cache keys, mobile outbound destinations, consent/data handling, independent axe/screen-reader accessibility, real-browser HTTP/CSP, real-user Core Web Vitals and QD/editorial/rights acceptance. The scripted tag formats are candidates, not Grok-published campaigns. No unreviewed merge or production install.

**One relevant continuation**: Grok Apollo 1 long-form or Short → Apollo Evidence Atlas → NASA source proof → free Apollo 1 investigation. A commercial step remains **blocked** until Founder/Commerce validates one presently payable rights-cleared and audience-matched FV product or independently confirmed affiliate offer, and Claude can reconcile confirmed paid orders, refunds, merchant fees and qualified human sessions. Apollo 11 memorabilia must not be misrepresented as Apollo 1 evidence. Net revenue per 1,000 qualified human sessions: **NOT COMPUTABLE**.
