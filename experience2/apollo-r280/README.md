# Apollo R280 — pending-source integrity / PHP compatibility (staging-only, HARD HOLD)

Parent: Apollo R279 draft PR #2010, exact parent `7fab8e189adf3d13ee2f48974501907fdf4aa961`. Scope: **only** the isolated WordPress shortcode adapter and this R280 QA. Do not merge, deploy, modify frozen homepage PR #49, original Research Desk PR #158, WordPress production, Grok's queue, or Claude's analytics lane.

## Verified regression and correction

The R279 adapter checks source-link counts and a `data-fv-review-ready="false"` marker, but it does *not* require the visible heading or review statuses to remain pending. A damaged sibling can replace “Editorial review remains open” or “Editorial review pending” with “approved” while keeping the old marker and three anchor counts. It would incorrectly pass the existing presentation-drift check. The adapter also called `str_contains` (PHP 8+), which is incompatible with PHP 7.4 even though staging integration needs a clear compatibility boundary.

R280 adds a narrowly pinned **pending-only source-custody presentation contract**: 2 independent editorial categories that cite **one** NASA Review Board report, two labeled NASA source anchors, one free Apollo investigation anchor, explicit `pending` review heading/status, shared-source dependency explanation, NASA non-endorsement notice, safe new-tab attributes, and an absence of unreviewed forms, remotely loaded images and executable inline/event markup. Invalid output fails open to the original source-and-investigation fallback. This detects unintended sibling drift; it is **NOT** an HTML sanitizer, malicious-plugin containment, editorial signoff, copyright determination or production authorization. `strpos` replaces PHP 8-only `str_contains`; no PHP 7.4 runtime was available to execute compatibility testing.

## Commands, exact evidence and limits

```bash
php -l experience2/apollo-r277/apollo-review-shortcode.php
php experience2/apollo-r277/qa/wp_contract_gate.php
php experience2/apollo-r280/qa/pending_contract_gate.php /tmp/apollo-r280-php
python experience2/apollo-r280/qa/browser_pending_gate.py /tmp/apollo-r280-chromium
```

Locally executed: PHP pending contract **17/17**, original WP API simulation **20/20**, inherited editorial PHP **13/13 + 15/15 + 8/8**, receipt integrity **15/15**, inherited R278 failopen **6/6 PHP, 30/30 Chromium**. Chromium exact PHP-rendered original panel, five viewport widths **320, 390, 768, 1440, 1920**, JavaScript enabled/disabled, keyboard-native disclosure, touch emulation at 320/390, reduced motion, forced colors at 320, print visibility of NASA sources, accessible role/name checks, no overflow, zero unexpected external requests or JS errors: **10/10**, independently executed twice with identical receipt SHA-256 `35788bca1d1c08de0d7ea202421e78f57968b9bd2291d8d019778bff879a8af9`, identical sampled screenshots. Browser is **in-memory Chromium**, not installed WordPress/Assembler or HTTP/CSP; genuine axe-core, independent screen-reader acceptance, browser-native zoom (an attempted root-size stress run was inconclusive), field LCP/CLS, media rights approval, hosted CI and independent QA all remain outstanding. No reported paid orders or revenues.

## Historical, rights and commercial custody

- One primary NASA report for both editorial categories, **not independent corroborations**: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . An electrical arc was the most probable ignition initiator; the exact ignition source was not established.
- NASA media/advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Links to official records do not imply NASA endorsement, imagery/astronaut likeness advertising rights or endorsement of a merchant.
- Existing Atlas (public, not edited): https://finalvestige.com/apollo-1-evidence-atlas/ ; free original article https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . The public Atlas still requires independent editorial review for two marked records.
- Conditional visitor path: actual **verified** Grok long-form Apollo `asset_id` and permitted source link (not established) → existing public Atlas → free investigation → an **optional separate disclosed** Mini Museum guide *only after* merchant approval and founder release → merchant-authenticated orders, fees, refunds and net realized revenue. No commerce is inserted into Apollo evidence. Creator posting remains Grok's; Praxxis owns external QA; Claude owns core site/analytics; founder owns spending/production release.
- Conversion experiment: verified audience landing → free investigation completion → separately disclosed, relevant collection guide CTR → **real merchant-confirmed purchases**, not clicks. KPI: net realized revenue per 1,000 qualified human sessions, compare 7/30d cohorts only with actual platform asset IDs, verified transactions and privacy-compliant attribution; otherwise **NOT COMPUTABLE**. No scripts added.

**Release: HARD HOLD.** No PR merge, WP/social/email/affiliate activation, tracking changes or paid services.
