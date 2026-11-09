# Apollo Experience 2.0 — R246 NASA template seal (STAGING HOLD)

Date: 2026-11-09 PT. Scope: **Research Desk only**, stacked on draft R245 PR #1796. See Experience Issue #150, commercial coordination #820, charter #818, and original Research Desk PR #158. Frozen homepage PR #49 is out of scope.

## Change and custody
- The shortcode adapter now verifies the Git blob identity of the **actual six-record Research Desk NASA source template** `templates/ledger.html` before rendering it. Protected template blob: `403d128c57b9bc82dac7c619651689070edef86c`.
- A modified, truncated, empty, redirected or script-injected template **fails open to the pre-existing free Apollo 1 original-investigation link**. It does not render unreviewed source claims as verified evidence.
- The template, source URLs, NASA imagery, narration, CSS, JS, Research Desk page/CTA, and all other site files are unchanged. No paid CTA, tracking service, social post, email or production setting is activated.
- The seal is a code-controlled provenance boundary, **not** proof that NASA granted commercial image rights and not a replacement for independent editorial review. If future reviewed edits legitimately change the template, update the pinned blob only through a separate source/rights QA decision.

## Reproducible local QA
- `php -l experience2/research-desk/final-vestige-ex2-research-desk.php`
- `python experience2/research-desk/qa/r246_seal_smoke.py --source experience2/research-desk --fixture`
- `python experience2/research-desk/qa/r246_seal_smoke.py --source experience2/research-desk` (release-relevant original NASA template; **NOT EXECUTED in the current local run**)
- Previous R245 browser acceptance `qa/r245_accessible_targets.py` remains available and unchanged.
- Separate local R246 synthetic adapter+Chromium acceptance: **two independent PASS executions**, 5 widths (320, 390, 768, 1440, 1920px) × JS on/off = **20 contexts**, including keyboard disclosure, fail-open source tampering (7/7 each), responsive/no-JS, unrequested network check, repeated shortcode IDs; two screenshot pairs and deterministic QA receipts matched exactly. **Synthetic fixture is NOT original NASA-template testing.**
- LCP/CLS from the separate offline synthetic browser probe are **not production Core Web Vitals**. Five JS-enabled fixture LCP readings in each run; no-JS LCP unavailable; observed CLS 0 in fixture. Genuine axe-core was **not executed**.

## NASA source and rights boundaries
- Apollo 204 Review Board (technical source): https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — probable electrical-arc initiator, **no conclusively identified ignition source**.
- NASA usage / advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no implied NASA commercial endorsement; agency identities, likenesses and advertisements require specific rights checks.
- Historical citations are **not** merchant approvals, licensed product media or independently confirmed purchases.

## Conversion-first decision
**One proposed high-intent journey:** Grok Apollo documentary / Shorts → source-backed Research Desk/Atlas landing → verified NASA source trail → **one free original-investigation link**. After approved offer/rights/affiliate acceptance, a contextually relevant space-history product pathway could be tested separately. The Mini Museum offer remains **COMMERCIAL HOLD** pending merchant approval/permissions, actual checkout, terms and confirmed settlements. No live affiliate CTA.

**OFFER → FUNNEL → BLOCKER → CHANGE/TEST → EVIDENCE → OWNER**
1. Mini Museum space-history affiliate → paid purchase → acceptance, checkout and settlement unverified → validate through authorized merchant records before activation → **HOLD** → Founder / Commerce / Claude.
2. Grok Apollo asset → qualified Atlas landing → immutable published asset_id and signed-out destination unverified → reconcile existing Drive TASK-008 without taking creator ownership → **UNVERIFIED** → Grok / Praxxis.
3. Research Desk → free original investigation → source-template tampering could masquerade as verified evidence → R246 PHP source seal and fail-open regression → **LOCAL SYNTHETIC PASS, EXACT SOURCE AND WP STILL HOLD** → Apollo.
4. Orders → net revenue per 1,000 qualified human sessions → paid orders, fees, refunds and 7/30-day attributed sessions unavailable → reconcile source-of-truth transactions and consent-respecting cohorts → **NOT COMPUTABLE** → Commerce / Analytics.

## Blocking release gates
EXACT NASA template PHP-to-browser acceptance, isolated WordPress/Assembler installation and reusable-block lifecycle, real axe-core and screen-reader acceptance, browser zoom, hosted CI on exact head, independent QA, rights clearance, R198 source-ancestry discrepancy and **founder release authorization**. No production writes, merge or publication permitted.
