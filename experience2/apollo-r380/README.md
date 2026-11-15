# Apollo Experience 2.0 · R380 — strict source-template dependency graph

**BUILT; local PHP API-stub and Chromium fixture QA only. DRAFT, HARD HOLD.**

## Security and usability regression identified in actual R379 code

The R379 resolved-template walker used one `visited` set and skipped already-seen references. This incorrectly treated a live recursion cycle as equivalent to a legitimate shared sibling reference. It also silently ignored malformed/missing/draft/foreign template-part and reusable-block references. If any other sibling contained a valid Apollo shortcode, the walker could still return **true** and enqueue R377 CSS despite the unresolved dependency. The claimed cycle rejection held only for fixtures with no separate shortcode sibling.

R380 is a **targeted correction to our own Apollo R379 guard**, not a new parallel plugin. It introduces an `active` recursion-path set plus a completed `visited` set. Cycles, malformed IDs, draft/missing/foreign dependencies and invalid reusable-block refs poison the scan, even if another sibling contains the expected shortcode. Repeated but acyclic template parts remain valid; the 7-level, 200-node, 1MiB limits and staging-only host/shortcode/source/CSS checks remain. No shortcode, new scripts, analytics, photos, map pins or commerce links are introduced. The existing free investigation CTA and the NASA source-role distinctions are preserved. This change does **not** claim the WordPress renderer cannot use legitimate unresolved dynamic references; it deliberately opts out rather than guess.

## Reproduction

Requires the stacked R377 → R378 → R379 files, PHP 7.4+, Python 3 with Playwright and installed Chromium at `/usr/bin/chromium`. From repository root:

```
python3 experience2/apollo-r380/qa/run.py
```

Regression matrix: 5 legitimate graph cases (including a DAG with a shared part), 6 adversarial graphs with a misleading valid shortcode sibling (two cycles, missing/draft/foreign parts, malformed reusable reference), 15 existing negative cases. A failing check returns nonzero. The local browser suite re-executes 10 real Chromium contexts from R379 (320–1920px, no-JS, keyboard, touch, reduced motion, forced colors, 4x root font, print source visibility), copying reproducible screenshots into R380/QA. The 4x root-font mode is **not** native browser zoom. No real axe-core or installed site claims.

## Owner/release and conversion gate

- **Grok/Praxxis:** video/short asset_id + link inventory and independent creator QA in TASK-008; no takeover of posting.
- **Apollo QA:** independently verify R377 NASA custody and the graph; rerun on an *approved installed* WordPress/Assembler staging URL with real HTTP/CSP, genuine axe-core, native 400% zoom, screen readers and CI before release.
- **Founder/Claude:** verify rights-cleared payable educator SKU, approved merchant checkout/delivery, refund and fees evidence before any paid CTA. Do not imply NASA endorsements or reproduction rights.
- **Commerce:** attribute verified qualified human sessions → relevant CTA clicks → confirmed leads where applicable → merchant-confirmed paid orders → refunds/fees → realized net revenue per 1,000 qualified sessions, with 7/30-day cohorts. All currently **NOT OBSERVABLE** in this lane.

The *one* proposed relevant pathway is Grok's approved Apollo long-form → source-role Research Desk → existing free Apollo investigation → educator dossier **only if separately rights-cleared and commerce-approved**. The hypothesis is that trustworthy document custody improves educator purchase qualification; uplift is unmeasured. No paid CTA is included.

**Strict release gate:** no merged site code, WordPress content/settings writes, analytics scripts, email, social posting, merchant activation or production deployment. Leave frozen homepage PR #49 and Research Desk PR #158 untouched. Track #150, #820 and #818.
