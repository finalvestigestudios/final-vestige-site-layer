# Apollo Experience 2.0 / R382 — filter-aware chronology navigation

**Status:** BUILT and Chromium contract tested locally, DRAFT ONLY. No installed WordPress/Assembler, real staging HTTPS/CSP, axe-core, screen reader, hosted exact-HEAD CI, commercial checkout or production acceptance.

## Verified defect and fix

The curated R381 Evidence Atlas filters source plates and hides entire chronology phases, but leaves all three chronology navigation links visible. A user selecting the `response` facet could follow a still-visible link to a hidden 1967 phase. In a keyboard/screen-reader source-navigation experience this is a dead destination.

R382 patches **only our curated R381** progressive enhancement. Its three chronology `<li>` navigation items now track visibility of their corresponding source phase. The initial/no-JS state keeps all sources and links visible. Reset restores every source, phase and navigation item and focuses the selector. A repeated script load does not duplicate listeners; if a runtime error occurs mid-filter, the component restores all records, all phases and all links and hides broken enhanced controls. There is no network, cookie, data capture, map pin, outside image or added purchase CTA. The verified source-custody JSON and six NASA citations are unchanged.

The companion R381 PHP SHA-256 pin is updated for the exact tested JS byte sequence, so a stale or unexpectedly changed script cannot pass asset verification.

## Actual verification / boundaries

- `python experience2/apollo-r382/qa/smoke.py` — self-contained, true Chromium on a local source-custody-derived DOM contract, five viewport widths, 30 checks, PASS.
- Extended `qa/run.py` in the separate review artifact — ten Chromium local contexts, 189 checks, screenshots at 320, 390, 768, 1440 and 1920 px plus no-JS, touch, reduced-motion, forced-colors, 4x root-font stress; PASS. The extended fixture is intentionally **not** an installed WP page, native 400% browser zoom or field CWV.
- R377 custody expected SHA-256: `60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f`.
- Exact R382 script SHA-256: `5a4d82f76a06b9c3781c522d0b2483a3ef36c21a897a0cb0b3a1f742992a5105`.
- Genuine axe-core, independent screen readers, installed WordPress/Assembler, actual SSL/CSP, hosted CI and actual conversion/revenue: **NOT VERIFIED**.

## PR ownership collision to resolve BEFORE merge

Both draft PR **#2603** (R381 conversion bridge) and **#2607** (R381 curated Atlas) independently add **different files under the same `experience2/apollo-r381/` paths**. This R382 fix stacks ONLY on #2607. Do not merge both R381 drafts unchanged: the reused directory and README are incompatible. Maintain the separate #2603 concept as unmerged research or re-scope/rebase it only after a reviewer establishes component coexistence and unique asset paths. No edits to #2603, homepage PR #49, Research Desk PR #158 or Grok/Praxxis TASK-008 are authorized here.

## Conversion contract / release hold

One reader pathway: founder-approved Grok Apollo film -> source-sealed Evidence Atlas -> free existing Apollo investigation -> separately verified and approved educator product. A paid offer is **not yet confirmed**; do not add purchase CTA. Without asset-ID sessions, verified merchant sales/refunds/fees and consent-safe attribution, revenue per 1,000 qualified sessions is **not computable**. Founder and QA control production release; Claude owns core WordPress/commercial engineering. No WordPress, merchant, social, email or analytics writes from this branch.
