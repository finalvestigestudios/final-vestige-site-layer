# Apollo Experience 2.0 R216 — archive custody / active-content safeguards

**STAGING ONLY. DO NOT MERGE OR DEPLOY.** Independently stacked on Apollo R215 PR #1592; no changes to frozen homepage PR #49, homepage lead, or Research Desk PR #158.

Source-pinned R215 parent manifest: `24de2b0adf1169a6c3b91873468d3af2be8216bb945ee0be8a3a24fb26d51033`.

R216 adds a strict HTML tag/attribute and CSS active-content denylist, URL allowlist, complete ID/ARIA/fragment references, and a runtime SHA check over *five* source/rights/commercial gate records. Modifying an accepted ledger causes WordPress to show only the original free investigation fallback rather than unverified source claims or a manipulated CTA. It retains the static NASA evidence, chronology, plain disclosures and **one** free investigation link; no new JavaScript, image, tracking, affiliate or purchase destination. Content/media-rights clearance is **not** represented or implied.

Run from the downloaded evidence package root (with `r215/dist` beside `r216`). From a GitHub checkout, supply the independently verified extracted parent path using `FV_APOLLO_R215_DIST=/absolute/path/to/r215/dist`; the parent distribution is not committed and cannot be substituted with a current production copy:

```bash
python r216/build_r216.py
php -l r216/dist/fv-ex2-apollo-r216.php
python r216/qa/gate_r216.py r216/qa-A
python r216/qa/gate_r216.py r216/qa-B
```

QA uses **actual Chromium/Playwright** and a Python HTTP fixture server. Browser localhost navigation is policy-blocked (`net::ERR_BLOCKED_BY_ADMINISTRATOR`), so Chromium necessarily runs the rendered PHP HTML via `set_content`; separate HTTP GET of HTML/CSS succeeded. 10 Chromium contexts each run, 320–1920 widths, keyboard and touch, no-JS disclosures, forced colors, reduced motion, print key, native accessibility-tree presence, PerformanceObserver local fixture metrics. Screenshot SHA comparisons are deterministic when scroll is stabilized. Adversarial markup/CSS 19/19 rejected; five distinct ledger/offer gate tamper attempts cause PHP's fail-open original investigation fallback. **No genuine axe-core, installed WordPress staging, NVDA/VoiceOver, live browser navigation, true browser zoom, field CWV/p75, hosted CI, or independent QD** has been established. Release stays HOLD.

The NASA Apollo 204 Review Board is the source of the probable electrical-arc finding, while the specific ignition remains unproven: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising rules are separate from citation provenance and do not imply FV's commercial rights: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No additional NASA media is packaged.

**Conversion-first:** Grok published Apollo `asset_id` and Praxxis review unverified; no approved rights-cleared Apollo educator dossier SKU; only present editorial CTA is free. Qualified sessions, subscriber confirmation, merchant-confirmed paid orders, affiliate commissions, refunds, fees, and realized net revenue per 1,000 qualified humans remain **UNKNOWN / NOT COMPUTABLE**, not zero. Founder/Claude must authorize any future product/analytics/release change.
