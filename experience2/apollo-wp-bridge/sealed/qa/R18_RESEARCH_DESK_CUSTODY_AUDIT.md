# Apollo Experience 2.0 R18 — Independent Research Desk source-custody reconciliation

**2026-10-31 • DRAFT / HOLD • Issue #150 • stacked on Apollo R17 PR #288**

## Observed cross-lane finding

Independently read Research Desk PR #158 at immutable commit `250d7f05a4de037e73826dcf0cfaef0ec4c29383`; `experience2/research-desk/templates/ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c`. Compared its six NASA image-detail links to Apollo canonical PR #215 (`74375657f2cdaac0710f94c6de6c24534ee06858`) source records.

All six URLs match **as literal source links**. The first identifier label **does not** match: the Research Desk says `NASA S67-19766` while the pinned casefile calls it `Apollo 1 crew training portrait`. The linked NASA source is titled *Apollo 1 Crew Honored* and describes a January 1967 crew training image; the exact accession code is **not established by this comparison**. Treat it as an editorial review hold, **not** as proof either label is correct. The five other labels match textually (after stripping the shared `NASA ` prefix), which is not independent archive verification.

## Implementation scope

- Added native `<details>` read-only Research Desk comparison: six links to NASA catalog originals, six links to Apollo SourceDrawer, one pinned GitHub source-code reference and one prominent unresolved identifier-label hold. No JS dependency; two-column cards collapse to one in narrow WordPress blocks.
- Added `qa/pr158_research_desk_witness.json` pinned to PR #158 exact Git SHA and ledger blob. Audit refuses URL/record-order/rights changes and silently resolved/masked catalog-label disagreement.
- Added per-record PR158 comparison metadata to existing private, SHA-256-verified source-context JSON. `editorial_findings_equivalence` stays NOT_ASSERTED; `media_reuse_rights` NOT_CLEARED; coordinates NONE. No independent Research Desk plugin or live WordPress writes.
- Enforced exactly six crosswalk records and one identifier-label review hold in both protected PHP page admission and the read-only HTTP staging auditor. Existing content and original archive data are unchanged.
- Tests and browsers updated to distinguish original six-source concordance controls from the expanded native crosswalk controls. Source-controlled QA receipts and deterministic build included.

## Executed local QA

- `python -m unittest discover -s qa -p 'test_*.py' -q` — **90 tests passed**, including eight new cross-lane adversarial, provenance, no-JS, escaping and export assertions.
- `python qa/browser_exact.py` — **7/7 real Chromium Playwright viewports passed**, widths 320/360/390/768/1024/1440/1920; original chronology/gallery/Atlas/source navigation, JS and no-JS, keyboard/touch/reduced-motion and synthetic 200%-equivalent zoom. Exact PHP built from verified source pins. Synthetic LCP/CLS are not hosted CWV.
- `python qa/browser_dual_witness_r17.py` — **7/7 Chromium widths passed**, including narrow CMS 420px embed with JS disabled.
- `python qa/browser_crosswalk_r18.py` — **7/7 Chromium widths passed**, 390px no-JS and 420px constrained desktop container; keyboard/summary, six source links, original SourceDrawer and visible label hold. Two reproducible screenshots.
- `python qa/ax_tree_r16.py` — **7/7 Chromium CDP accessibility-tree audits passed** with 187 named actionable elements at baseline/width and 13 new named links when native crosswalk opens; no duplicate IDs or broken internal fragments; not axe/WCAG certification.
- `python build_sealed.py --out ...` twice — byte-for-byte deterministic ZIP SHA-256 `e15a2d230731b3edbb382b49fc73b74a645a7f88703dbb7c9cf09dfaebf702fa`; built plugin PHP SHA-256 `1bbb95c0dc09b12ec51762447bf2c0be45f1dd1f3c0368a1429d6acee5620f28`.

## Non-waivable blockers

**HOLD.** No verified official axe-core bundle, hence strict axe gate not run (must fail closed). WordPress.com production has not been changed; no true installed WordPress staging/Assembler/Jetpack. Browser `page.goto()` to even intercepted test HTTPS is blocked by the environment (`ERR_BLOCKED_BY_ADMINISTRATOR`), so HTTP CSP/cookie/frame-ancestor enforcement remains unverified in Chromium. PHP HTTP tests use a synthetic WP stub, not a WordPress install. No hosted CWV, Safari/VoiceOver/NVDA, independent QD, green CI on exact new head, founder visual signoff or per-media rights approval. No NASA photographs copied. No map pins or speculative connection edges. **Do not merge, install or deploy.**

NASA references: https://www.nasa.gov/image-detail/apollo-1-crew-honored/ ; https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; https://www.nasa.gov/nasa-brand-center/ .
