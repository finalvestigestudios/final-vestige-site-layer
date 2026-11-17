# Apollo Experience 2.0 R423 — Source-custody bridge for existing Research Desk

**Status:** BUILT and locally TESTED on an independently generated fixture; **NOT INSTALLED, NOT LIVE, NOT RELEASE-APPROVED.** Stage-only PHP shortcode `[fv_ex2_apollo_research_bridge_r423]`. **No writes to WP, homepage PR #49, Research Desk PR #158, Grok/Praxxis or checkout.** Stacked as an isolated folder on R422 pending upstream review. Do not merge/release this stack.

## Why this exists
The actual Research Desk PR #158 (`250d7f05a4de037e73826dcf0cfaef0ec4c29383`) ships a six-record archival ledger with fixed `fv-ex2-ledger-apollo1-*` IDs, which may collide when inserted twice via reusable WordPress patterns. Its historical claims sometimes appear beside images documenting other years, including 2017 museum views. R423 uses the original ledger **without editing PR #158**, changes only its instance-bound IDs, adds a six-item source-photograph date/limitation index, and retains the existing one free-investigation CTA per shortcode instance. Photo links do not imply that their content proves the historical claim alongside them.

## Safety and provenance
Only renders if explicitly enabled on a single staging page; all other contexts get the existing investigation link. Define all of `FV_R423_ENABLED=true`, `FV_R423_STAGING_PAGE_ID=<approved page ID>`, and `FV_R423_RESEARCH_DESK_ROOT=<absolute read-only directory containing reviewed PR158 files>`. No default activation. The renderer requires actual local file bytes to match immutable Git blob SHA-1 for `templates/ledger.html` (`403d128c...`), CSS (`b8cf00af...`) and JS (`32e757cc...`); mismatched, unreadable or symlink-escaped dependencies return the free existing investigation. It reads **only** reviewed local files, never remote sources or shortcode parameters. It does not republish NASA media, infer geographic pins, set cookies or install analytics. It enqueues the already reviewed RD styling and progressive search JS only if the original plugin PHP exists and dependency verification succeeds. The new provenance index functions without JS.

NASA evidence: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) did not conclusively identify an ignition source; [NASA media-use rules](https://www.nasa.gov/nasa-brand-center/images-and-media/) govern image reuse, with no claimed endorsement. The 2017 exhibit photographs cannot be treated as primary 1967 accident imagery. Claims about later 102 deliberate ignition tests belong to NASA's separate [flammability-test history](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/), not the 2017 museum photograph.

## Reproduce the tests

```
php -l staging-research-desk-bridge.php
php qa/test_contract.php
php qa/render_fixture.php 2 > QA/fixture.html
python qa/test_browser.py
python qa/package_evidence.py
```

The synthetic fixture is intentionally **not** an installed WP instance and not a byte-identical copy of PR #158's full HTML; it exercises multi-instance IDs, disclosure semantics and responsive behavior on PHP-rendered shape-compatible markup. Browser QA uses `set_content` because Chromium navigation to even `file://` was blocked with `ERR_BLOCKED_BY_ADMINISTRATOR`. Final executed tests: **20 PHP assertions and 41 Chromium fixture assertions PASS**, 11 captures, 320–1920px, no-JS, keyboard, touch, reduced motion, forced colors and enlarged text. These do **not** prove genuine installed markup, axe-core, network requests, navigated LCP/CLS or CWV p75. Do not substitute screenshots for stage acceptance.

## Conversion-first acceptance

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Original Apollo educator evidence kit (hypothesis, no SKU) | verified paid order | No verified sellable rights-cleared product, checkout, fulfillment | Keep free narrative, independently validate offer prior to paid CTA | HOLD: no orders/paid event | Founder + Claude |
| Grok Apollo documentary | attributable qualified landing | No immutable published asset_id, approved post URL or human-session cohort | Grok/Praxxis use existing TASK-008 inventory; no new links/scripts | UNVERIFIED | Grok + Praxxis |
| Research Desk and provenance | existing free Apollo investigation | PR158 fixed IDs, mixed date associations; current real staging inaccessible | Source-pinned per-instance IDs + photo limitations; 1 relevant CTA | 20/20 PHP, 41/41 local Chromium fixture; staging HOLD | Apollo QA + independent QD |
| Paid orders to net revenue | net revenue per 1,000 qualified human sessions | No independently verified sale, settlement, fees, refunds or 7/30-day qualified sessions | Don't claim a conversion or calculate KPI until merchant evidence exists | NOT COMPUTABLE | Claude + Commerce |

**Journey:** approved published Grok Apollo video → date/claim-visible Research Desk → free [Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → separately founder-approved original classroom evidence kit if one becomes genuinely sellable. No commercial module was introduced.

## Outstanding release gates
1. Upstream R417 PR #2803 QA archive has **4/7** source divergence vs its GitHub exact HEAD; R422 #2828 quarantines it, but independent exact-head retest is still missing.
2. Independent QD review of exact R423 HEAD and complete upstream PR stack; no checks/CI claim without proof.
3. Actually install the isolated component **only on an explicitly authorized WordPress staging page**, verify Assembler and reusable shortcodes, source dependencies, and no-JS fallback. No install now.
4. Real Playwright navigation on approved staging, genuine pinned axe-core, WCAG 2.2 review, native screen reader, measured lab LCP/CLS/INP and appropriate field CWV (no fabricated metrics).
5. Founder approval for any production release, Grok posting, product offer, tracking or spending.

Coordination: [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Respect Grok/Praxxis TASK-008, homepage frozen PR #49 and Claude engineering lane.
