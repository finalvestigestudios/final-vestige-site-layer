# P0 — Exact-head isolated WordPress staging lineage and published-rights reconciliation
**Read-only audit: 2026-11-05 UTC. Draft / RELEASE HOLD. No CMS write, no merge, no deploy, no paid service.**

## Correction to the release history
It is **incorrect** to say the seven-chapter homepage has never undergone actual integrated WordPress/Assembler testing. [Draft PR #637](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/637) documents a genuinely running isolated WordPress/Assembler environment: exact tested HEAD `f9f9fc243ceed7df09a1674f533a9cf12c7a7c53`, 16/16 private interactions, 5-width Chromium/axe, 6/6 no-JS and media checks. Its actual Lighthouse 12.8.2 lab observations were mobile 390 **97/100/100** (LCP 2062ms, CLS 0), desktop 1440 **78/100/100** (LCP 2075ms, CLS 0). It reports a 320px clipped Library nav defect **found and corrected**, with before/after screenshots. Those results are real evidence **only for that tested SHA and isolated environment**, not WordPress.com hosted field CWV or current HEAD.

## Independently rechecked exact source lineage
GitHub `compare_commits` for qualified `f9f9fc243ceed7df09a1674f533a9cf12c7a7c53` versus latest inspected homepage QA PR #1042 `a0f403de362a8418bb77d5cf226ba5cc2daf5aec` returned:
- **status: ahead; 379 newer commits; zero behind; 159 changed files**, including 114 under `experience2/home-flagship/qa/`.
- Crucially, **actual candidate UI source changed**, not just tests: `experience2/home-flagship/index.html` (37 added/12 deleted), `flagship.css` (+118), `chronicle.css`, `observer-lab.css`.
- Source inspection identifies an additional mobile `<details>` Explore navigation, focusable chapter targets, modified chronicle/nav media behavior, observer-to-Focus contextual action, and an original editorial **NYPL source plate instead of embedded image**.

**Decision:** old genuine staging PASS is a valid historical baseline, but **cannot be inherited** by current #1042. The committed `qualification_freshness.py` deliberately returns HOLD for changed SHA and never grants release approval even for an exact SHA match. This is a lineage/qualification safeguard, not a replacement for Playwright/axe/Lighthouse.

## Published WordPress is a third, different source
Read-only WordPress.com `wpcom_user_sites(environment=all)`: only production ID **256784396**, no staging; the Personal plan's included wpcomstaging hostname is not a second environment. **Do not ask for a Business-plan clone or suggest a paid upgrade.**

Read-only published WordPress page **6**, modified **2026-11-04T14:39:24** according to WordPress, has seven chapter anchors, the Franklin editorial folio, 72 sequential Hidden in the Margins items and Focus links. **It still embeds the NYPL 1903 map derivative**, including a responsive `i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg` source. The latest GitHub candidate deliberately **does not embed** that image because capture-specific commercial reuse rights remain unresolved. See [PR #948](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/948) for source/rights review. This is an **unresolved provenance/release decision**, not a determination that production use is unlawful. No map removal or production change is authorized here.

Read-only Focus page **1579** remains published with native Jetpack signup and the 52-page Fieldbook offer. An older independent [PR #535](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/535) already covers source-only `#subscribe-blog` no-JS anchor uncertainty; **do not duplicate the work or claim a confirmed visitor-facing defect without real rendered browser evidence**.

## Immediate owner decision / evidence matrix
| Environment | BUILT | Actually TESTED | LIVE | Release significance |
|---|---|---|---|---|
| PR #637 isolated WordPress/Assembler at `f9f9fc2` | Yes | Yes, exact old SHA | No | Valuable comparison baseline, **stale for current candidate** |
| PR #1042 stack at `a0f403d` | Yes | Offline representative fixtures / source contracts reported | No | **Needs rerun on exact current SHA** |
| Published WP Page 6 | Yes | Read-only saved-source census here; browser not executed here | Yes | Never mistake public-source presence for 320px/390px/1280px CTA usability, axe or net revenue |
| Focus / Jetpack | Yes | Saved-source only this run | Yes | Confirmed subscriptions/order attribution **unknown** |

## Founder conversion directive
**Offer:** existing free Seven Day Focus Fieldbook, a **lead**, not a sale.
**Funnel:** qualified Grok asset → relevant archival evidence → unobstructed Focus header CTA → rendered Jetpack lead → independently confirmed subscriber → independently reported paid order minus fees/refunds.
**Blocker:** treating old Lighthouse/WordPress PASS or synthetic tests as current candidate acceptance can green-light an inaccessible or misleading funnel, while published NYPL media rights remain independently unresolved.
**Change:** exact-SHA lineage guard + clear three-environment handoff. **Pass/fail:** nine native Python tests pass on exact committed blob, but the current candidate returns HOLD pending a genuine private WordPress/Assembler run. **Owner:** homepage engineering and independent QD; Claude retains hosted/analytics/commerce integration; Grok/Praxxis retain social acquisition. **Commercial result:** no verified net sales, lead-to-customer conversion or attributable revenue this run.

## Release gate / safe next action
1. Re-run the already successful [#637 private WordPress/Assembler harness](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/637) **against the latest integrated candidate HEAD**, not its 2026-11-02 ancestry; include 320/390/768/1279/1280/1440/1920 as applicable, full-page screenshots, actual 200% browser zoom, no-JS, complete-document axe, keyboard/touch and real image HTTP bytes. Record exact SHA and source asset policy.
2. Use the current source's **two required archival images** (NASA & Franklin) and NYPL **original editorial source plate**, not the obsolete three-image candidate assumption; independently test what the published WP page actually serves.
3. Seek explicit capture-level NYPL reuse decision and independent QD, founder visual review, production approval. Quantify Lighthouse/CWV on the actual current candidate, not 379-commit-old metrics. WordPress Playground is **not WordPress.com host parity**, so separate hosted acceptance remains necessary.
4. No production WP writes, Jetpack form submissions, affiliate activation, marketing posts, email sends, spending, or merging under this branch. Frozen PR #49 and Apollo #158 untouched.

This source-grounded audit is coordination with Issue #150, conversion charter #818/#820 and rights #948. It does **not** claim 2026 Webby recognition, full WCAG 2.2 AA or paid conversions.
