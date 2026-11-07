# Apollo Experience 2.0 — R200 chronology evidence types (DRAFT / NOT LIVE)

Parent: R199 PR #1482, commit `d89b57bc8ea159077f6216c1d7aea50fc3fab815`. Isolated work only under `experience2/apollo-r200/`. Do not edit or merge homepage PR #49, Research Desk PR #158, or another owner’s lane.

## Improvement
The chronology had four dates and four source links but no visible differentiation between historical Board conclusions, pre-event photographs, written preparation context, and post-event photographic evidence. This is a meaningful source-custody risk: a dated photo is **not** a sensor recording or eyewitness image of ignition. R200 adds persistent, text-labeled evidence roles to the four chronology entries, a no-JS reading key, and a generated `chronology-source-ledger.json` with the specific NASA source URL, date, category, target and explicit **commercial media rights not certified** status. It changes no dated event, no source destination and no technical conclusion. No geo pins, imagery, paid product, JavaScript or tracking.

## Verification and reproducibility
```sh
python -I experience2/apollo-r200/build_r200.py
php -l experience2/apollo-r200/dist/fv-ex2-apollo-r200.php
python -I experience2/apollo-r200/qa/gate_r200.py /tmp/r200-a
python -I experience2/apollo-r200/qa/gate_r200.py /tmp/r200-b
sha256sum /tmp/r200-a/*.png /tmp/r200-b/*.png
```

Requires Python 3, bs4, playwright, PHP and Chromium at `/usr/bin/chromium`. The generator recursively builds inherited parents. The gate runs actual shortcode PHP inside a *mocked WordPress-function harness*, real Chromium Playwright/CDP accessibility tree, keyboard and touch chronology navigation, print and late fallback, 320–1920px, no-JS, reduced-motion, forced-colors and simulated CSS zoom. It rejects eight intentional mutations involving misdating, false image evidentiary status, invented purchase and paid-sales claims, and broken targets.

Local R200 run on November 7, 2026: 12/12 contexts, 48/48 navigation checks and 8/8 mutation detections per run; two independent screenshot passes had 12/12 matching PNG SHA-256 hashes. Real local Chromium was 144.0.7559.96. These are **offline fixture** checks, not installed-site acceptance. Local fixture LCP/CLS observations are not production Core Web Vitals.

**Unresolved:** exact full repo HEAD CI, installed WordPress/theme/CSP, genuine axe-core, NVDA/VoiceOver, true browser zoom and real URL/CDN navigation. R198’s local source archive was not byte-identical with its GitHub builder; reconstruct and verify the entire exact-GitHub-parent chain before release. No screenshot implies on-site approval.

## Evidence / rights boundary
- [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — ignition source not conclusively identified.
- [NASA Apollo 1 photo catalog](https://www.nasa.gov/gallery/apollo-1/) — dated photographs are not a continuous sensor recording.
- [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) — NASA source citation does not certify promotional use or endorsement.

## Conversion and owner gates
Flagship audience: viewers and educators interested in the evidence behind Apollo 1, potentially referred by a **future** approved Grok long-form asset. One editorial next action remains “Read original investigation.” An educator evidence dossier is still only a product **hypothesis**—no verified purchasable rights-cleared Apollo SKU, no confirmed partner approval, and no paid CTA. No confirmed Apollo asset_id, landing attribution, confirmed leads, paid orders or net revenue. Do not infer merchant sales from clicks.

**Offer → funnel → blocker → experiment → evidence → owner:** proposed educator dossier → purchase → no verified SKU → validate pricing/rights/checkout/fulfillment → blocked → Commerce/Claude; Grok video → Atlas → no published Apollo asset_id → reconcile TASK-008 → unverified → Grok/Praxxis; Atlas → free investigation → indistinct chronology provenance → R200 evidence-role labels → local fixture PASS → Apollo; paid purchases → realized net revenue per 1,000 qualified humans → missing 7/30-day source-linked orders/refunds/fees and visit denominator → reconcile native records with consent → not computable → Analytics. Source of truth: #150, #820, #818; Grok owns publishing, Praxxis external review, Claude production engineering and founder final release.

**HARD HOLD.** No WordPress writes, new analytics scripts, emails, affiliate activations, social publishing or unapproved deployment.