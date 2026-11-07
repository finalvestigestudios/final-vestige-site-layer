# Apollo Experience 2.0 R184 — WordPress-safe isolated adapter (DRAFT / RELEASE HOLD)

**Scope:** Issue #150, conversion/attribution #820 and charter #818. Stacked on Apollo R183 PR #1362; original Research Desk PR #158 and frozen homepage PR #49 are untouched. Grok owns creator videos, Praxxis owns creator review, Claude owns production engineering. Do not activate, install, merge, publish or add any tracking without independent staging acceptance and founder release approval.

## Material deliverable
The self-contained R183 Atlas was a full HTML document with global selectors (`body`, `:root`, `*`), `<main>` and unprefixed IDs. Dropping that document into a WordPress shortcode could pollute the theme and duplicate page landmarks. R184 includes an **executable source-pinned build generator** at `build_wp_atlas.py` which reconstructs the exact parent HTML via `../apollo-r183/reconstruct_atlas.py` and produces:

- `dist/templates/atlas-fragment.html`: one semantic `article` containing the original four dated ChronologyRail entries, four technical EvidencePlates, eight native details/SourceDrawers, four NASA-cited gallery records and **one** contextual `Read original investigation` link. Prefixes every local ID `fv-apollo-...`; turns nested `main` into a labelled region. Does not require JavaScript or include remote images/scripts.
- `dist/assets/atlas-scoped.css`: mechanically scopes every selector to `.fv-apollo-atlas` so the surrounding WP header, nav and footer do not inherit Atlas styles; maintains mobile, forced-colors and reduced-motion rules.
- `dist/fv-ex2-apollo-r184.php`: independently named shortcode `[fv_ex2_apollo_atlas]`. Registers only local generated CSS, checks immutable SHA-256 of the HTML/CSS, and **fails open** to the free original investigation if missing or altered. No content/settings writes.
- `dist/manifest.json`: identity and explicit release status.

## Reproducible build / QA (do not run against live WordPress)
```sh
python -m pip install beautifulsoup4 tinycss2 playwright
python experience2/apollo-r184/build_wp_atlas.py
php -l experience2/apollo-r184/dist/fv-ex2-apollo-r184.php
python -m unittest discover -s experience2/apollo-r184/qa -p 'test_adapter.py'
python experience2/apollo-r184/qa/browser_acceptance.py --out /tmp/apollo-r184-a
python experience2/apollo-r184/qa/browser_acceptance.py --out /tmp/apollo-r184-b
```

The browser harness exercises **real Chromium** in a *mock WordPress shell*, not an installed WP instance: 320, 360, 390, 768, 1440, 1920, JS-off, CSS+JS-off, forced-colors, reduced-motion and touch; deep links, keyboard disclosure, one CTA, external request count, overflow and screenshot SHA-256 receipts. LCP/CLS are **laboratory values only**. It does not claim genuine axe-core or screen reader acceptance.

## Historical source custody and rights
- Written technical findings, conditions, hatch and 23:31:19 GMT rupture: NASA Apollo 204 Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- October 18 1966 crew preparation NASA S66-58038, processing S67-15717, January 28 1967 aftermath NASA S67-21294: official photo catalog. Historical photos do not independently establish ignition or pressure readings. January 3 chronology comes from separate NASA written preparation history.
- Review Board found **no single conclusively identified ignition source**; electrical arc described as most probable.
- Commemorative hatch photo is retrospective, not accident-time imagery. Separate S67-19766 photo/caption match remains unconfirmed.
- No images embedded or licensed for paid promotion. NASA's advertising guidance does not permit implied NASA endorsement; identifiable astronaut likenesses can require further clearance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

## One conversion-relevant pathway, no fictitious sales
**Grok Apollo historical long-form viewer → source-grounded Atlas → free original investigation → potential original rights-cleared educator evidence kit after commerce validation.** The eventual B2B educator evidence kit is only a **product hypothesis**, not an existing verified sellable SKU. Therefore the Atlas maintains one nonintrusive *reading* action; no Payhip/Awin or unsupported checkout CTA. Actual destination response/WordPress routing remains an acceptance gate. `utm_content` must use Grok's *actual* asset ID; no fabricated publication or sessions.

Prioritized OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:
1. Educator kit → purchase → no vetted SKU/rights/checkout → validate real inventory, price, delivery, merchant transactions → **BLOCKED** → Commerce/Claude/founder.
2. Grok Apollo asset → landing → no confirmed published asset ID → TASK-008 handoff → **UNVERIFIED** → Grok/Praxxis.
3. Atlas → investigation → global CSS and nested landmarks unsafe inside WP → isolated R184 shortcode/theme scope → **BUILT; FIXTURE ONLY** → Apollo.
4. Investigation → paid offer → no approved contextual product → retain free investigation link → **HOLD** → Founder/Claude.
5. Orders → net revenue/1k qualified sessions → no reconciled denominator, fees, refunds or verified orders → governed 7/30-day source-of-truth measurement → **NOT COMPUTABLE** → Analytics.

## Release gates (ALL open)
1. Full installed Gutenberg/reusable shortcode acceptance in an approved nonproduction WordPress instance, including late stylesheet enqueue/CSP, theme/Jetpack compatibility and shortcode fallback.
2. Genuine axe-core + keyboard/Safari VoiceOver/NVDA testing; real media network/404 and source match review; real page LCP/CLS/INP and WCAG 2.2 AA evaluation.
3. Exact GitHub head build/unit/browser CI and independent QD review. A locally source-equivalent fixture pass is **not** exact-head CI.
4. Founder approval for any production action; separately verify offers, NASA rights, real checkout and merchant-confirmed paid revenue. No release by default.

**IMPORTANT:** No WordPress content/settings changes, theme edits, homepage PR modifications, paid services, audience tracking scripts, external media embeds, or social posting are part of this draft.
