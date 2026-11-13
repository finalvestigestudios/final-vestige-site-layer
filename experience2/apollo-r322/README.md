# Apollo Experience 2.0 — R322 capability-safe source printing

**STAGING ONLY / DRAFT / NOT LIVE / HARD RELEASE HOLD.** Stacked on R321 draft PR #2267 (head `d26b8156c70da1f508031dc7a24d35a474920a57`). This lane does not touch homepage #49, Research Desk #158, Grok/Praxxis TASK-008, production WordPress, analytics, affiliates, sales, or email.

## Reproduced compatibility issue

R321 corrected a genuine Chromium PDF defect for plate and media drawers; however, two independent NASA custody disclosures still suppressed their print `<summary>` **unconditionally**: `fv-r291__authority-disclosure` (four dates of Board authority) and `fv-r296__date-disclosure` (three related NASA records). In older print engines without `details::details-content` support, that can suppress the only meaningful printable summary while its closed content stays hidden. **This is a code-established older-engine risk, not an independently observed Safari/Firefox failure.**

R322 removes both unconditional print summary hiding rules. It only suppresses these summaries under `@supports selector(details::details-content)`, with the corresponding print body explicitly shown. Newer Chromium keeps printable custody without a false "closed" control; unsupported engines retain their native disclosure label. This does **not** certify full closed-content printing in older engines. Cache-bust version is pinned to reviewed CSS bytes. No NASA claim, link, map, photo, JS, CTA or attribution behavior was changed.

## Source identities

- Parent R321 CSS Git blob: `b71505d6ee462148e19594cab46a47a0fae90eaf`.
- R322 CSS Git blob: `7c0e58782a8ec7b23f28da784a84c827f117914a`; SHA-256 `2c6b72cab4860f9eec36fb3ea206ffa8973e438e60321e98e8eb91fae190764c`.
- R322 PHP Git blob: `c17c7ffb385905b47315631ad49cc7ada96bf7f4` (cache version only).
- Unchanged client JS Git blob: `a3c858b51005495ebebb326086badc155c1b7e5a`.

## Reproduce

Source-controlled compact gate:

```bash
python experience2/apollo-r322/qa/print_fallback_replay.py
```

Requires PHP CLI, Node, system Chromium at `/usr/bin/chromium`, Python Playwright, `tinycss2`, and `pypdf`. It uses **actual component PHP** rendered through the R320 WordPress lifecycle stub. It runs local offline Chromium and a real printed PDF; it is **not installed WordPress**. It checks source-identity pins, CSS structural feature-gating, an executable negative control reintroducing the risky R321 rule, browser source custody, accessible native focus/deep-links, unchanged free-editorial CTA and conditional campaign continuity.

The independent extended local gate in the downloadable evidence bundle ran **42/42 actual Chromium contexts**, covering 320–1920px, JS/no-JS, forced colors, CSS unavailable, reduced motion, touch-configured mobile, 200% and 400% text. It produced **four real Chromium PDFs** from initially closed disclosure states, six actual screenshots, SHA receipts, three WordPress lifecycle-stub checks, actual source/link/geo/rights invariants and a rejected R321 compatibility regression. It is important to distinguish that local extended runner from the smaller checked-in gate; the package contains both.

Observed offline fixture LCP/CLS are not production CWV. Native Chromium HTTP(S) is blocked by administrator; real axe-core was NOT executed (npm DNS EAI_AGAIN). Installed WordPress/Assembler/CDN, browser security headers, independent NVDA/VoiceOver, Safari/Firefox print, field CWV, hosted CI/QD, editorial/rights signoff and founder release approval remain unverified.

## Historical and commercial boundaries

NASA original primary institutional records: <https://www.nasa.gov/history/Apollo204/narr.html>, <https://www.nasa.gov/history/Apollo204/proceed.html>, <https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/>. Oral authorization January 27, first Board meeting January 28 and written confirmation February 3 are distinct acts. Later NASA summaries are not independent eyewitness corroboration. NASA's <https://www.nasa.gov/nasa-brand-center/advertising-guidelines/> forbids implying commercial endorsement; linked image records do not grant a product's media rights. This implementation adds no photos or geolocations.

Exactly one proposed pathway: an **unverified future** Grok Apollo documentary → NASA source-linked Atlas → the **existing free** FV Apollo investigation → only after separate founder/commerce clearance, a verified payable Apollo-aligned educational kit. No such SKU or published creator asset_id is authenticated; no paid CTA is added. No qualified sessions, confirmed orders, fees or refunds are reconciled, so **verified net revenue per 1,000 qualified human sessions is NOT COMPUTABLE**, not zero. See CONVERSION-GATE.md.

**Do not merge or deploy** without independent site QA/QD, installed WordPress/CDN, accessibility, rights/editorial, actual paid-offer validation and founder authorization.
