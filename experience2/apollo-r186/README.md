# Apollo Experience 2.0 / R186 — accessible named regions

**Unpublished; staging hold.** R186 repairs four broken `aria-labelledby` references inherited from R184's ID namespacing and R185's WordPress adapter. No homepage edits, production CMS writes, new trackers, third-party images, affiliate activations, or publishing.

## Reproduced defect

Existing R185 sections refer to `page-title`, `chronology-title`, `evidence-title` and `gallery-title`; their heading IDs are actually `fv-apollo-page-title`, `fv-apollo-chronology-title`, `fv-apollo-evidence-title`, `fv-apollo-gallery-title`. R186 changes **only those four attribute values**, preserves all historical text, chronology, 4 EvidencePlates, 4 NASA archive records, 8 native disclosures, CSS, the original links and single free investigation CTA. This restores four named regions in Chromium's accessibility tree.

## Build and test in full repository checkout

```sh
python experience2/apollo-r186/build_r186.py
php -l experience2/apollo-r186/dist/fv-ex2-apollo-r186.php
python -m unittest discover -s experience2/apollo-r186/qa -p 'test_*.py' -v
python experience2/apollo-r186/qa/browser_acceptance.py --out /tmp/apollo-r186-A
python experience2/apollo-r186/qa/browser_acceptance.py --out /tmp/apollo-r186-B
```

The builder uses R185/R184/R183 source-controlled generators, refuses mismatched SHA-256 parent assets, and writes an ignored local `dist/` plugin, not a deployed component. The optional `--reuse-r185-dist` flag uses previously generated, **hash-verified** R185 assets for offline testing.

## Evidence (2026-11-07)

Source-equivalent local archive tests: 7 Python unit tests PASS, PHP lint PASS, two full real Playwright/Chromium fixture runs with 148/148 assertions each across 12 browser contexts (320–1920px, no-JS/no-CSS, keyboard, touch, forced colors, reduced motion, 200% zoom simulation); 12/12 screenshot hashes match across runs. Chromium CDP accessibility tree confirmed all four corrected named regions. Laboratory fixture LCP 72–172ms / CLS 0; **not** production CWV.

**Not verified:** exact-head CI, genuine axe-core, NVDA/VoiceOver, installed WordPress, CDN NASA media decoding, real theme/CSP/cache, real Grok published asset attribution, actual product checkout, paid sales, or net revenue. Staging and founder release approval remain mandatory.

## Business bridge — no invented commerce

Flagship: Apollo 1 for an evidence-based long-form Grok audience of educators/history enthusiasts. Atlas landing → one free **Read original investigation** CTA → potential rights-cleared original educator dossier **only if** product, delivery, checkout, rights and price are verified. There is **no approved existing Apollo paid SKU**. Do not insert unrelated affiliate offers. Attribution: `utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=<approved_Grok_asset_id>` only on verified Grok links. Count qualified human sessions → CTA → confirmed lead if applicable → actual orders less refunds/fees → net revenue/1000 sessions for 7/30-day cohorts; otherwise report unknown.

Source/provenance: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (ignition not conclusively established); [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) (no implied endorsement/automatic likeness rights).

Governance: Issue #150; conversion #820; business #818; Grok/Praxxis TASK-008. Never activate R185 and R186 plugins together; same shortcode. Homepage frozen PR #49 and Research Desk PR #158 are untouched. Independent QD, actual staging with axe+AT, and exact-head CI precede any release.
