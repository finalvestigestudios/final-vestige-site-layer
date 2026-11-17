# R434 Reproducible static QA — source-only, not a production pass

This receipt will be supplemented with the exact final commit SHA and real execution result in Issue #171. `verify.mjs` uses only Node built-ins and reads its adjacent files. It tests that A/B have the same buyer section, the B concept is optional, the caption cues cover 0–42s, the buyer button remains disabled, disclosure is adjacent, no referral link or script/iframe/form/tracker is installed, all commercial gates remain HOLD, and the hub preserves the existing Focus route.

**Not tested or not established:** Native site integration, real-browser WCAG 2.2 AA at five viewport widths, true no-JS/CSP behavior in WordPress, actual media encoding or playback, performance budgets, WordPress sanitization, qualified social media IDs, affiliate approval/checkout, Jetpack confirmed lead, merchant-paid conversion or refunds.

Release hard stop: draft PR only; never merge, deploy, edit CMS/navigation, affiliate settings, email campaigns, homepage #49 / Issue #150, or canonical Mind PR #172 without release approval.
