# R317 — Apollo Atlas / TASK-008 History pilot compatibility (staging only)

**Status:** built and tested offline; **not WordPress-installed, live, revenue-verified, or authorized for release**. Isolated child of Apollo R316; homepage PR #49 and Research Desk PR #158 unchanged. Primary engineering tracking: #150; commercial coordination: #820 and #818.

## Exact source and scope

R316 accepted only `apollo1_pilot_2026_11`, while the founder's Grok TASK-008 explicitly specifies `utm_campaign=<topic_cluster>_pilot_2026_11`. R317 adds the **single exact** `history_pilot_2026_11` alias, while continuing to require all four fields, a supported `utm_source`, `utm_medium=organic_social` and an Apollo-specific `utm_content=apollo1_<platform-code>_<3..24 lowercase alnum>`.

The crosswalk is intentionally not an assertion that a Grok Apollo video or a specific `asset_id` exists. Current fake IDs in tests are synthetic. Other clusters, months, unsupported platforms, duplicate parameters, cross-platform inconsistencies, email-like IDs, JS-disabled traffic and all malformed inputs do not receive appended identifiers. The first-party free investigation URL never changes in server HTML. No cookies, beacons, pixels, network APIs or additional CTAs are added. PHP bumps the staged script cache version to avoid silently retaining R316 JS after a future reviewed installation.

## Reproduce on a local checkout

```sh
python experience2/apollo-r317/qa/source_controlled_gate.py
```

Extended QA in the separately distributed evidence archive:

```sh
python experience2/apollo-r317/qa/grok_crosswalk_gate.py
```

Test requirements: PHP CLI, Node, Python `playwright` + `beautifulsoup4`, Chromium at `/usr/bin/chromium`. Both tests render actual WordPress-adapter PHP against a local stub and use **real offline Chromium** trusted keyboard menu interactions across 320, 360, 390, 768, 1024, 1440 and 1920 px. Check no-JS, no-CSS, touch configuration, reduced motion, forced colors, independent component instances, NASA URLs, source-custody structure, cache invariance, old-R316 negative control, bad campaign rejection and actual keyboard context menu. Synthetic fixtures cannot prove live traffic or merchant conversions.

## Rights, accuracy and commerce

NASA's Apollo 204 Review Board report supports a **most probable** electrical arc, but no conclusively identified exact ignition source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/. NASA brand/advertising rules prohibit implying an agency commercial endorsement: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/. R317 adds no photographs and changes no historical statements. An Apollo 11 collectible must not be represented as an Apollo 1 artifact.

**Proposed journey only:** future approved Grok long-form Apollo 1 documentary → Apollo Atlas source proof → free FV investigation → a separately approved, payable, rights-cleared educational offer, if one exists. One nonintrusive free investigation CTA already in place. Do not add unrelated commerce to the accident narrative. The offer, merchant acceptance, Grok asset ID/CTA route, real qualified sessions, orders, fees, refunds and net revenue are all **unverified**.

**Revenue experiment:** after approval and real per-platform asset IDs, compare qualified human landing→continuation→verified paid order/lead (where applicable) with authenticated 7/30-day cohorts. Net realized revenue per 1,000 qualified human sessions is **not computable** from this staging work; clicks are never counted as purchases.

## Release HOLD

1. Grok/Praxxis and Claude must reconcile actual asset IDs, exact allowed `utm_content` format, link destinations and channel rules; the alias here is a *staging compatibility experiment*, not approval to relabel live posts.
2. Real installed WordPress/Assembler, CDN cache, asset versioning, script CSP, native HTTP browser navigation and real copied/opened context-menu destination are not verified. Chromium in this restricted environment blocks native HTTP(S) (`ERR_BLOCKED_BY_ADMINISTRATOR`).
3. Genuine axe-core, independent screen readers, accessibility, official image rights / editorial review, production LCP/CLS/INP, hosted CI and QD review remain open.
4. Founder retains release, merchant, publishing and spending authority. No WordPress changes, social posts, affiliate activation, emails or paid calls.
