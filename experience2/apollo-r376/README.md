# Apollo Evidence Atlas R376 — shortcode ownership and staging isolation

**DRAFT / NO DEPLOYMENT.** This is an independent successor to R375 on a stacked feature branch. Do not activate R375 and R376 together, change WordPress, merge frozen homepage PR #49, edit Research Desk PR #158, or alter Grok/Praxxis TASK-008. Founder/QD release approval still governs.

## Defect addressed

The R375 staging loader registered its fallback `fv_apollo_source_path_r372` shortcode at file load, before checking WordPress environment or whether another plugin already owned the tag. In WordPress, `add_shortcode` replaces an existing callback. Importing reviewed R365/R371 upstream files also registered extra unstyled shortcodes and a sitewide R365 stylesheet until cleanup. The R375 manifest rejected symlinked leaf files but did not explicitly inspect ancestor symlinks.

The R376 loader:

- Rejects production / wrong-HTTPS-host / disabled staging *without registering any shortcode*.
- Leaves a pre-owned shortcode and an already-loaded component family untouched.
- Pins six reviewed upstream PHP/CSS dependencies to their exact SHA-256 digests and rejects any symlink in an ancestor path.
- In an approved staging environment only, installs one free-article fallback pending integrity verification, then loads R372 and removes R365's global CSS enqueue plus R365/R371's auxiliary shortcodes. If post-include cleanup fails it restores the no-claim fallback.
- Retains only one source-backed Evidence Path CTA to the published free Apollo investigation. It introduces no JavaScript, media, map coordinates, tracking, email, product purchase link, or CMS write.

## Exact local tests

From the full stacked repository checkout with PHP 8+, Python playwright/pypdf and /usr/bin/chromium:

```sh
php -l experience2/apollo-r376/secure-gate.php
python3 experience2/apollo-r376/qa/run_tests.py --out /tmp/apollo-r376-qa
python3 experience2/apollo-r376/qa/package.py --out /tmp/Apollo_R376_Evidence.zip
```

`qa/scenario.php` exercises seven PHP lifecycle cases: enabled, disabled, production, wrong host, a pre-owned shortcode, a conflicting loaded family and source mutations including symlinked asset directories. The Playwright runner captures 10 Chromium fixtures (320–1920px, no-JS, keyboard, touch, reduced motion, forced colors, 4x root-font), source-to-stage joins and native PDF citations. Packaging is byte-stable on unchanged inputs. **These are PHP WordPress API stubs and browser fixtures, not an installed WordPress/Assembler test.** Genuine axe-core, browser HTTP/CSP, first-paint site timings, hosted exact-HEAD CI, native zoom and independent screen-reader verification are blocked/pending. Never claim fixture LCP/CLS as production CWV.

## Authorized staging acceptance — still BLOCKED

Only after independent approval, include `secure-gate.php` instead of R375 through an existing staging loader. Require PHP `FV_APOLLO_R376_STAGING_ENABLED === true`, exact `FV_APOLLO_R376_APPROVED_HOST` on HTTPS and `wp_get_environment_type() === 'staging'`. Use the previously reviewed R374 staging HTTPS acceptance runner and a verified genuine axe-core distribution; inspect actual CSS network response/first paint, NASA source custody, CSP, no-JS, keyboard/touch, native zoom, screen readers and LCP/CLS. Hosted CI and founder/QD approval are separate release requirements.

## Revenue-first boundary

One proposed path: founder-approved Grok Apollo documentary → NASA Evidence Path → [existing free investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → future rights-cleared educator dossier **only after** an actual payable SKU, licensing, checkout and settlement are independently verified. Historical primary evidence is never locked behind a purchase.

| Offer → funnel step | Blocker → experiment → evidence | Owner |
|---|---|---|
| Educator dossier → paid order | Rights-cleared payable offer and merchant unknown; withhold purchase CTA; BLOCKED | Founder / Claude |
| Grok video → qualified landing | Approved asset ID and attributable sessions missing; maintain UTM plan only; UNKNOWN | Grok / Praxxis |
| Evidence Path → free investigation | Unsafe fallback registration and auxiliary shortcode exposure; isolated and tested in PHP/Chromium; PASS LOCAL ONLY | Apollo QA |
| Confirmed orders → realized net revenue | Verified buyer transactions, fees/refunds and 7/30-day qualified-human denominator unavailable; KPI not computable | Claude / Commerce |

NASA's 1967 Apollo 204 Board report is the primary investigation; later retrospective accounts and engineering tests remain separately labeled. A link to NASA evidence does **not** grant commercial image/logo rights or NASA endorsement. No photography or invented geospatial pins are added.

Coordination: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).
