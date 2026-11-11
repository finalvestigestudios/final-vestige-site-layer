# Apollo R294 — reviewed CSS cache contract and staging QA

STAGING ONLY / DRAFT / HARD HOLD. Parent Apollo R293 PR #2096 at HEAD 797ecf0e3cc884661bc929276695e3f76f0ac021. Only the Apollo PHP is modified; Research Desk PR #158, homepage PR #49, WordPress and production are untouched.

## Reproduced and corrected

The actual inherited PHP still enqueued the Apollo stylesheet as version r285 after later accessibility/print improvements, and its no-preflight fallback generated an unversioned CSS URL. A persistent cache could therefore serve outdated styling. R294 binds both enqueue and fallback to r294-de213c4f113f, derived from the reviewed CSS SHA-256 de213c4f113f24f562571714068b8b210ea025cec4b30ab9ccf6ba1ade0dc474. A preexisting URL query uses &ver rather than a second ?. Future CSS changes must update and retest the version. This is a verified versioning defect, not proof of a live cache incident or CWV improvement.

## Execute

From the repo root: run PHP syntax on experience2/apollo-r281/apollo-source-experience.php, then python experience2/apollo-r294/qa/php_cache_gate.py, python experience2/apollo-r294/qa/verify_r294.py, and python experience2/apollo-r294/build_archive.py. Python Playwright and executable Chromium/PHP are required. The tests only use localhost; they do not call or edit production.

The PHP test covers enqueued, done, dynamic fallback and existing-query-string cases (25 assertions), including one CSS link across repeated instances. The browser gate checks 10 offline Chromium contexts from 320 to 1920 pixels, JS on/off, keyboard source/return focus, touch emulation, reduced motion, no horizontal overflow and unique IDs. It also fetches real PHP-served HTML/CSS and a restrictive CSP header with Python urllib. **System-managed Chromium blocks HTTP navigation, including localhost (ERR_BLOCKED_BY_ADMINISTRATOR).** Browser interactions therefore render the retrieved HTML and reviewed CSS OFFLINE. This is *not* a real browser HTTP/CSP pass. LCP/CLS and genuine axe-core were NOT measured, and no installed WordPress/Assembler, independent screen reader or hosted CI was tested. The release is blocked.

No NASA text, URLs, media, geographic edges, CSS visuals, analytics, affiliates or selling links were changed. NASA informational links are retained and NASA endorsement is not claimed. Rights: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/.

## One audience → one contextual next action

The evidence-informed Grok Apollo long-form viewer follows an authenticated approved platform asset_id/UTM link → source-led Atlas → the existing free Apollo investigation. Only once an Apollo classroom evidence kit is rights-cleared, actually sellable, buyer-validated, and founder-approved should a separate commercial continuation be considered; it is a proposed B2B product, not an existing offer. Mini Museum buyer-fit and payable affiliate eligibility remain unverified, so no commercial CTA is present. Grok owns social creative; Praxxis owns independent TASK-008 QA; Claude owns single privacy-safe attribution and production analytics; founder owns approvals.

KPI when valid data exists: settled FV net revenue per 1,000 qualified human sessions, analyzed by 7/30-day asset_id cohorts and adjusted for refunds/fees. Outbound clicks, views and leads are NOT purchases. No measured uplift, sales or revenue is claimed.

**Do not merge or deploy.** Outstanding: real browser HTTP/CSP, axe, independent screen reader, WordPress/Assembler, field CWV, hosted exact-head CI, editorial approval, offer authentication and founder release authorization. Coordination: Issues #150, #820 and charter #818.
