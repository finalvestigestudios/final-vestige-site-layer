# Apollo R140 — Verified reader-to-investigation source continuity (staging only)

2026-11-05. Governing #150; conversion #820; business charter #818. Source branch stacked only on R139 #1086. No edits to homepage PR #49, Research Desk PR #158, WordPress, Grok, analytics, or payments.

## Observed WordPress read-only sources

- **Atlas**: page 2017, `publish`, `https://finalvestige.com/apollo-1-evidence-atlas/`, modified 2026-11-04 17:09:24 (WP metadata).
- **Investigation**: post 434, `publish`, `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`, modified 2026-11-03 22:12:30 (WP metadata).
- Actual page 2017 source has one anchor labeled **Read the full investigation** leading to the exact post permalink. A second, separately labeled companion-article link has the same destination. Both page and post sources include NASA's Apollo 204 Review Board report link.
- The Atlas has no `#classroom-preview` worksheet CTA/target; do not advertise a nonexistent worksheet as a live next action. WordPress metadata and source checks are **not** actual browser-navigation evidence.

## R140 implementation

`r140_reader_continuity_gate.cjs` validates both independent read-only WordPress source snapshots, canonical same-site destination, post/publication identity, a single non-hidden keyboard-reachable static reader CTA, and NASA Review Board source context on both sides. It excludes script/template-defined fake controls, rejects altered URLs/query strings, unexpected new tabs and missing source proof. It reports only content SHA-256 hashes, structural counts and fixed canonical URLs.

It is deliberately **not a general-purpose HTML5 parser**, an HTTP availability test, a rights-clearance utility, or a revenue attribution service. Its clean result is `SOURCE_LINK_CONTINUITY_ONLY`, **never** `LIVE` or release approval.

The existing **Read the full investigation** action is the singular relevant next step while an Apollo-specific paid teaching product and classroom worksheet destination remain unverified. No production CTA or product was inserted.

## OFFER → FUNNEL → BLOCKER → CHANGE / EVIDENCE → OWNER

1. **Educator Apollo dossier → paid order:** No verified, rights-cleared Apollo SKU or merchant/refund record → verify real Payhip listing, fulfillment, rights and founder approval; **BLOCKED** → Claude Growth / founder.
2. **Grok Apollo long-form/Shorts → actual Atlas:** Grok asset IDs, post URLs, link placement and human-session attribution not verified → use WP-identified Atlas URL only when Grok/Praxxis confirm actual publication and Claude QA verifies mobile navigation; **WP SOURCE OBSERVED / GROK & BROWSER NOT VERIFIED** → Grok/Praxxis, Apollo QA.
3. **Atlas → investigation:** Static exact same-site CTA in current published source → validate cross-page canonical source identity, then actual keyboard/touch/no-JS browser traversal; **SOURCE MATCH / BROWSER NOT TESTED** → Apollo QA / Claude site lead.
4. **Educator interest → relevant paid product:** No approved matching offer → withhold checkout CTA and preserve source integrity; **NOT ACTIVATED** → Founder / Claude Growth.
5. **Qualified sessions → settled orders → net revenue:** Missing independent verified attribution, paid orders, fees/refunds → use existing #820 7/30-day cohorts; no duplicate analytics, no private buyer information; **NET REVENUE NOT COMPUTABLE** → Claude Analytics.

## Tests / release hold

`node --test experience2/apollo-creator-bridge/test_r140_reader_continuity_gate.cjs`

Native Node v22.16.0 completed **16/16 tests on files whose Git blob IDs match this PR**. This includes fake links in scripts, wrong destinations, missing evidence, hidden/keyboard-inaccessible links, duplicate CTA, and purchaser-data redaction. This is **source testing, not browser testing**. A local Chromium 144 navigation probe still returned `ERR_BLOCKED_BY_ADMINISTRATOR` on file navigation; no actual-page screenshots, Playwright/axe, LCP/CLS or responsive-browser evidence is claimed.

**Release: STAGING_HOLD.** Outstanding: actual-page 320–1920 browser+keyboard+touch+no-JS+reduced-motion, accessibility & performance, WordPress Assembler integration, image-specific rights, exact CI, independent editorial review, verified commercial offer, and founder release approval. Do not merge, activate or publish without those gates.
