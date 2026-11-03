# Experience 2.0 — actual public-host accessibility and interaction observation

**Release: HOLD.** This additive audit is stacked on anonymous structural/media PR #731, not frozen #49. It observes the **already published** homepage, not an unpublished candidate or a private WP.com staging site.

## Gap closed
The existing hosted admission checks that chapter anchors, 72 Margins, Focus links and Jetpack markup exist and that approved Apollo/Franklin bytes transfer. It does **not** click interactive evidence, establish no-JS fallbacks, inspect reflow, or run axe against the actual hosted DOM. This complementary audit adds those checks, without visual chapters or unrelated content work.

## Exact browser scope
- Anonymous Chromium at CSS widths 320, 390, 768, 1440, 1920; 390 without page JavaScript; 390 with prefers-reduced-motion.
- Five actual hosted interactions at 390: Victory Point reading-lens click, keyboard ArrowRight change, switching to Franklin evidence, Observer Frame B and chapter fragment navigation.
- No-JS: all three case panels visible, both observer frames visible, enhancement controls hidden, and native keyboard activation of source-explanation details.
- Real horizontal document overflow test at every width.
- Locally installed and pinned **axe-core 4.10.3** injected **only in the test browser** at 390/1440. Results are filtered to WCAG 2.0/2.1 A/AA and 2.2 AA tags. **Nonzero violations are reported as FAIL**, and a missing axe runtime fails closed. Automated zero findings still require manual accessibility assessment.
- To inject offline axe, the lab browser deliberately bypasses CSP. Thus it **cannot certify the live site's CSP**; rely on the separate exact-source CSP lane.

## Preservation and ethical restrictions
No auth, preloaded cookies, CMS mutation, POST, signup, subscriptions, live settings, theme changes, WordPress installs, merges, or navigation edits. Network routing aborts **every non-GET** and the unresolved NYPL Malbone image URL before retrieval, even when requested by a lazy-loaded tag. Catalog citation links are not conflated with binary reproduction. The browser does not click forms, payments, social or email links.

The receipt contains allowlisted statuses, axe rule IDs/impact/counts, overflow and interaction booleans only. **No screenshots, raw HTML, archive image bytes, DOM snippets, usernames, subscriber data or personal information** leave the browser.

This is not independent QD, screen-reader testing, a true 200% browser zoom test, a physical-device Safari test, performance-budget adjudication or field Core Web Vitals. Hosted Personal WordPress.com has no one-click native staging clone. An isolated WordPress Playground/Assembler clone remains a non-identical pre-release environment.

## Interpretation
CI job PASS means the instrumentation and source tests completed. Read the emitted JSON gates for actual accessibility/interaction outcomes; **CI green never overrides an automated violation FAIL or the unconditional release HOLD.**

Run source tests from the release-candidate directory:
    python -m unittest -v test_probe_hosted_wcag_interactions.py

Run hosted test only with locally installed axe:
    python probe_hosted_wcag_interactions.py --axe-source /tmp/fv-ex2-axe/node_modules/axe-core/axe.min.js --output HOSTED_WCAG_INTERACTIONS_HOLD.json

Remaining release requirements: image-specific NYPL rights review, publication authorization reconciliation, manual WCAG 2.2 AA / NVDA / VoiceOver, physical devices including Safari, hosted mobile LCP, independent QD on exact candidate, and founder's explicit exact-release approval. The existing seven chapters, protected Focus Fieldbook, native Jetpack and all 72 Margins remain untouched.
