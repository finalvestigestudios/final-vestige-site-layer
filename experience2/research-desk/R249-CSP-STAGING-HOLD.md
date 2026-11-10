# Apollo Experience 2.0 R249 — CSP-safe late CSS; staging HOLD

Date: 2026-11-09 Pacific. Based on draft R248, **not** homepage PR #49 or original Research Desk PR #158. Part of #150; cross-reference conversion #820 / #818.

## Defect and correction

The WordPress Research Desk shortcode loaded a sealed stylesheet as an **inline `<style>` fallback** after `wp_head`. A restrictive `style-src` Content Security Policy without `unsafe-inline` could block that fallback, leaving the Research Desk unstyled. The new guarded fallback emits a **single externally linked, verified plugin CSS asset** only after the normal `wp_head` opportunity and only if WordPress has not already printed its stylesheet. Before-head, rely on ordinary enqueue. After it was printed, emit no duplicate.

The **bytes of the six NASA evidence records and JS/CSS assets remain unchanged**. The CSS URL uses `plugins_url` and is escaped; the CSS file still must match Git blob `db531213e6f8dbaa44fba2885eefdd016dab93e3`. The historical HTML retains Git blob `403d128c57b9bc82dac7c619651689070edef86c`. No network, tracking or merchant script is added. **Do not loosen CSP** to accommodate this plugin. If `plugins_url` resolves to a CDN on a domain CSP does not permit, styling can still fail, but all six static evidence records remain readable.

## Local QA and its limits

- PHP syntax PASS and precise source/GitHub blob match are recorded in #150.
- Independent **two runs × (320, 390, 768, 1440, 1920) × JS on/off** = 20 Playwright/Chromium contexts, synthetic six-record PHP output with **temporary test-only hash substitutions**; original source in GitHub was not modified or re-pinned.
- PHP phases before-head, after-head, stylesheet printed; repeated shortcode instances; original-investigation fallback for changed HTML; changed stylesheet rejected; no JS; keyboard, touch, search, reduced motion, no horizontal overflow and no unsolicited network requests. **All passed**.
- Strict no-`unsafe-inline` CSP browser probe uses an intercepted `data:` transport for the reviewed CSS and JS because sandboxed Chromium blocks even intercepted HTTP navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). This proves stylesheets work when **inline styles are forbidden in the fixture**, not that the exact WordPress URL passes its site's CSP. The PHP source separately asserts the exact escaped plugin URL.
- Source-controlled exact-original regression: `python experience2/research-desk/qa/r249_exact_csp_gate.py`. Requires a full repo checkout and original sealed NASA/CSS/JS bytes; **not run in this runtime**.
- Local browser test is provided in the R249 deterministic artifact package, **not committed**. The committed executable exact-source regression is authoritative for the original-template smoke test.
- Not axe-core, screen-reader/manual keyboard review, HTTP transport/CSP testing in real WordPress, hosted CI, staging deployment or production CWV.

## Conversion-first path and owner boundaries

One evidence-led flagship: **Grok Apollo documentary (only when actually published) → Research Desk/Atlas NASA sources → single free Apollo investigation CTA**. A conditional space-artifact Mini Museum commercial follow-on is **on hold**, outside NASA source narrative, until Founder/Commerce validates affiliate acceptance, merchant terms, settlement/fees, disclosure and actual SKU. **Grok owns creator assets and channels; Praxxis owns independent creator QA; Claude owns website/analytics production; founder controls release and spend.** Existing TASK-008 queue is untouched.

Future metric: verified net revenue per 1,000 **qualified human** sessions, by creator asset ID and proper UTMs, via landing → relevant CTA → independently verified order/affiliate conversion → refunds/fees. No credible attributed sessions or settled orders provided; KPI **not computable**.

## Blocked release gate

Exact original NASA browser QA, independently installed WordPress/Assembler tests including actual CSP and nested blocks, genuine axe-core/assistive technology, real browser zoom, cross-browser/field LCP and CLS, media rights, R198 ancestry, green hosted CI, independent site QA and founder permission. **Do not merge, deploy, write WordPress settings/content, post creator media, activate affiliates, email users, add analytics scripts or purchase services.**
