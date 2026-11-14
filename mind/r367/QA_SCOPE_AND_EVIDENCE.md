# R367 — QA / scope manifest
- **Status:** UNPUBLISHED and not a WordPress CMS draft. Zero deployment or merchant activation.
- Branch: mind-r367-phantom-phoneme-buyer-qa-20261114. Root path `mind/r367/` only. Parent baseline main at creation; do not retarget homepage or Mind hub.
- A/B comparison: A source-only text guide. B exact same <main> plus optional SVG poster and transcript outside core; VTT is concept captions. **Not an encoded playable video.** A/B performance NOT TESTED.
- Core no-JS HTML, no cookie/script/forms/merchant anchors. Native disabled button adjacent to prospective FTC disclosure.
- Static layout uses responsive clamp and reduced-motion preference. Not proof of real device WCAG 2.2 AA or performance.
- Mechanical QA: Node verifier `node mind/r367/verify.mjs`. Independent source-level checks should be run against committed files and tests. Browser, network, contrast, keyboard-only, WordPress sanitizer, real video/captions, checkout and refunds all remain separate QA gates.
- Affiliate status: PUBLIC program exists; FV named acceptance/rights and earning URL UNKNOWN. Public advertised price $87.99 Premium on seller website November 14, 2026, **not verified checkout**. Owner/Commerce retains proof privately.
- Scope owner: this Mind lane creates source-only pages/articles, QA evidence, and contextual buyer decisions. Do not edit homepage flagship PR #49, Issue #150, Mind PR #172, newsletter Issue #174, Jetpack welcome, Grok queue, Site QA work, live WP, navigation, analytics, costs or merge state.
- The final SHA, exact test execution outcome and blockers must be recorded in Issues #171 and #820 after commit.